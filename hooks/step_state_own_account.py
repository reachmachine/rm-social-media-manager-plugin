#!/usr/bin/env python3
"""RMP-23, founder decision 6 (2026-09-24) -- setters for the four
`own_account_mismatch*` keys `step_state.py`'s `read_state`/
`reset_for_new_workspace` already know about (see that module's own
docstring for the full shape). Split out to keep `step_state.py` under the
300-line limit, same "split when it grows" precedent as
`step_gate_own_account.py`/`step_recorder_own_account.py`.
"""
from __future__ import annotations

import connection_state as cs
import step_state


def set_own_account_mismatch(session_id: str, handle: str, reason: str) -> None:
    """A NEW mismatch also resets the answer + both logged flags -- a
    mismatch that has just been (re-)detected has not been answered or
    logged yet."""
    cs.write_patch(
        session_id,
        {
            "own_account_mismatch": {"handle": handle, "reason": reason},
            "own_account_mismatch_answer": None,
            "own_account_mismatch_logged": False,
            "own_account_answer_logged": False,
        },
    )


def clear_own_account_mismatch(session_id: str) -> None:
    """A NEW own handle was captured (04-own-instagram-account.md) --
    whatever mismatch/answer/logged state applied to the OLD handle no
    longer means anything."""
    cs.write_patch(
        session_id,
        {
            "own_account_mismatch": None,
            "own_account_mismatch_answer": None,
            "own_account_mismatch_logged": False,
            "own_account_answer_logged": False,
        },
    )


def set_own_account_mismatch_answer(session_id: str, answer: str) -> None:
    cs.write_patch(session_id, {"own_account_mismatch_answer": answer})


def mark_own_account_mismatch_logged(session_id: str) -> None:
    cs.write_patch(session_id, {"own_account_mismatch_logged": True})


def mark_own_account_answer_logged(session_id: str) -> None:
    cs.write_patch(session_id, {"own_account_answer_logged": True})


def reset_steps_from(session_id: str, step_ids: list[str]) -> None:
    """RMP-113 -- a "different Instagram account" own-account change
    restarts the given step ids locally, mirroring the server's own
    checklist reset (`agent_checklist_store.reset_checklist_from`,
    `own_account_change_service.apply_different_account`). Unlike
    `step_state.reset_for_new_workspace`, this NEVER touches an EARLIER
    step (workspace pick, whose-account) -- only the business identity
    changed, so re-asking those would be wrong. Clears
    human_answers/steps_passed/ticked for exactly `step_ids`, plus every
    own-account-specific field (handle, refresh, mismatch) -- all of it
    described the OLD account and means nothing for the new one."""
    state = step_state.read_state(session_id)
    to_clear = set(step_ids)
    answers = {k: v for k, v in state["human_answers"].items() if k not in to_clear}
    passed = {k: v for k, v in state["steps_passed"].items() if k not in to_clear}
    ticked = [t for t in state["ticked"] if t not in to_clear]
    cs.write_patch(
        session_id,
        {
            "human_answers": answers,
            "steps_passed": passed,
            "ticked": ticked,
            "own_account_handle": None,
            "last_known_detail": None,
            "last_refresh": None,
            "own_account_refreshed": False,
            "own_account_mismatch": None,
            "own_account_mismatch_answer": None,
            "own_account_mismatch_logged": False,
            "own_account_answer_logged": False,
        },
    )
