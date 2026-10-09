#!/usr/bin/env python3
"""Read new lines from a Claude Code session transcript file and turn them
into the entries the server stores (RMP-27/RMP-44,
docs/plugin-v2/01c-session-transcript.md §3).

Two separate jobs, kept apart so each is testable alone (P1636 wires them
together and calls `transcript_redaction.redact_text` on every entry's text
before it is uploaded -- redaction does NOT happen here):
  - `read_new_lines`: read complete JSONL lines from a byte offset onward.
  - `to_entries`: turn those parsed lines into the exact 9-key entry shape
    the server (`agent_session_transcript_store._ENTRY_KEYS`) accepts.

FAIL-SAFE: this runs inside a hook on the customer's machine. Neither public
function raises -- a missing/unreadable file, a malformed line, or an
unexpected shape degrades to "nothing" (an empty result), never a crash.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

import plugin_api


def _keep_result_text_re() -> "re.Pattern[str]":
    """A tool_result's text is kept only for OUR OWN plugin's MCP tools
    (`reachmachine`/`apify`/`playwright`) or the built-in `AskUserQuestion`/
    `Skill` tools -- everything else (including a foreign plugin's
    same-named server, RMP-177) is dropped unless it errored. Recomputed on
    every call, not cached at import time, for the same reason as
    `plugin_api.server_of`: a stale plugin name would either upload a
    foreign plugin's tool output as if it were ours, or silently drop our
    own after a rename."""
    name = re.escape(plugin_api.plugin_name())
    return re.compile(
        rf"^(mcp__plugin_{name}_(reachmachine|apify|playwright)__.+|AskUserQuestion|Skill)$"
    )


_CUSTOMER_CAP = 20_000
_AGENT_CAP = 20_000
_TOOL_CALL_CAP = 1_000
_TOOL_RESULT_CAP = 2_000
_PLUGIN_NOTE_CAP = 2_000
_MARKER_TEXT = "The conversation was shortened here."


def read_new_lines(path: str, byte_offset: int) -> tuple[list[dict], int]:
    """Read complete JSONL lines from *byte_offset* onward.

    A last line with no trailing newline yet is NOT consumed -- Claude Code
    may still be writing it. A line that is not valid JSON (or not a JSON
    object) is skipped but still counted as consumed, so it is never
    re-read. Missing/unreadable file -> ([], byte_offset) unchanged.
    `byte_offset` past the current file size (file replaced/rotated)
    restarts from 0.
    """
    try:
        try:
            size = os.path.getsize(path)
        except OSError:
            return [], byte_offset
        start = byte_offset if 0 <= byte_offset <= size else 0
        with open(path, "rb") as fh:
            fh.seek(start)
            data = fh.read()

        lines: list[dict] = []
        pos = 0
        consumed = 0
        while True:
            newline_at = data.find(b"\n", pos)
            if newline_at == -1:
                break  # remainder (if any) is an unfinished line -- not consumed
            raw = data[pos:newline_at]
            consumed = newline_at + 1
            pos = newline_at + 1
            stripped = raw.decode("utf-8", errors="replace").strip()
            if not stripped:
                continue
            try:
                obj = json.loads(stripped)
            except Exception:
                continue
            if isinstance(obj, dict):
                lines.append(obj)
        return lines, start + consumed
    except Exception:
        return [], byte_offset


def _cap(text: str, limit: int) -> tuple[str, bool]:
    if len(text) > limit:
        return text[:limit], True
    return text, False


def _entry(
    uuid: str, block_index: int, seq: int, at: Any, kind: str, text: Any, *,
    tool_name: str | None = None, is_error: bool | None = None,
    text_chars: int | None = None, truncated: bool = False,
) -> dict:
    return {
        "entry_id": f"{uuid}:{block_index}", "seq": seq, "at": at, "kind": kind,
        "text": text, "tool_name": tool_name, "is_error": is_error,
        "text_chars": text_chars, "truncated": truncated,
    }


def _flatten_tool_result_content(content: Any) -> str:
    """A tool_result's `content` is a plain string, or a list of blocks --
    flatten by joining the `text` of `{"type": "text"}` items (spec §3).
    Anything else flattens to ``""``."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            b.get("text", "") for b in content
            if isinstance(b, dict) and b.get("type") == "text" and isinstance(b.get("text"), str)
        )
    return ""


def _user_line_entries(
    line: dict, uuid: str, at: Any, seq: int, tool_names_by_id: dict[str, str],
) -> tuple[list[dict], int]:
    entries: list[dict] = []
    if line.get("isCompactSummary") is True:
        return [_entry(uuid, 0, seq, at, "marker", _MARKER_TEXT)], seq + 1

    message = line.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    is_meta = line.get("isMeta") is True

    if isinstance(content, str):
        if is_meta and content.startswith("Stop hook feedback:"):
            text, trunc = _cap(content, _PLUGIN_NOTE_CAP)
            entries.append(_entry(uuid, 0, seq, at, "plugin_note", text, truncated=trunc))
            seq += 1
        elif not is_meta:
            text, trunc = _cap(content, _CUSTOMER_CAP)
            entries.append(_entry(uuid, 0, seq, at, "customer", text, truncated=trunc))
            seq += 1
        # else: skip -- some other isMeta shape (skill bodies, etc.)
    elif isinstance(content, list):
        for idx, block in enumerate(content):
            if not isinstance(block, dict) or block.get("type") != "tool_result":
                continue
            tool_use_id = block.get("tool_use_id")
            tool_name = tool_names_by_id.get(tool_use_id) if isinstance(tool_use_id, str) else None
            is_error = bool(block.get("is_error"))
            flat = _flatten_tool_result_content(block.get("content"))
            keep = is_error or bool(tool_name and _keep_result_text_re().match(tool_name))
            text, trunc = _cap(flat, _TOOL_RESULT_CAP) if keep else (None, False)
            entries.append(_entry(
                uuid, idx, seq, at, "tool_result", text, tool_name=tool_name,
                is_error=is_error, text_chars=len(flat), truncated=trunc,
            ))
            seq += 1
    return entries, seq


def _assistant_line_entries(
    line: dict, uuid: str, at: Any, seq: int, tool_names_by_id: dict[str, str],
) -> tuple[list[dict], int]:
    entries: list[dict] = []
    message = line.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, list):
        return entries, seq
    for idx, block in enumerate(content):
        if not isinstance(block, dict):
            continue
        block_type = block.get("type")
        if block_type == "text":
            raw_text = block.get("text")
            text, trunc = _cap(raw_text if isinstance(raw_text, str) else "", _AGENT_CAP)
            entries.append(_entry(uuid, idx, seq, at, "agent", text, truncated=trunc))
            seq += 1
        elif block_type == "tool_use":
            tool_id, tool_name = block.get("id"), block.get("name")
            if isinstance(tool_id, str) and isinstance(tool_name, str):
                tool_names_by_id[tool_id] = tool_name
            try:
                input_json = json.dumps(block.get("input", {}), ensure_ascii=False)
            except Exception:
                input_json = ""
            text, trunc = _cap(input_json, _TOOL_CALL_CAP)
            entries.append(_entry(
                uuid, idx, seq, at, "tool_call", text,
                tool_name=tool_name if isinstance(tool_name, str) else None, truncated=trunc,
            ))
            seq += 1
        # thinking, server_tool_use, advisor_tool_result, anything else: skip
    return entries, seq


def _attachment_line_entries(line: dict, uuid: str, at: Any, seq: int) -> tuple[list[dict], int]:
    attachment = line.get("attachment")
    if not isinstance(attachment, dict):
        return [], seq
    kind = attachment.get("type")
    if kind == "hook_additional_context":
        content = attachment.get("content")
        joined = "\n".join(str(c) for c in content) if isinstance(content, list) else ""
        text, trunc = _cap(joined, _PLUGIN_NOTE_CAP)
    elif kind == "hook_blocking_error":
        blocking_error = attachment.get("blockingError")
        message = blocking_error.get("blockingError") if isinstance(blocking_error, dict) else None
        text, trunc = _cap(message if isinstance(message, str) else "", _PLUGIN_NOTE_CAP)
    else:
        return [], seq  # any other type (system prompt, skill listing, tool list, ...): skip
    return [_entry(uuid, 0, seq, at, "plugin_note", text, truncated=trunc)], seq + 1


def to_entries(
    lines: list[dict], *, start_seq: int, tool_names_by_id: dict[str, str]
) -> tuple[list[dict], int]:
    """Turn parsed transcript lines into stored entries (spec §3 table,
    exactly). `tool_names_by_id` maps a `tool_use` id to its tool name; it is
    both read from and updated in place, because a `tool_result` can arrive
    in a later batch than its `tool_use` (P1636 persists this dict across
    calls in the session's cursor file)."""
    entries: list[dict] = []
    seq = start_seq
    try:
        for line in lines:
            if not isinstance(line, dict) or line.get("isSidechain") is True:
                continue
            line_type = line.get("type")
            if line_type not in ("user", "assistant", "attachment"):
                continue
            uuid = line.get("uuid")
            if not isinstance(uuid, str) or not uuid:
                continue
            at = line.get("timestamp")

            if line_type == "user":
                new_entries, seq = _user_line_entries(line, uuid, at, seq, tool_names_by_id)
            elif line_type == "assistant":
                new_entries, seq = _assistant_line_entries(line, uuid, at, seq, tool_names_by_id)
            else:
                new_entries, seq = _attachment_line_entries(line, uuid, at, seq)
            entries.extend(new_entries)
        return entries, seq
    except Exception:
        return entries, seq
