#!/usr/bin/env python3
"""Tells the server "the customer just wrote a message" (RMP-201, live
2026-09-29), so it serves a pending question again.

WHY: the server holds back a question it already served (per chat, 900 s)
so a background job's notification turn cannot repeat it. When the model
DROPS a question (the live run: the shop question rode inside an
`open_workspace` reply and was never shown), the customer's next message got
`ask: null, waiting: <node>` and the customer was stuck for 15 minutes. A
real customer turn releases the hold: `POST /api/v1/plugin/customer-turn`.

Called from `capture_last_prompt.py`, ONLY for text the customer typed --
never for a `<task-notification>` or other system-made prompt (that is
exactly the turn the hold exists for).

DORMANT OUTSIDE DRIVE MODE, same as `plan_status_poll.py`. FAIL-SAFE: never
raises, never blocks a prompt, 2 s timeout; any failure just leaves today's
behaviour (the hold waits out its quiet time). Not throttled: one call per
typed message is already rare, and it must land before the model's next
`next_actions`."""
from __future__ import annotations

import os
import urllib.error
import urllib.parse
import urllib.request

import planner_mode_state
import plugin_api
import step_state
import transcript_cursor as tc

_PATH = "/api/v1/plugin/customer-turn"
_ENV_OVERRIDE = "RM_CUSTOMER_TURN_URL_OVERRIDE"
_DEFAULT_TIMEOUT_S = 2


def _timeout_s() -> float:
    try:
        return float(os.environ.get("CUSTOMER_TURN_TIMEOUT_S", _DEFAULT_TIMEOUT_S))
    except (TypeError, ValueError):
        return _DEFAULT_TIMEOUT_S


def _post(workspace_id: str, upload_key: str) -> bool:
    query = urllib.parse.urlencode({"workspace_id": workspace_id})
    url = plugin_api.api_url(f"{_PATH}?{query}", _ENV_OVERRIDE)
    request = urllib.request.Request(
        url, method="POST", data=b"",
        headers={"X-RM-Upload-Key": upload_key, "User-Agent": plugin_api.user_agent()},
    )
    try:
        with urllib.request.urlopen(request, timeout=_timeout_s()):
            return True
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return False


def release(session_id: str) -> bool:
    """`True` when the server was told. Never raises."""
    try:
        if not planner_mode_state.is_drive(session_id):
            return False
        upload_key = tc.read_cursor(session_id).get("upload_key")
        if not isinstance(upload_key, str) or not upload_key:
            return False
        workspace = step_state.read_state(session_id)["workspace"]
        if workspace is None:
            return False
        return _post(workspace["id"], upload_key)
    except Exception:
        return False
