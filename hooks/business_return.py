#!/usr/bin/env python3
"""Step 7's "come back when ready" return offer (RMP-194 P2, design doc Part
4 point 5). Shape copied from `website_return.py`'s reoffer case, split into
its own module for the same reason every sibling reminder module is split
out (keeps `priority_reminders.py` a thin chain, not a growing file).

`business_ready_poll.py` (a DIFFERENT `UserPromptSubmit` hook, possibly run
in parallel this same turn -- see that module's docstring) writes to its OWN
file, never this one. This module only ever READS that file, plus its own
`business_review_offered` flag through the shared `connection_state` file --
safe, because this module is only ever called from the SAME synchronous
reminder chain (`checklist_recorder.build_step_reminder` ->
`priority_reminders.first_priority_reminder`) every other reminder module
already writes through, never from a second concurrent hook invocation.

ONCE PER SESSION (design doc): the offer is shown once; whether the answer
is "Yes" or "Later", it never repeats THIS session. A fresh session gets a
fresh `connection_state` file (`SessionStart` resets it), so "Later" is
naturally re-offered next session -- no separate re-offer flag needed, same
reasoning `website_return.py`'s own module docstring gives for its case.

FAIL-SAFE: nothing here may crash a hook, same convention as every sibling
module.
"""
from __future__ import annotations

from typing import Any

import business_ready_poll
import connection_state as cs
import offer_lines
import planner_mode_state
import step_recorder_business_review as business_review_recorder

_OFFERED_KEY = "business_review_offered"


def _was_offered(session_id: str) -> bool:
    raw = cs.read_raw(session_id).get(_OFFERED_KEY)
    return raw if isinstance(raw, bool) else False


# RMP-198 (live 2026-09-30): the bare "Start the ... skill now." invited the
# model to announce it ("Next, the business check. Loading that step.").
START_INSTRUCTION = (
    "Start the confirm-your-business skill now. Say nothing about it: "
    "no 'next step', no 'loading', no step name."
)


def _offer_of(ready_state: dict[str, Any]) -> dict[str, Any] | None:
    """The server's step 7 offer (line + buttons, owner's language) as an `offer_lines` offer."""
    return offer_lines.clean_offer({"say": ready_state.get("say"), "options": ready_state.get("opts")})


def _start_pending(session_id: str) -> bool:
    """True once, right after "Yes, show me" was picked -- tells the model
    to start the `confirm-your-business` skill. Consumed (cleared) the first
    time this is shown, same one-shot convention as `website_return.py`'s
    reread instruction."""
    raw = cs.read_raw(session_id).get("business_review_start_pending")
    if raw is True:
        cs.write_patch(session_id, {"business_review_start_pending": False})
        return True
    return False


def build_return_reminder(session_id: str, state: dict[str, Any]) -> dict[str, Any] | None:
    """Returns the server-written offer question, the one-shot "start now"
    instruction after "Yes" was picked, or `None`. Format matches every
    other priority reminder: `{"instruction": <prose>}`. The offer question
    consumes nothing on its own -- `try_capture_*` below is what marks it
    spent, once the customer actually answers it, exactly like
    `website_return.build_return_reminder`'s reoffer case."""
    if "business_review" in state["ticked"]:
        return None
    if business_review_recorder.is_started(session_id):
        # Live salon transcript, 2026-09-28: the review can start WITHOUT
        # ever going through this offer (this session's own flow reached it
        # straight from next_actions/the skill) -- once it has, "come back
        # when ready?" is stale and must never interrupt the conversation
        # already under way (it fired between the top-earner answer and the
        # summary in the live transcript). See step_recorder_business_
        # review.py's own docstring.
        return None
    if planner_mode_state.is_drive(session_id):
        # Drive mode: `next_actions` itself brings step 7 up when it is
        # ready (see `business_ready_poll._should_poll`'s own note), so this
        # offer stays dormant -- never two prompts for the same thing.
        return None
    if _start_pending(session_id):
        return {"instruction": START_INSTRUCTION}
    if _was_offered(session_id):
        return None
    ready_state = business_ready_poll.read_state(session_id)
    if not ready_state["ready"] or not ready_state["say"] or not ready_state["opts"]:
        return None
    opts = ready_state["opts"]
    labels = [opt.get("label") for opt in opts if isinstance(opt, dict)]
    options_text = " / ".join(f'"{label}"' for label in labels if isinstance(label, str))
    return {
        "instruction": (
            f'Ask the customer with AskUserQuestion: "{ready_state["say"]}" '
            f'Options: {options_text}'
        )
    }


def _consume(session_id: str, matched_value: str | None) -> bool:
    cs.write_patch(session_id, {_OFFERED_KEY: True})
    if matched_value == "show_me":
        cs.write_patch(session_id, {"business_review_start_pending": True})
    return True


def handle_reoffer_answer(session_id: str, question_text: str, answer_label: str) -> bool:
    ready_state = business_ready_poll.read_state(session_id)
    if not ready_state["ready"] or _was_offered(session_id):
        return False
    if question_text != ready_state.get("say"):
        return False
    matched_value = offer_lines.match_clicked(_offer_of(ready_state), answer_label)
    return _consume(session_id, matched_value)


def handle_reoffer_answer_typed(session_id: str, typed_answer: str) -> bool:
    """Headless fallback: a label, an `also` word, an id or an option number (all server-written, in the
    owner's language) -- an unrelated typed reply never matches by accident."""
    ready_state = business_ready_poll.read_state(session_id)
    if not ready_state["ready"] or _was_offered(session_id):
        return False
    matched_value = offer_lines.match(_offer_of(ready_state), typed_answer)
    if matched_value is None:
        return False
    return _consume(session_id, matched_value)


def try_capture_ask_user_answer(session_id: str, question_text: str, label: str) -> bool:
    return handle_reoffer_answer(session_id, question_text, label)


def try_capture_typed_answer(session_id: str, message: str) -> bool:
    return handle_reoffer_answer_typed(session_id, message)
