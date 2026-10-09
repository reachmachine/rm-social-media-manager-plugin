#!/usr/bin/env python3
"""Workspace-related PostToolUse handlers split from `step_recorder.py` to keep
that file under 300 lines (RMP-52).

Handles `list_workspaces` and `set_active_workspace` recording. Unchanged split
-- no behavior changes, exactly the same code that lived in `step_recorder.py`
before."""
from __future__ import annotations

import json
from typing import Any

import connection_state as cs
import own_account_not_found
import own_account_suggestion
import plan_cache
import revenue_dont_know
import revenue_suggest
import step_state
import website_mismatch


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def handle_list_workspaces(session_id: str, payload: dict) -> None:
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    workspaces = data.get("workspaces")
    if isinstance(workspaces, list):
        step_state.set_workspace_options(session_id, workspaces)


def handle_set_active_workspace(session_id: str, payload: dict) -> None:
    data = _parse_json_response(payload.get("tool_response"))
    if data is None or data.get("confirmed") is not True:
        return
    workspace_id = data.get("workspace_id")
    workspace_name = data.get("workspace_name")
    if not isinstance(workspace_id, str) or not workspace_id:
        return
    step_state.set_workspace(
        session_id, workspace_id, workspace_name if isinstance(workspace_name, str) else "",
    )
    # "After a confirmed switch, clear that answer, so one pick gives one
    # switch" (spec) -- a second set_active_workspace needs a fresh pick.
    # RMP-9: the checklist and the creator brief are both PER WORKSPACE, so
    # every workspace-scoped answer/tick from whichever workspace was active
    # before must not leak into the new one either -- see step_state.py's
    # `reset_for_new_workspace` docstring (it clears `human_answers` too, so
    # there is no separate `clear_human_answer` call left here). Applies to
    # the FIRST pick too (a no-op there, since everything is already empty).
    step_state.reset_for_new_workspace(session_id)
    plan_cache.clear_early_allow(session_id)  # RMP-201/RMP-76: a grant is per-workspace too
    website_mismatch.clear(session_id)  # RMP-66: a mismatch is per-workspace too
    own_account_not_found.clear(session_id)  # RMP-175: same rule, own-account "not found" state
    own_account_suggestion.clear(session_id)  # RMP-161: same rule, own-account website suggestion
    revenue_suggest.clear(session_id)  # RMP-24: same rule, step 5's typed-sentence guess
    revenue_dont_know.clear(session_id)  # RMP-24: same rule, step 5's "I don't know" count


def handle_create_workspace(session_id: str, payload: dict) -> None:
    """RMP-22: a workspace the customer just asked for IS their pick.

    Live bug 2026-09-29: "make a new one called X" at step 2 was denied, the
    customer was pushed into "Default workspace", and every answer was saved
    there. A successful create records the new id as the pick, so the one
    `open_workspace` call that follows (which does the real switch, the
    session event, the checklist read and the ticks) passes `check_workspace_pick`.
    A refused create (plan limit) records nothing. Works at any step: a later
    "make a new workspace" restarts steps 3+ through the same open_workspace
    reset (`handle_set_active_workspace` -> `reset_for_new_workspace`)."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None or data.get("created") is not True:
        return
    workspace_id = data.get("workspace_id")
    if not isinstance(workspace_id, str) or not workspace_id:
        return
    step_state.set_human_answer(session_id, "choose_workspace", workspace_id)
