#!/usr/bin/env python3
"""PreToolUse gate on the built-in `Read`/`Bash`/`Glob` tools (RMP-194 part 4
+ RMP-201 P0). Two independent checks, both fail-open, sharing this one
dispatcher because they cover the SAME matcher (`hooks.json`'s own
`Read|Bash|Glob` entry) -- one more entry there would be a second wiring
change for no reason, and both belong under "things a built-in tool must not
do while Reach Machine work is in flight":

1. **The upload-path guard** (RMP-194 part 4, design doc "the gate that
   denies Read/Bash/Glob on the upload path while an upload is open") --
   unchanged, see `_touches_active_path`.
2. **The sleep guard** (RMP-201 P0, founder's live report 2026-09-27): the
   model looped `Bash sleep`/`timeout N` while `get_business_review` said
   `ready: false`, burning about $1 with nothing to show for it. There is
   NEVER a reason for this plugin's own model to sleep or wait on a shell
   timer -- every real wait already has its own poll/reminder mechanism
   (`business_ready_poll.py`, the background reader, `wait_for_website_
   read`). Denied only while a Reach Machine workspace is open (`step_
   state.read_state(session_id)["workspace"]`) -- a totally unrelated Bash
   sleep in a session that never touched this plugin must never be touched.

FAILS OPEN -- the opposite of `connections_gate.py`, and deliberately so:
these are BUILT-IN tools, not this plugin's own MCP tools, so this hook now
runs on every `Read`/`Bash`/`Glob` call in EVERY session, whether or not this
plugin's other checks have even started. A crash here (a corrupt state file,
a missing session_id) must never brick an unrelated tool call -- the correct
degraded behaviour is "allow", not "deny". Early-exits the moment neither
check applies, so the common case (no upload open, no sleep, or no workspace
yet) costs at most one or two cheap state reads.
"""
from __future__ import annotations

import json
import re
import sys

import customer_upload_state as cus
import deny_lines
import step_state
from customer_upload_path_guard import normalize_for_match
from payload_util import tool_args

# RMP-291 P2320: reason ids; the owner-language texts come from the server (`deny_lines`).
_DENY_REASON = "file_sent_for_you"
_SLEEP_DENY_REASON = "no_wait"

# `sleep <n>` or `timeout <n> ...`, at the start of the command or right
# after a shell separator (`;`, `&`, `|`) -- so `cmd1 && sleep 5` is caught
# too, not only a bare leading `sleep`. Rule 3: this regex, deleted -> RED
# (`test_sleep_guard.py`'s own break-and-restore).
_SLEEP_RE = re.compile(r"(?:^|[;&|]\s*)(sleep\s|timeout\s+\d)")


def _deny(reason_id: str, session_id: str = "") -> dict:
    return deny_lines.deny(deny_lines.reason(session_id, reason_id))   # RMP-291 P2320: the text is the server's


def _touches_active_path(tool_name: str, tool_input: dict, active: str) -> bool:
    needle = normalize_for_match(active)
    if tool_name == "Read":
        value = tool_input.get("file_path")
        return isinstance(value, str) and needle in normalize_for_match(value)
    if tool_name == "Glob":
        value = tool_input.get("path")
        return isinstance(value, str) and needle in normalize_for_match(value)
    if tool_name == "Bash":
        value = tool_input.get("command")
        return isinstance(value, str) and needle in normalize_for_match(value)
    return bool(_SLEEP_RE.search(command))


def _is_sleep_command(command: str) -> bool:
    return bool(_SLEEP_RE.search(command))


def _workspace_is_open(session_id: str) -> bool:
    try:
        return step_state.read_state(session_id).get("workspace") is not None
    except Exception:
        return False


def decide(payload: dict) -> dict | None:
    """None = allow. Never raises -- see module docstring."""
    tool_name = payload.get("tool_name")
    if tool_name not in ("Read", "Bash", "Glob"):
        return None
    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return None

    tool_input = tool_args(payload)

    if tool_name == "Bash":
        command = tool_input.get("command")
        if (
            isinstance(command, str)
            and _is_sleep_command(command)
            and _workspace_is_open(session_id)
        ):
            return _deny(_SLEEP_DENY_REASON, session_id)

    active = cus.active_path(session_id)
    if not active:
        return None
    if _touches_active_path(tool_name, tool_input, active):
        return _deny(_DENY_REASON, session_id)
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    try:
        result = decide(payload)
    except Exception:
        # Fails OPEN (module docstring) -- an unanticipated crash here must
        # never brick an ordinary Read/Bash/Glob call.
        return 0
    if result is not None:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
