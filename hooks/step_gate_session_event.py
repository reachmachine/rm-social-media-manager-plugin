#!/usr/bin/env python3
"""`record_session_event` rules, split out of `step_gate.py` (RMP-201 wave-30
integration: `step_gate.py` crossed the 300-line cap once P4's plan-gate
glue landed, same reason `step_gate_own_account.py`/`step_gate_checklist.py`/
`step_gate_revenue.py`/`step_gate_workspace.py`/`step_gate_rules.py` already
exist as siblings). No behaviour change -- this is the exact body of the old
`step_gate._check_record_session_event`, moved verbatim.

RMP-9 rule 1: truthful only -- `workspace_id` must be the workspace already
confirmed, and `kind` must match what happened: "selected" for the first
pick, "switched" after (`workspace_logged_ever`). RMP-23: `profile_refreshed`
delegates to `step_gate_own_account.check_profile_refreshed_event` once the
workspace itself matches. RMP-38: `revenue_described` delegates to
`step_gate_revenue.check_revenue_described_event` the same way. RMP-68:
`business_fact_saved` delegates to `fact_events.check_event` the same way.
"""
from __future__ import annotations

import deny_lines
import fact_events
import own_account_mismatch
import step_gate_own_account as own_account
import step_gate_revenue as revenue_gate
import step_gate_workspace as workspace_gate
import step_recorder_revenue as revenue_recorder
import website_mismatch

_EVENT_MISMATCH_REASON = "event_mismatch"


def _deny(reason_id: str, **fill: object) -> dict:
    return deny_lines.deny_id(reason_id, **fill)


def check_record_session_event(tool_input: dict, state: dict, session_id: str) -> dict | None:
    """`None` = allow. See module docstring."""
    workspace = state["workspace"]
    if workspace is None:
        return _deny(workspace_gate.PICK_WORKSPACE_REASON)
    if tool_input.get("workspace_id") != workspace["id"]:
        return _deny(_EVENT_MISMATCH_REASON)

    kind = tool_input.get("kind")
    if kind == "profile_refreshed":
        return own_account.check_profile_refreshed_event(tool_input, state)
    if kind == "revenue_described":
        progress = revenue_recorder.read_progress(session_id)
        return revenue_gate.check_revenue_described_event(tool_input, progress)
    if kind == fact_events.FACT_EVENT_KIND:
        return fact_events.check_event(tool_input, session_id)
    if kind in own_account_mismatch.MISMATCH_EVENT_KINDS:
        return own_account_mismatch.check_mismatch_event(kind, tool_input, state)
    if kind in website_mismatch.MISMATCH_EVENT_KINDS:
        progress = website_mismatch.read_progress(session_id)
        return website_mismatch.check_mismatch_event(kind, tool_input, state, progress, session_id)

    expected_kind = "workspace_switched" if state["workspace_logged_ever"] else "workspace_selected"
    if kind != expected_kind:
        return _deny(_EVENT_MISMATCH_REASON)
    return None
