#!/usr/bin/env python3
"""Step 6 in later sessions: re-offer a skipped website, re-read a month-old one (RMP-66).

Founder decision: step 6 skip is allowed, "same pattern as step 4" (step 4 re-offers once
in every later session); "the website is read once, re-read once a month when the plugin
is used". Spec: docs/plugin-v2/06-website-and-business-knowledge.md SS4, "Wave 2 design".

Once step 6 is ticked (`done`, any `how`), the resume checklist never sends the agent back
to it (`checklist_recorder.build_step_reminder`'s step loop skips every ticked step). So
without this module, a skipped website is never offered again, and a read website is never
re-read. Shape copied from `step_skip.py` (step 4's reoffer), split into its own module
instead of editing that file (298 lines already).

TWO INDEPENDENT CASES, called from `checklist_recorder.handle_get_resume_checklist` once
per `get_resume_checklist` result, keyed on the checklist's OWN `how` for the `website`
step (see `maybe_set_website_return`):
  - `how == "skipped"` AND the server's `skip_reason == "later"` (P2358: not "no website") ->
    `website_reoffer_pending`: a real question, same shape as step 4's reoffer, kept pending until
    the customer answers it.
  - `how in ("answered", "already_known")` -> `website_reread_check`: a one-shot INSTRUCTION
    (call a tool, no question), consumed the first time `build_return_reminder` shows it, so
    it can never repeat mid-session even though nothing "answers" it.

Both cases share ONE `website_return_handled` raw flag: once set, `maybe_set_website_return`
never sets EITHER pending flag again this session -- set immediately (not deferred to an
answer), because the reread case has no answer to defer to.

FAIL-SAFE, same convention as every sibling module: nothing here may crash a hook.
"""
from __future__ import annotations

from typing import Any

import connection_state as cs
import offer_lines
import step_state

WEBSITE_STEP_ID = "website"

# RMP-281 P2272: the re-offer question and its buttons come from the SERVER in the owner's language
# (`offers.website_reoffer`, ids `read_now` / `later`; see offer_lines.py). No English text here.
REOFFER_OFFER_ID = "website_reoffer"

_REREAD_INSTRUCTION_TEXT = (
    "Call get_website_read_status. If due_for_reread is true, re-read the website now "
    "(skill your-website, section 'Monthly re-read')."
)


def _is_website_reoffer_pending(session_id: str) -> bool:
    raw = cs.read_raw(session_id).get("website_reoffer_pending")
    return raw if isinstance(raw, bool) else False


def _is_website_reread_check_pending(session_id: str) -> bool:
    raw = cs.read_raw(session_id).get("website_reread_check")
    return raw if isinstance(raw, bool) else False


def _was_website_return_handled(session_id: str) -> bool:
    raw = cs.read_raw(session_id).get("website_return_handled")
    return raw if isinstance(raw, bool) else False


def record_skip_reason(session_id: str, value: Any) -> None:
    """P2358: remember WHY step 6 was skipped ("no_website" or "later"), so the model's tick tells the server and only "later" is
    offered the re-read in a later session. Any other value is ignored."""
    if value in ("no_website", "later"):
        cs.write_patch(session_id, {"website_skip_reason": value})


def skip_reason(session_id: str) -> str | None:
    raw = cs.read_raw(session_id).get("website_skip_reason")
    return raw if raw in ("no_website", "later") else None


def maybe_set_website_return(session_id: str, how: str, reason: str | None = None) -> None:
    """Called from `checklist_recorder.handle_get_resume_checklist` for every `done`
    `website` checklist entry, regardless of whether it was newly ticked this call (same
    call pattern `step_skip.maybe_set_reoffer_pending` uses for step 4). Sets exactly one
    of the two pending flags, and `website_return_handled`, ONCE per session -- a second
    `get_resume_checklist` call this session is always a no-op here."""
    if _was_website_return_handled(session_id):
        return
    if how == "skipped":
        # P2358: only an owner who said "later" is offered the read again. "No website" (and an older record with no reason) never is.
        cs.write_patch(session_id, {"website_reoffer_pending": reason == "later", "website_return_handled": True})
    elif how in ("answered", "already_known"):
        cs.write_patch(session_id, {"website_reread_check": True, "website_return_handled": True})
    # anything else -> nothing (table row 3)


def build_return_reminder(session_id: str, state: dict[str, Any]) -> dict[str, Any] | None:
    """Returns the reoffer question, or the re-read instruction, or None. Format matches
    `checklist_recorder.build_step_reminder`: `{"instruction": <prose>}`. Called from there
    right after `step_skip.build_reoffer_reminder`, so it appears at the same-turn prompt.

    The reread instruction is CONSUMED here (cleared the first time it is shown) -- it has
    no answer to wait for, so nothing else would ever clear it. The reoffer question is NOT
    consumed here -- it stays pending, reminding every turn, until the customer answers it,
    same as step 4's reoffer."""
    if _is_website_reoffer_pending(session_id):
        offer = offer_lines.get(session_id, REOFFER_OFFER_ID)
        return offer_lines.ask_instruction(offer) if offer is not None else None   # no line yet: stay pending
    if _is_website_reread_check_pending(session_id):
        cs.write_patch(session_id, {"website_reread_check": False})
        return {"instruction": _REREAD_INSTRUCTION_TEXT}
    return None


def _apply(session_id: str, matched_value: str | None) -> None:
    """"read_now" -> un-pass and un-tick `website`, so step 6 runs again from its skill. Either way the
    pending flag is cleared."""
    if matched_value == "read_now":
        step_state.unmark_step_passed(session_id, WEBSITE_STEP_ID)
        step_state.unmark_ticked(session_id, WEBSITE_STEP_ID)
    cs.write_patch(session_id, {"website_reoffer_pending": False})


def handle_reoffer_answer(session_id: str, question_text: str, answer_label: str) -> bool:
    """A click on the server's re-offer. Returns True if the answer was consumed (the caller must not
    run normal step matching). A malformed answer is consumed too, with no further action."""
    if not _is_website_reoffer_pending(session_id):
        return False
    offer = offer_lines.get(session_id, REOFFER_OFFER_ID)
    if offer is None or question_text != offer["say"]:
        return False
    matched_value = offer_lines.match_clicked(offer, answer_label)
    if matched_value is not None:
        _apply(session_id, matched_value)
    return True


def handle_reoffer_answer_typed(session_id: str, typed_answer: str) -> bool:
    """Headless typed fallback: only a label, an `also` word, an id or an option number counts, so an
    unrelated typed reply is never read as this answer by accident."""
    if not _is_website_reoffer_pending(session_id):
        return False
    matched_value = offer_lines.match(offer_lines.get(session_id, REOFFER_OFFER_ID), typed_answer)
    if matched_value is None:
        return False
    _apply(session_id, matched_value)
    return True


def try_capture_ask_user_answer(session_id: str, question_text: str, label: str) -> bool:
    """Entry point for `AskUserQuestion` answers, called from `step_recorder.
    handle_ask_user_question` BEFORE normal step matching (same spot `step_skip.
    try_capture_ask_user_answer` runs), since this question is not one of `steps.json`'s
    own `question.text` values."""
    return handle_reoffer_answer(session_id, question_text, label)


def try_capture_typed_answer(session_id: str, message: str) -> bool:
    """Entry point for typed (headless) answers, called from `step_recorder.
    handle_typed_answer`."""
    return handle_reoffer_answer_typed(session_id, message)
