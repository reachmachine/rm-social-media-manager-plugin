#!/usr/bin/env python3
"""Step 9's "come back when ready" offer (RMP-205), same shape as
`niche_return.py` (step 8's own version): "Otherwise a new `hooks/dream_
customer_return.py`, added to `priority_reminders` right after `niche_
return`, offers it once per session at a turn boundary."

SIMPLER THAN `business_return.py` ON PURPOSE, same reason `niche_return.py`'s
own docstring gives for ITS simplification: step 9 needs no server POLL hook
of its own -- step 9's own readiness is exactly "is `pick_niche` ticked",
already tracked locally in `state["ticked"]` the instant `step_recorder_
niche.py` sets it, no round trip needed.

ONCE PER SESSION: consumed the moment it is shown, whatever the customer
says next -- a fresh session (`SessionStart` resets `connection_state`)
naturally re-offers it, same reasoning `niche_return.py`'s own docstring
gives for its case.

FAIL-SAFE: nothing here may crash a hook, same convention as every sibling
module.
"""
from __future__ import annotations

from typing import Any

import connection_state as cs
import offer_lines
import plan_cache

_OFFERED_KEY = "dream_customer_offered"
# The offer line comes from the SERVER (next_actions `next_offer`, in the owner's language, with the job's real time limit),
# cached by plan_recorder. This hook shows exactly that line and writes none of its own (RMP-281 P2268).


def _was_offered(session_id: str) -> bool:
    raw = cs.read_raw(session_id).get(_OFFERED_KEY)
    return raw if isinstance(raw, bool) else False


def build_return_reminder(session_id: str, state: dict[str, Any]) -> dict[str, Any] | None:
    """Returns the same `{"instruction": <prose>}` shape every sibling
    priority reminder uses, or `None`.

    Rule 3 target. Drop the `"dream_customer" in state["ticked"]` guard
    below and this would keep re-offering step 9 forever, even after the
    customer already finished it -- `test_dream_customer_return.
    test_rule3_never_offered_once_dream_customer_is_ticked` proves this."""
    ticked = state.get("ticked", [])
    if "dream_customer" in ticked:
        return None
    if "pick_niche" not in ticked:
        return None
    if _was_offered(session_id):
        return None
    offer = offer_lines.get(session_id, "dream_customer")   # RMP-281 P2272: the line AND its buttons, from the server
    if offer is not None:
        cs.write_patch(session_id, {_OFFERED_KEY: True})
        return offer_lines.ask_instruction(offer)
    say = plan_cache.read_state(session_id)["next_offer"]   # older server: a line with no buttons
    if not say:
        return None   # the server has not given a line yet: say nothing, and offer on a later turn
    cs.write_patch(session_id, {_OFFERED_KEY: True})
    return {
        "instruction": (
            f'Ask the customer with AskUserQuestion: "{say}" '
            "Give two buttons, a yes and a later, in the same language as that line."
        )
    }
