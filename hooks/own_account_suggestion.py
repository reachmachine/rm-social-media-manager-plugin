#!/usr/bin/env python3
"""RMP-161 -- the website->Instagram suggestion becomes a real step-4 answer.

Live bug, 2026-09-26: `open_workspace`/`get_resume_checklist` now returns the
`own_instagram_account` step's `suggested_handle` (`suggestion_source:
"website"`) once RMP-161's server-side fix landed (`2a3c06a55`) -- the bio
link on the customer's own read website pointed at an Instagram handle with
no own account on file yet (dev: `detailssalonmarinette`). `own-instagram-
account/SKILL.md`, "no `detail`, but `suggested_handle` is set" then asks
the customer "Is **@<handle>** your Instagram account?" with "Yes, that's
my account" / "No, it's a different one". But nothing ever recorded the
server's suggestion as a step-4 human answer -- a "Yes" reply had nowhere to
land, so the model tried to self-authorise the add (`add_to_watchlist` with
the suggested handle as both `handles` and `self_handle`) and
`step_gate_own_account.check_own_account_add` correctly denied it (only a
handle already stored in `human_answers["own_instagram_account"]` may ever
be added there) -- the chat fell back to asking the customer to type the
handle, and the suggestion was useless.

THE SERVER decides (RMP-76): this module never invents a suggestion, it
only turns the ONE the server already sent into: state (this session
remembers a pending suggested handle), and the AskUserQuestion/typed-reply
capture that turns a real "Yes" into the SAME `human_answers["own_
instagram_account"]` write `step_recorder.handle_ask_user_question`/
`handle_typed_answer` would have made for a typed handle -- so `step_gate_
own_account.check_own_account_add`'s existing gate (UNCHANGED) allows the
add exactly as if the customer had typed the handle themselves. A "No" (or
any other reply) discards the suggestion; the normal "ask for the handle"
flow (section 2 of the skill) then applies, and `check_own_account_add`
still refuses any handle that never became the stored human answer -- a
model can never self-authorise a DIFFERENT account this way.

`note_checklist_entry` also owns the pre-existing "a fresh self row is
already known" detail check (moved here, unchanged behaviour, from
`checklist_recorder.handle_get_resume_checklist` -- that file was one line
under its 300-line cap, and both checks read the SAME `own_instagram_
account` checklist entry, so one call site replaces two).

STATE lives under ONE raw `connection_state` key, `own_account_suggested_
handle` (read/written via `connection_state.read_raw`/`write_patch`
directly, kept OUT of `step_state.read_state`'s own typed shape --
`step_state.py` is at the 300-line limit, same reasoning as `own_account_
not_found.py`'s own docstring). Shape, safe default for anything missing or
wrong-typed:
    {"handle": str, "source": "website"} | None

Cleared: on every workspace switch (`step_recorder_workspace.handle_set_
active_workspace`, same per-workspace rule as `own_account_not_found.
clear`), on every fresh `get_resume_checklist`/`open_workspace` read once
the account is known or already answered (`note_checklist_entry` itself),
and the moment a "Yes"/"No" answer is captured either way (`_apply_answer`)
-- a stale suggestion must never outlive its own question.

FAIL-SAFE: nothing here may crash a hook -- same convention as every
sibling module.
"""
from __future__ import annotations

from typing import Any

import connection_state as cs
import offer_lines
import own_account_mismatch
import own_account_not_found
import step_gate_own_account as own_account_gate
import step_state

STEP_ID = "own_instagram_account"

OFFER_ID = "instagram_suggested"   # the SERVER's question and buttons (ids `yes` / `no`), RMP-281 P2359

_DEFAULT_STATE: dict[str, Any] = {"suggested": None}


def read_state(session_id: str) -> dict[str, Any]:
    """The safe shape, with the safe default for anything missing or wrong-typed."""
    raw = cs.read_raw(session_id).get("own_account_suggested_handle")
    result = dict(_DEFAULT_STATE)
    if not isinstance(raw, dict):
        return result
    handle = raw.get("handle")
    if isinstance(handle, str) and handle and raw.get("source") == "website":
        result["suggested"] = {"handle": handle, "source": "website"}
    return result


def _save(session_id: str, suggested: dict[str, Any] | None) -> None:
    cs.write_patch(session_id, {"own_account_suggested_handle": suggested})


def clear(session_id: str) -> None:
    """A workspace switch, the suggestion no longer applying (see
    `note_checklist_entry`), or a captured answer (see `_apply_answer`) --
    same per-workspace/per-question lifecycle as `own_account_not_found.
    clear`."""
    _save(session_id, None)


clear_on_new_handle = clear


def suggestion_question_text(session_id: str, handle: str) -> str | None:
    """The question the SERVER wrote (`offers.instagram_suggested.say`, `{handle}` filled), rebuilt from the STORED
    handle so the AskUserQuestion capture can match it back. None when the server sent no such offer (the plugin
    keeps no English of its own: a missing line means this hook skips)."""
    offer = offer_lines.get(session_id, OFFER_ID)
    return None if offer is None else offer["say"].replace("{handle}", handle)


def note_checklist_entry(session_id: str, entry: dict[str, Any]) -> None:
    """Called from `checklist_recorder.handle_get_resume_checklist` for the
    `own_instagram_account` checklist entry, every `get_resume_checklist`/
    `open_workspace` read.

    A known `detail` (a real handle already on file) means there is nothing
    to suggest -- runs the pre-existing "already known" tick (RMP-23,
    founder decision 2) and clears any stale suggestion. Otherwise, a
    website-sourced `suggested_handle` is stored for the AskUserQuestion/
    typed capture below; anything else (no suggestion, or a suggestion from
    a source this module doesn't recognise) clears it. Also clears (does
    NOT re-suggest) once the customer's own answer is already on file this
    session (a captured "Yes", or a real add already recorded) -- a later
    checklist read must never reopen a question that has already been
    answered."""
    detail = entry.get("detail")
    if isinstance(detail, dict) and isinstance(detail.get("handle"), str) and detail["handle"]:
        step_state.set_own_account_handle(session_id, detail["handle"])
        step_state.set_last_known_detail(session_id, detail)
        current = step_state.read_state(session_id)
        # Only a NOT-yet-ticked step becomes "already_known" here. When the
        # server already shows state "done" (a real tick from an earlier
        # session), leave it to the done-branch in `handle_get_resume_
        # checklist`, so the local `how` stays equal to the server's (e.g.
        # "answered").
        if STEP_ID not in current["steps_passed"] and entry.get("state") != "done":
            step_state.mark_step_passed(session_id, STEP_ID, "already_known")
        clear(session_id)
        return

    state = step_state.read_state(session_id)
    if state["own_account_handle"] or state["human_answers"].get(STEP_ID):
        clear(session_id)
        return
    if entry.get("suggestion_source") != "website":
        clear(session_id)
        return
    handle = own_account_gate.normalize_handle(entry.get("suggested_handle"))
    if not isinstance(handle, str) or not handle:
        clear(session_id)
        return
    _save(session_id, {"handle": handle, "source": "website"})


# --------------------------------------------------- typed/clicked answer --

def _apply_answer(session_id: str, suggested: dict[str, Any], answer: str | None) -> bool:
    """`answer` is the server's option id (`yes` / `no`), or None when the reply meant neither."""
    if answer not in ("yes", "no"):
        return False
    if answer == "yes":
        step_state.set_human_answer(session_id, STEP_ID, suggested["handle"])
        # Same two clears `step_recorder.handle_ask_user_question`/
        # `handle_typed_answer` run for every fresh own-account handle --
        # this capture bypasses that normal path, so it must run them too.
        own_account_mismatch.clear_on_new_handle(session_id)
        own_account_not_found.clear_on_new_handle(session_id)
    clear(session_id)
    return True


def try_capture_ask_user_answer(session_id: str, question_text: str, label: str) -> bool:
    """True if this WAS our own suggestion question -- caller must not also
    run normal step matching in that case, whether or not the label
    actually resolved to yes/no. The question text is dynamic (it carries
    the suggested handle), so it is rebuilt from the STORED handle and
    compared -- never matched against a fixed constant like the sibling
    mismatch/not-found questions."""
    suggested = read_state(session_id)["suggested"]
    if suggested is None:
        return False
    if question_text != suggestion_question_text(session_id, suggested["handle"]):
        return False
    _apply_answer(session_id, suggested, offer_lines.match_clicked(offer_lines.get(session_id, OFFER_ID), label))
    return True


def try_capture_typed_answer(session_id: str, message: str) -> bool:
    """True only if this typed reply WAS captured as the suggestion answer
    -- caller must skip normal step matching in that case. Unlike the
    `AskUserQuestion` path, an unrelated typed reply must still fall
    through to normal matching (a bare "yes" only counts while a suggestion
    is genuinely pending -- `read_state` returns `None` the instant it isn't,
    so a bare "yes" answering some other, later question can never be
    misread as this one)."""
    suggested = read_state(session_id)["suggested"]
    if suggested is None:
        return False
    return _apply_answer(session_id, suggested, offer_lines.match(offer_lines.get(session_id, OFFER_ID), message))
