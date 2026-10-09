#!/usr/bin/env python3
"""Step 4's 7-day auto-refresh reminder (RMP-23), split out of
`checklist_recorder.build_step_reminder`'s own tail so that file has room
for RMP-194's website tick-ready gate without going over the 300-line cap
(same "split when it grows" precedent RMP-190's `tool_result_dispatch.py`
already set for `connection_state_cli.py`). Pure move: same function, same
order, same calls -- no behaviour change.

Runs LAST, once every known step in `checklist_recorder.build_step_
reminder`'s own loop is already ticked: a stale/missing `profile_fetched_at`
reminds for a free `refresh_competitor`, and a completed refresh not yet
logged reminds for `record_session_event(profile_refreshed)`. RMP-53: the
`profile_refreshed` reminder also carries the "We'll plan for" line with the
refreshed numbers.
"""
from __future__ import annotations

from typing import Any

import own_account_reminder


def auto_refresh_reminder(session_id: str, state: dict) -> dict[str, Any] | None:
    """`state["workspace"]` is guarded defensively (own_instagram_account
    can only be ticked after a workspace is chosen, but this never raises
    even if that somehow fails)."""
    if "own_instagram_account" not in state["ticked"]:
        return None
    if state["last_refresh"] is not None:
        if state["workspace"] is None:
            return None
        # Build the line with refreshed numbers (as of today).
        detail = state["last_refresh"]
        handle = detail.get("handle", "")
        line = own_account_reminder.known_line(
            session_id, handle, detail.get("follower_count"), detail.get("media_count"), own_account_reminder.AS_OF_TODAY
        )
        return own_account_reminder._with_say({
            "call": "record_session_event",
            "payload": {
                "client_session_id": session_id, "kind": "profile_refreshed",
                "workspace_id": state["workspace"]["id"], "detail": state["last_refresh"],
            },
        }, line)
    detail = state["last_known_detail"]
    if (
        detail is not None
        and not state["own_account_refreshed"]
        and own_account_reminder._profile_is_stale(detail.get("profile_fetched_at"))
    ):
        return {
            "call": "refresh_competitor",
            "payload": {"handles": [detail["handle"]]},
        }
    return None
