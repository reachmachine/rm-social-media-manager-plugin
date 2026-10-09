#!/usr/bin/env python3
"""RMP-66 -- founder decision (2026-09-24): "The step 4 Instagram account is
cross-checked against the business facts. A mismatch -> warn and ask."

Spec: `docs/plugin-v2/06-website-and-business-knowledge.md`, "Wave 2 design"
-> "Facts" (Instagram cross-check). Same SHAPE as step 4's own
`own_account_mismatch.py` (RMP-23, founder decision 6) -- copied structure,
not code, per this prompt's own instruction.

THE AGENT decides the mismatch itself, by reading the step 4 account (bio
link, name, bio, location) against the website facts -- `your-website`
SKILL.md's own "Check the Instagram account" section. There is no server-
side screening step here (unlike step 4's `add_to_watchlist` preview): this
module's job starts once the agent calls `record_session_event(kind=
"website_mismatch_shown")` on its own initiative. From there it gates the
call (only while `website` is the customer's current step, and only while
no mismatch is already pending), records it as pending, captures the
customer's yes/no answer through the same `AskUserQuestion`/typed-reply
paths step 4 uses, gates the matching `..._answered` event against that
REAL captured answer (never whatever the model claims), reminds the model
to log it, and denies the step 6 tick while a shown mismatch has no logged
answer yet.

STATE lives under ONE raw `connection_state` key, `website_mismatch`
(read/written straight through `connection_state.read_raw`/`write_patch`,
kept OUT of `step_state.read_state`'s own typed shape, exact-equality-
asserted in `test_step_state.py`) -- same pattern as `step_recorder_revenue.
py`'s `revenue_progress` (`step_state.py` is at the 300-line limit, so a new
key there would need a split first; this needs no new key at all). Shape,
safe defaults for anything missing or wrong-typed:
    {"mismatch": {"handle": str, "reason": str} | None,
     "answer": "yes" | "no" | None,
     "answered_logged": bool}
Cleared by `step_recorder_workspace.handle_set_active_workspace` on every
workspace switch (a mismatch belongs to the workspace it was raised in,
same per-workspace rule `step_state.reset_for_new_workspace` already
applies to the own-account pair) and by `handle_mismatch_event_recorded`
once the answer is logged (RMP-66: "After ..._answered is logged -> clear").

FAIL-SAFE: nothing here may crash a hook -- same convention as every
sibling module.
"""
from __future__ import annotations

import json
from typing import Any

import connection_state as cs
import deny_lines
import offer_lines
from payload_util import tool_args
import step_recorder_website as website_step
import steps_manifest

# RMP-281 P2272: the question and its two buttons are written by the SERVER in the owner's language and
# arrive in the `record_session_event` reply as `offers.website_mismatch` (ids `yes` / `no`, see
# offer_lines.py). No English text here.
OFFER_ID = "website_mismatch"

MISMATCH_EVENT_KINDS: frozenset[str] = frozenset(
    {"website_mismatch_shown", "website_mismatch_answered"},
)

# RMP-291 P2320: reason ids; the owner-language texts come from the server (`deny_lines`).
_ASK_FIRST_REASON = "ask_instagram_first"
_EVENT_MISMATCH_REASON = "event_mismatch"
_MAX_REASON_LEN = 200

_DEFAULT_PROGRESS: dict[str, Any] = {
    "mismatch": None, "answer": None, "answered_logged": False, "read_finished_with_pages": False,
}


def _deny(reason_id: str, session_id: str = "") -> dict:
    return deny_lines.deny(deny_lines.reason(session_id, reason_id))   # RMP-291 P2320: the text is the server's


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


# ---------------------------------------------------------------- state --

def read_progress(session_id: str) -> dict[str, Any]:
    """The safe shape, with the safe default for anything missing or wrong-typed."""
    full = cs.read_raw(session_id)
    raw = full.get("website_mismatch")
    result = dict(_DEFAULT_PROGRESS)
    # The gate's normalised `state` drops raw keys, so this per-session flag
    # (set by step_recorder_website on a finished read with pages) is read
    # here, from the raw file, where the gate can see it (RMP-66 live bug).
    result["read_finished_with_pages"] = full.get("website_read_finished_with_pages") is True
    if not isinstance(raw, dict):
        return result
    mismatch = raw.get("mismatch")
    handle_ok = isinstance(mismatch, dict) and isinstance(mismatch.get("handle"), str) and mismatch.get("handle")
    if handle_ok and isinstance(mismatch.get("reason"), str):
        result["mismatch"] = {"handle": mismatch["handle"], "reason": mismatch["reason"]}
    if raw.get("answer") in ("yes", "no"):
        result["answer"] = raw["answer"]
    if isinstance(raw.get("answered_logged"), bool):
        result["answered_logged"] = raw["answered_logged"]
    return result


def _save_progress(session_id: str, progress: dict[str, Any]) -> None:
    cs.write_patch(session_id, {"website_mismatch": progress})


def clear(session_id: str) -> None:
    """A workspace switch clears whatever mismatch belonged to the PREVIOUS
    workspace -- called from `step_recorder_workspace.handle_set_active_
    workspace`, same per-workspace rule as the own-account pair."""
    _save_progress(session_id, dict(_DEFAULT_PROGRESS))


# ---------------------------------------------------------------- the gate --

def check_mismatch_event(
    kind: str, tool_input: dict[str, Any], state: dict[str, Any], progress: dict[str, Any], session_id: str = "",
) -> dict | None:
    """`website_mismatch_shown` is allowed only while `website` is the
    customer's current step (`step_recorder_website.typed_answer_waiting` --
    the SAME "is step 6 actually current" test that module already uses for
    a typed reply, reused here rather than a second definition), and only
    while no mismatch is already pending. `website_mismatch_answered` is
    allowed only once an answer has actually been CAPTURED from the
    customer (never invented by the model) and `detail` equals exactly
    `{handle, answer}` from that stored mismatch/answer -- same "last is
    None -> deny" shape as `own_account_mismatch.check_mismatch_event`, so a
    `detail: null` payload never passes a bare `!=` comparison by accident."""
    if kind == "website_mismatch_shown":
        if progress["mismatch"] is not None:
            return _deny(_EVENT_MISMATCH_REASON, session_id)
        if not (
            website_step.typed_answer_waiting(steps_manifest.load_steps(), state)
            or _step6_just_finished_after_a_read(state, progress)
        ):
            return _deny(_EVENT_MISMATCH_REASON, session_id)
        detail = tool_input.get("detail")
        handle = detail.get("handle") if isinstance(detail, dict) else None
        reason = detail.get("reason") if isinstance(detail, dict) else None
        if not isinstance(handle, str) or not handle:
            return _deny(_EVENT_MISMATCH_REASON, session_id)
        if not isinstance(reason, str) or not reason or len(reason) > _MAX_REASON_LEN:
            return _deny(_EVENT_MISMATCH_REASON, session_id)
        return None
    mismatch = progress["mismatch"]
    answer = progress["answer"]
    if mismatch is None or answer is None or tool_input.get("detail") != {
        "handle": mismatch["handle"], "answer": answer,
    }:
        return _deny(_EVENT_MISMATCH_REASON, session_id)
    return None


def _step6_just_finished_after_a_read(state: dict[str, Any], progress: dict[str, Any]) -> bool:
    """Since RMP-92/96 step 6 is marked passed the moment the facts are saved
    (`save_business_facts` / `get_next_fact_task` done) -- BEFORE the skill's
    Instagram cross-check runs. So the cross-check must also be allowed when
    step 6 was passed "answered" in THIS session right after a website read
    with pages (live 2026-09-25: @nasa vs a hair salon -- the mismatch was
    found but `website_mismatch_shown` was refused twice). `steps_passed` and
    the read flag are both per-session keys, so a stale earlier session can
    never unlock it."""
    return (
        state.get("steps_passed", {}).get("website") == "answered"
        and progress.get("read_finished_with_pages") is True
    )


def check_tick(tool_input: dict[str, Any], session_id: str) -> dict | None:
    """`record_checklist_step("website", "done", ...)` is denied while a
    mismatch has been shown but not yet answered-and-logged (RMP-66) --
    once logged, `handle_mismatch_event_recorded` has already cleared
    `mismatch` back to None, so this reads as allowed again."""
    if tool_input.get("step_id") != "website" or tool_input.get("state") != "done":
        return None
    if read_progress(session_id)["mismatch"] is not None:
        return _deny(_ASK_FIRST_REASON, session_id)
    return None


# --------------------------------------------------- typed/clicked answer --

def _id_to_answer(value: str | None) -> str | None:
    return value if value in ("yes", "no") else None


def try_capture_ask_user_answer(session_id: str, question_text: str, label: str) -> bool:
    """True if this WAS our own mismatch question -- caller must not also
    run normal step matching in that case, whether or not the label
    actually resolved to yes/no."""
    offer = offer_lines.get(session_id, OFFER_ID)
    if offer is None or question_text != offer["say"]:
        return False
    _try_capture(session_id, offer_lines.match_clicked(offer, label))
    return True


def try_capture_typed_answer(session_id: str, message: str) -> bool:
    """True only if this typed reply WAS captured as the mismatch answer --
    caller must skip normal step matching in that case. Unlike the
    `AskUserQuestion` path, an unrelated typed reply must still fall through
    to normal matching."""
    return _try_capture(session_id, offer_lines.match(offer_lines.get(session_id, OFFER_ID), message))


def _try_capture(session_id: str, picked: str | None) -> bool:
    progress = read_progress(session_id)
    if progress["mismatch"] is None or progress["answer"] is not None:
        return False
    answer = _id_to_answer(picked)
    if answer is None:
        return False
    _save_progress(session_id, {**progress, "answer": answer})
    return True


# --------------------------------------------------------------- reminder --

def pending_event_reminder(session_id: str, state: dict[str, Any]) -> dict[str, Any] | None:
    """The exact `record_session_event` call this session owes for
    `website_mismatch_answered`, once the customer has answered but the log
    entry has not landed yet. `website_mismatch_shown` is never reminded
    for -- the agent calls it on its own initiative (the skill), not via a
    hook nudge, so there is nothing to hand back before that first call."""
    progress = read_progress(session_id)
    mismatch = progress["mismatch"]
    answer = progress["answer"]
    if mismatch is None or answer is None or progress["answered_logged"] or state["workspace"] is None:
        return None
    return {
        "call": "record_session_event",
        "payload": {
            "client_session_id": session_id, "kind": "website_mismatch_answered",
            "workspace_id": state["workspace"]["id"],
            "detail": {"handle": mismatch["handle"], "answer": answer},
        },
    }


# ------------------------------------------------------------ event -> log --

def handle_mismatch_event_recorded(session_id: str, kind: str, detail: Any) -> None:
    """A successful (`recorded: true`) `record_session_event` for one of our
    two kinds spends the reminder: `..._shown` stores the pending mismatch
    (the ONLY place it is ever set -- there is no server-side screening to
    set it earlier); `..._answered` clears everything once it matches the
    stored `{handle, answer}` exactly (RMP-66, "After ..._answered is
    logged -> clear")."""
    progress = read_progress(session_id)
    if kind == "website_mismatch_shown":
        handle = detail.get("handle") if isinstance(detail, dict) else None
        reason = detail.get("reason") if isinstance(detail, dict) else None
        if not isinstance(handle, str) or not handle or not isinstance(reason, str) or not reason:
            return
        _save_progress(session_id, {
            "mismatch": {"handle": handle, "reason": reason}, "answer": None, "answered_logged": False,
        })
    elif kind == "website_mismatch_answered":
        mismatch = progress["mismatch"]
        if mismatch is None or progress["answer"] is None:
            return
        if detail != {"handle": mismatch["handle"], "answer": progress["answer"]}:
            return
        clear(session_id)


def handle_record_session_event_dispatch(session_id: str, payload: dict) -> None:
    """`record_session_event`'s single dispatch entry in `step_recorder.py`'s
    table -- called from `step_recorder_revenue.handle_record_session_event_
    dispatch` (this tool's one shared dispatch entry), same pattern as
    `fact_events`/step 4's own dispatch entries. Checks its own `kind`
    before doing anything, so it is safe alongside every other kind."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None or data.get("recorded") is not True:
        return
    tool_input = tool_args(payload)
    kind = tool_input.get("kind")
    if kind not in MISMATCH_EVENT_KINDS:
        return
    handle_mismatch_event_recorded(session_id, kind, tool_input.get("detail"))
