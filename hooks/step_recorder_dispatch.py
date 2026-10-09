#!/usr/bin/env python3
"""PostToolUse dispatch table for `step_recorder.py` (RMP-96).

Split out of `step_recorder.py` once it reached the 300-line limit -- same
"split when it grows" precedent `step_recorder_website.py`/`step_recorder_
revenue.py` already used. Owns the `_POST_TOOL_USE_HANDLERS` map (every
real reachmachine tool result this plugin records against) plus the two
`get_creator_brief`/`update_creator_brief` handlers that only that map
uses. `step_recorder.py`'s own top-level `handle()` (the AskUserQuestion
case needs functions that still live there) imports `_POST_TOOL_USE_
HANDLERS` and `_tool_suffix` from here, so `test_hooks_json_wiring.py`'s
`step_recorder._POST_TOOL_USE_HANDLERS` reference keeps working unchanged
-- `step_recorder.py` re-exports the name at its own bottom.

FAIL-SAFE: nothing here may crash a hook -- same convention as every
sibling module.
"""
from __future__ import annotations

import json
from typing import Any

import checklist_recorder as ckl
import connection_state as cs
import fact_events
from payload_util import tool_args
import step_recorder_business_review as business_review_recorder
import step_recorder_dream_customer as dream_customer_recorder
import step_recorder_niche as niche_recorder
import step_recorder_open_workspace as open_workspace_recorder
import step_recorder_own_account as own_account_recorder
import step_recorder_revenue as revenue_recorder
import step_recorder_website as website_recorder
import step_recorder_workspace as workspace_recorder
import step_state
import steps_manifest
import website_search_state


def _tool_suffix(tool_name: str) -> str:
    return tool_name.rsplit("__", 1)[-1]


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _handle_get_creator_brief(session_id: str, payload: dict) -> None:
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    fields = data.get("fields")
    if not isinstance(fields, dict):
        return
    for step in steps_manifest.load_steps(session_id):
        brief_key = step.get("brief_key")
        if not isinstance(brief_key, str) or steps_manifest.answer_type(step) != "options":
            continue  # step 5's two-question shape (P1627) is delegated below instead
        entry = fields.get(brief_key)
        if not isinstance(entry, dict):
            continue
        value = entry.get("value")
        allowed_values = {opt["value"] for opt in steps_manifest.question_options(step)}
        if isinstance(value, str) and value in allowed_values:
            step_state.mark_step_passed(session_id, step["id"], "already_known")
    revenue_recorder.handle_brief_read(session_id, fields)


def _handle_update_creator_brief(session_id: str, payload: dict) -> None:
    data = _parse_json_response(payload.get("tool_response"))
    if data is None or data.get("saved") is not True:
        return
    tool_input = tool_args(payload)  # RMP-5/RMP-10: see payload_util.tool_args
    fields = tool_input.get("fields")
    if not isinstance(fields, dict):
        return
    state = step_state.read_state(session_id)
    for step in steps_manifest.load_steps(session_id):
        brief_key = step.get("brief_key")
        if not isinstance(brief_key, str) or steps_manifest.answer_type(step) != "options":
            continue  # step 5's two-question shape (P1627) is delegated below instead
        entry = fields.get(brief_key)
        if not isinstance(entry, dict):
            continue
        value = entry.get("value")
        if isinstance(value, str) and value == state["human_answers"].get(step["id"]):
            step_state.mark_step_passed(session_id, step["id"], "answered")
            # P1615 (03-whose-account.md, "Changing the answer later"): a
            # re-answer of a step that already passed must earn a NEW
            # checklist tick, so the server writes a NEW step_done event --
            # unticking is a no-op the first time (nothing to remove yet).
            step_state.unmark_ticked(session_id, step["id"])
            # One saved answer spends the pick, same rule as step 2's "one
            # pick, one switch" (`_handle_set_active_workspace`) -- a second
            # identical save without a fresh AskUserQuestion/typed answer is
            # denied by `step_gate._check_brief_answers`, never a replay of
            # the old one.
            step_state.clear_human_answer(session_id, step["id"])
    revenue_recorder.handle_brief_write(session_id, fields)


_POST_TOOL_USE_HANDLERS = {
    "list_workspaces": workspace_recorder.handle_list_workspaces,
    "set_active_workspace": workspace_recorder.handle_set_active_workspace,
    "create_workspace": workspace_recorder.handle_create_workspace,  # RMP-22
    "open_workspace": open_workspace_recorder.handle_open_workspace,  # RMP-76
    "record_session_event": revenue_recorder.handle_record_session_event_dispatch,
    "get_resume_checklist": ckl.handle_get_resume_checklist,
    "record_checklist_step": ckl.handle_record_checklist_step,
    "get_creator_brief": _handle_get_creator_brief,
    "update_creator_brief": _handle_update_creator_brief,
    "add_to_watchlist": own_account_recorder.handle_add_to_watchlist,
    "refresh_competitor": own_account_recorder.handle_refresh_competitor,
    "change_own_account": own_account_recorder.handle_change_own_account,  # RMP-113
    "finish_website_read": website_recorder.handle_finish_website_read,
    "wait_for_website_read": website_recorder.handle_wait_for_website_read,  # RMP-76
    "get_website_read_status": website_recorder.handle_get_website_read_status,
    "get_next_fact_task": website_recorder.handle_get_next_fact_task,  # RMP-92
    "save_business_fact": fact_events.handle_save_business_fact,  # RMP-68
    "search_business_knowledge": website_search_state.handle_search_business_knowledge,  # RMP-72
    "get_fact_tasks": website_search_state.handle_get_fact_tasks,  # RMP-96
    "save_business_facts": website_recorder.handle_save_business_facts,  # RMP-96
    "get_business_review": business_review_recorder.handle_get_business_review,  # RMP-194 drive-polish
    "answer_business_review": business_review_recorder.handle_answer_business_review,  # RMP-194 P3
    "start_niche_pick": niche_recorder.handle_start_niche_pick,  # RMP-197 P3
    "save_niche_research": niche_recorder.handle_save_niche_research,  # RMP-197 P3
    "choose_niche": niche_recorder.handle_choose_niche,  # RMP-197 P3
    "start_dream_customer": dream_customer_recorder.handle_start_dream_customer,  # RMP-205
    "save_dream_customer": dream_customer_recorder.handle_save_dream_customer,  # RMP-205
    "choose_main_persona": dream_customer_recorder.handle_choose_main_persona,  # RMP-205
}

