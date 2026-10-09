#!/usr/bin/env python3
"""The `MessageDisplay` hook for step 1 (RMP-159 / RMP-198, 2026-09-30).

THE PROBLEM. In step 1 the model makes five tool calls across three MCP
servers, and before them it keeps printing lines like "Now the three calls."
or "Running the three probes now." Wording fixes shortened these but never
stopped them: there is always something to announce. `PreToolUse` cannot talk
back to the model and `PostToolUse` runs after the customer saw the line.

WHAT THIS DOES. Claude Code has a display-only hook event, `MessageDisplay`
(found by decoding the installed build, 2.1.285: input `{session_id,
turn_id, message_id, index, final, delta}`, output
`{"hookSpecificOutput": {"hookEventName": "MessageDisplay",
"displayContent": "<text shown instead of the delta>"}}`; the code only
replaces when `displayContent !== undefined`, so "" hides a line). The stored
message and what the model sees are untouched.

RULE. Until step 1 has been REPORTED for this session, every line the model
writes is hidden unless it is a report line: starts with a status emoji, or
is one of the fixed fix-hint lines from connection-check's table. Wording no
longer matters: any new phrasing of "I am about to call things" is hidden
too. "Reported" = both probes that always run (Apify, browser) finished AND
(the session is recorded OR Reach Machine is not ok -- then the record call
cannot succeed and the report goes out right away).

FAIL-OPEN, on purpose (opposite of the gate). A bug here must never blank a
customer's chat:
  - any error, bad payload, missing session id -> print nothing (text shows);
  - hiding stops after MAX_TURNS distinct turns and MAX_LINES hidden lines
    per session (env `RM_STEP1_SILENCE_MAX_TURNS` / `_MAX_LINES`);
  - if the counters cannot be written, nothing is hidden;
  - `RM_STEP1_SILENCE=0` switches the hook off.
No token, tool input or message text is ever logged or written to disk.

WHY NOT the zero-call design the ticket first asked for: see prompts/COMMS.md,
2026-09-30. Short version: an `mcp_tool` hook's result never reaches
`connection_state.py`'s state file, so the gate could not learn from it.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any

import connection_state as cs
import session_record as sr
import state_file_io

_TURNS_KEY = "step1_silence_turns"
_LINES_KEY = "step1_silence_lines"

DEFAULT_MAX_TURNS = 2
DEFAULT_MAX_LINES = 40

_STATUS_EMOJI = ("✅", "⚠", "❌")
_BULLETS = "-*•> \t"

# Fragments of the fixed report / fix-hint lines in connection-check/SKILL.md
# section 3 (and the server's own `say`). Lower-case; matched as substrings.
_REPORT_FRAGMENTS = (
    "/mcp",
    "check again",
    "switched off",
    "didn't answer",
    "sign-in expired",
    "isn't installed yet",
    "install the browser",
    "nodejs.org",
    "this conversation is saved",
    "saved on your computer",
)


def _env_int(name: str, default: int) -> int:
    try:
        return max(0, int(os.environ.get(name, default)))
    except (TypeError, ValueError):
        return default


def is_reported(state: dict[str, Any]) -> bool:
    """True once the customer's step-1 report may be shown."""
    if not sr.check_complete(state):
        return False
    return state.get("recorded") is True or state.get("reachmachine") is not True


def is_report_line(line: str) -> bool:
    text = line.strip().lstrip(_BULLETS).strip()
    if not text:
        return False
    if text.startswith(_STATUS_EMOJI):
        return True
    lowered = text.lower()
    return any(fragment in lowered for fragment in _REPORT_FRAGMENTS)


def filter_delta(delta: str) -> str:
    """Keep only report lines. Blank lines go too (they only frame hidden text)."""
    kept = [ln for ln in delta.splitlines(keepends=True) if is_report_line(ln)]
    return "".join(kept)


def _may_hide(session_id: str, turn_id: str, hidden_lines: int) -> bool:
    """Reserve budget for this delta. False = leave the text alone."""
    max_turns = _env_int("RM_STEP1_SILENCE_MAX_TURNS", DEFAULT_MAX_TURNS)
    max_lines = _env_int("RM_STEP1_SILENCE_MAX_LINES", DEFAULT_MAX_LINES)

    def mutate(current: dict[str, Any]) -> bool:
        turns = current.get(_TURNS_KEY)
        turns = [t for t in turns if isinstance(t, str)] if isinstance(turns, list) else []
        lines = current.get(_LINES_KEY)
        lines = lines if isinstance(lines, int) else 0
        if turn_id not in turns:
            if len(turns) >= max_turns:
                return False
            turns.append(turn_id)
        if lines + hidden_lines > max_lines:
            return False
        current[_TURNS_KEY] = turns
        current[_LINES_KEY] = lines + hidden_lines
        return True

    result = state_file_io.modify_json(
        cs.state_path(session_id), lambda: cs.read_raw(session_id), mutate
    )
    return result is True


def decide(payload: dict[str, Any]) -> str | None:
    """The text to show instead of the delta, or None to leave it alone."""
    if os.environ.get("RM_STEP1_SILENCE") == "0":
        return None
    if payload.get("hook_event_name") != "MessageDisplay":
        return None
    session_id = payload.get("session_id")
    delta = payload.get("delta")
    turn_id = payload.get("turn_id")
    if not (isinstance(session_id, str) and session_id and isinstance(delta, str) and delta):
        return None
    if not isinstance(turn_id, str) or not turn_id:
        return None
    if is_reported(cs.read_state(session_id)):
        return None
    shown = filter_delta(delta)
    if shown == delta:
        return None
    hidden = sum(1 for ln in delta.splitlines() if ln.strip() and not is_report_line(ln))
    if hidden == 0:
        return None  # only blank lines differ: not worth a write
    if not _may_hide(session_id, turn_id, hidden):
        return None
    return shown


def main() -> int:
    try:
        data = json.loads(sys.stdin.read())
        if not isinstance(data, dict):
            return 0
        shown = decide(data)
        if shown is None:
            return 0
        print(json.dumps({
            "hookSpecificOutput": {"hookEventName": "MessageDisplay", "displayContent": shown}
        }))
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
