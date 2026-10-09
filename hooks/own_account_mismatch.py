#!/usr/bin/env python3
"""RMP-23 -- founder decision 6 (2026-09-24): "get confirmation from the
user and then add if there is a mismatch."

Spec: `docs/plugin-v2/04-own-instagram-account.md`, "The own account does
not fit the business". The server's own-account-only preview
(`backend/app/mcp/_self_add_preview.py`) now tells the plugin when the
customer's own account fails the authenticity or fit screen, via
`add_to_watchlist`'s `screened` field. This module is the ONE place that
turns that into: state (this session knows a mismatch is pending), a gate
(the `include_flagged=true` skip is earned only by a real "yes" to exactly
this mismatch), two session-event kinds, and a checklist reminder.

STATE lives in `step_state.py` (`own_account_mismatch`,
`own_account_mismatch_answer`, `own_account_mismatch_logged`,
`own_account_answer_logged`) -- this module reads/writes it through
`step_state.py`/`step_state_own_account.py`, never `connection_state`
directly.

COORDINATOR DECISION (2026-09-24): a "yes" answers BOTH checks (fit and
authenticity) at once, because the customer is answering exactly what was
shown to them in one message -- there is no second, separate yes for the
other check. A future prompt can split them if the founder wants
authenticity kept strict.

Handles are compared through `step_gate_own_account.normalize_handle`
(`strip().lstrip("@").lower()`) ONLY -- never a second helper, so this
module and the server always agree on what "the same handle" means.
"""
from __future__ import annotations

import re
from typing import Any

import connection_state as cs
import deny_lines
import offer_lines
import step_gate_own_account as own_account_gate
import step_state
import step_state_own_account as own_account_state

OFFER_ID = "own_account_mismatch"   # P2361: the SERVER's question and buttons (ids `yes` / `no`); the plugin holds no words

MISMATCH_EVENT_KINDS: frozenset[str] = frozenset(
    {"own_account_mismatch_shown", "own_account_mismatch_answered"},
)

_ASK_FIRST_REASON = "ask_account_right_first"
_EVENT_MISMATCH_REASON = "event_mismatch"
_EVENT_NO_ANSWER_REASON = "waiting_reply_1_or_2"
_MAX_REASON_LEN = 200


def _deny(reason_id: str, **fill: object) -> dict:
    return deny_lines.deny_id(reason_id, **fill)


# --------------------------------------------------------------- the gate --

def check_include_flagged(tool_input: dict[str, Any], state: dict[str, Any]) -> dict | None:
    """`add_to_watchlist`'s `include_flagged=true` skip is earned only by a
    real "yes" to exactly the mismatch the customer was shown -- never on a
    preview (the preview must run WITHOUT the skip, so the flag is found
    first), never without a stored mismatch, never for a different handle,
    never without `own_account_mismatch_answer == "yes"`."""
    if tool_input.get("include_flagged") is not True:
        return None
    if tool_input.get("confirm") is not True:
        return _deny(_ASK_FIRST_REASON)
    mismatch = state["own_account_mismatch"]
    if mismatch is None:
        return _deny(_ASK_FIRST_REASON)
    if own_account_gate.normalize_handle(tool_input.get("self_handle")) != mismatch.get("handle"):
        return _deny(_ASK_FIRST_REASON)
    if state["own_account_mismatch_answer"] != "yes":
        return _deny(_ASK_FIRST_REASON)
    return None


# ------------------------------------------------------------- the events --

def check_mismatch_event(kind: str, tool_input: dict[str, Any], state: dict[str, Any]) -> dict | None:
    """`own_account_mismatch_shown` -> `detail` must equal the stored
    mismatch exactly. `own_account_mismatch_answered` -> `detail` must equal
    `{handle, answer}` from the stored mismatch/answer, and an answer must
    actually be stored. Same "last is None -> deny" shape as
    `step_gate_own_account.check_profile_refreshed_event` -- a `detail:
    null` payload must never pass a bare `!=` comparison by accident."""
    mismatch = state["own_account_mismatch"]
    if mismatch is None:
        return _deny(_EVENT_MISMATCH_REASON)
    if kind == "own_account_mismatch_shown":
        if tool_input.get("detail") != mismatch:
            return _deny(_EVENT_MISMATCH_REASON)
        return None
    answer = state["own_account_mismatch_answer"]
    if answer is None:
        return _deny(_EVENT_NO_ANSWER_REASON)
    if tool_input.get("detail") != {"handle": mismatch["handle"], "answer": answer}:
        return _deny(_EVENT_MISMATCH_REASON)
    return None


# ------------------------------------------------------------- detection --

def note_preview_result(session_id: str, tool_input: dict[str, Any], data: dict[str, Any]) -> None:
    """Called from the PostToolUse recorder after an own-account-only
    preview (`requires_confirmation: true`) returns. Sets the mismatch when
    the `screened` entry for the typed handle is flagged/off; a clean
    preview does nothing (spec: "a clean preview -> not set")."""
    handles = tool_input.get("handles")
    self_handle = own_account_gate.normalize_handle(tool_input.get("self_handle"))
    if not isinstance(handles, list) or len(handles) != 1 or not isinstance(self_handle, str) or not self_handle:
        return
    if own_account_gate.normalize_handle(handles[0]) != self_handle:
        return
    screened = data.get("screened")
    if not isinstance(screened, list):
        return
    entry = next(
        (e for e in screened if isinstance(e, dict)
         and own_account_gate.normalize_handle(e.get("handle")) == self_handle),
        None,
    )
    if entry is None:
        return
    if entry.get("verdict") != "flagged" and entry.get("niche_fit_verdict") != "off":
        return
    reasons = entry.get("reasons")
    reason = "; ".join(r for r in reasons if isinstance(r, str)) if isinstance(reasons, list) else ""
    reason = reason[:_MAX_REASON_LEN] or "This account did not pass the check for this workspace."
    existing = step_state.read_state(session_id)["own_account_mismatch"]
    if existing is not None and existing.get("handle") == self_handle:
        return  # RMP-23: the price re-preview after the customer's yes must not undo it
    own_account_state.set_own_account_mismatch(session_id, self_handle, reason)


def clear_on_new_handle(session_id: str) -> None:
    """A fresh own-account handle was just captured (`step_recorder.py`,
    both the `AskUserQuestion` and typed paths) -- whatever mismatch state
    applied to the OLD handle no longer means anything."""
    own_account_state.clear_own_account_mismatch(session_id)


# --------------------------------------------------- typed/clicked answer --

# RMP-23 (live 2026-09-29): the chat prints "1. <yes> / 2. <no> -- Type 1 or 2", and a typed "1" was ignored. The two options
# are ALWAYS in the server's order, so a typed number is safe to read: "1", "1.", "1)", "#1", or the whole numbered line.
# P2361: the words come from the server's offer (label, `also`, id, option number); the plugin keeps only this number SYNTAX.
_NUMBER_LINE_RE = re.compile(r"^#?\s*(\d)\s*[.):]\s*(.*)$")


def _answer_of(session_id: str, text: str) -> str | None:
    """The server's option id (`yes` / `no`) a reply means, or None."""
    offer = offer_lines.get(session_id, OFFER_ID)
    if offer is None or not isinstance(text, str):
        return None
    key = text.strip()
    answer = offer_lines.match(offer, key.lstrip("#"))
    if answer is not None:
        return answer
    line = _NUMBER_LINE_RE.match(key)
    if line is None:
        return None
    by_number = offer_lines.match(offer, line.group(1))
    rest = line.group(2).strip()   # a numbered LINE ("1. <label>") counts only when the text after the number names the same option
    return by_number if by_number is not None and (not rest or offer_lines.match(offer, rest) == by_number) else None


def try_capture_ask_user_answer(session_id: str, question_text: str, label: str) -> bool:
    """True if this WAS our own mismatch question (the server's line, `offers.own_account_mismatch.say`) -- caller must not
    also run normal step matching in that case, whether or not the label actually resolved to yes/no."""
    offer = offer_lines.get(session_id, OFFER_ID)
    if offer is None or question_text != offer["say"]:
        return False
    _try_capture(session_id, label)
    return True


def try_capture_typed_answer(session_id: str, message: str) -> bool:
    """True only if this typed reply WAS captured as the mismatch answer --
    caller must skip normal step matching in that case. Unlike the
    `AskUserQuestion` path, an unrelated typed reply must still fall
    through to normal matching."""
    return _try_capture(session_id, message)


def _try_capture(session_id: str, text: str) -> bool:
    state = step_state.read_state(session_id)
    if state["own_account_mismatch"] is None or state["own_account_mismatch_answer"] is not None:
        return False
    answer = _answer_of(session_id, text)
    if answer is None:
        return False
    own_account_state.set_own_account_mismatch_answer(session_id, answer)
    return True


# --------------------------------------------------------------- reminder --

def build_reminder(session_id: str, state: dict[str, Any]) -> dict[str, Any] | None:
    """Checked BEFORE the per-step loop (`checklist_recorder.
    build_step_reminder`), so the log entry comes right after the thing it
    records: mismatch shown but not logged first, then the answer once
    logged too."""
    mismatch = state["own_account_mismatch"]
    if mismatch is None or state["workspace"] is None:
        return None
    workspace_id = state["workspace"]["id"]
    if not state["own_account_mismatch_logged"]:
        return {
            "call": "record_session_event",
            "payload": {
                "client_session_id": session_id, "kind": "own_account_mismatch_shown",
                "workspace_id": workspace_id, "detail": mismatch,
            },
        }
    answer = state["own_account_mismatch_answer"]
    if answer is not None and not state["own_account_answer_logged"]:
        return {
            "call": "record_session_event",
            "payload": {
                "client_session_id": session_id, "kind": "own_account_mismatch_answered",
                "workspace_id": workspace_id, "detail": {"handle": mismatch["handle"], "answer": answer},
            },
        }
    return None


# ------------------------------------------------------------ event -> log --

def handle_mismatch_event_recorded(session_id: str, kind: str, detail: Any) -> None:
    """A successful `record_session_event` for one of our two kinds spends
    the reminder -- one shown log, one answered log, same "spend the pick"
    shape every other recorder in this plugin uses."""
    state = step_state.read_state(session_id)
    mismatch = state["own_account_mismatch"]
    if mismatch is None:
        return
    if kind == "own_account_mismatch_shown" and detail == mismatch:
        own_account_state.mark_own_account_mismatch_logged(session_id)
    elif kind == "own_account_mismatch_answered" and detail == {
        "handle": mismatch["handle"], "answer": state["own_account_mismatch_answer"],
    }:
        own_account_state.mark_own_account_answer_logged(session_id)
