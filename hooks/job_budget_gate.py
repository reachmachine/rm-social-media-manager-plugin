#!/usr/bin/env python3
"""PreToolUse job-budget hook (RMP-201 P4, design doc §6: "generalises
RMP-197's `niche_search_budget`. It counts tool calls and searches while a
job lease is active and denies past the cap").

A RUNAWAY SAFETY STOP ONLY, not a precise per-node budget -- the founder
said no real spend cap (`prompts/COMMS.md`), so the default below is
GENEROUS on purpose: it only ever fires once a background `rm-job` subagent
is far past what any real job spec (`job_specs.py`'s own `max_tool_calls`,
the biggest step 10 job is 320 calls, P1855) should ever need, the same "something is clearly wrong,
stop it" role `customer_upload_gate.py`'s sleep guard plays for the main
thread.

SCOPED TO A SUBAGENT, cheap for everyone else. `payload.get("agent_id")` is
only present when a tool call happens INSIDE a Task subagent (`spend_gate.py`
already reads this same field for its own subagent check) -- this hook
returns immediately, before any file I/O, the moment that key is absent, so
an ordinary main-thread tool call (the overwhelming majority) costs one
dict lookup. Counted PER `(session_id, agent_id)` pair -- design's own "if
the hook payload carries a subagent id, count per job" (each background
launch gets its own `agent_id`, so this is naturally per-job without
needing to cross-reference a `job_id`/lease at all).

NEVER DENIES `get_job`/`report_job` THEMSELVES -- a job that is over budget
must still be able to call `report_job` to close out cleanly (design's own
"Save what you have and report" instruction only makes sense if that call
itself is never the thing being denied); otherwise the lease just expires
and the customer waits for nothing.

FAILS OPEN, same direction as `customer_upload_gate.py`: a crash here must
never brick a subagent's own tool call."""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys

import deny_lines
import state_file_io

_DEFAULT_MAX_TOOL_CALLS = 340   # P1855: above the largest step 10 job (recheck, 320 calls)
_NEVER_DENIED = re.compile(r"__(get_job|report_job)$")
_DENY_REASON = "job_limit"


def _max_tool_calls() -> int:
    try:
        return int(os.environ.get("RM_JOB_MAX_TOOL_CALLS", _DEFAULT_MAX_TOOL_CALLS))
    except (TypeError, ValueError):
        return _DEFAULT_MAX_TOOL_CALLS


def _counter_path(session_id: str, agent_id: str) -> pathlib.Path:
    tmp_dir = os.environ.get("TMPDIR") or "/tmp"
    safe_agent = re.sub(r"[^A-Za-z0-9_-]", "_", agent_id)
    return pathlib.Path(tmp_dir) / f"rm-plugin-v2-job-budget-{session_id}-{safe_agent}.json"


def _increment(session_id: str, agent_id: str) -> int:
    path = _counter_path(session_id, agent_id)
    with state_file_io.locked(path):  # RMP-76: two parallel calls must count as two
        try:
            count = json.loads(path.read_text(encoding="utf-8")).get("count", 0)
        except Exception:
            count = 0
        count += 1
        try:
            state_file_io.write_atomic(path, json.dumps({"count": count}))
        except Exception:
            pass
    return count


def _deny(reason_id: str, **fill: object) -> dict:
    return deny_lines.deny_id(reason_id, **fill)


def decide(payload: dict) -> dict | None:
    """None = allow. Never raises -- see module docstring."""
    agent_id = payload.get("agent_id")
    if not isinstance(agent_id, str) or not agent_id:
        return None  # the overwhelming common case: not inside a subagent

    tool_name = payload.get("tool_name")
    if isinstance(tool_name, str) and _NEVER_DENIED.search(tool_name):
        return None  # a job must always be able to close itself out

    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return None

    count = _increment(session_id, agent_id)
    if count > _max_tool_calls():
        return deny_lines.resolve(session_id, _deny(_DENY_REASON))
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
        return 0
    if result is not None:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
