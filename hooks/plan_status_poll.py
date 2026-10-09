#!/usr/bin/env python3
"""UserPromptSubmit hook: polls `GET /api/v1/plugin/plan-status` so a
drive-mode session notices a plan change with no model tokens spent (RMP-201
P4, design doc §3: "replaces `business_ready_poll.py` ... its gate is 'the
cached plan lists a running node or a pending server node' ... it adds one
`additionalContext` line: 'Call next_actions once.'").

OWN FILE, SAME REASONING `business_ready_poll.py`'s docstring gives (two
`UserPromptSubmit` hooks can run for the same event in parallel) -- this one
only ever touches `plan_cache.py`'s own file, never `connection_state.py`,
so it can never race `business_ready_poll.py` or anything else.

DORMANT OUTSIDE DRIVE MODE (design's own scope line: "drive enables it,
anything else keeps today's behaviour exactly") -- checked first, before
any state read or network call, so a `shadow`/`off` session pays nothing
for this hook existing.

GATE: only polls while the cached plan says there is something worth
checking on -- a `running` node (a background job in flight) or a `gate`
with at least one deny entry (something server-side is still blocking).
An idle plan (nothing running, nothing denied) has nothing that could have
changed without the model already knowing, so polling would just spend a
network round-trip for no reason.

THROTTLE + TIMEOUT, same env-configurable pattern as `business_ready_poll.py`
(`PLAN_STATUS_POLL_INTERVAL_S` default 30, `PLAN_STATUS_POLL_TIMEOUT_S`
default 2), stored in its own tiny state file so the throttle survives
across turns without touching `plan_cache.py`'s own shape.

FAIL-SAFE: never raises, never blocks a prompt. A network failure, timeout,
or malformed response is silently ignored -- the next turn's poll simply
tries again once the throttle window has passed."""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

import plan_cache
import planner_mode_state
import plugin_api
import state_file_io
import step_state
import transcript_cursor as tc

_DEFAULT_INTERVAL_S = 30
_DEFAULT_TIMEOUT_S = 2
_PATH = "/api/v1/plugin/plan-status"
_ENV_OVERRIDE = "RM_PLAN_STATUS_URL_OVERRIDE"
_NUDGE = "Call next_actions once."


def _poll_interval_s() -> float:
    try:
        return float(os.environ.get("PLAN_STATUS_POLL_INTERVAL_S", _DEFAULT_INTERVAL_S))
    except (TypeError, ValueError):
        return _DEFAULT_INTERVAL_S


def _poll_timeout_s() -> float:
    try:
        return float(os.environ.get("PLAN_STATUS_POLL_TIMEOUT_S", _DEFAULT_TIMEOUT_S))
    except (TypeError, ValueError):
        return _DEFAULT_TIMEOUT_S


def _throttle_path(session_id: str) -> pathlib.Path:
    tmp_dir = os.environ.get("TMPDIR") or "/tmp"
    return pathlib.Path(tmp_dir) / f"rm-plugin-v2-plan-poll-{session_id}.json"


def _last_poll_at(session_id: str) -> float | None:
    try:
        data = json.loads(_throttle_path(session_id).read_text(encoding="utf-8"))
    except Exception:
        return None
    value = data.get("last_poll_at") if isinstance(data, dict) else None
    return value if isinstance(value, (int, float)) else None


def _set_last_poll_at(session_id: str, when: float) -> None:
    try:
        state_file_io.write_atomic(_throttle_path(session_id), json.dumps({"last_poll_at": when}))
    except Exception:
        pass


def _throttled(session_id: str) -> bool:
    last = _last_poll_at(session_id)
    if last is None:
        return False
    return (time.monotonic() - last) < _poll_interval_s()


def _fetch(workspace_id: str, upload_key: str) -> dict[str, Any] | None:
    query = urllib.parse.urlencode({"workspace_id": workspace_id})
    url = plugin_api.api_url(f"{_PATH}?{query}", _ENV_OVERRIDE)
    request = urllib.request.Request(
        url, method="GET",
        headers={"X-RM-Upload-Key": upload_key, "User-Agent": plugin_api.user_agent()},
    )
    try:
        with urllib.request.urlopen(request, timeout=_poll_timeout_s()) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None
    return data if isinstance(data, dict) else None


def poll(session_id: str) -> str | None:
    """The one entry point: fail-silent, never raises, never blocks. Returns
    the nudge text to print, or `None`."""
    try:
        if not planner_mode_state.is_drive(session_id):
            return None
        cached = plan_cache.read_state(session_id)
        if not cached["running"] and not cached["gate"]["deny"]:
            return None  # nothing in flight, nothing blocked -- nothing to learn
        if _throttled(session_id):
            return None
        _set_last_poll_at(session_id, time.monotonic())

        cursor = tc.read_cursor(session_id)
        upload_key = cursor.get("upload_key")
        if not isinstance(upload_key, str) or not upload_key:
            return None
        workspace = step_state.read_state(session_id)["workspace"]
        if workspace is None:
            return None
        workspace_id = workspace["id"]

        data = _fetch(workspace_id, upload_key)
        if data is None:
            return None
        server_version = data.get("plan_version")
        if not isinstance(server_version, int):
            return None
        if server_version == cached["plan_version"]:
            return None
        # RMP-193 (live re-run 2026-09-29): the nudge tells the model to call
        # next_actions -- but the repeat-call guard (step_gate_plan) denies it
        # with "Nothing new yet" while the cache is not dirty, so the nudge
        # defeated itself. The server just said the plan moved: it IS dirty.
        plan_cache.mark_dirty(session_id)
        return _NUDGE
    except Exception:
        return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    session_id = payload.get("session_id")
    if isinstance(session_id, str) and session_id:
        text = poll(session_id)
        if text:
            print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
