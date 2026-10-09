#!/usr/bin/env python3
"""The chain of "priority" reminders `checklist_recorder.build_step_reminder`
checks before its normal step-by-step loop -- split out to keep both
`checklist_recorder.py` and `step_recorder.py` under 300 lines after the
RMP-66 website-return/website-mismatch hooks landed on top of RMP-52's
reoffer hook (P1671, P1672). Pure move: same functions, same order, same
calls -- no behaviour change.

ORDER (do not reorder without re-reading the founder decisions behind it):
  1. `own_account_mismatch.build_reminder` -- founder decision 6: a mismatch
     just shown, or just answered, gets its log entry right after the thing
     it records, before all other reminders.
  1b. `revenue_suggest.build_confirm_reminder` (RMP-24) -- a step 5 typed-
     sentence guess is pending, right after the mismatch reminder, so the
     model confirms it before anything else moves on.
  2. `step_skip.build_reoffer_reminder` (RMP-52) -- so the model asks the
     reoffer question at the same-turn additionalContext.
  3. `website_return.build_return_reminder` (RMP-66) -- right after the
     reoffer reminder, for the same reason.
  4. `business_return.build_return_reminder` (RMP-194 P2) -- step 7's own
     "come back when ready" offer, right after the website return, for the
     same reason.
  4b. (removed, RMP-25: the planner's generic "a background job finished,
     quick look?" offer -- "Yes" had nothing to show. Under drive mode
     `next_actions` itself brings up the next step when it is ready.)
  4c. `niche_return.build_return_reminder` (RMP-197 P3) -- step 8's own
     "come back when ready" offer, right after the planner's offer, once
     `business_review` is ticked and `pick_niche` is not yet started.
  4d. `dream_customer_return.build_return_reminder` (RMP-205) -- step 9's
     own "come back when ready" offer, right after step 8's, once
     `pick_niche` is ticked and `dream_customer` is not yet started.
  5. `fact_events.pending_event_reminder` (RMP-68) -- a fact the customer
     just gave gets logged right away, whatever step is current.
  6. `website_mismatch.pending_event_reminder` (RMP-66) -- right after the
     fact-event reminder.
  6. `website_robots_offer.build_reminder` (RMP-199) -- appended last: fires
     only right after a robots_blocked read, in practice mutually exclusive
     with everything above it.

RMP-164: step 2 and step 3 above are each gated by `step_order.earlier_steps_done` for the
step they re-offer (`own_instagram_account` / `website`) -- a pending re-offer or monthly
re-read never shows while an EARLIER step (e.g. step 3, "whose account?") is still
unfinished. Bug: `open_workspace` can return a checklist where step 6 is already
`skipped`/`done` but step 3 is `not_started` -- without this guard, the customer got asked
"Do you want us to read your website now?" before ever being asked step 3's own question.
The guard is checked BEFORE calling the builder, not after: `website_return.
build_return_reminder`'s re-read branch CONSUMES its own flag (clears it) as a side effect
of being called at all, so calling it first and only checking afterwards would silently
lose that one-shot instruction forever instead of holding it for later. Once the earlier
steps finish later in the same session, `state` changes and the SAME already-set pending
flag is free to show -- no re-setting needed, because `step_skip.maybe_set_reoffer_pending`
and `website_return.maybe_set_website_return` still set it unconditionally, exactly as
before this fix.
"""
from __future__ import annotations

from typing import Any

import business_return
import dream_customer_return
import fact_events
import niche_return
import own_account_mismatch
import revenue_suggest
import step_order
import step_skip
import steps_manifest
import website_mismatch
import website_return
import website_robots_offer


def first_priority_reminder(session_id: str, state: dict) -> dict[str, Any] | None:
    """The first reminder in the chain above that is currently pending, or
    None if none of the modules has anything to say right now."""
    mismatch_reminder = own_account_mismatch.build_reminder(session_id, state)
    if mismatch_reminder is not None:
        return mismatch_reminder

    revenue_confirm_reminder = revenue_suggest.build_confirm_reminder(session_id)
    if revenue_confirm_reminder is not None:
        return revenue_confirm_reminder

    steps = steps_manifest.load_steps(session_id)

    if step_order.earlier_steps_done(steps, state, "own_instagram_account"):
        reoffer_reminder = step_skip.build_reoffer_reminder(session_id, state)
        if reoffer_reminder is not None:
            return reoffer_reminder

    if step_order.earlier_steps_done(steps, state, "website"):
        website_return_reminder = website_return.build_return_reminder(session_id, state)
        if website_return_reminder is not None:
            return website_return_reminder

    if step_order.earlier_steps_done(steps, state, "business_review"):
        business_return_reminder = business_return.build_return_reminder(session_id, state)
        if business_return_reminder is not None:
            return business_return_reminder

    niche_return_reminder = niche_return.build_return_reminder(session_id, state)
    if niche_return_reminder is not None:
        return niche_return_reminder

    dream_customer_return_reminder = dream_customer_return.build_return_reminder(session_id, state)
    if dream_customer_return_reminder is not None:
        return dream_customer_return_reminder

    fact_reminder = fact_events.pending_event_reminder(session_id, state)
    if fact_reminder is not None:
        return fact_reminder

    website_mismatch_reminder = website_mismatch.pending_event_reminder(session_id, state)
    if website_mismatch_reminder is not None:
        return website_mismatch_reminder

    if step_order.earlier_steps_done(steps, state, "website"):
        robots_offer_reminder = website_robots_offer.build_reminder(session_id)
        if robots_offer_reminder is not None:
            return robots_offer_reminder

    return None
