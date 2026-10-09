#!/usr/bin/env python3
"""RMP-9/RMP-18 resume-checklist gate rules -- split out of `step_gate.py` to
stay under the 300-line file limit, same "split when it grows" precedent as
`step_gate_own_account.py` (RMP-23).

Spec: docs/plugin-v2/00-resume-checklist.md, "The model cannot tick a box it
didn't earn". Each function here returns a ready `_deny(...)` dict or `None`
(allow), exactly like every check function in `step_gate.py` itself --
`_decide_steps` just calls straight through. Pure move, no behaviour change:
same bodies as the private functions this replaces in `step_gate.py`.
"""
from __future__ import annotations

import deny_lines
import planner_mode_state
import steps_manifest

# RMP-291 P2320: the texts are the server's (`next_actions.deny_reasons`, shown through `deny_lines`); the plugin holds ids.
_MANIFEST_MISMATCH_REASON = "manifest_outdated"
_TICK_DENY_REASON = "tick_not_done"
# RMP-201/RMP-190 (live BU, 2026-09-30): the model tried to tick "website" 3
# times and got the generic line above each time -- a permanent no it read as
# "try again". A server-ticked step names itself and says stop, so the model
# neither retries nor guesses why (advice-only, never loop).
_SERVER_TICK_REASON = "tick_server_done"

# RMP-194 P2: business_review ticks ONLY on the server, inside
# `answer_business_review` (RMP-76: logic on the server, the plugin only
# executes -- `step_recorder_business_review.py` reads the tick back from
# that tool's own `ticked: true` result, never from a model-issued
# `record_checklist_step` call). Denied unconditionally, even when
# `state["steps_passed"]` already agrees -- a model that noticed the local
# flag and tried to "helpfully" tick it anyway must still be refused, since
# the real tick has side effects (`business_reviews.mark_completed`) this
# gate has no way to also trigger. Rule 3 break: remove this check -> RED
# (a model-issued `record_checklist_step(business_review, done, answered)`
# would be allowed the moment `steps_passed` locally agreed).
# RMP-197 P2: `pick_niche` ticks ONLY on the server, inside `choose_niche` --
# same reasoning (the real tick also writes `growth_focus` and, on the doc,
# `chosen`), `step_recorder_niche.py` reads it back the same way.
# RMP-205: `dream_customer` ticks ONLY on the server, inside
# `choose_main_persona` -- same reasoning (the real tick also writes
# `main_persona.approved_id`/`approved_at`), `step_recorder_dream_customer.
# py` reads it back the same way.
_SERVER_ONLY_TICKS = frozenset({"business_review", "pick_niche", "dream_customer", "where_to_find"})

# RMP-201/RMP-194 F4 fix (2026-09-27, live pilot): "website" joins the
# server-only ticks, but DRIVE MODE ONLY -- `drive_ticks.sync_drive_ticks`
# (backend, design §4) is the one that writes this tick once the planner's
# own graph shows every website node (N6a/N6a2/N6b/N6c/N6d/N6e) really
# done/skipped, matching that module's own docstring: "the plugin's own
# step_gate_checklist._SERVER_ONLY_TICKS frozenset must ALSO gain 'website'
# before the plugin stops letting the model tick it a second time on its
# own -- that edit is P4's job." Live evidence this was still missing: the
# model ticked "website" itself (`how="already_known"`) the instant the read
# FINISHED, before a single business fact had been filled -- `get_fact_
# tasks`/`save_business_facts` never ran, and `get_business_review` looped
# "Still getting your website ready" forever. Outside drive mode nothing
# changes: the plugin's own `your-website` skill still ticks "website" itself
# once it reaches section 12, exactly as before -- there is no server-side
# planner tick to defer to there.
_DRIVE_ONLY_SERVER_TICKS = frozenset({"website"})


def _customer_skipped(step_id: str, how: object, state: dict) -> bool:
    """RMP-281 (P2257, live twin run baker_es, 2026-10-07): the owner answered step 6's own question "No website" or
    "Not now", so the plugin recorded the step as `skipped` -- but ONLY in its local file. The server checklist is
    written by `record_checklist_step` alone, and this gate refused that call in drive mode ("marked done for you"),
    so the server never heard. The planner then asked its own "Do you have a website?" (N6a2) a second time.
    The planner writes no tick for a website that was never read, so there is nothing to defer to: let the tick that
    records the customer's own skip through. `how` must match what the hooks recorded, so the model cannot claim a
    skip the customer did not make.
    Rule 3: return False here -> test_rmp281_p2257_no_website_asked_once_chain and the gate test go RED."""
    return how == "skipped" and state["steps_passed"].get(step_id) == "skipped"


def _deny(reason_id: str, session_id: str = "") -> dict:
    return deny_lines.deny(deny_lines.reason(session_id, reason_id))


def check_resume_checklist_manifest(tool_input: dict, session_id: str = "") -> dict | None:
    """00-resume-checklist.md: "The manifest sent must equal the plugin's
    own steps.json" -- the server always holds the true list, never a
    manifest the model could have edited or forgotten fields from.

    RMP-173 P4: an up-to-date plugin no longer sends `steps_manifest` at all
    (the server seeds its own -- `agent_step_rules.merge_manifest`), so a
    MISSING manifest is now allowed. Only a manifest that IS present and
    does not match this plugin's own steps.json is denied -- the same
    protection against a model fabricating or editing one this check always
    gave, now conditional on the field being sent at all."""
    manifest = tool_input.get("steps_manifest")
    if manifest is None:
        return None
    if manifest != steps_manifest.public_manifest():
        return _deny(_MANIFEST_MISMATCH_REASON, session_id)
    return None


def check_checklist_tick(tool_input: dict, state: dict, session_id: str) -> dict | None:
    """RMP-9 rule 3: "Only earned ticks" -- `in_progress` always allowed
    (it only says "started"); `done` allowed only if `step_id` is really in
    `steps_passed` AND the `how` sent matches the `how` the hooks themselves
    recorded, so the model can never claim credit ("answered") for a step
    that was actually free ("already_known"), or vice versa.

    **Rule 3 target (the drive-mode website gate).** Drop the
    `_DRIVE_ONLY_SERVER_TICKS` branch below and a drive-mode session would
    let the model tick "website" itself again, the instant the read
    finishes, before the planner's own fact-fill job (N6e) ever ran --
    `test_step_gate_checklist.
    test_rule3_website_tick_denied_in_drive_mode_even_when_locally_earned`
    proves this (the tick is otherwise allowed: `steps_passed` already
    agrees)."""
    new_state = tool_input.get("state")
    if new_state == "in_progress":
        return None
    if new_state != "done":
        return _deny(_TICK_DENY_REASON, session_id)
    step_id = tool_input.get("step_id")
    how = tool_input.get("how")
    if not isinstance(step_id, str) or not step_id:
        return _deny(_TICK_DENY_REASON, session_id)
    if step_id in _SERVER_ONLY_TICKS:
        return _deny(_SERVER_TICK_REASON, session_id)
    if (
        step_id in _DRIVE_ONLY_SERVER_TICKS
        and planner_mode_state.is_drive(session_id)
        and not _customer_skipped(step_id, how, state)
    ):
        return _deny(_SERVER_TICK_REASON, session_id)
    if state["steps_passed"].get(step_id) != how:
        return _deny(_TICK_DENY_REASON, session_id)
    return None
