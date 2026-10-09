#!/usr/bin/env python3
"""Step 8 recorder rules (RMP-197 P3): `start_niche_pick`,
`save_niche_research`, `choose_niche`.

Two jobs, same shape as `step_recorder_business_review.py`:
  1. `choose_niche`'s own `ticked: true` is the ONLY place `pick_niche` is
     marked passed+ticked on the plugin side (`step_gate_checklist.
     _SERVER_ONLY_TICKS` denies a model-issued tick unconditionally).
  2. Either tool's response can carry `stage: "research"` (a fresh
     `save_niche_research(phase="niches")` call returns it directly, or a
     later `start_niche_pick` poll re-shows it) -- that is the ONE signal
     that starts the search-budget window (`niche_search_budget.activate`).
     A `save_niche_research(phase="evidence")` call that actually saved
     (any resulting stage) closes the window again -- research is over
     either way, whether it moved on to "checking"/"choose" or the save
     itself failed validation and never reached the tool result at all
     (in which case there is nothing to deactivate and this is a no-op).

FAIL-SAFE: nothing here may crash a hook, same convention as every sibling
module.
"""
from __future__ import annotations

import json
from typing import Any

import connection_state as cs
import niche_pick_said
import niche_search_budget
import step_state
from payload_util import tool_args

PICK_NICHE_STEP_ID = "pick_niche"


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def handle_start_niche_pick(session_id: str, payload: dict) -> None:
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    niche_pick_said.note_reply(session_id, data)   # RMP-281 P2260: the pick question is shown now
    if data.get("stage") == "research":
        niche_search_budget.activate(
            session_id, data.get("search_budget", {}).get("max"), data.get("webfetch_budget", {}).get("max"),
        )


def handle_save_niche_research(session_id: str, payload: dict) -> None:
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    niche_pick_said.note_reply(session_id, data)
    if data.get("stage") == "research":
        niche_search_budget.activate(
            session_id, data.get("search_budget", {}).get("max"), data.get("webfetch_budget", {}).get("max"),
        )
        return
    tool_input = tool_args(payload)
    if tool_input.get("phase") == "evidence":
        niche_search_budget.deactivate(session_id)


def handle_choose_niche(session_id: str, payload: dict) -> None:
    """Rule 3 break: drop the `ticked is True` check -> RED (any
    `choose_niche` call, even one that only re-asked an unclear answer,
    would mark step 8 passed+ticked)."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    niche_pick_said.note_reply(session_id, data, closes=True)   # RMP-281 P2260: the pick was answered; a re-ask starts fresh
    if data.get("ticked") is not True:
        return
    step_state.mark_step_passed(session_id, PICK_NICHE_STEP_ID, "answered")
    step_state.mark_ticked(session_id, PICK_NICHE_STEP_ID)
