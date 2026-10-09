#!/usr/bin/env python3
"""Per-module "is this reply mine, not a step answer" checks
`step_recorder.py`'s AskUserQuestion and typed-answer handlers run before
treating a reply as a normal step answer -- split out to keep both
`step_recorder.py` and `checklist_recorder.py` under 300 lines after the
RMP-66 website-return/website-mismatch hooks landed (P1671, P1672). Pure
move: same functions, same order, same calls -- no behaviour change.

`own_account_mismatch`'s own capture call stays inline in `step_recorder.py`
(it runs FIRST, and its import stays there anyway for `clear_on_new_handle`).
This module holds the checks that were added afterwards, run right after
it, in the SAME order as before the split:
  1. `website_mismatch.try_capture_*` (RMP-66)
  2. `step_skip.try_capture_*` (RMP-52)
  3. `website_return.try_capture_*` (RMP-66)
  4. `business_return.try_capture_*` (RMP-194 P2) -- right after the website
     return, same reason `priority_reminders.py` orders them that way.
  5. `website_robots_offer.try_capture_*` (RMP-199) -- the "do you have
     another website" pick, right after the two return offers.
  6. `own_account_not_found.try_capture_*` (RMP-175)
  7. `own_account_suggestion.try_capture_*` (RMP-161)
  8. `revenue_suggest.try_capture_*` (RMP-24) -- step 5's typed-sentence-guess confirm
"""
from __future__ import annotations

import business_return
import offer_step_answer
import own_account_not_found
import own_account_suggestion
import revenue_suggest
import step_skip
import website_mismatch
import website_return
import website_robots_offer


def capture_ask_user_answer(session_id: str, question_text: str, label: str) -> bool:
    """True if one of the eight modules above consumed this AskUserQuestion
    answer as its own (a website mismatch confirmation, a skip/reoffer pick,
    a website re-offer pick, a step-7 return offer pick, a "do you have
    another website" pick, a "fix the spelling / add it anyway" pick, an
    "is this your account" suggestion pick, or a step-5 typed-sentence-guess
    confirm) -- the caller must not also treat it as a normal step answer."""
    if website_mismatch.try_capture_ask_user_answer(session_id, question_text, label):
        return True
    if step_skip.try_capture_ask_user_answer(session_id, question_text, label):
        return True
    if website_return.try_capture_ask_user_answer(session_id, question_text, label):
        return True
    if business_return.try_capture_ask_user_answer(session_id, question_text, label):
        return True
    if website_robots_offer.try_capture_ask_user_answer(session_id, question_text, label):
        return True
    if revenue_suggest.try_capture_ask_user_answer(session_id, question_text, label):
        return True
    if offer_step_answer.try_capture_ask_user_answer(session_id, question_text, label):  # RMP-281 P2272
        return True
    if own_account_not_found.try_capture_ask_user_answer(session_id, question_text, label):
        return True
    if own_account_suggestion.try_capture_ask_user_answer(session_id, question_text, label):
        return True
    return False


def capture_typed_answer(session_id: str, message: str, transcript_path: str | None = None) -> bool:
    """Typed (headless) fallback for `capture_ask_user_answer`, same eight
    modules, same order."""
    if website_mismatch.try_capture_typed_answer(session_id, message):
        return True
    if step_skip.try_capture_typed_answer(session_id, message, transcript_path):
        return True
    if website_return.try_capture_typed_answer(session_id, message):
        return True
    if business_return.try_capture_typed_answer(session_id, message):
        return True
    if website_robots_offer.try_capture_typed_answer(session_id, message):
        return True
    # P2361: a pending step-5 guess is answered BEFORE the step's own offer is read: a typed "1" means the guess's first button, not option 1 of the five
    if revenue_suggest.try_capture_typed_answer(session_id, message):
        return True
    if offer_step_answer.try_capture_typed_answer(session_id, message):  # RMP-281 P2272
        return True
    if own_account_not_found.try_capture_typed_answer(session_id, message):
        return True
    if own_account_suggestion.try_capture_typed_answer(session_id, message):
        return True
    return False
