#!/usr/bin/env python3
"""The plan cache file (RMP-201 P4, design doc §3 hooks: "writes the plan
cache file `rm-plugin-v2-plan-<session>.json`").

OWN FILE, same reasoning `business_ready_poll.py`'s own docstring gives:
several PostToolUse hooks can fire for the SAME event in parallel, so this
never shares a file with `connection_state.py` (`step_state.py`'s own
keys) -- a write here can never race a sibling module's write to a
DIFFERENT file. `planner_mode` (a much smaller, much less frequently
changed flag) lives in that shared file instead -- see
`planner_mode_state.py`'s own docstring for why the two are split.

SHAPE: `{"plan_version": int, "gate": {"v": int, "deny": {...}}, "running":
[...], "checklist": {...}|None, "dirty": bool, "early_allow": [...]}`.
`dirty` starts `True` for a session that has never cached anything yet
(design's own "first call has no cache -- always allowed" rule for the
repeat-call guard, `plan_repeat_guard.py`) -- the CALLER (`plan_recorder.py`)
always writes a fresh cache with `dirty: False` right after a real
`next_actions` call, so this default only ever matters before the very
first one.

**`early_allow` (RMP-201/RMP-76 live bug, 2026-09-28).** A set of tool
suffixes `step_gate.py`'s cumulative step order should allow RIGHT NOW even
though their own step is not current yet, because the SERVER itself just
proposed the action: `answer_question`'s `next_tool` (a "yes" to N6a2/N6f
while step 5 is still open), or `get_job`'s own `job_tools` (N8a's niche
research launched the moment its graph-level needs are met, well before the
"website"/step 6 checklist tick lands -- the live bug: `start_niche_pick`
was denied "Finish step 6 first." even though `get_job` had just said
`available: true` for that exact tool, moments earlier, in the SAME
subagent). UNLIKE `job_tool_cache.py` (scoped to one `(session_id,
agent_id)` job, precise but depends on a subagent's own `agent_id` reaching
every hook call), this is session-wide and agent_id-independent -- a
coarser, second safety net for the SAME class of bug, not a replacement.
Merged onto (never replaces) whatever is already granted, and PRESERVED
across `write_full` -- a routine
`next_actions` refresh must never silently take back a grant nothing has
consumed yet. Cleared on a workspace switch (`step_recorder_workspace.
handle_set_active_workspace`) -- a grant earned in one workspace must never
leak into another.

FAIL-SAFE: a missing or corrupt file reads as "never cached" (`plan_
version: 0`, empty gate, `dirty: True`) -- this is what makes design §4 G3
("ordering fails open when the cache is missing") a real code path: `step_
gate_plan.gate_for` checks `is_drive` and `read_state` independently, so
"drive mode, cache gone" reads as an EMPTY deny map (allow everything),
never a crash and never today's cumulative-allow fallback (that fallback is
for "mode is not drive" instead -- see `step_gate_plan.py`)."""
from __future__ import annotations

import json
import os
import pathlib
import time
from typing import Any

import state_file_io

_DEFAULT: dict[str, Any] = {
    "plan_version": 0,
    "gate": {"v": 0, "deny": {}},
    "running": [],
    "checklist": None,
    "dirty": True,
    "early_allow": [],
    "cached_at": 0.0,  # epoch seconds of the last write_full (RMP-218 P1994: a cache has an age)
    "retry_ats": [],  # ISO times from the server's `stuck[].retry_at` (a back-off waiting to end)
    "next_offer": "",  # the step 9 offer line the SERVER wrote in the owner's language (RMP-281 P2268); "" = none
    "offers": {},  # server-written customer lines by offer id (RMP-281 P2272, see offer_lines.py)
    "deny_reasons": {},  # server-written deny reasons by reason id (RMP-291 P2320, see deny_lines.py)
}


def state_path(session_id: str) -> pathlib.Path:
    tmp_dir = os.environ.get("TMPDIR") or "/tmp"
    return pathlib.Path(tmp_dir) / f"rm-plugin-v2-plan-{session_id}.json"


def read_state(session_id: str) -> dict[str, Any]:
    """Never raises. A missing/corrupt file, or one with the wrong shape
    for any single field, reads as that field's own safe default -- never
    a half-trusted mix of old and new."""
    result = dict(_DEFAULT)
    result["gate"] = dict(_DEFAULT["gate"])
    result["offers"] = {}
    result["deny_reasons"] = {}
    try:
        data = json.loads(state_path(session_id).read_text(encoding="utf-8"))
    except Exception:
        return result
    if not isinstance(data, dict):
        return result

    version = data.get("plan_version")
    if isinstance(version, int) and not isinstance(version, bool):
        result["plan_version"] = version

    gate = data.get("gate")
    if isinstance(gate, dict) and isinstance(gate.get("deny"), dict):
        gate_v = gate.get("v")
        result["gate"] = {
            "v": gate_v if isinstance(gate_v, int) and not isinstance(gate_v, bool) else 0,
            "deny": {k: v for k, v in gate["deny"].items() if isinstance(k, str) and isinstance(v, str)},
        }

    running = data.get("running")
    if isinstance(running, list):
        result["running"] = running

    checklist = data.get("checklist")
    if isinstance(checklist, dict):
        result["checklist"] = checklist

    if isinstance(data.get("dirty"), bool):
        result["dirty"] = data["dirty"]

    early_allow = data.get("early_allow")
    if isinstance(early_allow, list):
        result["early_allow"] = [t for t in early_allow if isinstance(t, str)]

    cached_at = data.get("cached_at")
    if isinstance(cached_at, (int, float)) and not isinstance(cached_at, bool):
        result["cached_at"] = float(cached_at)

    retry_ats = data.get("retry_ats")
    if isinstance(retry_ats, list):
        result["retry_ats"] = [t for t in retry_ats if isinstance(t, str)]

    next_offer = data.get("next_offer")
    if isinstance(next_offer, str):
        result["next_offer"] = next_offer

    offers = data.get("offers")
    if isinstance(offers, dict):
        result["offers"] = {k: v for k, v in offers.items() if isinstance(k, str) and isinstance(v, dict)}

    deny_reasons = data.get("deny_reasons")
    if isinstance(deny_reasons, dict):
        result["deny_reasons"] = {k: v for k, v in deny_reasons.items() if isinstance(k, str) and isinstance(v, str)}

    return result


def _modify(session_id: str, mutate: Any) -> Any:
    """RMP-76: read, change, write as ONE locked, atomic step. Two hooks (a
    `next_actions` refresh and a `pop_return`, say) used to each read the whole
    file and write it back, so the later writer erased the earlier one's
    change (a queued "quick look?" offer, an early-allow grant). `mutate`
    changes the state dict in place; its return value comes back. Never raises."""
    return state_file_io.modify_json(state_path(session_id), lambda: read_state(session_id), mutate)


def write_full(
    session_id: str, *, plan_version: int, gate: dict[str, Any], running: list, checklist: dict | None,
    retry_ats: list[str] | None = None, next_offer: str = "",
) -> None:
    """Replaces the whole cache after a real `next_actions`/`open_workspace`/
    `get_resume_checklist` call -- always clears `dirty` (design: this is
    the one point that means "the plugin has now seen the latest plan").
    `early_allow` is preserved from whatever was already cached -- see the
    module docstring."""
    def _replace(current: dict[str, Any]) -> None:
        current.update({
            "plan_version": plan_version, "gate": gate, "running": running,
            "checklist": checklist, "dirty": False,
            "cached_at": time.time(), "retry_ats": list(retry_ats or []), "next_offer": next_offer,
        })  # early_allow stays exactly as cached

    _modify(session_id, _replace)


def merge_offers(session_id: str, offers: dict[str, Any]) -> None:
    """Server-written customer lines (`offer_lines.py`), merged by id. A `None` value removes that offer."""
    def _merge(current: dict[str, Any]) -> None:
        merged = dict(current["offers"])
        for key, value in offers.items():
            if value is None:
                merged.pop(key, None)
            elif isinstance(key, str) and isinstance(value, dict):
                merged[key] = value
        current["offers"] = merged

    _modify(session_id, _merge)


def set_deny_reasons(session_id: str, deny_reasons: dict[str, str]) -> None:
    """The server's deny reasons (`deny_lines.py`), merged by id so a later partial map never drops an earlier line."""
    _modify(session_id, lambda current: current.update(deny_reasons={**current["deny_reasons"], **deny_reasons}))


def mark_dirty(session_id: str) -> None:
    """Something may have changed server-side (a save tool call, an
    `answer_question`, a `report_job`) since the last real `next_actions`
    read -- merges onto whatever is already cached, never clobbers the rest
    of the state, same convention as `business_ready_poll._write_state`."""
    _modify(session_id, lambda current: current.update(dirty=True))


def grant_early_allow(session_id: str, tool_suffixes: list[str]) -> None:
    """Adds `tool_suffixes` to the early-allow set (module docstring).
    Merges onto whatever is already granted -- never clobbers a suffix
    granted for a DIFFERENT reason moments earlier (e.g. N6a2's `next_tool`
    and a job's own `job_tools` in the same turn)."""
    def _grant(current: dict[str, Any]) -> None:
        current["early_allow"] = sorted(set(current["early_allow"]) | {t for t in tool_suffixes if isinstance(t, str)})

    _modify(session_id, _grant)


def clear_early_allow(session_id: str) -> None:
    """A workspace switch's own reset (module docstring) -- never raises,
    safe even when nothing was ever granted."""
    _modify(session_id, lambda current: current.update(early_allow=[]))
