#!/usr/bin/env python3
"""The `Stop`-hook voice checker (RMP-14, RMP-15, RMP-49, RMP-159).

Spec: docs/plugin-v2/00-voice.md, "Enforcement". This is a SAFETY NET, not
the main tool -- the main tool is the rules block at the top of every skill
file. This file only catches what the model forgot.

STOP HOOK INPUT (Claude Code 2.1.281, confirmed via the bundled CLI's own
zod schema): a `Stop` payload carries `session_id`, `transcript_path`,
`prompt_id`, `stop_hook_active: bool`, and `last_assistant_message: str,
optional` -- the LAST text block Claude Code wrote. RMP-159:
`_turn_text_to_check` prefers every assistant text block of the current
turn instead (`voice_check_transcript.collect_turn_text_blocks`, every
block since the last real customer message), falling back to
`last_assistant_message` only when that returns nothing.

RULES (docs/plugin-v2/00-voice.md): a paragraph is a non-empty,
non-heading/bullet/numbered/table/blockquote line outside a code fence with
more than 25 words. A jargon hit is a whole-word/phrase match from
`voice/jargon.json`'s `avoid_terms`, ignoring backticks/code fences/`allow`.
RMP-76: an internal-term hit is a whole-word match from `internal_terms` --
checked EVERYWHERE, including inside backticks (one exception, see
`voice_check_internal.py`); a code fence is still skipped.

RMP-49: jargon/paragraph misses never block -- logged, with a note the
UserPromptSubmit reminder delivers next turn. RMP-159 part 5 added a block
for a genuine internal-name leak (the `leak` flag); part 6 (founder,
2026-09-26) turned it OFF BY DEFAULT -- a live test found it cannot un-show
an already-streamed line and costs an extra turn. Code stays, gated by
`voice_check_block.BLOCK_LEAKS_ENV`.

FAILS OPEN, on purpose -- the opposite of `connections_gate.py`. A crash,
a missing jargon.json, or missing python means NO note and NO block: this
checker must never be the reason a customer gets stuck. Every function
here catches its own exceptions and `main()` wraps everything again.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from typing import Any

import connection_state as cs
import voice_check_block as vcb
import voice_check_transcript as vct
from voice_check_internal import internal_term_hits_in_line
from voice_check_log import (  # noqa: F401 -- MISSES_FILENAME/MISSES_MAX_LINES re-exported for tests
    MISSES_FILENAME,
    MISSES_MAX_LINES,
    append_entry,
)

REMINDER_LINE = "Reply in simple English: short bullets, no jargon."
MAX_ITEMS_SHOWN = 3

_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s")
_BULLET_RE = re.compile(r"^\s*[-*+]\s")
_NUMBERED_RE = re.compile(r"^\s*\d+[.)]\s")
_TABLE_RE = re.compile(r"^\s*\|")
_BLOCKQUOTE_RE = re.compile(r"^\s*>")
_FENCE_RE = re.compile(r"^\s*```")
_BACKTICK_SPAN_RE = re.compile(r"`[^`]*`")


def _jargon_path() -> pathlib.Path:
    return pathlib.Path(__file__).resolve().parent.parent / "voice" / "jargon.json"


_EMPTY_JARGON: dict[str, Any] = {"avoid_terms": [], "allow": [], "internal_terms": []}


def load_jargon() -> dict[str, Any]:
    """Fails to the safe empty shape (nothing flagged) on any error --
    a missing or broken jargon.json must never block a reply."""
    try:
        data = json.loads(_jargon_path().read_text(encoding="utf-8"))
    except Exception:
        return dict(_EMPTY_JARGON)
    if not isinstance(data, dict):
        return dict(_EMPTY_JARGON)
    avoid_terms = data.get("avoid_terms")
    allow = data.get("allow")
    internal_terms = data.get("internal_terms")
    return {
        "avoid_terms": avoid_terms if isinstance(avoid_terms, list) else [],
        "allow": allow if isinstance(allow, list) else [],
        "internal_terms": internal_terms if isinstance(internal_terms, list) else [],
    }


def _phrase_pattern(phrase: str) -> re.Pattern[str]:
    tokens = phrase.split()
    body = r"[\s-]+".join(re.escape(t) for t in tokens)
    return re.compile(r"(?<![\w-])" + body + r"(?![\w-])", re.IGNORECASE)


def is_paragraph(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    for pattern in (_HEADING_RE, _BULLET_RE, _NUMBERED_RE, _TABLE_RE, _BLOCKQUOTE_RE):
        if pattern.match(line):
            return False
    return len(stripped.split()) > 25


def _mask_allowed(text: str, allow: list[str]) -> str:
    """Blanks out every allowed name/phrase FIRST, longest first, so a
    two-word name like "Reach Machine" can never leave a dangling "Reach"
    that then false-positives against the bare jargon word "reach"."""
    masked = text
    for phrase in sorted((p for p in allow if isinstance(p, str) and p), key=len, reverse=True):
        masked = _phrase_pattern(phrase).sub(lambda m: " " * len(m.group(0)), masked)
    return masked


def jargon_hits_in_line(line: str, avoid_terms: list[dict], allow: list[str]) -> list[tuple[str, str]]:
    """Returns `(matched_variant, say)` pairs, at most one per jargon row."""
    text = _BACKTICK_SPAN_RE.sub(lambda m: " " * len(m.group(0)), line)
    text = _mask_allowed(text, allow)
    hits: list[tuple[str, str]] = []
    for entry in avoid_terms:
        if not isinstance(entry, dict):
            continue
        variants = entry.get("avoid")
        say = entry.get("say")
        if not isinstance(variants, list) or not isinstance(say, str):
            continue
        for variant in variants:
            if not isinstance(variant, str) or not variant:
                continue
            if _phrase_pattern(variant).search(text):
                hits.append((variant, say))
                break
    return hits


def check_message(text: str, jargon: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """The full rule set applied to one reply. Returns problems in line
    order: `{"line": n, "kind": "paragraph"|"jargon"|"internal", "detail":
    str, "say": str|None}`, plus `"term": str, "leak": bool` on `"internal"`
    problems (what `voice_check_block` blocks on, when enabled)."""
    if jargon is None:
        jargon = load_jargon()
    avoid_terms = jargon.get("avoid_terms", [])
    allow = jargon.get("allow", [])
    internal_terms = jargon.get("internal_terms", [])

    problems: list[dict[str, Any]] = []
    in_fence = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        if _FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if is_paragraph(line):
            words = len(line.strip().split())
            problems.append({
                "line": line_no, "kind": "paragraph",
                "detail": f"line {line_no} is a paragraph ({words} words)",
                "say": None,
            })
        for variant, say in jargon_hits_in_line(line, avoid_terms, allow):
            problems.append({
                "line": line_no, "kind": "jargon",
                "detail": f"line {line_no} uses jargon \"{variant}\"",
                "say": say,
            })
        # RMP-76: checked on the RAW line, including inside backticks --
        # a customer must never see an internal name "hidden" as inline code.
        for term, say, leak in internal_term_hits_in_line(line, internal_terms):
            problems.append({
                "line": line_no, "kind": "internal", "term": term, "leak": leak,
                "detail": f"line {line_no} mentions the internal term \"{term}\"",
                "say": say,
            })
    return problems


def format_reason(problems: list[dict[str, Any]]) -> str:
    shown = problems[:MAX_ITEMS_SHOWN]
    parts = []
    for p in shown:
        if p["say"]:
            parts.append(f'{p["detail"]} → say "{p["say"]}"')
        else:
            parts.append(f'{p["detail"]} → use headings/bullets instead')
    return "Your last reply: " + "; ".join(parts) + ". Do not repeat that reply. Just follow the rules in this one."


def log_miss(
    session_id: str, prompt_id: Any, problems: list[dict[str, Any]], blocked: bool, source: str = "stop",
) -> None:
    """Every miss, blocked or let through (spec: "capped at 200 lines").
    `source` (RMP-198) tells this file's own end-of-turn `Stop` scan apart
    from `voice_check_midturn.py`'s mid-turn `PostToolUse` scan, in the log
    the architect reads for leak counts -- the two scans can overlap (the
    mid-turn scan catches a message early; `Stop` re-walks the whole turn
    at the end and may find the SAME message again), so a reader needs the
    tag to tell one real leak from two log lines. Never raises -- a logging
    failure must never affect the decision."""
    entry = {
        "session_id": session_id, "prompt_id": prompt_id,
        "blocked": blocked, "problems": [p["detail"] for p in problems],
        # RMP-159 part 6: "blocked" is always False by default now --
        # "leak" still tells a genuine leak apart from plain narration.
        "leak": any(p.get("leak") for p in problems),
        "source": source,
    }
    append_entry(entry)


def take_voice_note(session_id: str) -> str | None:
    """Returns the pending voice note and clears it, so it is delivered once.
    Never raises."""
    try:
        raw = cs.read_raw(session_id)
        note = raw.get("voice_note")
        if not isinstance(note, str) or not note:
            return None
        cs.write_patch(session_id, {"voice_note": None})
        return note
    except Exception:
        return None


def _read_stdin_payload() -> dict | None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _turn_text_to_check(payload: dict) -> str | None:
    """RMP-159: prefer every assistant text block of the current turn (read
    from the transcript); fall back to `last_assistant_message` when the
    transcript can't be read or has nothing after the last customer
    message -- same text this hook always checked before."""
    transcript_path = payload.get("transcript_path")
    if isinstance(transcript_path, str) and transcript_path:
        blocks = vct.collect_turn_text_blocks(transcript_path)
        if blocks:
            return "\n\n".join(blocks)
    text = payload.get("last_assistant_message")
    return text if isinstance(text, str) and text.strip() else None


def main() -> int:
    """The `Stop` hook entry point. Always returns 0 -- fails open. Every
    miss logs and saves a pending note for the UserPromptSubmit reminder
    (RMP-49); the RMP-159 part 5 block is off by default (part 6, see
    `voice_check_block.BLOCK_LEAKS_ENV`)."""
    try:
        payload = _read_stdin_payload()
        if payload is None:
            return 0
        session_id = payload.get("session_id")
        if not isinstance(session_id, str) or not session_id:
            return 0
        text = _turn_text_to_check(payload)
        if not text:
            return 0

        problems = check_message(text)
        if not problems:
            return 0

        prompt_id = payload.get("prompt_id")
        leak = vcb.should_block(payload, problems, session_id)
        if leak is not None:
            log_miss(session_id, prompt_id, problems, blocked=True)
            vcb.mark_blocked(session_id, prompt_id)
            print(json.dumps({"decision": "block", "reason": vcb.format_block_reason(leak)}))
            return 0

        log_miss(session_id, prompt_id, problems, blocked=False)
        cs.write_patch(session_id, {"voice_note": format_reason(problems)})
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
