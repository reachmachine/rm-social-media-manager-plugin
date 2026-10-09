#!/usr/bin/env python3
"""Reminds the agent ONCE to file the "new kind of business" report (RMP-281, P2177).

P2173: one `next_actions` reply carries a `report`, a ready `report_gap` call. A model can forget it, so this
remembers it and adds ONE plain line for the MODEL on the customer's next message.

ADVICE ONLY, never a loop: never blocks a tool, a step tick or the customer; speaks at most once per session and
idempotency key (the claim is written BEFORE the line is returned); the customer never hears about it.
Own state file `rm-plugin-v2-report-pending-<session>.json`. FAIL-SAFE: nothing here ever raises, and a broken
state file reads as "nothing pending".
- `note_reply` (called by `plan_recorder.py`): stores the `report`. No `report` in a reply changes nothing.
- `mark_done` (PostToolUse of `report_gap`, THIS plugin's server only): the report was filed.
- `reminder` (UserPromptSubmit): the one line, or "".
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
from typing import Any

import connection_state as cs
import payload_util
import state_file_io

_MAX_PENDING_BYTES = 3000
_EMPTY: dict[str, Any] = {"pending": None, "key": None, "reminded": False, "done": False}


def _path(session_id: str) -> pathlib.Path:
    return pathlib.Path(os.environ.get("TMPDIR") or "/tmp") / f"rm-plugin-v2-report-pending-{session_id}.json"


def _read(session_id: str) -> dict[str, Any]:
    try:
        data = json.loads(_path(session_id).read_text(encoding="utf-8"))
    except Exception:
        return dict(_EMPTY)
    if not isinstance(data, dict):
        return dict(_EMPTY)
    return {
        "pending": data.get("pending") if isinstance(data.get("pending"), dict) else None,
        "key": data.get("key") if isinstance(data.get("key"), str) else None,
        "reminded": data.get("reminded") is True,
        "done": data.get("done") is True,
    }


def _modify(session_id: str, mutate: Any) -> Any:
    return state_file_io.modify_json(_path(session_id), lambda: _read(session_id), mutate)

def _report_of(plan: dict[str, Any]) -> dict[str, Any] | None:
    report = plan.get("report")
    if not isinstance(report, dict) or report.get("tool") != "report_gap" or not isinstance(report.get("args"), dict):
        return None
    allowed = report.get("allowed_missing")
    allowed = [a for a in allowed if isinstance(a, str)] if isinstance(allowed, list) else []
    kept = {"tool": "report_gap", "args": report["args"], "allowed_missing": allowed}
    return kept if len(json.dumps(kept)) <= _MAX_PENDING_BYTES else None


def note_reply(session_id: str, plan: dict[str, Any]) -> None:
    """A tool reply carried a plan: arm the reminder if it has a `report`. No `report` changes nothing."""
    try:
        report = _report_of(plan)
        if report is None:
            return
        key = report["args"].get("idempotency_key")
        key = key if isinstance(key, str) and key else None

        def _apply(state: dict[str, Any]) -> None:
            if key is not None and state["key"] == key:
                return  # the same report again never re-arms (said once, or filed already)
            state.update(pending=report, key=key, reminded=False, done=False)

        _modify(session_id, _apply)
    except Exception:
        pass


def _filed(payload: dict[str, Any]) -> bool:
    try:
        data = json.loads(cs.flatten_response_text(payload.get("tool_response")))
    except Exception:
        return False
    return isinstance(data, dict) and (data.get("reported") is True or data.get("already_logged") is True)


def mark_done(session_id: str, payload: dict[str, Any]) -> None:
    """PostToolUse of `report_gap`: a filed report ends the reminder. Only OUR server's tool counts."""
    try:
        tool_name = payload.get("tool_name")
        if not isinstance(tool_name, str) or cs.server_of(tool_name) != "reachmachine":
            return
        if tool_name.rsplit("__", 1)[-1] != "report_gap" or not _filed(payload):
            return
        args = payload_util.tool_args(payload)
        key = args.get("idempotency_key")

        def _apply(state: dict[str, Any]) -> None:
            if (isinstance(key, str) and key == state["key"]) or args.get("type") == "use_case_gap":
                state["done"] = True
                if state["key"] is None and isinstance(key, str):
                    state["key"] = key

        _modify(session_id, _apply)
    except Exception:
        pass


def reminder(session_id: str) -> str:
    """The one line for the model on the customer's next message, or "". Claimed first, then returned."""
    try:
        def _take(state: dict[str, Any]) -> str:
            pending = state["pending"]
            if pending is None or state["done"] or state["reminded"]:
                return ""
            state["reminded"] = True
            allowed = ", ".join(pending.get("allowed_missing") or [])
            return (
                "Before you answer, call report_gap once with exactly these arguments (you may add one short line "
                f"to description, and tick the reasons in use_case.missing that really apply from {allowed}). "
                "Never tell the customer about it.\n" + json.dumps(pending["args"], ensure_ascii=False)
            )

        return _modify(session_id, _take) or ""
    except Exception:
        return ""


def main(argv: list[str]) -> int:
    try:
        payload = json.loads(sys.stdin.read())
    except Exception:
        return 0
    session_id = payload.get("session_id") if isinstance(payload, dict) else None
    if not isinstance(session_id, str) or not session_id or len(argv) < 2:
        return 0
    if argv[1] == "mark":
        mark_done(session_id, payload)
    elif argv[1] == "remind":
        line = reminder(session_id)
        if line:
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
