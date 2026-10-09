#!/usr/bin/env python3
"""PostToolUse: records/clears `job_tool_cache` from `get_job`/`report_job`'s
own results (RMP-201 drive-mode follow-up #2, "early research gets
blocked"). See `job_tool_cache.py`'s own docstring for the mechanism.

SCOPED TO A SUBAGENT, same as `job_budget_gate.py`: `payload.get("agent_id")`
is absent for every ordinary foreground call, so this returns immediately,
before any file I/O, for the overwhelming majority of tool calls.

`get_job`'s `available: false` never caches anything (nothing this agent_id
may now do early) -- only a real `{available: true, node, job_tools}` does.
A missing/malformed `budget.max_minutes` falls back to a short, safe default
rather than caching an unbounded early-access window.

**ALSO grants `plan_cache.early_allow` (RMP-201/RMP-76 live bug,
2026-09-28).** The live bug: `job_tool_cache`'s own precise, `agent_id`-
scoped grant did not save `start_niche_pick` from a cumulative-ordering
deny -- `step_gate.job_ordering_bypass` never engaged for that exact
subagent call, for a reason this session could not pin down for certain
(the plugin's own `agent_id` threading through every hook call was never
end-to-end verified against a real subagent before this bug). Rather than
chase that one call site, EVERY successful `get_job` also grants its
`job_tools` into the session-wide `plan_cache.early_allow` set (`step_gate_
plan.early_allow`'s own docstring) -- a second, coarser net for the exact
same signal (the server just said this tool is fine to call now), agent_id-
independent so it cannot be defeated by whatever broke the first one.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from typing import Any

import connection_state as cs
import job_tool_cache
import plan_cache

_DEFAULT_LEASE_MINUTES = 20


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _handle_get_job(session_id: str, agent_id: str, payload: dict) -> None:
    data = _parse_json_response(payload.get("tool_response"))
    if data is None or data.get("available") is not True:
        return
    node = data.get("node")
    job_tools = data.get("job_tools")
    if not isinstance(node, str) or not isinstance(job_tools, list):
        return
    allowed_tools = [t for t in job_tools if isinstance(t, str)]
    budget = data.get("budget") if isinstance(data.get("budget"), dict) else {}
    max_minutes = budget.get("max_minutes")
    minutes = max_minutes if isinstance(max_minutes, int) and max_minutes > 0 else _DEFAULT_LEASE_MINUTES
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()
    job_tool_cache.write_active(
        session_id, agent_id, node=node, allowed_tools=allowed_tools, expires_at=expires_at,
    )
    if allowed_tools:
        plan_cache.grant_early_allow(session_id, allowed_tools)


def handle(session_id: str, agent_id: str, tool_name: Any, payload: dict) -> None:
    """Never raises."""
    if not isinstance(tool_name, str):
        return
    if tool_name.endswith("__get_job"):
        _handle_get_job(session_id, agent_id, payload)
    elif tool_name.endswith("__report_job"):
        job_tool_cache.clear_active(session_id, agent_id)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    session_id = payload.get("session_id")
    agent_id = payload.get("agent_id")
    if not isinstance(session_id, str) or not session_id:
        return 0
    if not isinstance(agent_id, str) or not agent_id:
        return 0  # the overwhelming common case: not inside a subagent
    try:
        handle(session_id, agent_id, payload.get("tool_name"), payload)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
