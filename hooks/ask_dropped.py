#!/usr/bin/env python3
"""Notices a question the server handed over and the model never showed
(RMP-201, live 2026-09-29), and reminds the model on the customer's next turn.

THE LIVE BUG. `open_workspace` and `next_actions` replies carry an `ask`
(the shop's "I found 692 products ... use these?"). The model wrote
"Reading your website in the background" and never asked it. The customer
never saw the question.

THREE SMALL HOOKS, one own state file (`rm-plugin-v2-ask-dropped-<session>`):
- `note_reply` (PostToolUse of next_actions/open_workspace/get_resume_checklist,
  called by `plan_recorder.py`): remembers the first pending question, or
  forgets it when the reply has none.
- `mark_shown` (PostToolUse of AskUserQuestion): the model did ask something.
- `check_stop` (Stop): a pending question that was not asked with
  AskUserQuestion and whose numbered list / text is not in the turn's text
  is DROPPED.
- `reminder` (UserPromptSubmit): one plain line on the next turn naming the
  dropped question and its options. Cleared once said.

The SERVER half of the fix is separate: a real customer message releases the
ask-repeat hold (`customer_turn_release.py`), so `next_actions` serves the
question again on that turn.

FAIL-SAFE: every function never raises and never blocks; a broken state file
reads as "nothing pending".
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
from typing import Any

import state_file_io
import voice_check_transcript as vct  # the reader the Stop voice check uses

_NUMBERED_LIST = re.compile(r"(?m)^\s*(?:\*\*)?1[.)]\s+\S")
_MAX_OPTIONS = 4


def _path(session_id: str) -> pathlib.Path:
    return pathlib.Path(os.environ.get("TMPDIR") or "/tmp") / f"rm-plugin-v2-ask-dropped-{session_id}.json"


def _read(session_id: str) -> dict[str, Any]:
    try:
        data = json.loads(_path(session_id).read_text(encoding="utf-8"))
    except Exception:
        return {"pending": None, "shown": False, "dropped": False}
    if not isinstance(data, dict):
        return {"pending": None, "shown": False, "dropped": False}
    return {
        "pending": data.get("pending") if isinstance(data.get("pending"), dict) else None,
        "shown": data.get("shown") is True,
        "dropped": data.get("dropped") is True,
    }


def _modify(session_id: str, mutate: Any) -> Any:
    return state_file_io.modify_json(_path(session_id), lambda: _read(session_id), mutate)


def _first_question(plan: dict[str, Any]) -> dict[str, Any] | None:
    ask = plan.get("ask")
    questions = ask.get("questions") if isinstance(ask, dict) else None
    if not isinstance(questions, list) or not questions or not isinstance(questions[0], dict):
        return None
    q = questions[0]
    text = q.get("text")
    if not isinstance(text, str) or not text:
        return None
    labels = [
        o["label"] for o in (q.get("options") or []) if isinstance(o, dict) and isinstance(o.get("label"), str)
    ][:_MAX_OPTIONS]
    return {"node": q.get("node"), "text": text, "options": labels}


def note_reply(session_id: str, plan: dict[str, Any]) -> None:
    """A tool reply carried a plan: remember its first question, or forget it."""
    try:
        question = _first_question(plan)

        def _apply(state: dict[str, Any]) -> None:
            same = question is not None and state["pending"] is not None and (
                state["pending"].get("node"), state["pending"].get("text")
            ) == (question["node"], question["text"])
            if not same:
                state.update(pending=question, shown=False, dropped=False)

        _modify(session_id, _apply)
    except Exception:
        pass


def mark_shown(session_id: str) -> None:
    try:
        _modify(session_id, lambda s: s.update(shown=True, dropped=False))
    except Exception:
        pass


def check_stop(session_id: str, turn_text: str) -> None:
    """End of a turn: was the pending question put in front of the customer?"""
    try:
        def _apply(state: dict[str, Any]) -> None:
            pending = state["pending"]
            if pending is None or state["shown"]:
                return
            said = turn_text or ""
            if _NUMBERED_LIST.search(said) or pending["text"][:40].casefold() in said.casefold():
                state.update(shown=True, dropped=False)
            else:
                state["dropped"] = True

        _modify(session_id, _apply)
    except Exception:
        pass


def reminder(session_id: str) -> str | None:
    """The one line for the next customer turn, or `None`. Said once."""
    try:
        def _take(state: dict[str, Any]) -> str | None:
            pending = state["pending"]
            if not state["dropped"] or pending is None:
                return None
            state["dropped"] = False
            options = " / ".join(pending.get("options") or [])
            tail = f" Options: {options}." if options else ""
            return (
                "You did not show the customer this question from the last reply: "
                f'"{pending["text"]}".{tail} Ask it now with AskUserQuestion, word for word.'
            )

        return _modify(session_id, _take)
    except Exception:
        return None


def _payload() -> dict[str, Any] | None:
    try:
        data = json.loads(sys.stdin.read())
    except Exception:
        return None
    return data if isinstance(data, dict) else None


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
    payload = _payload()
    session_id = (payload or {}).get("session_id")
    if not isinstance(session_id, str) or not session_id or len(argv) < 2:
        return 0
    mode = argv[1]
    if mode == "mark":
        mark_shown(session_id)
    elif mode == "stop":
        check_stop(session_id, _turn_text(payload))
    elif mode == "remind":
        line = reminder(session_id)
        if line:
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
