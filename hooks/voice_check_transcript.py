#!/usr/bin/env python3
"""RMP-159: collect every assistant TEXT block of the CURRENT turn, not just
the final one.

Bug it fixes (live, 2026-09-26): a customer saw internal narration ("the
hook instructs it...", "held elsewhere per the last check") in a text block
that came BEFORE a tool call, in the middle of a multi-step turn.
`voice_check.py` used to check only `last_assistant_message` -- the Stop
payload's own field for "text of the last assistant message before
stopping" -- which is the LAST text block Claude Code wrote, not every text
block the customer actually saw during the turn. A turn can have several
assistant JSONL lines (one per tool round-trip), and each one can carry its
own `text` block before a `tool_use` block. All of those text blocks reach
the customer's screen; only the LAST one was ever checked.

Reads the transcript file (JSONL -- one line per message) from the END,
capped at `TRANSCRIPT_TAIL_CAP_BYTES`, so a long session's history is never
fully re-read on every `Stop`. Finds the last REAL customer message (a
`"user"` line whose `message.content` is a plain string and is not one of
this plugin's own `isMeta` notes -- see `transcript_extract.py`'s identical
shape) and returns every `"type": "text"` block from every `"assistant"`
line AFTER that point, in order. A `"tool_use"` block's `input` is never
included -- that JSON is sent to a tool, never shown to the customer.

FAILS SAFE: any read/parse problem returns `None`. The caller
(`voice_check.py`) then falls back to `last_assistant_message`, same as
before this file existed -- never a crash, never a reply held up.
"""
from __future__ import annotations

import json
import os

# A generous cap, not a tight one: big enough to hold a normal multi-tool-call
# turn's text blocks, small enough that a huge/ancient session transcript is
# never fully re-read on every single `Stop`.
TRANSCRIPT_TAIL_CAP_BYTES = 200_000


def _read_tail(path: str, cap_bytes: int) -> str | None:
    try:
        size = os.path.getsize(path)
    except OSError:
        return None
    try:
        with open(path, "rb") as fh:
            if size > cap_bytes:
                fh.seek(size - cap_bytes)
            data = fh.read()
    except OSError:
        return None
    text = data.decode("utf-8", errors="replace")
    if size > cap_bytes:
        # The read very likely starts mid-line -- drop that partial line.
        _, _, text = text.partition("\n")
    return text


def _is_real_customer_message(line: dict) -> bool:
    """A genuine customer chat message -- NOT a tool result (those are also
    `"type": "user"` lines, but with a list `content`) and NOT one of this
    plugin's own `isMeta` notes (e.g. "Stop hook feedback: ...")."""
    if line.get("type") != "user" or line.get("isMeta") is True:
        return False
    message = line.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    return isinstance(content, str) and bool(content.strip())


def _assistant_text_blocks(line: dict) -> list[str]:
    message = line.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, list):
        return []
    blocks = []
    for block in content:
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text")
            if isinstance(text, str) and text:
                blocks.append(text)
    return blocks


def _non_sidechain_lines(transcript_path: str) -> list[dict] | None:
    """The tail-capped transcript, parsed to JSON objects, sidechain lines
    dropped -- the shared first step of both `collect_turn_text_blocks` and
    `last_assistant_message_blocks` (RMP-198). Returns `None` on any
    read/parse failure."""
    raw = _read_tail(transcript_path, TRANSCRIPT_TAIL_CAP_BYTES)
    if raw is None:
        return None
    lines: list[dict] = []
    for raw_line in raw.splitlines():
        stripped = raw_line.strip()
        if not stripped:
            continue
        try:
            obj = json.loads(stripped)
        except Exception:
            continue
        if isinstance(obj, dict) and obj.get("isSidechain") is not True:
            lines.append(obj)
    return lines


def collect_turn_text_blocks(transcript_path: str) -> list[str] | None:
    """Every assistant text block since the last real customer message, in
    order. Returns `None` on any read/parse failure -- the caller falls back
    to `last_assistant_message`."""
    try:
        lines = _non_sidechain_lines(transcript_path)
        if lines is None:
            return None

        boundary = -1
        for idx, line in enumerate(lines):
            if _is_real_customer_message(line):
                boundary = idx

        blocks: list[str] = []
        for line in lines[boundary + 1:]:
            if line.get("type") == "assistant":
                blocks.extend(_assistant_text_blocks(line))
        return blocks
    except Exception:
        return None


def last_assistant_message_blocks(transcript_path: str) -> tuple[str | None, list[str]] | None:
    """RMP-198: `(uuid, text_blocks)` of the SINGLE most recent assistant
    message in the transcript -- every `"text"` block in ITS content, in
    order. `uuid` is that message's own transcript line id (or `None` if it
    has none), used by the caller to scan each assistant message at most
    once even if it holds several `tool_use` blocks (parallel tool calls
    all see the SAME last message).

    This is the narration a `PreToolUse`-adjacent scan needs: live evidence
    (prompts/COMMS.md, 2026-09-28) showed a leaked line and the tool_use
    that followed it were TWO CONTENT BLOCKS OF THE SAME ASSISTANT MESSAGE
    -- `collect_turn_text_blocks` above only ever re-discovers that message
    once the WHOLE turn ends and `Stop` fires, by which point the customer
    has already seen it stream, possibly several tool round-trips earlier.
    Scanning the last message on every tool call (see
    `voice_check_midturn.py`) catches it within one tool round-trip
    instead. Returns `None` on any read/parse failure, or when there is no
    assistant line at all -- same fail-safe contract as
    `collect_turn_text_blocks`."""
    try:
        lines = _non_sidechain_lines(transcript_path)
        if lines is None:
            return None
        last: dict | None = None
        for line in lines:
            if line.get("type") == "assistant":
                last = line
        if last is None:
            return None
        # RMP-159/RMP-198 (real transcript shape, checked 2026-09-29): Claude
        # Code writes ONE jsonl line per content block -- the text block and
        # the tool_use that follows it are separate lines sharing one
        # `message.id`. Reading only the last line found the tool_use and no
        # text, so this scan was a silent no-op on real sessions. Group every
        # line of the last message by that id (fallback: last line alone).
        msg = last.get("message")
        mid = msg.get("id") if isinstance(msg, dict) else None
        mid = mid if isinstance(mid, str) and mid else None
        group = [
            ln for ln in lines
            if ln.get("type") == "assistant" and isinstance(ln.get("message"), dict)
            and ln["message"].get("id") == mid
        ] if mid else [last]
        uuid = mid or last.get("uuid")
        uuid = uuid if isinstance(uuid, str) and uuid else None
        blocks: list[str] = []
        for ln in group:
            blocks.extend(_assistant_text_blocks(ln))
        return uuid, blocks
    except Exception:
        return None
