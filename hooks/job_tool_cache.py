#!/usr/bin/env python3
"""Per-job tool allow-list cache (RMP-201 drive-mode follow-up #2, "early
research gets blocked").

**The problem this fixes.** `step_gate.py`'s cumulative ordering denies a
tool that belongs to a LATER step even when a background job (same
`session_id`, design F3: "Hooks fire inside subagents with the same
session_id") needs it right now -- e.g. `start_niche_pick` (step 8) fired
by an N8a job while the customer is still on step 3.

**The narrow fix.** `payload.get("agent_id")` is the ONE thing that
actually differs between the subagent's own tool calls and the foreground's
(`job_budget_gate.py`/`spend_gate.py` already read this same field for
their own subagent checks) -- present only while a call happens inside a
Task subagent. When `get_job` succeeds inside a job's own subagent, this
module caches `{node, allowed_tools, expires_at}` keyed by
`(session_id, agent_id)`, from the server's own `job_tools` field
(`get_job_service.get_job`) -- server-decided, plugin-enforced, same split
every other drive-mode gate in this design uses. `report_job` (or the
lease's own `max_minutes` expiring) clears it.

OWN FILE, same "no shared state with a sibling module's file" reasoning
`plan_cache.py`/`job_budget_gate.py` already give -- keyed by BOTH
`session_id` and `agent_id` (never just one) so two jobs launched in the
same session cannot clobber each other's cache.

FAIL-SAFE: a missing/corrupt/expired file reads as "no active job for this
agent" -- never a crash, never a wider allow than the caller asked for.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
from datetime import datetime, timezone
from typing import Any

import state_file_io


def _safe(agent_id: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", "_", agent_id)


def _path(session_id: str, agent_id: str) -> pathlib.Path:
    tmp_dir = os.environ.get("TMPDIR") or "/tmp"
    return pathlib.Path(tmp_dir) / f"rm-plugin-v2-job-tools-{session_id}-{_safe(agent_id)}.json"


def write_active(
    session_id: str, agent_id: str, *, node: str, allowed_tools: list[str], expires_at: str,
) -> None:
    """Never raises. `expires_at` is an ISO-8601 UTC string (the same shape
    `store_claims`' own lease uses) -- a job that runs past it is treated as
    inactive even if `report_job` is never reached (a crashed session)."""
    try:
        state_file_io.write_atomic(
            _path(session_id, agent_id),
            json.dumps({"node": node, "allowed_tools": allowed_tools, "expires_at": expires_at}),
        )
    except Exception:
        pass


def clear_active(session_id: str, agent_id: str) -> None:
    """Never raises. Safe to call even when nothing was ever cached."""
    try:
        _path(session_id, agent_id).unlink(missing_ok=True)
    except Exception:
        pass


def read_active(session_id: str, agent_id: str) -> dict[str, Any] | None:
    """`None` for "nothing cached", "corrupt", or "expired" -- all three are
    the same safe answer to the gate's only question, "is there a live job
    for this exact agent_id right now". Never raises.

    **Rule 3 target.** Drop the expiry check below and a job whose session
    crashed mid-run (never called `report_job`) would keep its early tool
    access forever, past its own lease -- `test_job_tool_cache.
    test_rule3_an_expired_entry_is_never_returned` proves this."""
    try:
        data = json.loads(_path(session_id, agent_id).read_text(encoding="utf-8"))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    node, allowed_tools, expires_at = data.get("node"), data.get("allowed_tools"), data.get("expires_at")
    if not isinstance(node, str) or not isinstance(allowed_tools, list) or not isinstance(expires_at, str):
        return None
    try:
        expiry = datetime.fromisoformat(expires_at)
    except Exception:
        return None
    if expiry.tzinfo is None:
        expiry = expiry.replace(tzinfo=timezone.utc)
    if expiry <= datetime.now(timezone.utc):
        return None
    return {"node": node, "allowed_tools": [t for t in allowed_tools if isinstance(t, str)]}
