#!/usr/bin/env python3
"""PostToolUse recorder for `open_workspace` (RMP-76 phase 1).

Spec: docs/plugin-v2/07-server-owned-steps.md "Phase 1". `open_workspace`
replaces five calls after a workspace pick (`set_active_workspace`,
`record_session_event`, `get_resume_checklist`, and two `record_checklist_
step` ticks) with one -- see `tests/fixtures/real_payloads.py`'s
`OPEN_WORKSPACE_RESULT_TEXT` for the exact response shape.

DOES NOT RE-IMPLEMENT: every effect below is produced by feeding a
synthetic payload, built from `open_workspace`'s own real fields, straight
into the SAME recorder function the replaced tool's own PostToolUse would
have called -- `step_recorder_workspace.handle_set_active_workspace`,
`checklist_recorder.handle_record_session_event`,
`checklist_recorder.handle_get_resume_checklist`. This is deliberate: the
guard checks inside those functions (workspace-id match, expected event
kind, workspace-scoped checklist read) all keep running exactly as before,
so a bug fixed there is fixed here too, and a bug introduced there is
caught here too.

`confirmed=false` (locked) records nothing -- same as `set_active_workspace`
today (00-resume-checklist.md, "a locked target changes nothing")."""
from __future__ import annotations

import json
from typing import Any

import checklist_recorder as ckl
import connection_state as cs
import step_recorder_workspace as workspace_recorder
import step_state

_TICKED_STEP_IDS = ("connection_check", "choose_workspace")


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def handle_open_workspace(session_id: str, payload: dict) -> None:
    step_state.sync_connection_check(session_id)
    data = _parse_json_response(payload.get("tool_response"))
    if data is None or data.get("confirmed") is not True:
        return  # locked, or an unparsable result -- record nothing

    # 1. Workspace confirmed -- same fields (workspace_id/workspace_name/
    # confirmed), so the ORIGINAL payload feeds straight into the same
    # handler `set_active_workspace`'s own PostToolUse would have called.
    workspace_recorder.handle_set_active_workspace(session_id, payload)

    # 2. The event the server already decided (`event_kind`) -- fed into
    # the same `record_session_event` handler, which still double-checks it
    # against local state (its own docstring: "never trust a sibling module
    # without checking").
    workspace_id = data.get("workspace_id")
    event_kind = data.get("event_kind")
    if isinstance(workspace_id, str) and isinstance(event_kind, str):
        event_payload = {
            "tool_response": json.dumps({"recorded": True}),
            "tool_input": {
                "args": {
                    "client_session_id": session_id, "kind": event_kind,
                    "workspace_id": workspace_id,
                },
            },
        }
        ckl.handle_record_session_event(session_id, event_payload)

    # 3. The checklist this same call already returned -- fed into the same
    # `get_resume_checklist` handler (known-step handling, skip re-offer,
    # own-account detail all run from there).
    checklist = data.get("checklist")
    if isinstance(checklist, dict) and isinstance(workspace_id, str):
        checklist_payload = {
            "tool_response": json.dumps({
                "workspace_id": workspace_id, "steps": checklist.get("steps"),
            }),
        }
        ckl.handle_get_resume_checklist(session_id, checklist_payload)

    # 4. `connection_check`/`choose_workspace` ticks -- the server already
    # decided these (`ticked`); steps 1-3 above already earned the local
    # `steps_passed` entry each one needs, so this only records the tick.
    ticked = data.get("ticked")
    if isinstance(ticked, list):
        state = step_state.read_state(session_id)
        for step_id in _TICKED_STEP_IDS:
            if step_id in ticked and step_id in state["steps_passed"]:
                step_state.mark_ticked(session_id, step_id)
