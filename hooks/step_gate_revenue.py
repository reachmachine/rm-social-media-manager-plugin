#!/usr/bin/env python3
"""RMP-38 step-5 gate rules -- split out of `step_gate.py` to stay under the
300-line file limit, same "split when it grows" precedent as
`step_gate_own_account.py` (RMP-23).

Spec: `docs/plugin-v2/05-how-you-make-money.md`, "Gate rules". Hooks, never
sentences: the model must not be able to (a) save a different set of picks
than the customer ticked, (b) save a description before the customer has
replied in this session, or (c) log its own summary as "the customer's
words". Each function here returns a ready `_deny(...)` dict or `None`
(allow), exactly like every check function in `step_gate.py` itself --
`_decide_steps` just calls straight through, passing the `progress` it read
from `step_recorder_revenue.read_progress` (P1627) -- one source of truth
for that shape, no second parser here.
"""
from __future__ import annotations

from typing import Any

import deny_lines

_REVENUE_STEP_ID = "revenue_model"
_WRONG_PICK_REASON = "revenue_wrong_pick"
_ASK_FIRST_REASON = "ask_question_first"
_EVENT_MISMATCH_REASON = "revenue_words_mismatch"


def _deny(reason_id: str, **fill: object) -> dict:
    return deny_lines.deny_id(reason_id, **fill)


def check_revenue_brief_write(
    tool_input: dict[str, Any], state: dict[str, Any], progress: dict[str, Any],
) -> dict | None:
    """For `update_creator_brief`. Runs on EVERY such call, whatever the
    current step (a later re-answer is protected the same way the first
    answer is -- same "regardless of step order" rule as
    `step_gate._check_brief_answers`)."""
    fields = tool_input.get("fields")
    if not isinstance(fields, dict):
        return None

    model_entry = fields.get(_REVENUE_STEP_ID)
    if isinstance(model_entry, dict):
        model_value = model_entry.get("value")
        picked = state["human_answers"].get(_REVENUE_STEP_ID)
        if (
            not isinstance(model_value, list)
            or not isinstance(picked, list)
            or len(model_value) != len(set(model_value))
            or set(model_value) != set(picked)
        ):
            return _deny(_WRONG_PICK_REASON)

    description_entry = fields.get("revenue_description")
    if isinstance(description_entry, dict):
        description_value = description_entry.get("value")
        stored_description = state["human_answers"].get("revenue_description")
        if (
            not progress["model_saved"]
            or not isinstance(stored_description, str)
            or not stored_description
            or not isinstance(description_value, str)
            or not description_value
        ):
            return _deny(_ASK_FIRST_REASON)

    return None


def check_revenue_described_event(tool_input: dict[str, Any], progress: dict[str, Any]) -> dict | None:
    """For `record_session_event(kind="revenue_described")`. `words` is the
    exact words the plugin's own hooks captured and is waiting to have
    logged back -- never compared with a fresh paraphrase, only with itself.
    The explicit `words is None` check matters: without it, a model sending
    `detail: null` (or a made-up detail) when nothing is stored would pass a
    bare `None != None` comparison and be wrongly ALLOWED -- the same bug
    `step_gate_own_account.check_profile_refreshed_event` was written to
    avoid (architect review, 2026-09-24)."""
    words = progress["words_to_log"]
    if words is None or tool_input.get("detail") != {"customer_words": words}:
        return _deny(_EVENT_MISMATCH_REASON)
    return None
