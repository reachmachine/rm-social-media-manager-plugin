#!/usr/bin/env python3
"""UserPromptSubmit hook: polls the server for step 7's "ready to review"
signal, with no model tokens spent (RMP-194 P2, design doc Part 4 point 4).

WHY A SEPARATE HOOK, OWN FILE. `connection-reminder.sh` already runs on
every `UserPromptSubmit` and reads/writes the SHARED `connection_state` file
(`step_state.py`'s own keys). Claude Code can run two `UserPromptSubmit`
hook entries for the SAME event in parallel (RMP-194 P4 hit exactly this
race between two hooks both patching that one file -- see
`capture_last_prompt.py`'s own docstring). This hook makes a real network
call, so it is slower and more likely to overlap a sibling hook's write --
giving it its OWN file (never touched by `connection_state.write_patch`)
means it can never race anything else, the same fix P4 already used.

GATE (all three must hold, checked from the READ-ONLY shared state):
  - step 6 ("website") is ticked -- nothing to review before then;
  - step 7 ("business_review") is NOT ticked -- nothing left to poll for
    once the customer has already finished it;
  - this session has not already learned `ready: true` -- once known, it
    stays known for the rest of the session (a fresh session gets a fresh
    file, so a "Later" answer is naturally re-offered next session, same as
    step 4's own re-offer).

THROTTLE + TIMEOUT (env-configurable, never hardcoded per CLAUDE.md):
`BUSINESS_READY_POLL_INTERVAL_S` (default 30) between real calls;
`BUSINESS_READY_POLL_TIMEOUT_S` (default 2) per call. Both read fresh on
every call (a test can override the env var without reloading the module).

FAIL-SAFE: never blocks a prompt, never raises, never prints anything (this
hook has nothing to say to the model -- `business_return.py` is what turns
a "ready" flag into a customer-facing offer, from the shared reminder
chain). A network failure, timeout, or malformed response leaves the file
untouched -- the NEXT turn's poll simply tries again once the throttle
window has passed.
"""
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

import planner_mode_state
import plugin_api
import state_file_io
import step_state
import transcript_cursor as tc

_DEFAULT_INTERVAL_S = 30
_DEFAULT_TIMEOUT_S = 2
_PATH = "/api/v1/plugin/business-ready"
_ENV_OVERRIDE = "RM_BUSINESS_READY_URL_OVERRIDE"


def _poll_interval_s() -> float:
    try:
        return float(os.environ.get("BUSINESS_READY_POLL_INTERVAL_S", _DEFAULT_INTERVAL_S))
    except (TypeError, ValueError):
        return _DEFAULT_INTERVAL_S


def _poll_timeout_s() -> float:
    try:
        return float(os.environ.get("BUSINESS_READY_POLL_TIMEOUT_S", _DEFAULT_TIMEOUT_S))
    except (TypeError, ValueError):
        return _DEFAULT_TIMEOUT_S


def state_path(session_id: str) -> pathlib.Path:
    tmp_dir = os.environ.get("TMPDIR") or "/tmp"
    return pathlib.Path(tmp_dir) / f"rm-plugin-v2-business-ready-{session_id}.json"


def read_state(session_id: str) -> dict[str, Any]:
    """`{"ready": bool, "say": str|None, "opts": list|None, "last_poll_at":
    float|None}`. Corrupt/missing file reads as "never polled, not ready" --
    never raises."""
    result: dict[str, Any] = {"ready": False, "say": None, "opts": None, "last_poll_at": None}
    try:
        data = json.loads(state_path(session_id).read_text(encoding="utf-8"))
    except Exception:
        return result
    if not isinstance(data, dict):
        return result
    if isinstance(data.get("ready"), bool):
        result["ready"] = data["ready"]
    if isinstance(data.get("say"), str):
        result["say"] = data["say"]
    if isinstance(data.get("opts"), list):
        result["opts"] = data["opts"]
    if isinstance(data.get("last_poll_at"), (int, float)):
        result["last_poll_at"] = data["last_poll_at"]
    return result


def _write_state(session_id: str, patch: dict[str, Any]) -> None:
    state_file_io.update_json(state_path(session_id), lambda: read_state(session_id), patch)


def _should_poll(session_id: str) -> str | None:
    """The active workspace id if this session's gate allows a poll right
    now, else `None`. Pure state reads only -- see the module docstring for
    the three conditions.

    RMP-201 P4: dormant once the server said `mode: "drive"` --
    `plan_status_poll.py` is the drive-mode replacement for this exact
    signal (design §7 Phase 2 migration table), and polling both endpoints
    every turn would double the network calls for nothing; `business_
    return.py`'s own offer is gated off the same way, so the two hooks
    never race to show two different step-7 return offers.

    **Rule 3 target.** Drop the `is_drive` guard below and a drive-mode
    session would poll (and could offer) through BOTH this hook and `plan_
    status_poll.py` at once -- `test_business_ready_poll.
    test_rule3_dormant_under_drive_mode` proves this."""
    if planner_mode_state.is_drive(session_id):
        return None
    state = step_state.read_state(session_id)
    if "website" not in state["ticked"]:
        return None
    if "business_review" in state["ticked"]:
        return None
    workspace = state["workspace"]
    if workspace is None:
        return None
    if read_state(session_id)["ready"]:
        return None  # already known ready -- nothing left to learn this session
    return workspace["id"]


def _throttled(session_id: str) -> bool:
    last = read_state(session_id)["last_poll_at"]
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


def poll(session_id: str) -> None:
    """The one entry point: fail-silent, never raises, never blocks."""
    try:
        workspace_id = _should_poll(session_id)
        if workspace_id is None:
            return
        if _throttled(session_id):
            return
        # Record the attempt BEFORE the network call, so a slow/failing
        # server still throttles the NEXT try -- never hammers a down
        # endpoint every single turn.
        _write_state(session_id, {"last_poll_at": time.monotonic()})

        cursor = tc.read_cursor(session_id)
        upload_key = cursor.get("upload_key")
        if not isinstance(upload_key, str) or not upload_key:
            return

        data = _fetch(workspace_id, upload_key)
        if data is None or data.get("ready") is not True:
            return
        say = data.get("say")
        opts = data.get("opts")
        if not isinstance(say, str) or not isinstance(opts, list):
            return
        _write_state(session_id, {"ready": True, "say": say, "opts": opts})
    except Exception:
        pass


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    session_id = payload.get("session_id")
    if isinstance(session_id, str) and session_id:
        poll(session_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
