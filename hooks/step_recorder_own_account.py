#!/usr/bin/env python3
"""RMP-23 step-4 PostToolUse handlers -- split out of `step_recorder.py` to
stay under the 300-line file limit (same "split when it grows" precedent as
`checklist_recorder.py`'s own split off `step_recorder.py`, RMP-9).

Spec: `docs/plugin-v2/04-own-instagram-account.md`. Owns the three Reach
Machine tool results RMP-23 adds: `add_to_watchlist` (the self add),
`refresh_competitor` (the free 7-day refresh of the OWN account), and the
`profile_refreshed` half of `record_session_event`. `step_recorder.py`
imports these into its own `_POST_TOOL_USE_HANDLERS` dispatch table, so
there is still one place PostToolUse events are wired, not two.

FAIL-SAFE: nothing here may crash a hook -- same convention as every
sibling module.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from typing import Any

import checklist_recorder as ckl
import connection_state as cs
import own_account_mismatch
import own_account_not_found
import own_account_reminder
from payload_util import tool_args
import step_gate_own_account as own_account_gate
import step_state
import step_state_own_account
import steps_manifest


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def handle_add_to_watchlist(session_id: str, payload: dict) -> None:
    """A REAL add (`added >= 1`) is step 4's "answered" -- founder decision
    1, nothing charged/added means nothing to mark. Also spends the typed
    handle (`clear_human_answer`), same "one pick, one add" rule as
    `step_recorder._handle_update_creator_brief`'s "one saved answer spends
    the pick".

    RMP-23, founder decision 6: a PREVIEW (`requires_confirmation: true`)
    is handed to `own_account_mismatch.note_preview_result` instead -- it
    may have just told us the customer's own account is flagged. RMP-175:
    the SAME preview is also handed to `own_account_not_found.
    note_preview_result` -- it may instead have told us Instagram had no
    data for the handle at all (the two never fire on the same preview:
    the server only reaches the fit/authenticity screen once the not_found
    check has already passed)."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    tool_input = tool_args(payload)
    if data.get("requires_confirmation") is True:
        own_account_mismatch.note_preview_result(session_id, tool_input, data)
        own_account_not_found.note_preview_result(session_id, tool_input, data)
        return
    if int(data.get("added", 0) or 0) < 1:
        return
    handle = own_account_gate.normalize_handle(tool_input.get("self_handle"))
    state = step_state.read_state(session_id)
    if not isinstance(handle, str) or not handle or handle != state["human_answers"].get("own_instagram_account"):
        return  # defense in depth -- step_gate.py should already have denied a mismatched add
    step_state.set_own_account_handle(session_id, handle)
    step_state.mark_step_passed(session_id, "own_instagram_account", "answered")
    step_state.clear_human_answer(session_id, "own_instagram_account")
    # RMP-53: clear the "counts read" flag so the next reminder re-reads.
    own_account_reminder.handle_add_to_watchlist(session_id)


def _record_cooldown_skip(session_id: str, own_handle: str, row: dict) -> None:
    """RMP-171: the server skipped the refresh (its own cooldown is still
    running). Mark the attempt as spent -- same no-loop guard as a real
    refresh, see `handle_refresh_competitor`'s own docstring -- but do NOT
    set `last_refresh` (nothing changed, nothing to log), and sync
    `last_known_detail`'s as-of date to the server's own answer instead of
    leaving our stale local guess in place."""
    step_state.set_own_account_refreshed(session_id)
    as_of = row.get("as_of")
    existing_detail = step_state.read_state(session_id)["last_known_detail"] or {}
    step_state.set_last_known_detail(session_id, {
        "handle": own_handle,
        "follower_count": row.get("follower_count"),
        "media_count": row.get("media_count"),
        "profile_fetched_at": as_of or existing_detail.get("profile_fetched_at"),
        "profile_id": existing_detail.get("profile_id"),
    })


def handle_refresh_competitor(session_id: str, payload: dict) -> None:
    """Remembers a successful refresh of the WORKSPACE'S OWN account (never
    a competitor's) so `checklist_recorder.build_step_reminder` can prompt
    `record_session_event(profile_refreshed)` next, and `step_gate_own_
    account.check_profile_refreshed_event` can verify that event's `detail`
    against a real result. `own_account_refreshed` caps this to once per
    session -- see `step_state.py`'s own docstring for why (no-loop guard).

    RMP-171: the SERVER decides whether a real refresh happened, not our own
    day math -- `own_account_reminder.py`'s staleness check is only a HINT
    for when to try the call. A row's `refreshed: false` means the server's
    own free-refresh cooldown was still running: nothing changed on
    Instagram, so there is nothing to log with `record_session_event`. A
    missing `refreshed` key (an older server) defaults to True, so this
    stays correct against the pre-RMP-171 response shape too."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    state = step_state.read_state(session_id)
    own_handle = state["own_account_handle"]
    if not own_handle:
        return  # not this workspace's own account -- not our business
    for row in (data.get("refreshed") or []):
        if not isinstance(row, dict) or row.get("handle") != own_handle:
            continue
        if row.get("refreshed", True) is False:
            _record_cooldown_skip(session_id, own_handle, row)
            return
        refresh_detail = {
            "handle": own_handle,
            "follower_count": row.get("follower_count"),
            "media_count": row.get("media_count"),  # P1619 added this field
        }
        step_state.set_last_refresh(session_id, refresh_detail)
        # Set own_account_refreshed BEFORE detail update, so the once-per-session cap holds
        # even if a later line fails (RMP-58 follow-up).
        step_state.set_own_account_refreshed(session_id)
        # RMP-53: also update last_known_detail with the refreshed numbers.
        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        # Defense: handle None last_known_detail without AttributeError
        existing_detail = step_state.read_state(session_id)["last_known_detail"] or {}
        step_state.set_last_known_detail(session_id, {
            "handle": own_handle,
            "follower_count": row.get("follower_count"),
            "media_count": row.get("media_count"),
            "profile_fetched_at": now_iso,
            "profile_id": existing_detail.get("profile_id"),
        })
        return


def handle_change_own_account(session_id: str, payload: dict) -> None:
    """RMP-113 -- a real `change_own_account` result (`applied: true`)
    updates local state to match what the server just did, so the NEXT
    read of step 4 reflects it instead of quietly going stale. A preview
    (`applied: false`, still deciding or waiting for confirm) changes
    nothing here -- there is nothing to record yet.

    `rename`: swaps the handle/numbers in place -- the step was already
    done, so it stays done, no re-tick. `different_account`: the server
    already reset the checklist from the account step onward
    (`own_account_change_service.apply_different_account`); this mirrors
    that locally so the NEXT `get_resume_checklist`/step-order read agrees
    with the server instead of a stale local tick."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None or data.get("applied") is not True:
        return
    path = data.get("path")
    if path == "rename":
        new_handle = own_account_gate.normalize_handle(data.get("new_handle"))
        if not isinstance(new_handle, str) or not new_handle:
            return
        step_state.set_own_account_handle(session_id, new_handle)
        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        step_state.set_last_known_detail(session_id, {
            "handle": new_handle,
            "follower_count": data.get("follower_count"),
            "media_count": data.get("media_count"),
            "profile_fetched_at": now_iso,
            "profile_id": None,
        })
    elif path == "different_account":
        reset_ids = [s["id"] for s in steps_manifest.load_steps(session_id) if s.get("number", 0) >= 4]
        if reset_ids:
            step_state_own_account.reset_steps_from(session_id, reset_ids)


def _handle_profile_refreshed_event(session_id: str, payload: dict) -> None:
    """A successful `profile_refreshed` log spends the refresh -- one
    refresh, one log entry, same "spend the pick" shape as
    `handle_add_to_watchlist`'s `clear_human_answer`. Runs alongside
    `checklist_recorder.handle_record_session_event`, never instead of it --
    see `handle_record_session_event_dispatch` below."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None or data.get("recorded") is not True:
        return
    tool_input = tool_args(payload)
    if tool_input.get("kind") != "profile_refreshed":
        return
    step_state.set_last_refresh(session_id, None)


def _handle_mismatch_event(session_id: str, payload: dict) -> None:
    """A successful (`recorded: true`) `own_account_mismatch_shown`/
    `..._answered` spends that reminder -- same "spend the pick" shape as
    `_handle_profile_refreshed_event` above."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None or data.get("recorded") is not True:
        return
    tool_input = tool_args(payload)
    kind = tool_input.get("kind")
    if kind not in own_account_mismatch.MISMATCH_EVENT_KINDS:
        return
    own_account_mismatch.handle_mismatch_event_recorded(session_id, kind, tool_input.get("detail"))


def handle_record_session_event_dispatch(session_id: str, payload: dict) -> None:
    """All three inner calls are safe for EVERY `record_session_event`
    call -- each checks its own `kind` before doing anything, so there is
    still one dispatch entry for this tool in `step_recorder.py`, not
    three."""
    ckl.handle_record_session_event(session_id, payload)
    _handle_profile_refreshed_event(session_id, payload)
    _handle_mismatch_event(session_id, payload)
