#!/usr/bin/env python3
"""Notices that the one honest "this kind of business is new to us" line was never said (RMP-281, P2189).

LIVE BUG: in 2 of 9 runs the server told the line (it sits in `say`) and the model wrote other words. The customer
never heard the promise. The server now also sends the same line as `must_say`, and this hook checks it was said.

Same family as `ask_dropped.py`, own state file `rm-plugin-v2-say-dropped-<session>.json`:
- `note_reply` (called by `plan_recorder.py`): a reply with a `must_say` list arms the first line. A reply WITHOUT
  `must_say` changes nothing (it never clears a pending line).
- `check_stop` (Stop): the line in the turn's assistant text -> shown for good; otherwise dropped.
- `reminder` (UserPromptSubmit): one plain line for the MODEL, once per session (claimed before it is returned).

ADVICE ONLY: never blocks a tool or the customer. FAIL-SAFE: nothing here raises; a broken state file reads as
"nothing pending".
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
from typing import Any

import state_file_io
import voice_check_transcript as vct  # the same reader ask_dropped uses

_EMPTY: dict[str, Any] = {"pending": None, "shown": False, "dropped": False, "reminded": False}
_MAX_LINE = 600


def _path(session_id: str) -> pathlib.Path:
    return pathlib.Path(os.environ.get("TMPDIR") or "/tmp") / f"rm-plugin-v2-say-dropped-{session_id}.json"


def _read(session_id: str) -> dict[str, Any]:
    try:
        data = json.loads(_path(session_id).read_text(encoding="utf-8"))
    except Exception:
        return dict(_EMPTY)
    if not isinstance(data, dict):
        return dict(_EMPTY)
    return {
        "pending": data.get("pending") if isinstance(data.get("pending"), str) and data["pending"] else None,
        "shown": data.get("shown") is True,
        "dropped": data.get("dropped") is True,
        "reminded": data.get("reminded") is True,
    }


def _modify(session_id: str, mutate: Any) -> Any:
    return state_file_io.modify_json(_path(session_id), lambda: _read(session_id), mutate)


def _norm(text: str) -> str:
    """Collapse whitespace, ignore case and a trailing full stop."""
    return re.sub(r"\s+", " ", text).strip().casefold().rstrip(".").strip()


def _first_line(plan: dict[str, Any]) -> str | None:
    lines = plan.get("must_say")
    first = lines[0] if isinstance(lines, list) and lines else None
    return first if isinstance(first, str) and first.strip() and len(first) <= _MAX_LINE else None


def note_reply(session_id: str, plan: dict[str, Any]) -> None:
    """A tool reply carried a plan. `must_say` arms the check; no `must_say` changes nothing."""
    try:
        line = _first_line(plan)
        if line is None:
            return

        def _apply(state: dict[str, Any]) -> None:
            if state["pending"] == line:
                return  # the same line again never re-arms (said, or already reminded)
            state.update(pending=line, shown=False, dropped=False, reminded=False)

        _modify(session_id, _apply)
    except Exception:
        pass


def check_stop(session_id: str, turn_text: str) -> None:
    """End of a turn: was the pending line said to the customer?"""
    try:
        def _apply(state: dict[str, Any]) -> None:
            if state["pending"] is None or state["shown"]:
                return
            if _norm(state["pending"]) in _norm(turn_text or ""):
                state.update(shown=True, dropped=False)
            else:
                state["dropped"] = True

        _modify(session_id, _apply)
    except Exception:
        pass


def reminder(session_id: str) -> str:
    """The one line for the model on the next customer message, or "". Claimed first, then returned."""
    try:
        def _take(state: dict[str, Any]) -> str:
            if state["pending"] is None or state["shown"] or not state["dropped"] or state["reminded"]:
                return ""
            state["reminded"] = True
            return (
                "Before you answer, tell the customer, in your own words or exactly: "
                f'"{state["pending"]}". Say it once.'
            )

        return _modify(session_id, _take) or ""
    except Exception:
        return ""


def _turn_text(payload: dict[str, Any]) -> str:
    try:
        path = payload.get("transcript_path")
        if isinstance(path, str) and path:
            blocks = vct.collect_turn_text_blocks(path)
            if blocks:
                return "\n\n".join(blocks)
    except Exception:
        pass
    text = payload.get("last_assistant_message")
    return text if isinstance(text, str) else ""


def main(argv: list[str]) -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        return 0
    session_id = payload.get("session_id") if isinstance(payload, dict) else None
    if not isinstance(session_id, str) or not session_id or len(argv) < 2:
        return 0
    if argv[1] == "stop":
        check_stop(session_id, _turn_text(payload))
    elif argv[1] == "remind":
        line = reminder(session_id)
        if line:
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
