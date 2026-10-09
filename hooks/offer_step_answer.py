#!/usr/bin/env python3
"""A step's own question, when the SERVER wrote it in the owner's language (RMP-281 P2272, P2356).

`steps.json` keeps the English question for English owners, and `step_recorder` matches an answer to a step
by that exact text. A Spanish or Hindi owner is asked the server's own line (`offers.<id>` with a `step`
field, see `offer_lines.py`), so the English text never matches. This module closes that gap for step 6
("website", the question with `yes` / `no_website` / `later` buttons): it matches the click by the SERVER's
line and the neutral option id, then records the same answer the English path records.

P2356 adds step 3 ("Who is this workspace for?", offer `account_owner_type`) and step 5 ("How does this business
make money?", offer `revenue_model`, several picks allowed): a click or a typed reply is matched HERE, by the
server's line and the neutral option id, with no call to the match server. A reply this module cannot place falls
through to the normal path, which sees the same translated question and labels (`steps_localize.py`).

Called from `answer_captures.py` BEFORE normal step matching, like every sibling capture.
FAIL-SAFE: returns False (not mine) on anything unexpected; never raises.
"""
from __future__ import annotations

import offer_lines
import step_order
import step_recorder_website as website_recorder
import step_state
import steps_manifest

WEBSITE_STEP_ID = "website"
# step id -> (offer id, True when the customer may pick several)
_QUESTION_STEPS = {"account_owner_type": ("account_owner_type", False), "revenue_model": ("revenue_model", True)}
_LIST_SEPARATORS = ",;،、"


def _record(session_id: str, step_id: str, value: str) -> None:
    step_state.set_human_answer(session_id, step_id, value)
    if step_id == WEBSITE_STEP_ID:
        website_recorder.handle_website_question_answer(session_id, value)


def _picked_labels(offer: dict, answer: str) -> list[str] | None:
    """Every option whose label is inside a clicked answer (a label may hold commas, so never split on them).
    None when something other than separators is left over, or nothing matched."""
    rest, found = answer.casefold(), set()
    for opt in sorted(offer["options"], key=lambda o: -len(o["label"])):
        label = opt["label"].strip().casefold()
        if label and label in rest:
            found.add(opt["value"])
            rest = rest.replace(label, " ")
    if not found or any(ch.isalnum() for ch in rest):
        return None
    return [o["value"] for o in offer["options"] if o["value"] in found]


def _picked_typed(offer: dict, message: str, several: bool) -> str | list[str] | None:
    whole = offer_lines.match(offer, message)
    if whole is not None:
        return [whole] if several else whole
    if not several:
        return None
    for sep in _LIST_SEPARATORS[1:]:
        message = message.replace(sep, _LIST_SEPARATORS[0])
    hits = [offer_lines.match(offer, part) for part in message.split(_LIST_SEPARATORS[0]) if part.strip()]
    if not hits or None in hits:
        return None
    return list(dict.fromkeys(hits))


def _capture_question_step_click(session_id: str, question_text: str, label: str) -> bool:
    for step_id, (offer_id, several) in _QUESTION_STEPS.items():
        offer = offer_lines.get(session_id, offer_id)
        if offer is None or offer["say"] != question_text:
            continue
        value = _picked_labels(offer, label) if several else offer_lines.match_clicked(offer, label)
        if value is None:
            return False
        step_state.set_human_answer(session_id, step_id, value)
        return True
    return False


def _capture_question_step_typed(session_id: str, message: str) -> bool:
    """Only while step 3 / step 5 is the customer's current step and still unanswered."""
    state = step_state.read_state(session_id)
    current = step_order.first_unfinished(steps_manifest.load_steps(session_id), state)
    if current is None or current["id"] not in _QUESTION_STEPS:
        return False
    step_id = current["id"]
    if step_id in state["human_answers"] or step_id in state["steps_passed"]:
        return False
    offer_id, several = _QUESTION_STEPS[step_id]
    offer = offer_lines.get(session_id, offer_id)
    value = _picked_typed(offer, message, several) if offer is not None else None
    if value is None:
        return False
    step_state.set_human_answer(session_id, step_id, value)
    return True


def try_capture_ask_user_answer(session_id: str, question_text: str, label: str) -> bool:
    try:
        if _capture_question_step_click(session_id, question_text, label):
            return True
        found = offer_lines.find_by_question(session_id, question_text)
        if found is None:
            return False
        _, offer = found
        value = offer_lines.match_clicked(offer, label)
        if value is None:
            return False
        _record(session_id, offer["step"], value)
        return True
    except Exception:
        return False


def try_capture_typed_answer(session_id: str, message: str) -> bool:
    """Typed fallback: only while the step is the customer's current step (a stray "1" long before it must
    never be read as its answer), and only a label, an `also` word, an id or an option number."""
    try:
        if _capture_question_step_typed(session_id, message):
            return True
        found = offer_lines.find_for_step(session_id, WEBSITE_STEP_ID)
        if found is None:
            return False
        state = step_state.read_state(session_id)
        if not website_recorder.typed_answer_waiting(steps_manifest.load_steps(session_id), state):
            return False
        value = offer_lines.match(found[1], message)
        if value is None:
            return False
        _record(session_id, WEBSITE_STEP_ID, value)
        return True
    except Exception:
        return False
