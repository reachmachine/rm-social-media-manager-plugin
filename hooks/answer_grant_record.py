#!/usr/bin/env python3
"""PostToolUse recorder for `answer_question`'s own `next_tool` field
(RMP-201/RMP-76 live bug, 2026-09-28).

**The bug this fixes.** A "yes" to N6a2 ("do you have a website?") answered
early, while step 5 (revenue) is still open, makes `answer_service.
answer_question` reply with `next_tool: "start_website_read"` -- the
server's own instruction to call that tool next (`answer_service.py`'s own
docstring). The model did exactly that, and `step_gate.py`'s cumulative
step order denied it: "Finish step 5 first." -- the customer answered the
website question for nothing, and saw it twice once the model recovered by
running step 5 first. The SAME shape applies to N6f (reviews consent) ->
`next_tool: "start_reviews_fetch"`.

**The fix.** `next_tool` always names a tool from `step_gate._STEP_ALLOW`'s
"website" entry today (both N6a2's and N6f's own next steps live there) --
rather than hard-code that mapping a second time, this finds whichever
`_STEP_ALLOW` step CONTAINS `next_tool` and grants that step's WHOLE set
early (`plan_cache.grant_early_allow`), not just the one named tool: a
website read is a multi-call flow (`wait_for_website_read`, `get_next_fact_
task`, ...), and granting only the first call would just move the same
denial one call later. Never a general widening -- only the exact set
`step_gate.py` would grant once "website" genuinely became the current
step, just granted a little early because the SERVER itself proposed the
action.

No `is_drive` check here (unlike `step_gate_plan.py`'s read side) -- this
only WRITES a cache entry nothing reads outside drive mode (`step_gate_
plan.early_allow`'s own `is_drive` check), same "write freely, gate on
read" split `job_tool_cache_record.py` already uses for `get_job`."""
from __future__ import annotations

import json
import re
import sys
from typing import Any

import connection_state as cs
import plan_cache
import step_gate
import steps_manifest


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _step_allow_set_containing(tool_suffix: str) -> frozenset[str]:
    """The full `_STEP_ALLOW` set for whichever step names `tool_suffix` --
    never a second, hand-maintained mapping (module docstring). Empty when
    no step names it (a `next_tool` value `answer_service.py` never sends,
    or a stale/future plugin talking to a newer backend)."""
    for suffixes in step_gate._STEP_ALLOW.values():
        if tool_suffix in suffixes:
            return frozenset(suffixes)
    return frozenset()


_NODE_STEP_NUMBER = re.compile(r"^N(\d+)")


def record_ask(session_id: str, plan: dict[str, Any]) -> None:
    """The planner's own ASK grants that step's tools early (RMP-201, live run
    BT 2026-09-30). The server asked "Do you have a website?" (N6a2) while step
    5 was still open; the customer said yes, the model went straight to
    `start_website_read`, and the cumulative step order denied it "Finish step
    5 first." -- the gate contradicted the planner. In drive mode the planner's
    order wins: a question it asks in step N means step N's tools are wanted
    now. The node id names the step number (N6a2 -> 6); the step's tools come
    from `step_gate._STEP_ALLOW`, the same one mapping `record` above uses.
    The server's own `gate.deny` still applies on top (`step_gate_plan.
    gate_deny`), so a tool the planner itself guards stays denied.

    Never raises; no `is_drive` check for the same reason as `record`."""
    try:
        ask = plan.get("ask")
        questions = ask.get("questions") if isinstance(ask, dict) else None
        if not isinstance(questions, list):
            return
        steps = steps_manifest.load_steps(session_id)
        by_number = {step.get("number"): step.get("id") for step in steps}
        granted: set[str] = set()
        for question in questions:
            node = question.get("node") if isinstance(question, dict) else None
            match = _NODE_STEP_NUMBER.match(node) if isinstance(node, str) else None
            if match is None:
                continue
            step_id = by_number.get(int(match.group(1)))
            granted |= step_gate._STEP_ALLOW.get(step_id, set())
        if granted:
            plan_cache.grant_early_allow(session_id, sorted(granted))
    except Exception:
        pass


def record(session_id: str, payload: dict) -> None:
    """Never raises. No-op on anything that doesn't parse, or that carries
    no `next_tool` at all (the overwhelming common case -- most `answer_
    question` replies have nothing to grant)."""
    try:
        data = _parse_json_response(payload.get("tool_response"))
        if data is None:
            return
        next_tool = data.get("next_tool")
        if not isinstance(next_tool, str) or not next_tool:
            return
        granted = _step_allow_set_containing(next_tool)
        if not granted:
            return
        plan_cache.grant_early_allow(session_id, sorted(granted))
    except Exception:
        pass


def main() -> int:
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
