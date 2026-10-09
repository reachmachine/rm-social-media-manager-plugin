#!/usr/bin/env python3
"""Workspace-pin and workspace-pick gate rules, split out of `step_gate.py`
to keep it under 300 lines (RMP-76 phase 1, `open_workspace`).

Shared by `set_active_workspace` AND `open_workspace` -- both tools exist
only to point the session at a (possibly different) workspace, so both are
exempt from the pin check, and both are checked against the SAME
picked-workspace-id rule. See docs/plugin-v2/07-server-owned-steps.md
"Phase 1": `open_workspace` "may only target the workspace id the customer
actually picked ... a locked target returns the same locked preview and
changes nothing" -- exactly `set_active_workspace`'s existing rule, reused
here rather than re-implemented."""
from __future__ import annotations

import deny_lines

_WORKSPACE_PIN_REASON = "workspace_pin"
PICK_WORKSPACE_REASON = "pick_workspace"
_SESSION_MISMATCH_REASON = "session_mismatch"


def _deny(reason_id: str, **fill: object) -> dict:
    return deny_lines.deny_id(reason_id, **fill)


def check_workspace_pin(tool_input: dict, state: dict) -> dict | None:
    """Rule: "only that workspace, until a switch" -- ANY tool input
    carrying a `workspace_id` that differs from the one already chosen is
    denied, once a workspace has been chosen. Never applied to
    `set_active_workspace`/`open_workspace` themselves (see `step_gate.
    decide`), whose whole job is to change it."""
    workspace = state["workspace"]
    if workspace is None:
        return None
    workspace_id = tool_input.get("workspace_id")
    if isinstance(workspace_id, str) and workspace_id and workspace_id != workspace["id"]:
        return _deny(_WORKSPACE_PIN_REASON)
    return None


def check_workspace_pick(tool_input: dict, state: dict) -> dict | None:
    """`set_active_workspace`/`open_workspace` may only target the workspace
    id the customer actually picked (an `AskUserQuestion` answer or an
    exact typed match) -- never a self-authorised switch, and never a
    second switch off the same pick (the recorder clears it after a
    confirmed switch)."""
    picked = state["human_answers"].get("choose_workspace")
    workspace_id = tool_input.get("workspace_id")
    if not isinstance(workspace_id, str) or not workspace_id or workspace_id != picked:
        return _deny(PICK_WORKSPACE_REASON)
    return None


def check_open_workspace_session(tool_input: dict, session_id: str) -> dict | None:
    """`open_workspace` alone (of the two picking tools) carries its own
    `client_session_id` field -- must equal the hook's own known session id,
    the same rule `connections_gate._decide_record_session_start` already
    applies to `record_session_start`, the other tool a forged id could
    otherwise misdirect."""
    if tool_input.get("client_session_id") != session_id:
        return _deny(_SESSION_MISMATCH_REASON)
    return None
