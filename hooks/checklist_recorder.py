#!/usr/bin/env python3
"""PostToolUse recording + UserPromptSubmit reminder for the resume checklist
and session-event logging (RMP-9, RMP-18). Split from `step_recorder.py` to
keep both under 300 lines. Handles `record_session_event`, `get_resume_
checklist`, `record_checklist_step` -- imported into `step_recorder.py`'s
dispatch table. Fail-safe: never crashes."""
from __future__ import annotations

import json
from typing import Any

import connection_state as cs
import own_account_reminder
import own_account_suggestion
from payload_util import tool_args
import priority_reminders
import revenue_dont_know
import step_recorder_revenue as revenue_recorder
from step_reminder_format import format_step_reminder  # noqa: F401 -- re-exported, see connection_state_cli.py
import step_recorder_refresh
import step_recorder_website as website_recorder
import step_rules_cache
import step_skip
import step_state
import steps_manifest
import website_return


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _maybe_finish_choose_workspace(session_id: str) -> None:
    """00-resume-checklist.md / 02-workspace-selection.md: `choose_workspace`
    only enters `steps_passed` once ALL THREE are true -- a confirmed
    workspace, a logged selection/switch event, and a successful checklist
    read for that same workspace."""
    state = step_state.read_state(session_id)
    if state["workspace"] is None:
        return
    if not state["workspace_logged"] or not state["checklist_read"]:
        return
    if "choose_workspace" in state["steps_passed"]:
        return
    step_state.mark_step_passed(session_id, "choose_workspace", "passed")


# ------------------------------------------------------- record_session_event --

def handle_record_session_event(session_id: str, payload: dict) -> None:
    """Rule 1, double-checked here even though `step_gate.py` already
    required it ("never trust a sibling module without checking")."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None or data.get("recorded") is not True:
        return
    tool_input = tool_args(payload)  # RMP-5/RMP-9: see payload_util.tool_args
    state = step_state.read_state(session_id)
    workspace = state["workspace"]
    if workspace is None or tool_input.get("workspace_id") != workspace["id"]:
        return
    expected_kind = "workspace_switched" if state["workspace_logged_ever"] else "workspace_selected"
    if tool_input.get("kind") != expected_kind:
        return
    step_state.set_workspace_logged(session_id)
    _maybe_finish_choose_workspace(session_id)


# ------------------------------------------------------- get_resume_checklist --

def handle_get_resume_checklist(session_id: str, payload: dict) -> None:
    """Rule 2 (the read half) and rule 4 (resume): a successful read for the
    CURRENT workspace marks `checklist_read`. Any workspace-kind step the
    server already shows `state: "done"` for is accepted as already
    finished this session -- not re-asked, and not re-ticked, because the
    real tick already happened in an earlier session (P1603's
    `get_resume_checklist` response shape: `steps: [{id, ..., state, how}]`)."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    state = step_state.read_state(session_id)
    workspace = state["workspace"]
    if workspace is None or data.get("workspace_id") != workspace["id"]:
        return
    step_state.set_checklist_read(session_id)

    entries = data.get("steps")
    if isinstance(entries, list):
        by_id = {s["id"]: s for s in steps_manifest.load_steps(session_id)}
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            step_id = entry.get("id")
            if not isinstance(step_id, str):
                continue

            if step_id == "own_instagram_account":
                # RMP-23 "already known" tick + RMP-161 website suggestion
                # capture both live in one call now -- see
                # `own_account_suggestion.note_checklist_entry`'s own
                # docstring for why this replaced the old inline block.
                own_account_suggestion.note_checklist_entry(session_id, entry)

            if by_id.get(step_id, {}).get("kind") != "workspace":
                continue
            if entry.get("state") != "done":
                continue
            how = entry.get("how")
            how = how if isinstance(how, str) and how else "already_known"
            current = step_state.read_state(session_id)
            if step_id not in current["steps_passed"]:
                step_state.mark_step_passed(session_id, step_id, how)
            if step_id not in current["ticked"]:
                step_state.mark_ticked(session_id, step_id)
            # RMP-52: if step 4 is done/skipped, set the reoffer flag
            if step_id == "own_instagram_account" and how == "skipped":
                # RMP-58: read fresh state AFTER the two writes above
                fresh = step_state.read_state(session_id)
                step_skip.maybe_set_reoffer_pending(session_id, fresh)
            # RMP-66: website re-offer (skipped) / monthly re-read check (answered)
            if step_id == "website":
                website_return.maybe_set_website_return(session_id, how, entry.get("skip_reason"))

    # RMP-53: mark counts as read (even if detail is missing).
    own_account_reminder.handle_get_resume_checklist(session_id)
    _maybe_finish_choose_workspace(session_id)


# ------------------------------------------------------- record_checklist_step --

def handle_record_checklist_step(session_id: str, payload: dict) -> None:
    """Rule 3: a successful "done" tick is the ONLY thing that lets gate
    ordering (`step_gate._first_unpassed`) move past this step."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None or data.get("recorded") is not True:
        return
    tool_input = tool_args(payload)  # RMP-5/RMP-9: see payload_util.tool_args
    if tool_input.get("state") != "done":
        return
    step_id = tool_input.get("step_id")
    how = tool_input.get("how")
    if not isinstance(step_id, str) or not step_id:
        return
    state = step_state.read_state(session_id)
    if state["steps_passed"].get(step_id) != how:
        return  # defense in depth -- step_gate.py should already have denied this
    step_state.mark_ticked(session_id, step_id)


# ------------------------------------------------------------- the reminder --

def build_step_reminder(session_id: str) -> dict[str, Any] | None:
    """The exact next call the model must make to finish the current
    question step (rule 5), the same way `session_record.build_reminder_
    payload` does for step 1's `record_session_start`. Returns
    `{"call": <tool suffix>, "payload": <exact kwargs>}`, or None once every
    known step is ticked, or nothing is waiting on the model right now.

    P1615 (bug 2): step 1's tick is earned once `choose_workspace` itself passes -- remind for it
    FIRST, before step 2's own tick reminder below (`reset_for_new_workspace` re-earns it per
    workspace, same as step 2).

    RMP-23: once every step is ticked (the loop below falls through), a last
    check remains for step 4's 7-day auto-refresh -- a stale/missing
    `profile_fetched_at` reminds for a free `refresh_competitor`, and a
    completed refresh not yet logged reminds for `record_session_event
    (profile_refreshed)`. Runs LAST, after the normal step 1-4 flow.

    A chain of "priority" reminders -- a mismatch just shown/answered, a
    skip/reoffer pick, a website re-offer pick, a pending fact event, a
    pending website-mismatch event -- runs FIRST, before all of the above.
    See `priority_reminders.first_priority_reminder` for the exact order and
    the founder decisions behind it (split out to keep this file under 300
    lines, RMP-66)."""
    step_state.sync_connection_check(session_id)
    state = step_state.read_state(session_id)

    priority_reminder = priority_reminders.first_priority_reminder(session_id, state)
    if priority_reminder is not None:
        return priority_reminder

    if "connection_check" not in state["ticked"] and "choose_workspace" in state["steps_passed"]:
        return {
            "call": "record_checklist_step",
            "payload": {
                "client_session_id": session_id, "step_id": "connection_check",
                "state": "done", "how": "passed",
            },
        }

    for step in steps_manifest.load_steps(session_id):
        step_id = step["id"]
        if step_id == "connection_check" or step_id in state["ticked"]:
            continue
        if step.get("wait_for"):
            continue
        # RMP-194 P1: a `wait_for` step (business_review) has no recorder yet
        # (P3) and never blocks ordering (step_order.py) -- skip it here too,
        # or "every known step ticked" below would never fire once step 6 is
        # done, and the step-4 auto-refresh reminder (RMP-23) would silently
        # stop appearing. Rule 3 break: remove this guard -> RED
        # (test_own_account_reminder_part2.test_all_ticked_stale_profile_
        # refreshed_line and the two test_step4_checklist_and_reminder cases).

        if step_id == "choose_workspace":
            if state["workspace"] is None:
                picked = state["human_answers"].get("choose_workspace")
                if picked is None:
                    return None  # no pick yet -- nothing to remind about
                # RMP-76: one call replaces set_active_workspace + the
                # session-event log + the checklist read + both ticks below.
                # RMP-173 P2/P4: rules_version tells the server whether this
                # session already has the current step rules cached, so an
                # up-to-date plugin never re-downloads them -- steps_manifest
                # is no longer sent at all; the server seeds its own.
                return {
                    "call": "open_workspace",
                    "payload": {
                        "client_session_id": session_id, "workspace_id": picked,
                        "rules_version": step_rules_cache.cached_rules_version(session_id),
                    },
                }
            if not state["workspace_logged"]:
                kind = "workspace_switched" if state["workspace_logged_ever"] else "workspace_selected"
                return {
                    "call": "record_session_event",
                    "payload": {
                        "client_session_id": session_id, "kind": kind,
                        "workspace_id": state["workspace"]["id"],
                    },
                }
            if not state["checklist_read"]:
                # RMP-173 P4: steps_manifest is no longer sent -- the server
                # already seeded its own manifest when open_workspace ran.
                return {
                    "call": "get_resume_checklist",
                    "payload": {
                        "rules_version": step_rules_cache.cached_rules_version(session_id),
                    },
                }

        if step_id == "revenue_model" and step_id not in state["steps_passed"]:
            # RMP-24 (S5-B6): the one-shot "I don't know" follow-up takes priority over the
            # words-to-log reminder below -- they are mutually exclusive in practice (no real
            # description was ever saved while a "don't know" count is pending).
            waiting = revenue_recorder.description_waiting(
                steps_manifest.load_steps(session_id), state, revenue_recorder.read_progress(session_id),
            )
            has_fresh_reply = bool(state["human_answers"].get("revenue_description"))
            follow_up = revenue_dont_know.build_follow_up_reminder(session_id, waiting and not has_fresh_reply)
            if follow_up is not None:
                return follow_up
            return revenue_recorder.pending_event_reminder(session_id, state)

        how = state["steps_passed"].get(step_id)
        if how is None:
            return None  # not answered yet -- its own question flow handles that

        # RMP-194: hold step 6's own tick until the your-website skill's
        # reviews-consent question (section 8) has had its turn -- ticking
        # the instant facts are saved would make step 7's "come back when
        # ready" offer reachable mid-flow (see `website_tick_ready`'s own
        # docstring for the live bug this closes).
        if step_id == "website" and not website_recorder.website_tick_ready(session_id):
            return None

        # RMP-53: step 4 reminder with the "We'll plan for" / "Added" line.
        if step_id == "own_instagram_account":
            own = own_account_reminder.step4_reminder(session_id, state, how)
            if own is not None:
                return own

        payload = {"client_session_id": session_id, "step_id": step_id, "state": "done", "how": how}
        if step_id == "website" and how == "skipped" and website_return.skip_reason(session_id):
            payload["skip_reason"] = website_return.skip_reason(session_id)  # P2358: "no_website" or "later"
        return {"call": "record_checklist_step", "payload": payload}

    # RMP-23: every known step ticked -- the one thing still worth reminding
    # about is step 4's 7-day auto-refresh, split into step_recorder_
    # refresh.py to keep this file under the 300-line cap (RMP-194).
    return step_recorder_refresh.auto_refresh_reminder(session_id, state)

