#!/usr/bin/env python3
"""Stop hook: do not let a chat go quiet while the step 10 research is still being built (RMP-280, P2169).

Live run (release 5): sessions ended their turn with "Pinterest and YouTube need about 3 more minutes. Say check again"
and nothing woke them. The SERVER decides (`GET /api/v1/plugin/wait-until-ready` holds the answer up to its own
deadline and says `running`/`ready`, the line to use, and the cap). This hook only carries it out: when the server says the
research is running and not ready, it blocks the stop with the server's own line, so the model carries on (it calls
next_actions again). No business logic lives here.

GATE (local, cheap): a workspace is open, step 9 ("dream_customer") is ticked, step 10 ("where_to_find") is not. Any
other session makes no call at all.

FAIL OPEN, ALWAYS: no key, no workspace, a slow or down server, a bad answer, any error -> print nothing (the stop goes
through). It also stops blocking after the SERVER's `max_blocks` in a row (default 12 here if the server sent none), so a
stuck research can never trap a session. A "ready" or "not running" answer resets the count; so does a quiet gap of
`KEEP_WAITING_RESET_S` (a new customer turn long after the last block).
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

import plugin_api
import state_file_io
import step_state
import transcript_cursor as tc

_PATH = "/api/v1/plugin/wait-until-ready"
_ENV_OVERRIDE = "RM_WAIT_READY_URL_OVERRIDE"
_DEFAULT_WAIT_S = 80.0
_DEFAULT_MAX_BLOCKS = 12
_DEFAULT_RESET_S = 1800.0
_HTTP_SLACK_S = 10.0
_MAX_SAY_CHARS = 600
_PLANNER_KIND = "planner"


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, default))
    except (TypeError, ValueError):
        return default


def _state_path(session_id: str) -> pathlib.Path:
    return pathlib.Path(os.environ.get("TMPDIR") or "/tmp") / f"rm-plugin-v2-keep-waiting-{session_id}.json"


def _read_count(session_id: str) -> int:
    try:
        data = json.loads(_state_path(session_id).read_text(encoding="utf-8"))
        blocks, at = data["blocks"], data["last_block_at"]
        if not isinstance(blocks, int) or isinstance(blocks, bool) or not isinstance(at, (int, float)):
            return 0
        return blocks if time.time() - at < _env_float("KEEP_WAITING_RESET_S", _DEFAULT_RESET_S) else 0
    except Exception:
        return 0


def _write_count(session_id: str, blocks: int) -> None:
    try:
        state_file_io.write_atomic(_state_path(session_id), json.dumps({"blocks": blocks, "last_block_at": time.time()}))
    except Exception:
        pass


def _gate(session_id: str) -> tuple[str, str | None] | None:
    """`(workspace id, kind)` for a session that can be waiting, else `None`. Step 10 (step 9 ticked, step 10 not) is
    kind `None`, the call it has always made. Steps 6-9 (step 4 ticked, step 9 not) are kind `"planner"` (RMP-281, P2262):
    the server then reads the planner's own running jobs. Anything earlier makes no call at all."""
    state = step_state.read_state(session_id)
    ticked = state["ticked"]
    if "where_to_find" in ticked:
        return None
    if "dream_customer" in ticked:
        kind = None
    elif "own_instagram_account" in ticked:
        kind = _PLANNER_KIND
    else:
        return None
    workspace = state["workspace"]
    return (workspace["id"], kind) if workspace else None


def _fetch(workspace_id: str, upload_key: str, wait_s: float, kind: str | None = None) -> dict[str, Any] | None:
    params: dict[str, Any] = {"workspace_id": workspace_id, "max_wait_s": wait_s}
    if kind:
        params["kind"] = kind
    query = urllib.parse.urlencode(params)
    request = urllib.request.Request(
        f"{plugin_api.api_url(_PATH, _ENV_OVERRIDE)}?{query}", method="GET",
        headers={"X-RM-Upload-Key": upload_key, "User-Agent": plugin_api.user_agent()},
    )
    try:
        with urllib.request.urlopen(request, timeout=wait_s + _HTTP_SLACK_S) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError, OSError):
        return None
    return data if isinstance(data, dict) else None


def decide(session_id: str) -> str | None:
    """The block reason to print, or `None` to let the stop through. Never raises."""
    try:
        gate = _gate(session_id)
        if gate is None:
            return None
        workspace_id, kind = gate
        upload_key = tc.read_cursor(session_id).get("upload_key")
        if not isinstance(upload_key, str) or not upload_key:
            return None
        answer = _fetch(workspace_id, upload_key, _env_float("KEEP_WAITING_WAIT_S", _DEFAULT_WAIT_S), kind)
        if answer is None:
            return None
        if answer.get("running") is not True or answer.get("ready") is not False:
            _write_count(session_id, 0)
            return None
        say = answer.get("say")
        if not isinstance(say, str) or not say.strip():
            return None
        cap = answer.get("max_blocks")
        cap = cap if isinstance(cap, int) and not isinstance(cap, bool) and cap > 0 else _DEFAULT_MAX_BLOCKS
        blocks = _read_count(session_id)
        if blocks >= cap:
            return None
        _write_count(session_id, blocks + 1)
        extra = answer.get("keep_going")
        reason = say if not isinstance(extra, str) else f"{say} {extra}"
        return reason[:_MAX_SAY_CHARS]
    except Exception:
        return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    session_id = payload.get("session_id") if isinstance(payload, dict) else None
    if isinstance(session_id, str) and session_id:
        reason = decide(session_id)
        if reason:
            print(json.dumps({"decision": "block", "reason": reason}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
