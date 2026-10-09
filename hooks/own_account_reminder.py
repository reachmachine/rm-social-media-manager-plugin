#!/usr/bin/env python3
"""Step-4 reminder logic (RMP-53): tell the customer which Instagram account
the plan uses, with its follower/post numbers. Split from `checklist_
recorder.py` to keep both under 300 lines. Never crashes."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import os
from typing import Any

import connection_state as cs
from own_account_lines import AS_OF_TODAY, added_line, as_of_label, known_line  # noqa: F401  (re-exported: the line builders live there)
import step_rules_cache
import step_state

# RMP-23: how old (days) a known follower/post count may get before the
# session-start reminder asks for a free re-scrape. Env var, not hardcoded
# (CLAUDE.md) -- the sandbox sets this to 0 to exercise the refresh path
# live without waiting a week.
_REFRESH_STALE_DAYS = int(os.environ.get("RMP_OWN_ACCOUNT_REFRESH_DAYS", "7"))

# Raw flag key for "counts read since the add" -- kept out of
# `step_state.read_state` to avoid bumping `step_state.py` over 300 lines.
_COUNTS_READ_KEY = "own_account_counts_read"


def _profile_is_stale(profile_fetched_at: str | None) -> bool:
    """RMP-23: True when the timestamp is missing, unparsable, or older than
    `_REFRESH_STALE_DAYS`. Never raises."""
    if not isinstance(profile_fetched_at, str) or not profile_fetched_at:
        return True
    try:
        fetched = datetime.fromisoformat(profile_fetched_at.replace("Z", "+00:00"))
    except Exception:
        return True
    if fetched.tzinfo is None:
        fetched = fetched.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - fetched) > timedelta(days=_REFRESH_STALE_DAYS)


def _normalize_handle(handle: str | None) -> str:
    """Strip leading '@' and casefold for comparison. Never raises."""
    if not isinstance(handle, str):
        return ""
    return handle.lstrip("@").casefold()


def _counts_have_been_read(session_id: str) -> bool:
    """Raw flag: has `get_resume_checklist` been called since the add? Never raises."""
    raw = cs.read_raw(session_id)
    return raw.get(_COUNTS_READ_KEY) is True


def _mark_counts_read(session_id: str) -> None:
    """Set the flag: counts have been read. Never raises."""
    cs.write_patch(session_id, {_COUNTS_READ_KEY: True})


def _clear_counts_read(session_id: str) -> None:
    """Clear the flag: a new add just happened. Never raises."""
    cs.write_patch(session_id, {_COUNTS_READ_KEY: False})


def _with_say(reminder: dict[str, Any], line: str | None) -> dict[str, Any]:
    """The reminder with the server's line to say, or without `say` when the server sent none (the hook invents no English)."""
    return {**reminder, "say": line} if line else reminder


def step4_reminder(session_id: str, state: dict[str, Any], how: str) -> dict[str, Any] | None:
    """The next step-4 reminder when step 4 has passed but is not ticked yet.
    `how` is state["steps_passed"]["own_instagram_account"]. Returns the exact
    call dict `{"call": <tool suffix>, "payload": {...}, "say": <line>}`, or
    None to fall through to the generic tick. Never raises."""
    # RMP-58 follow-up: The handle for the line comes from own_account_handle
    # (set by the add or by checklist detail), not from last_known_detail.
    # For a brand-new customer (S4-1 case), last_known_detail is None at the
    # moment of the add.
    handle = state["own_account_handle"]
    if not isinstance(handle, str) or not handle:
        return None  # defensive: no handle set, nothing to say

    # RMP-58: skipped → no line; return None so the generic tick runs.
    if how == "skipped":
        return None

    detail = state["last_known_detail"]

    # already_known: needs a detail whose handle matches. Use its numbers.
    if how == "already_known":
        # Check if we have a matching detail
        if detail is None:
            return None  # No detail yet, fall through to generic tick
        if _normalize_handle(detail.get("handle")) != _normalize_handle(handle):
            return None  # Detail is for a different handle, fall through
        # Stale + not yet refreshed → remind for refresh_competitor BEFORE tick.
        if _profile_is_stale(detail.get("profile_fetched_at")) and not state["own_account_refreshed"]:
            return {
                "call": "refresh_competitor",
                "payload": {"handles": [handle]},
            }
        # A refresh result waiting to be logged → remind for the log.
        if state["last_refresh"] is not None:
            workspace = state["workspace"]
            if workspace is None:
                return None  # defensive: no workspace, can't build the payload
            return {
                "call": "record_session_event",
                "payload": {
                    "client_session_id": session_id,
                    "kind": "profile_refreshed",
                    "workspace_id": workspace["id"],
                    "detail": state["last_refresh"],
                },
            }
        # Otherwise: tick with the "We'll plan for" line.
        # If refreshed this session, label is "today"; else use the real date.
        label = AS_OF_TODAY if state["own_account_refreshed"] else as_of_label(detail.get("profile_fetched_at"))
        return _with_say({
            "call": "record_checklist_step",
            "payload": {
                "client_session_id": session_id,
                "step_id": "own_instagram_account",
                "state": "done",
                "how": how,
            },
        }, known_line(session_id, handle, detail.get("follower_count"), detail.get("media_count"), label))

    # answered: the add has just happened. Read the counts if not yet read.
    if how == "answered":
        if not _counts_have_been_read(session_id):
            # Whether or not a detail exists, ask for get_resume_checklist to
            # fetch it. RMP-173 P4: steps_manifest is no longer sent, and
            # rules_version was missing entirely here before this fix (it
            # defaulted to 0 server-side, re-downloading the full rules body
            # on every one of these reminders).
            return {
                "call": "get_resume_checklist",
                "payload": {"rules_version": step_rules_cache.cached_rules_version(session_id)},
            }
        # Counts have been read. If detail matches handle, use its numbers.
        # Otherwise, fall back to "Added **@h**." with no numbers.
        if detail is not None and _normalize_handle(detail.get("handle")) == _normalize_handle(handle):
            follower_count = detail.get("follower_count")
            media_count = detail.get("media_count")
        else:
            # Detail missing or for different handle → "Added **@h**."
            follower_count = None
            media_count = None
        return _with_say({
            "call": "record_checklist_step",
            "payload": {
                "client_session_id": session_id,
                "step_id": "own_instagram_account",
                "state": "done",
                "how": how,
            },
        }, added_line(session_id, handle, follower_count, media_count))

    # Unknown how value: defensive fallback to generic tick.
    return None


def handle_add_to_watchlist(session_id: str) -> None:
    """Clear the 'counts read' flag when a real add is recorded. Called from
    `step_recorder_own_account.handle_add_to_watchlist`. Never raises."""
    _clear_counts_read(session_id)


def handle_get_resume_checklist(session_id: str) -> None:
    """Set the 'counts read' flag on any successful checklist read. Called from
    `checklist_recorder.handle_get_resume_checklist`. Set even when `detail`
    is missing or names another handle, so a missing detail makes the line fall
    back to 'Added **@h**.' and never loops. Never raises."""
    _mark_counts_read(session_id)
