#!/usr/bin/env python3
"""Step 6, mid-turn: "Do you have another website?" after robots_blocked OR
failed (RMP-199, RMP-25).

Live bug: TTown Fitness's Instagram bio linked ttownfitness.wodify.com (its
class-booking tool, not its website). Wodify's robots.txt blocks reading, so
the read ended `robots_blocked` and step 6 used to tick "skipped" at once --
before anyone asked whether a real, readable website existed. It did.

RMP-25 (S6-A9): the same overeager skip happened for a `failed` read, so this
pending-offer flow covers both outcomes (only the module name still says
"robots").

RMP-281 P2272: the question and its two buttons are written by the SERVER in
the owner's language (`offers.website_another`, carried by the
`wait_for_website_read` reply, see `offer_lines.py`). This hook holds no
English text. It matches the answer by the neutral option id (`yes` /
`no`), so a Spanish "no" or a Hindi button works. With no offer from the
server the hook shows nothing and stays pending.

FLOW: `step_recorder_website.handle_wait_for_website_read` calls `set_pending`
on a `robots_blocked`/`failed` outcome instead of ticking "skipped".
`priority_reminders.py` shows `build_reminder`'s `AskUserQuestion` every turn
until answered. `answer_captures.py` calls `try_capture_*` BEFORE normal step
matching. "yes" clears the flag only (the skill asks for the new address).
"no" clears the flag AND ticks step 6 "skipped".

FAIL-SAFE, same convention as every sibling module: nothing here may crash a
hook.
"""
from __future__ import annotations

from typing import Any

import connection_state as cs
import offer_lines
import step_state

WEBSITE_STEP_ID = "website"

_PENDING_KEY = "website_robots_blocked_offer_pending"
OFFER_ID = "website_another"


def set_pending(session_id: str) -> None:
    """Called from `step_recorder_website.handle_wait_for_website_read` on a
    `robots_blocked` outcome, in place of the old immediate skip tick."""
    cs.write_patch(session_id, {_PENDING_KEY: True})


def _is_pending(session_id: str) -> bool:
    raw = cs.read_raw(session_id).get(_PENDING_KEY)
    return raw if isinstance(raw, bool) else False


def build_reminder(session_id: str) -> dict[str, Any] | None:
    """The exact `AskUserQuestion` this session owes, or None. Not consumed
    here -- it stays pending (repeated every turn) until the customer answers."""
    if not _is_pending(session_id):
        return None
    offer = offer_lines.get(session_id, OFFER_ID)
    return offer_lines.ask_instruction(offer) if offer is not None else None


def _consume(session_id: str, matched: str | None) -> bool:
    """"yes" -> just clear the pending flag. "no" -> clear the flag AND tick step 6 "skipped" now
    (the customer confirmed there is nothing else to try). A reply that matches neither clears the
    flag and does nothing else.

    Rule 3 break: drop the `matched == "no"` tick -> RED (declining would leave step 6 stuck open)."""
    cs.write_patch(session_id, {_PENDING_KEY: False})
    if matched == "no":
        step_state.mark_step_passed(session_id, WEBSITE_STEP_ID, "skipped")
    return True


def try_capture_ask_user_answer(session_id: str, question_text: str, label: str) -> bool:
    """`AskUserQuestion` entry point, wired into `answer_captures.py`."""
    if not _is_pending(session_id):
        return False
    offer = offer_lines.get(session_id, OFFER_ID)
    if offer is None or question_text != offer["say"]:
        return False
    return _consume(session_id, offer_lines.match_clicked(offer, label))


def try_capture_typed_answer(session_id: str, message: str) -> bool:
    """Headless typed fallback -- only a label, an `also` word, an id or an option number counts, so an
    unrelated typed reply is never swallowed."""
    if not _is_pending(session_id):
        return False
    matched = offer_lines.match(offer_lines.get(session_id, OFFER_ID), message)
    if matched is None:
        return False
    return _consume(session_id, matched)
