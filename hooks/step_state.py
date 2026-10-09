#!/usr/bin/env python3
"""Session-scoped state for question steps 2+ (RMP-10, RMP-19), plus the
resume-checklist bookkeeping (RMP-9, RMP-18).

Spec: docs/plugin-v2/02-workspace-selection.md "Enforcement", 03-whose-
account.md "The reusable question step", and 00-resume-checklist.md "The
model cannot tick a box it didn't earn".

SAME per-session file as step 1 (`connection_state.state_path`), new
top-level keys on top of step 1's own (`reachmachine`, `apify`, ...):
  - `workspace`: {id, name, chosen_at} | None -- the confirmed active pick.
  - `workspace_options`: [{id, name, locked}] -- from the last
    `list_workspaces` call, so a typed reply or an `AskUserQuestion` label
    can be matched back to a workspace id.
  - `human_answers`: {step_id: value} -- the customer's own pick, proved by
    a real `AskUserQuestion` result or an exact typed match. `step_gate.py`
    only allows a write to match this; `step_recorder.py` is the only writer.
  - `steps_passed`: {step_id: how} -- "answered" | "already_known" |
    "passed" (connection_check, and choose_workspace once RMP-9's three
    conditions below all hold).
  - `workspace_logged`: bool -- a `record_session_event` call has been
    accepted for the CURRENT workspace this session. Reset on every switch.
  - `workspace_logged_ever`: bool -- true forever once ANY workspace has
    ever been logged this session. Never reset -- it is what tells a later
    `record_session_event` call apart as a "switch" instead of the first
    pick (02-workspace-selection.md, "the session log gets the update").
  - `checklist_read`: bool -- `get_resume_checklist` has succeeded for the
    CURRENT workspace this session. Reset on every switch.
  - `ticked`: [step_id] -- `record_checklist_step(step_id, "done", ...)` has
    been accepted for this step. Gate ordering (`step_gate._first_unpassed`)
    only advances past a step once it is ticked, not merely `steps_passed`,
    so "every step writes to three places" (03-whose-account.md) is
    enforced, not just documented.
  - `own_account_handle`: str | None -- the workspace's own Instagram
    handle, once known, from either a confirmed `add_to_watchlist` or a live
    `get_resume_checklist` `detail` (RMP-23, 04-own-instagram-account.md).
  - `last_known_detail`: dict | None -- the most recent `detail` object
    `get_resume_checklist` returned for `own_instagram_account`
    (`{handle, follower_count, media_count, profile_fetched_at, profile_id}`),
    refreshed on every checklist read.
  - `last_refresh`: dict | None -- `{handle, follower_count, media_count}`
    from the most recent successful `refresh_competitor` call, cleared once
    the matching `record_session_event(profile_refreshed)` is accepted (one
    refresh, one log entry).
  - `own_account_refreshed`: bool -- a `refresh_competitor` call for the own
    account has already succeeded THIS session, for THIS workspace. At most
    one auto-refresh per session -- without this flag the 7-day reminder
    would loop, because `last_known_detail.profile_fetched_at` is only
    updated on the NEXT `get_resume_checklist` read (architect review,
    2026-09-24).
  - `own_account_mismatch`/`own_account_mismatch_answer`/`own_account_
    mismatch_logged`/`own_account_answer_logged` -- RMP-23, founder decision
    6 (2026-09-24); shape + lifecycle in `own_account_mismatch.py`'s own
    docstring. Setters live in the sibling `step_state_own_account.py`.

Missing/corrupt/wrong-typed keys all read back as the safe empty default --
same fail-safe direction as `connection_state.py`, so nothing here ever has
to guard against a partially-written or hand-edited file.

Every write goes through `connection_state.write_patch`, which merges onto
whatever is already in the file, so a step-1 probe write (which only knows
its OWN keys) can never wipe these out, and vice versa.
"""
from __future__ import annotations

import datetime
from typing import Any

import connection_state as cs


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def read_state(session_id: str) -> dict[str, Any]:
    """All eight keys, defaulting to the safe empty shape for anything
    missing, corrupt, or not the right type."""
    raw = cs.read_raw(session_id)
    result: dict[str, Any] = {
        "workspace": None,
        "workspace_options": [],
        "human_answers": {},
        "steps_passed": {},
        "workspace_logged": False,
        "workspace_logged_ever": False,
        "checklist_read": False,
        "ticked": [],
        "own_account_handle": None,
        "last_known_detail": None,
        "last_refresh": None,
        "own_account_refreshed": False,
        "own_account_mismatch": None,
        "own_account_mismatch_answer": None,
        "own_account_mismatch_logged": False,
        "own_account_answer_logged": False,
    }

    workspace = raw.get("workspace")
    if (
        isinstance(workspace, dict)
        and isinstance(workspace.get("id"), str)
        and workspace.get("id")
        and isinstance(workspace.get("name"), str)
    ):
        result["workspace"] = workspace

    options = raw.get("workspace_options")
    if isinstance(options, list):
        result["workspace_options"] = [
            o for o in options
            if isinstance(o, dict) and isinstance(o.get("id"), str) and isinstance(o.get("name"), str)
        ]

    answers = raw.get("human_answers")
    if isinstance(answers, dict):
        result["human_answers"] = {k: v for k, v in answers.items() if isinstance(k, str)}

    passed = raw.get("steps_passed")
    if isinstance(passed, dict):
        result["steps_passed"] = {
            k: v for k, v in passed.items() if isinstance(k, str) and isinstance(v, str)
        }

    ticked = raw.get("ticked")
    if isinstance(ticked, list):
        result["ticked"] = [t for t in ticked if isinstance(t, str)]

    for flag in (
        "workspace_logged", "workspace_logged_ever", "checklist_read", "own_account_refreshed",
        "own_account_mismatch_logged", "own_account_answer_logged",
    ):
        value = raw.get(flag)
        if isinstance(value, bool):
            result[flag] = value

    handle = raw.get("own_account_handle")
    if isinstance(handle, str) and handle:
        result["own_account_handle"] = handle

    for key in ("last_known_detail", "last_refresh"):
        value = raw.get(key)
        if isinstance(value, dict):
            result[key] = value

    mismatch = raw.get("own_account_mismatch")
    handle_ok = isinstance(mismatch, dict) and isinstance(mismatch.get("handle"), str) and mismatch.get("handle")
    if handle_ok and isinstance(mismatch.get("reason"), str):
        result["own_account_mismatch"] = {"handle": mismatch["handle"], "reason": mismatch["reason"]}

    answer = raw.get("own_account_mismatch_answer")
    if answer in ("yes", "no"):
        result["own_account_mismatch_answer"] = answer

    return result


def set_workspace_options(session_id: str, options: list[dict[str, Any]]) -> None:
    """From the last `list_workspaces` result. Keeps only the shape
    `step_gate.py` and the typed-fallback matcher need (id, name, locked) --
    never the raw server response, so a future field on `list_workspaces`
    can't leak into the state file unexamined."""
    cleaned = [
        {"id": o["id"], "name": o["name"], "locked": bool(o.get("locked"))}
        for o in options
        if isinstance(o, dict) and isinstance(o.get("id"), str) and isinstance(o.get("name"), str)
    ]
    cs.write_patch(session_id, {"workspace_options": cleaned})


def set_workspace(session_id: str, workspace_id: str, name: str) -> None:
    cs.write_patch(
        session_id,
        {"workspace": {"id": workspace_id, "name": name, "chosen_at": _now_iso()}},
    )


def reset_for_new_workspace(session_id: str) -> None:
    """Every confirmed `set_active_workspace` (the first pick, and every later switch alike)
    starts this workspace's own progress from scratch: `workspace_logged`/`checklist_read` reset
    (02-workspace-selection.md, "reset on a switch"), and every workspace-scoped answer/tick from
    the PREVIOUS workspace is cleared, because the checklist and the creator brief are both
    per-workspace -- a tick earned for Gym Brand must never be read as earned for Yoga Studio too.
    `connection_check` (session-kind, never workspace-scoped) is the one entry `steps_passed`
    keeps. `workspace_logged_ever` is NOT reset -- it must survive every switch, so
    `record_session_event` can tell "first pick" from "switch" (rule 1). Also clears raw-key
    per-workspace state (spend/revenue/skip flags, own account handle/detail/refresh/mismatch,
    RMP-68/RMP-72's pending business-fact events -- a fact belongs to the workspace it was saved in)."""
    state = read_state(session_id)
    kept_passed = {k: v for k, v in state["steps_passed"].items() if k == "connection_check"}
    cs.write_patch(
        session_id,
        {
            "human_answers": {},
            "steps_passed": kept_passed,
            "ticked": [],
            "workspace_logged": False,
            "checklist_read": False,
            "spend_previews": {},
            "revenue_progress": {},
            "pending_fact_events": [],
            "skip_reoffer_pending": False,
            "skip_reoffer_handled": False,
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


def set_workspace_logged(session_id: str) -> None:
    cs.write_patch(session_id, {"workspace_logged": True, "workspace_logged_ever": True})


def set_checklist_read(session_id: str) -> None:
    cs.write_patch(session_id, {"checklist_read": True})


def set_human_answer(session_id: str, step_id: str, value: str) -> None:
    answers = dict(read_state(session_id)["human_answers"])
    answers[step_id] = value
    cs.write_patch(session_id, {"human_answers": answers})


def clear_human_answer(session_id: str, step_id: str) -> None:
    answers = dict(read_state(session_id)["human_answers"])
    if step_id in answers:
        del answers[step_id]
        cs.write_patch(session_id, {"human_answers": answers})


def mark_step_passed(session_id: str, step_id: str, how: str) -> None:
    passed = dict(read_state(session_id)["steps_passed"])
    passed[step_id] = how
    cs.write_patch(session_id, {"steps_passed": passed})


def mark_ticked(session_id: str, step_id: str) -> None:
    """`record_checklist_step(step_id, "done", ...)` was accepted -- the
    only thing that lets gate ordering move past this step."""
    ticked = list(read_state(session_id)["ticked"])
    if step_id not in ticked:
        ticked.append(step_id)
        cs.write_patch(session_id, {"ticked": ticked})


def unmark_ticked(session_id: str, step_id: str) -> None:
    """The inverse of `mark_ticked` (P1615): removes an earlier tick so gate
    ordering (`step_gate._first_unpassed`) closes again until a FRESH
    `record_checklist_step("done")` lands for this step. A no-op if the
    step was never ticked -- the ordinary first-time pass. Used only when a
    step is genuinely being answered AGAIN (03-whose-account.md, "Changing
    the answer later"), so the server ends up writing a new `step_done`
    event, not silently reusing the old tick."""
    ticked = [t for t in read_state(session_id)["ticked"] if t != step_id]
    cs.write_patch(session_id, {"ticked": ticked})


def unmark_step_passed(session_id: str, step_id: str) -> None:
    """Removes `step_id` from `steps_passed` (a no-op if absent) -- used only by a step-5
    re-answer (`step_recorder_revenue.py`, P1627), not passed again until both answers are saved."""
    passed = {k: v for k, v in read_state(session_id)["steps_passed"].items() if k != step_id}
    cs.write_patch(session_id, {"steps_passed": passed})


def is_step_passed(session_id: str, step_id: str) -> bool:
    return step_id in read_state(session_id)["steps_passed"]


def set_own_account_handle(session_id: str, handle: str) -> None:
    cs.write_patch(session_id, {"own_account_handle": handle})


def set_last_known_detail(session_id: str, detail: dict[str, Any] | None) -> None:
    cs.write_patch(session_id, {"last_known_detail": detail})


def set_last_refresh(session_id: str, refresh: dict[str, Any] | None) -> None:
    cs.write_patch(session_id, {"last_refresh": refresh})


def set_own_account_refreshed(session_id: str) -> None:
    cs.write_patch(session_id, {"own_account_refreshed": True})


def sync_connection_check(session_id: str) -> None:
    """`connection_check` enters `steps_passed` (how="passed") the moment
    step 1's own `all_passed` becomes true (spec, 00-resume-checklist.md).
    Idempotent, safe to call from every gate decision and every recorder
    entry point -- it only ever adds the one key, so callers never have to
    care which of them ran first."""
    if is_step_passed(session_id, "connection_check"):
        return
    if cs.all_passed(session_id):
        mark_step_passed(session_id, "connection_check", "passed")
