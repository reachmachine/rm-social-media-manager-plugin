#!/usr/bin/env python3
"""Step 9 recorder rules (RMP-205): `start_dream_customer`,
`save_dream_customer`, `choose_main_persona`.

Same shape as `step_recorder_niche.py` (step 8's own recorder):
  1. `choose_main_persona`'s own `ticked: true` is the ONLY place
     `dream_customer` is marked passed+ticked on the plugin side
     (`step_gate_checklist._SERVER_ONLY_TICKS` denies a model-issued tick
     unconditionally).
  2. Either tool's response can carry `stage: "research"` -- that is the ONE
     signal that starts the WebSearch/WebFetch budget window. This REUSES
     `niche_search_budget` rather than adding a second near-identical hook:
     the two flows never run in the same session at once (step 8 finishes
     before step 9 starts), so one shared window is correct, not a
     coincidence -- see that module's own docstring for the cap mechanics.
     A `save_dream_customer(phase="research_log")` call that actually saved
     closes the window again -- research is over either way, same "closes
     on the last phase" convention `step_recorder_niche.handle_save_niche_
     research` uses for `phase="evidence"`.

FAIL-SAFE: nothing here may crash a hook, same convention as every sibling
module.
"""
from __future__ import annotations

import json
from typing import Any

import connection_state as cs
import niche_search_budget
import step_state
from payload_util import tool_args

DREAM_CUSTOMER_STEP_ID = "dream_customer"


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def handle_start_dream_customer(session_id: str, payload: dict) -> None:
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    if data.get("stage") == "research":
        budget = data.get("web_search_budget")
        max_value = budget.get("max") if isinstance(budget, dict) else None
        niche_search_budget.activate(session_id, max_value, max_value)


def handle_save_dream_customer(session_id: str, payload: dict) -> None:
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    if data.get("stage") == "research":
        budget = data.get("web_search_budget")
        max_value = budget.get("max") if isinstance(budget, dict) else None
        niche_search_budget.activate(session_id, max_value, max_value)
        return
    tool_input = tool_args(payload)
    if tool_input.get("phase") == "research_log":
        niche_search_budget.deactivate(session_id)


def handle_choose_main_persona(session_id: str, payload: dict) -> None:
    """Rule 3 break: drop the `ticked is True` check -> RED (any
    `choose_main_persona` call, even one that only re-asked an unclear
    answer, would mark step 9 passed+ticked)."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    if data.get("ticked") is not True:
        return
    step_state.mark_step_passed(session_id, DREAM_CUSTOMER_STEP_ID, "answered")
    step_state.mark_ticked(session_id, DREAM_CUSTOMER_STEP_ID)
