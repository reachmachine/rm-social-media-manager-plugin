#!/usr/bin/env python3
"""Step 8's "come back when ready" offer (RMP-197 P3, design section 6):
"Otherwise a new `hooks/niche_return.py`, added to `priority_reminders`
after `business_return`, offers it once per session at a turn boundary."

SIMPLER THAN `business_return.py` ON PURPOSE, same reason the
old planner offer was simple: step 8 needs no server POLL
hook of its own (`business_ready_poll.py`'s whole reason to exist is that
step 7's readiness needs a website-read/indexer check only the server can
see) -- step 8's own readiness is exactly "is `business_review` ticked",
already tracked locally in `state["ticked"]` the instant
`step_recorder_business_review.py` sets it, no round trip needed.

ONCE PER SESSION: consumed the moment it is shown, whatever the customer
says next -- a fresh session (`SessionStart` resets `connection_state`)
naturally re-offers it, same reasoning `business_return.py`'s own docstring
gives for its case.

FAIL-SAFE: nothing here may crash a hook, same convention as every sibling
module.
"""
from __future__ import annotations

from typing import Any

import connection_state as cs
import offer_lines

_OFFERED_KEY = "pick_niche_offered"
# The line and its buttons come from the SERVER (`offers.niche`, in the owner's language); none here (RMP-281 P2272).


def _was_offered(session_id: str) -> bool:
    raw = cs.read_raw(session_id).get(_OFFERED_KEY)
    return raw if isinstance(raw, bool) else False


def build_return_reminder(session_id: str, state: dict[str, Any]) -> dict[str, Any] | None:
    """Returns the same `{"instruction": <prose>}` shape every sibling
    priority reminder uses, or `None`.

    Rule 3 target. Drop the `"pick_niche" in state["ticked"]` guard below
    and this would keep re-offering step 8 forever, even after the customer
    already finished it -- `test_niche_return.
    test_rule3_never_offered_once_pick_niche_is_ticked` proves this."""
    ticked = state.get("ticked", [])
    if "pick_niche" in ticked:
        return None
    if "business_review" not in ticked:
        return None
    if _was_offered(session_id):
        return None
    offer = offer_lines.get(session_id, "niche")   # RMP-281 P2272: the server wrote the line and the buttons
    if offer is None:
        return None   # no line from the server yet: say nothing, offer on a later turn (no English here)
    cs.write_patch(session_id, {_OFFERED_KEY: True})
    return offer_lines.ask_instruction(offer)
