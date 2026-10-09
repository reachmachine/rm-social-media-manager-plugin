#!/usr/bin/env python3
"""Drive-mode additions to `step_gate.py` (RMP-201 P4, design doc §4 G2/G3):
the server's own gate map, and the repeat-`next_actions`-call guard.

Both are ADDITIVE and DORMANT outside drive mode -- `step_gate.py` calls
into this module only from behind its own `planner_mode_state.is_drive`
check, so neither function needs to repeat that guard itself; both are still
written to also do nothing useful if somehow called outside drive (an empty
gate map denies nothing; the repeat guard only OMITS a call that would
otherwise be denied by something else, an allow is always safe).

**G2/G3 (`gate_deny`).** Denies a tool suffix the server's own `gate.deny`
map (cached from the last `next_actions`/`open_workspace`/`get_resume_
checklist` response, `plan_cache.py`) currently flags -- design's own
"denied only when its declared inputs are not ready", additive on top of
whatever `step_gate.py`'s existing cumulative ordering already decided (it
can only turn an allow into a deny, never the reverse). A missing/corrupt
plan cache reads as an EMPTY deny map (`plan_cache.read_state`'s own
fail-safe default) -- this IS the documented fail-open behaviour, not a
special case this module has to build.

**Arg-conditional entries** (`"tool_suffix:arg_prefix"`, e.g.
`"update_creator_brief:revenue_"`) are matched against the ONE shape that
exists on `main` today: `update_creator_brief`'s `fields` dict, denied only
when at least one key in it starts with the prefix. A future arg-
conditional entry for a different tool needs a new branch here -- this is
data-driven for the suffix, not for the prefix-matching rule itself.

**The repeat-call guard (`repeat_call_deny`).** Design §3: "denies
`next_actions` when the cached `plan_version` is unchanged and no answer,
save, or job event has happened since." `plan_cache.py`'s own `dirty` flag
already tracks exactly that (`plan_events.py` sets it on every OTHER
reachmachine/apify/playwright tool call; `plan_recorder.py` clears it on
every real `next_actions`/`open_workspace`/`get_resume_checklist` read) --
a session with no cache yet (`dirty` defaults `True`) is always allowed
(design's own "first call has no cache -- always allowed").

**The job ordering bypass (`job_ordering_bypass`, drive-mode follow-up #2,
"early research gets blocked").** `step_gate.py`'s cumulative ordering
denies a tool that belongs to a LATER step even when a background job
(same `session_id` as the foreground, design F3) needs it right now, e.g.
`start_niche_pick` (only allowed from step 8) fired by an N8a job while the
customer is still on step 3. `job_tool_cache.read_active` answers "does
THIS EXACT subagent (`agent_id`) currently hold a live job, and is `suffix`
one of the tools its OWN job spec named" -- only an exact match on BOTH
narrows the widening to that one job's own declared tools, never the whole
session. A foreground call carries no `agent_id` at all, so it is refused
this bypass structurally, not by a mode check -- see `job_allows` below.

**`early_allow` (RMP-201/RMP-76 live bug, 2026-09-28) -- a second, coarser
safety net for the SAME class of bug.** The live evidence: an N8a subagent
called `get_job` (`available: true`, `job_tools: ["start_niche_pick", ...]`),
then called `start_niche_pick` in the very next turn and was STILL denied
"Finish step 6 first." -- `job_ordering_bypass` above never engaged (its
own precise, `agent_id`-scoped cache either never got written or never got
read back for that exact subagent). `plan_cache.early_allow` is written by
`job_tool_cache_record.py` (any successful `get_job`) and by a new recorder
for `answer_question`'s `next_tool` -- session-wide, no `agent_id` needed --
so a genuine "the server just told us to do this" signal is honoured even
when the precise, subagent-scoped mechanism above does not fire for
whatever reason. Checked from `step_gate.py` ALONGSIDE `job_ordering_
bypass`, never instead of it."""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from typing import Any

import deny_lines
import job_tool_cache
import plan_cache
import planner_mode_state

_REPEAT_DENY_REASON = "repeat_call"
_STALE_DENY_REASON = "plan_stale"


_DEFAULT_MAX_AGE_S = 60.0


def _max_age_s() -> float:
    """How long a cache that lists waiting work may hide the server. 60 s: one `next_actions` call is
    one fast server read plus a short reply, so asking once a minute is cheap, while a customer
    who says "check again" never waits longer than a minute for a real answer. Set
    `RM_PLAN_CACHE_MAX_AGE_S` to change it."""
    try:
        value = float(os.environ.get("RM_PLAN_CACHE_MAX_AGE_S", _DEFAULT_MAX_AGE_S))
    except ValueError:
        return _DEFAULT_MAX_AGE_S
    return value if value >= 0 else _DEFAULT_MAX_AGE_S


def _retry_is_due(retry_ats: list[str]) -> bool:
    now = datetime.now(timezone.utc)
    for text in retry_ats:
        try:
            at = datetime.fromisoformat(text)
        except ValueError:
            continue
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
        if at <= now:
            return True
    return False


def _cache_is_stale(cached: dict[str, Any]) -> bool:
    """RMP-218 P1994. Time passing is a reason to ask the server again, even though nothing marked
    the cache dirty. (1) a back-off the server said would end has ended; (2) work is running or
    waiting and the cache is older than the max age. (A background task ending is NOT a hook event
    -- `hooks.json` has no task-finished hook -- so rules 1 and 2 are what cover it.)"""
    if _retry_is_due(cached["retry_ats"]):
        return True
    waiting = bool(cached["running"]) or bool(cached["retry_ats"])
    return waiting and time.time() - cached["cached_at"] > _max_age_s()


def _deny(reason_id: str, **fill: object) -> dict:
    return deny_lines.deny_id(reason_id, **fill)


def _arg_prefix_matches(suffix: str, tool_input: dict[str, Any], prefix: str) -> bool:
    if suffix != "update_creator_brief":
        return False
    fields = tool_input.get("fields")
    if not isinstance(fields, dict):
        return False
    return any(isinstance(key, str) and key.startswith(prefix) for key in fields)


def gate_deny(session_id: str, suffix: str, tool_input: dict[str, Any]) -> dict | None:
    """`None` = allow. See module docstring.

    **Rule 3 target.** Skip the `":" in key` branch below (only ever check
    exact-suffix entries) and a call that should be blocked by an
    arg-conditional entry (`update_creator_brief:revenue_`) would slip
    through -- `test_step_gate_plan.
    test_rule3_arg_conditional_gate_entries_are_enforced` proves this."""
    cached = plan_cache.read_state(session_id)
    deny_map = cached["gate"]["deny"]
    # RMP-201: a dirty cache means a save happened since the map was written,
    # so the reason may be out of date (the save may be the very thing that
    # unblocked this tool). Say "refresh first" instead of a stale reason.
    def shown(say: str) -> dict:   # `say` is the SERVER's gate line (already in the owner's language)
        return _deny(_STALE_DENY_REASON) if cached["dirty"] else deny_lines.deny(say)

    if suffix in deny_map:
        return shown(deny_map[suffix])
    for key, say in deny_map.items():
        if ":" not in key:
            continue
        entry_suffix, prefix = key.split(":", 1)
        if entry_suffix == suffix and _arg_prefix_matches(suffix, tool_input, prefix):
            return shown(say)
    return None


def repeat_call_deny(session_id: str) -> dict | None:
    """`None` = allow.

    **Rule 3 target.** Drop the `dirty` check below (deny whenever a cache
    merely exists) and the model would be denied `next_actions` on its very
    FIRST real check-in after `open_workspace` already embedded one --
    `test_step_gate_plan.test_rule3_a_dirty_cache_is_never_denied` proves
    this."""
    cached = plan_cache.read_state(session_id)
    if cached["dirty"] or _cache_is_stale(cached):
        return None
    return _deny(_REPEAT_DENY_REASON)


def job_ordering_bypass(payload: dict[str, Any], session_id: str, suffix: str) -> bool:
    """True when `step_gate.py`'s cumulative ordering deny should be SKIPPED
    for this call -- see the module docstring for the mechanism. Called only
    from the one cumulative-ordering check site in `step_gate.py`; every
    other gate (G1 integrity, the pin, spend) still runs regardless of this
    result.

    **Rule 3 target (drive mode off -> unchanged).** Drop the `is_drive`
    check below and a job's early tool access would widen even with the
    planner off -- `test_step_gate_plan.
    test_rule3_job_ordering_bypass_is_dormant_outside_drive_mode` proves
    this."""
    if not planner_mode_state.is_drive(session_id):
        return False
    agent_id = payload.get("agent_id")
    if not isinstance(agent_id, str) or not agent_id:
        return False  # a foreground call never carries one -- see docstring
    active = job_tool_cache.read_active(session_id, agent_id)
    if active is None:
        return False
    return suffix in active["allowed_tools"]


def early_allow(session_id: str, suffix: str) -> bool:
    """True when `suffix` is in the session's `plan_cache.early_allow` set
    (module docstring) -- `step_gate.py`'s cumulative-ordering check treats
    this exactly like `job_ordering_bypass`: it can only turn a deny into an
    allow for THIS one call, never touch the checklist tick itself.

    **Rule 3 target (drive mode off -> unchanged, same convention as
    `job_ordering_bypass`).** Drop the `is_drive` check below and a grant
    would widen access even with the planner off -- `test_step_gate_plan.
    test_rule3_early_allow_is_dormant_outside_drive_mode` proves this."""
    if not planner_mode_state.is_drive(session_id):
        return False
    return suffix in plan_cache.read_state(session_id)["early_allow"]


def maybe_deny(session_id: str, suffix: str, tool_input: dict[str, Any]) -> dict | None:
    """The one call `step_gate.py` makes -- combines both checks above so
    the caller needs no `is_drive` check of its own. `None` (dormant)
    outside drive mode, and for every suffix the repeat-call guard does not
    apply to (only `next_actions` can ever trigger it; the ordering check
    already allows it unconditionally from step 2 on, design's own P4
    hand-off #1, so this guard is the only thing that can still deny it).

    **Rule 3 target.** Drop the `suffix == "next_actions"` check below
    (call `repeat_call_deny` for every suffix) and an ordinary tool call
    made right after a fresh cache write (`dirty` still `False`, correctly)
    would be wrongly denied with "Nothing new yet." --
    `test_step_gate_plan.test_rule3_repeat_guard_only_applies_to_next_actions`
    proves this."""
    if not planner_mode_state.is_drive(session_id):
        return None
    if suffix == "next_actions":
        deny = repeat_call_deny(session_id)
        if deny is not None:
            return deny
    return gate_deny(session_id, suffix, tool_input)
