#!/usr/bin/env python3
"""Step order predicates: which earlier steps are done, which step is first unfinished
(P1641, RMP-50).

Spec: docs/plugin-v2/05-how-you-make-money.md "Hand-test fix: one order rule for both
halves". Split out of `step_gate.py` (already at 286 lines) and `step_state.py` (at
300, the limit) to keep both under the file-length limit.

GATE ORDERING uses "tick" not "pass" (RMP-9, step_gate.py docstring): `connection_check`
(step 1) is finished once in `state["steps_passed"]`; every step after it additionally
needs its tick (`state["ticked"]`). This makes "every step writes to three places"
(03-whose-account.md) a hook rule, not a sentence: `steps_passed` alone only proves the
Reach Machine write happened.

A `wait_for` STEP NEVER BLOCKS ORDERING (RMP-194 P1). Step 7 ("business_review") carries
`wait_for: "business_ready"` in `steps.json` -- a signal only the server can compute
(`business_review_ready.business_ready`). The plugin has no live copy of that signal yet
(RMP-194 P2 adds the poll hook that would), so the only ordering rule that can ship
alongside the step-7 DATA without re-blocking every customer the moment step 6 ticks is
"skip a `wait_for` step here unconditionally" -- never counted as the current/blocking
step, but (see `first_unfinished`) also never counted as finished, so it still shows up
correctly on the resume checklist. Rule 3 break: delete the `step.get("wait_for")` guard
below -> RED (`test_step_gate_order.test_everything_allowed_once_all_known_steps_passed`
and `test_step_gate_workspace`'s two tests all go back to denying everything with "Finish
step 7 first." the moment step 6 is ticked).
"""
from __future__ import annotations


def earlier_steps_done(steps: list[dict], state: dict, step_id: str) -> bool:
    """True when every step numbered below `step_id` is finished, with the SAME meaning
    the order gate uses: `connection_check` is in state["steps_passed"]; every other
    step is in state["ticked"]. False if `step_id` is not in `steps`. Never raises.

    Used by: `step_gate._check_brief_answers` (to deny brief writes before earlier
    steps are done); `step_recorder_revenue.description_waiting` (to gate capturing the
    description reply)."""
    target_step = None
    for step in steps:
        if step.get("id") == step_id:
            target_step = step
            break
    if target_step is None:
        return False

    for step in steps:
        if not isinstance(step.get("number"), int):
            continue
        if step["number"] >= target_step["number"]:
            continue
        if step.get("wait_for"):
            continue  # RMP-194 P1: a waiting step is never "not done" for this check either.
        step_id_inner = step.get("id")
        if step_id_inner == "connection_check":
            if step_id_inner not in state.get("steps_passed", []):
                return False
        else:
            if step_id_inner not in state.get("ticked", []):
                return False
    return True


def first_unfinished(steps: list[dict], state: dict) -> dict | None:
    """The first step not yet finished FOR GATE ORDERING. `connection_check` keeps its
    original, pre-RMP-9 definition (done once in `steps_passed`). Every step after it
    additionally needs its tick to have succeeded (`state["ticked"]`) -- see the module
    docstring, "gate ordering uses 'tick' not 'pass'". A `wait_for` step (RMP-194 P1) is
    skipped here unconditionally -- see the module docstring's own paragraph.

    Moved here from `step_gate._first_unpassed` (unchanged, P1641)."""
    for step in steps:
        if step.get("wait_for"):
            continue
        step_id = step.get("id")
        if step_id == "connection_check":
            if step_id not in state.get("steps_passed", []):
                return step
            continue
        if step_id not in state.get("ticked", []):
            return step
    return None
