#!/usr/bin/env python3
"""PostToolUse recorder for `next_actions`/`open_workspace`/`get_resume_
checklist` (RMP-201 P4, design doc §3: "writes the plan cache file ... and
applies the tick sync").

TWO RESPONSE SHAPES, one dispatcher. A bare `next_actions` call's own JSON
result carries `plan_version`/`gate`/`running`/`checklist`/`mode` at the TOP
level. `open_workspace`/`get_resume_checklist` carry the exact same dict,
unchanged, one level down under their own `next_actions` key (`tools_
workspace_open.py`/`tools_checklist_read.py`'s `next_actions=next_actions`
field -- see `next_actions_if_enabled`'s docstring on the backend). `_extract`
below checks the top level first, then that nested key, so one function
covers all three tool names without needing to know which one just ran.

`data.get("next_actions")` is `None` whenever `PLANNER_MODE == "off"` (the
embedding tool's own contract) -- `_extract` returns `None` in that case
too, and `record` below does nothing at all, which is correct: nothing to
cache, nothing to tick, exactly today's behaviour."""
from __future__ import annotations

import json
from typing import Any

import answer_grant_record
import ask_dropped
import connection_state as cs
import niche_pick_said
import deny_lines
import offer_lines
import plan_cache
import plan_tick_sync
import planner_mode_state
import report_pending
import say_dropped


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _extract(data: dict[str, Any]) -> dict[str, Any] | None:
    if "plan_version" in data and "gate" in data:
        return data
    nested = data.get("next_actions")
    return nested if isinstance(nested, dict) else None


def _retry_ats(plan: dict[str, Any]) -> list[str]:
    """The `retry_at` of every `stuck` row that carries one (RMP-218 P1994)."""
    stuck = plan.get("stuck")
    if not isinstance(stuck, list):
        return []
    return [row["retry_at"] for row in stuck if isinstance(row, dict) and isinstance(row.get("retry_at"), str)]


def embeds_plan(tool_response: Any) -> bool:
    """True when a tool's response carries a fresh plan (RMP-197 round 10b): the recorder
    refreshes the cache from it, so ``plan_events`` must NOT mark it dirty again."""
    data = _parse_json_response(tool_response)
    return data is not None and _extract(data) is not None


def record(session_id: str, payload: dict) -> None:
    """Never raises. No-op on anything that doesn't parse, or whenever the
    planner has nothing to report (`PLANNER_MODE == "off"`)."""
    try:
        data = _parse_json_response(payload.get("tool_response"))
        if data is None:
            return
        plan = _extract(data)
        if plan is None:
            return

        planner_mode_state.record_mode(session_id, plan.get("mode"))

        plan_version = plan.get("plan_version")
        gate = plan.get("gate")
        running = plan.get("running") if isinstance(plan.get("running"), list) else []
        checklist = plan.get("checklist")

        plan_cache.write_full(
            session_id,
            plan_version=plan_version if isinstance(plan_version, int) else 0,
            gate=gate if isinstance(gate, dict) else {"v": 0, "deny": {}},
            running=running,
            checklist=checklist if isinstance(checklist, dict) else None,
            retry_ats=_retry_ats(plan),
            next_offer=plan["next_offer"] if isinstance(plan.get("next_offer"), str) else "",
        )
        offer_lines.capture_from_payload(session_id, payload)  # RMP-281 P2272: the lines the server wrote for the hooks
        deny_lines.capture_from_payload(session_id, payload)  # RMP-291 P2320: the deny reasons the server wrote
        plan_tick_sync.apply_tick_sync(session_id, checklist)
        answer_grant_record.record_ask(session_id, plan)  # planner asked in step N -> step N's tools are allowed
        ask_dropped.note_reply(session_id, plan)  # RMP-201: was this question ever shown?
        niche_pick_said.note_plan(session_id, plan)  # RMP-281 P2260: the planner asked the niche pick question
        report_pending.note_reply(session_id, plan)  # RMP-281: remember the report_gap call the server handed over
        say_dropped.note_reply(session_id, plan)  # RMP-281 P2189: was the honest line ever said?
    except Exception:
        pass


def main() -> int:
    import sys

    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    session_id = payload.get("session_id")
    if isinstance(session_id, str) and session_id:
        record(session_id, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
