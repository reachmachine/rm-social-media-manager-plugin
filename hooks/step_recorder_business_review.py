#!/usr/bin/env python3
"""Step 7 recorder rules: `get_business_review` / `answer_business_review`
(RMP-194 P3; `business_review_started` added RMP-194 drive-polish,
2026-09-28).

The ONLY place `business_review` is marked passed+ticked on the plugin side
-- the server decides the tick (RMP-76), and this just reads it back from
the tool's own `ticked: true` result the moment it happens, so the model
never has to make a separate `get_resume_checklist` round trip to learn its
own step 7 is done this turn (a LATER `get_resume_checklist` call would also
pick this up, through `checklist_recorder.handle_get_resume_checklist`'s
generic workspace-kind-step loop -- this is the same-turn fast path, not the
only path).

`step_gate_checklist.check_checklist_tick` denies a model-issued
`record_checklist_step` for this step id unconditionally (P2) -- this
recorder is the one place `steps_passed`/`ticked` actually gets set for it.

`business_review_started` (live salon transcript, 2026-09-28): the moment
the customer's own review conversation actually begins -- a
`get_business_review` call that comes back `ready: true` (any stage), or a
real `answer_business_review` call -- this flag goes up.
`business_return.py`'s "come back when ready" offer checks it and never
fires again once the review is already under way. Before this fix, a
session whose review started WITHOUT ever going through that offer (this
transcript's own flow reached it straight from `next_actions`/the skill,
never asking "quick look?" first) left the offer PENDING the whole time --
it then fired MID-REVIEW, between the top-earner answer and the summary,
asking "Your website check is done. Quick look?" for a check the customer
was already looking at. `ready: false` (e.g. still indexing) never sets it
-- that is NOT "already reviewing", the offer is still the right thing to
show once real progress is possible.

FAIL-SAFE: nothing here may crash a hook, same convention as every sibling
module.
"""
from __future__ import annotations

import json
from typing import Any

import connection_state as cs
import step_state

BUSINESS_REVIEW_STEP_ID = "business_review"
_STARTED_KEY = "business_review_started"


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def handle_get_business_review(session_id: str, payload: dict) -> None:
    """Rule 3 break: drop the `data.get("ready") is True` check -> RED (a
    `ready: false, reason: "indexing"` result -- the customer has NOT
    started reviewing anything yet -- would also mark the review "started",
    wrongly cancelling a still-legitimate "come back when ready" offer)."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    if data.get("ready") is not True:
        return
    cs.write_patch(session_id, {_STARTED_KEY: True})


def handle_answer_business_review(session_id: str, payload: dict) -> None:
    """Rule 3 break (ticked): drop the `ticked is True` check -> RED (any
    `answer_business_review` call, even one that only saved a correction
    and did NOT finish the step, would mark step 7 passed+ticked).

    Rule 3 break (started): drop the `data.get("ok") is True` check on the
    `_STARTED_KEY` write -> RED (a malformed-but-parseable response with no
    real `ok` field would still mark the review "started")."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    if data.get("ok") is True:
        cs.write_patch(session_id, {_STARTED_KEY: True})
    if data.get("ticked") is not True:
        return
    step_state.mark_step_passed(session_id, BUSINESS_REVIEW_STEP_ID, "answered")
    step_state.mark_ticked(session_id, BUSINESS_REVIEW_STEP_ID)


def is_started(session_id: str) -> bool:
    """True once this session's own review conversation has visibly begun
    -- see the module docstring. Read the same way `business_return.py`'s
    own `_was_offered` reads its flag (`cs.read_raw`, not `step_state`)."""
    raw = cs.read_raw(session_id).get(_STARTED_KEY)
    return raw if isinstance(raw, bool) else False
