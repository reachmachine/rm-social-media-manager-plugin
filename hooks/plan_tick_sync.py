#!/usr/bin/env python3
"""The tick-sync rule (RMP-201 P4, design doc §3: "For every checklist step
that is `done` in any `next_actions`/`open_workspace`/`get_resume_checklist`
result: the plugin calls `step_state.mark_ticked` locally; server truth
always wins, never the reverse.").

`open_workspace`/`get_resume_checklist` ALREADY do most of this today
(`checklist_recorder.handle_get_resume_checklist`'s own `state == "done"`
loop, wired through the pre-existing `record-connection-probe.sh` PostToolUse
dispatch) -- this module exists for the ONE case that isn't covered yet: a
bare `next_actions` call the model makes on its own (a background job just
finished, or the model wants to check in), whose response never goes near
that existing handler. Calling `step_state.mark_ticked` twice for the SAME
step from two different code paths is harmless (`mark_ticked` is itself
idempotent -- see its own docstring), so this never needs to coordinate with
the existing handler, only to cover its gap.

SCOPED TO `kind == "workspace"` STEPS, same restriction the existing handler
uses -- `connection_check`/`choose_workspace` have their own multi-part
"steps_passed AND logged AND checklist_read" state machine (`checklist_
recorder._maybe_finish_choose_workspace`) that a bare tick would bypass.
Nothing the planner drives is a session-kind step anyway (`graph_def.
TICKABLE_STEP_NODES` only maps workspace-kind steps 3-8), so this
restriction costs nothing in practice.
"""
from __future__ import annotations

from typing import Any

import step_state
import steps_manifest


def apply_tick_sync(session_id: str, checklist: dict[str, Any] | None) -> None:
    """Never raises. `checklist` is the `{"steps": [...], "resume_at": ...}`
    shape `checklist_view.build_checklist` (backend) sends -- see that
    module's own docstring for the exact per-step keys (`id`, `state`,
    `how`, `phase`, `note`).

    **Rule 3 target.** Replace the `state.get("ticked", [])` re-check below
    with an unconditional `step_state.mark_ticked` call and this stays
    behaviourally identical (idempotent), so the REAL Rule 3 target is the
    `kind == "workspace"` guard: delete it and a `next_actions` call
    returning `connection_check`/`choose_workspace` as `"done"` (which
    should never drive those two steps' own multi-part state machine) would
    tick them directly -- `test_plan_tick_sync.
    test_rule3_session_kind_steps_are_never_ticked_from_here` proves this."""
    if not isinstance(checklist, dict):
        return
    steps = checklist.get("steps")
    if not isinstance(steps, list):
        return

    try:
        by_id = {s["id"]: s for s in steps_manifest.load_steps(session_id)}
    except Exception:
        return

    for entry in steps:
        if not isinstance(entry, dict):
            continue
        step_id = entry.get("id")
        if not isinstance(step_id, str):
            continue
        if entry.get("state") != "done":
            continue
        if by_id.get(step_id, {}).get("kind") != "workspace":
            continue
        try:
            state = step_state.read_state(session_id)
            if step_id not in state["ticked"]:
                step_state.mark_ticked(session_id, step_id)
        except Exception:
            pass
