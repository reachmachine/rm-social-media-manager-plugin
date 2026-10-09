#!/usr/bin/env python3
"""Step 6 recorder rules: "your website" (P1668, RMP-66).

Spec: docs/plugin-v2/06-website-and-business-knowledge.md, "Wave 2 design", "Step 6 in the
manifest". Split out of `step_recorder.py` to keep it under the 300-line limit, same
"split when it grows" precedent as `step_recorder_revenue.py` (RMP-38).

A TYPED REPLY ONLY COUNTS WHILE STEP 6 IS THE CUSTOMER'S CURRENT STEP (found via architect
review, P1668): `answer_matcher.match_typed_reply` matches a message against EVERY question
step's own options, regardless of step order (steps 3 and 5 already work this way). Step 6's
own option VALUES are the plain words "yes"/"later" -- a stray "yes" or "not now" typed for
something unrelated, long before step 6 is even reached, would otherwise be read as step 6's
own answer and mark it `steps_passed["website"] = "skipped"`. That is not merely inert: the
very next `checklist_recorder.build_step_reminder` call reads `steps_passed` (not `ticked`)
for a step's `how`, so it would then tell the model to TICK step 6 as skipped -- closing it
without the customer ever having been asked. `typed_answer_waiting` (below) is the same
"only once this step is actually current" guard `_handle_steps_waiting` already applies to a
bare handle for step 4, and `step_recorder.handle_typed_answer` drops the `website` step out
of its matching candidates entirely unless this returns True.

WHAT MARKS STEP 6 PASSED:
  - the customer answers the step's own question "no_website" or "later" -> `mark_step_passed
    (..., "skipped")`, called from `step_recorder.py`'s AskUserQuestion/typed-answer handlers
    right after the generic answer capture (same spot `own_account_mismatch.clear_on_new_handle`
    runs for step 4's own question);
  - RMP-92 (bug found in the live plugin chat, 2026-09-25, salon site): a `wait_for_website_read`
    (or `finish_website_read`) that reports pages read is NOT enough to tick step 6 on its own
    any more -- the background reader's own tool call was firing this hook and ticking "answered"
    before a single `get_next_fact_task`/`save_business_fact` call had ever run, so "23 pages
    saved" turned into "All setup steps are complete" with zero business facts filled. Reading
    pages now only REMEMBERS, for this session, that a read finished with pages
    (`read_finished_with_pages`, a raw `connection_state` key, same pattern as `website_search_
    state.is_available` below -- `step_state.py` is already at the 300-line limit):
      - `wait_for_website_read` reports `status: "finished"` with `read >= 1` -> remember only;
        `status: "failed"`, or `"finished"` with `read == 0` -> "skipped" immediately, unchanged
        -- there is nothing to fill if nothing was read. `status: "robots_blocked"` (RMP-199) no
        longer ticks immediately -- it sets a pending "Do you have another website?" offer first
        (see that function's own docstring); "skipped" only follows once the customer says no;
      - `finish_website_read` (the OLD, plugin-driven path, kept only for a last-resort
        plugin-driven read) succeeds with `pages_received >= 1` -> remember only, same as above;
        `pages_received == 0` -> "skipped" immediately, unchanged.
  - `get_next_fact_task` (`handle_get_next_fact_task`, below) is now the ONLY place step 6 ticks
    "answered": a `{"step": "done"}` response, AND this session remembered a finished read with
    pages, AND search is not known to be down this session (`website_search_state.is_available`,
    the RMP-72 rule, moved here from the read handlers above) -> "answered". A `done` with no
    finished read this session (e.g. a monthly re-read that found nothing new) -> nothing.
    `{"step": "fill_fact", ...}` -> nothing, the loop keeps going. Search down -> nothing, left
    NOT passed on purpose, not "skipped", so the next session runs step 6 again once search is
    back;
  - `get_website_read_status` shows a `finished` read that is not `due_for_reread`, AND step 6 has
    not already passed this session -- the "already known" case (a website read from an earlier
    session, or from earlier in THIS session, is not re-asked). The "not already passed" guard
    stops a LATER status poll (the skill polls it while waiting for indexing, section 8 of the
    skill) from silently downgrading a real "answered" pass back to "already_known".

FAIL-SAFE: nothing here may crash a hook -- same convention as every sibling module.
"""
from __future__ import annotations

import json
from typing import Any

import connection_state as cs
import fact_events
import reviews_read_state
import step_order
import step_state
import website_return
import website_robots_offer
import website_search_state

WEBSITE_STEP_ID = "website"
_SKIP_VALUES = ("no_website", "later")
_READ_FINISHED_WITH_PAGES_KEY = "website_read_finished_with_pages"


def typed_answer_waiting(steps: list[dict], state: dict) -> bool:
    """True only once step 6 is genuinely the customer's current step: not already passed,
    and every earlier step is done (same "done" meaning `step_order.earlier_steps_done` and
    `step_order.first_unfinished` already use). See the module docstring for the bug this
    guards -- a stray "yes"/"later" typed long before step 6 is reached must never be read as
    its answer."""
    if WEBSITE_STEP_ID in state["steps_passed"]:
        return False
    return step_order.earlier_steps_done(steps, state, WEBSITE_STEP_ID)


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _mark_read_finished_with_pages(session_id: str) -> None:
    cs.write_patch(session_id, {_READ_FINISHED_WITH_PAGES_KEY: True})


def read_finished_with_pages(session_id: str) -> bool:
    """True once, THIS session, a website read has reported pages found
    (`wait_for_website_read` "finished" with `read >= 1`, or the old
    `finish_website_read` with `pages_received >= 1`) -- the one thing
    `handle_get_next_fact_task` requires before it may tick step 6 "answered"
    (RMP-92, module docstring). Missing/wrong-typed reads back as False, the
    safe default -- a `done` response proves nothing on its own if no read
    ever actually happened this session."""
    return cs.read_raw(session_id).get(_READ_FINISHED_WITH_PAGES_KEY) is True


def handle_website_question_answer(session_id: str, value: Any) -> None:
    """Called right after the generic AskUserQuestion/typed handler stores the customer's
    answer to step 6's own question. "no_website"/"later" close the step immediately -- there
    is nothing else to wait for (design doc, "Ask": "No website / Not now -> one line, tick").
    "yes" needs a website read first, so it does nothing here."""
    if value in _SKIP_VALUES:
        website_return.record_skip_reason(session_id, value)   # P2358: the tick tells the server why
        step_state.mark_step_passed(session_id, WEBSITE_STEP_ID, "skipped")


def handle_wait_for_website_read(session_id: str, payload: dict) -> None:
    """RMP-76: the server-first read reports progress through `wait_for_
    website_read`, not a plugin-driven `finish_website_read` call, so THIS
    is the normal way a read finishes now. `finish_website_read` (below)
    stays wired for the last-resort, plugin-driven read.

    RMP-92: `finished` with pages no longer ticks step 6 by itself -- it
    only REMEMBERS the read for `handle_get_next_fact_task` (module
    docstring). Rule 3 break: put the old `mark_step_passed(..., "answered")`
    back here -> RED (a "23 pages saved" read would tick step 6 again before
    a single fact was ever filled -- the exact live bug this ticket fixes).

    RMP-199/RMP-25: a `robots_blocked` OR `failed` read no longer ticks
    "skipped" immediately -- the SERVER decides this (founder rule: the
    plugin only executes), via the `offer_another_website` field
    `website_progress_say.progress` sets (true for either outcome). When
    that field is true this sets a pending offer instead (`website_robots_
    offer.py`'s own `set_pending`/`build_reminder`/`handle_answer`, split
    into its own module so this file stays under the 300-line limit; its
    name predates RMP-25 -- it now covers both outcomes, not just robots),
    so the customer gets one chance to give another address first. When the
    server does NOT set it (a payload from before this field existed, or any
    other mismatch), the read still falls back to the old immediate skip --
    never left stuck open with nothing recorded at all. The live bugs this
    closes: TTown Fitness's Instagram bio linked its Wodify booking page,
    robots.txt blocked the read, and step 6 was skipped before anyone asked
    whether a real website existed (RMP-199); and a site that was simply
    down (S6-A9, RMP-25) got the exact same overeager skip with no chance to
    give a working address instead.

    Rule 3 break: drop the `if data.get("offer_another_website") is True:`
    check (always call `set_pending`) -> a `robots_blocked` payload with
    `offer_another_website: False` would still offer -- a field the hook
    never actually reads is exactly the G137 shape (CLAUDE.md Rule 3).
    Caught by `test_robots_blocked_without_the_offer_field_falls_back_to_
    skipped` below."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    status = data.get("status")
    read = data.get("read")
    if status == "finished":
        if not isinstance(read, int):
            return
        if read >= 1:
            _mark_read_finished_with_pages(session_id)
        else:
            step_state.mark_step_passed(session_id, WEBSITE_STEP_ID, "skipped")
    elif status in ("robots_blocked", "failed"):
        if data.get("offer_another_website") is True:
            website_robots_offer.set_pending(session_id)
        else:
            step_state.mark_step_passed(session_id, WEBSITE_STEP_ID, "skipped")
    # status == "reading": nothing to record yet -- the loop keeps waiting.


def handle_finish_website_read(session_id: str, payload: dict) -> None:
    """The old, plugin-driven read path -- RMP-92: same rule as `handle_wait_for_
    website_read` above, no tick on finish. `pages_received >= 1` only remembers the
    read; `pages_received == 0` still ticks "skipped" immediately, since there is
    nothing to fill either way."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    pages_received = data.get("pages_received")
    if not isinstance(pages_received, int):
        return
    if pages_received >= 1:
        _mark_read_finished_with_pages(session_id)
    else:
        step_state.mark_step_passed(session_id, WEBSITE_STEP_ID, "skipped")


def handle_get_next_fact_task(session_id: str, payload: dict) -> None:
    """RMP-92: the ONLY place step 6 ticks "answered" now. `{"step": "done"}` alone
    proves nothing -- it just means nothing is missing -- so it only ticks when THIS
    session also remembered a finished read with pages (`read_finished_with_pages`),
    and search is not known to be down this session (`website_search_state.is_
    available`, RMP-72's rule, moved here from the read handlers above).

    Rule 3 break 1: drop the `read_finished_with_pages` check -> RED (a `done` with no
    read this session -- e.g. a monthly re-read that found nothing new -- would tick).
    Rule 3 break 2: drop the `is_available` check -> RED (ticking "answered" while
    search never actually worked this session would be a false claim)."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    if data.get("step") != "done":
        return  # "fill_fact" -- the loop keeps going, nothing to record yet
    if not read_finished_with_pages(session_id):
        return
    if not website_search_state.is_available(session_id):
        return  # RMP-72: nothing about the business was actually searched for
    step_state.mark_step_passed(session_id, WEBSITE_STEP_ID, "answered")


def handle_save_business_facts(session_id: str, payload: dict) -> None:
    """RMP-96: the batch counterpart of `handle_get_next_fact_task` above --
    ticks step 6 "answered" straight off `save_business_facts`' own
    `missing` list, so the model no longer needs a separate `get_next_fact_
    task` "done" call after the batch save. Same two extra conditions as
    the single-task path (module docstring): this session must have
    remembered a finished read with pages, and search must not be known to
    be down. Also queues one `business_fact_saved` session-log event per
    field the batch call actually saved (`fact_events.handle_save_business_
    facts`) -- run first, since a `missing` field never blocks logging the
    OTHER fields this same call did save.

    Rule 3 break: drop the `missing != []` check -> RED (a batch call that
    still owes missing fields would tick step 6 "answered" early)."""
    fact_events.handle_save_business_facts(session_id, payload)
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    if data.get("missing") != []:
        return
    if not read_finished_with_pages(session_id):
        return
    if not website_search_state.is_available(session_id):
        return
    step_state.mark_step_passed(session_id, WEBSITE_STEP_ID, "answered")


def handle_get_website_read_status(session_id: str, payload: dict) -> None:
    """Rule 3 break (the guard this test exists for): drop the "not already passed" check and a
    later status poll (the skill's own "wait for the index" step) would overwrite a real
    "answered" pass with "already_known" the moment the read it just finished shows up as
    `finished` + not `due_for_reread` -- the customer's earned "answered" credit would be lost.

    RMP-194 live bug (2026-09-27, gym site): `finished` + not-`due_for_reread` also
    describes a read that just finished THIS session (section 6's own status check,
    called right after a fresh read) -- indistinguishable from section 2's real
    "already known" case unless `read_finished_with_pages` (set the instant a read
    reports pages) is checked first. Without this guard step 6 ticked `already_known`
    before a single fact was filled, which then let step 7's "come back when ready"
    reminder fire mid-flow and skip the reviews-consent question (section 8). Only
    `handle_get_next_fact_task`/`handle_save_business_facts` may tick a fresh read.
    Rule 3 break: drop this guard -> RED
    (`test_status_finished_this_session_before_facts_filled_does_not_mark_already_known`)."""
    if read_finished_with_pages(session_id):
        return
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    if WEBSITE_STEP_ID in step_state.read_state(session_id)["steps_passed"]:
        return
    current_read = data.get("current_read")
    if not isinstance(current_read, dict):
        return
    if current_read.get("status") != "finished":
        return
    if data.get("due_for_reread") is not False:
        return
    step_state.mark_step_passed(session_id, WEBSITE_STEP_ID, "already_known")


def website_tick_ready(session_id: str) -> bool:
    """RMP-194 (live bug, 2026-09-27, gym site): step 6 must not be TICKED
    (`checklist_recorder.build_step_reminder`'s generic loop fires the
    instant `steps_passed["website"]` gets any value) until section 8
    (Google reviews consent) has had its turn -- otherwise step 7's "come
    back when ready" offer becomes reachable and preempts the skill
    mid-flow ("Your website check is done. Quick look?" hijacking the
    reviews question live).

    No real read this session (no website, or an already-known read from
    before) -- nothing to wait for, tick right away. A real read WITH pages
    -- section 8 always calls `start_reviews_fetch` once reached (whatever
    it answers), so that call is the signal section 8 has run.

    Rule 3 break: always `return True` -> RED
    (`test_website_tick_ready_false_until_reviews_consent_is_asked`)."""
    if not read_finished_with_pages(session_id):
        return True
    return reviews_read_state.consent_asked(session_id)
