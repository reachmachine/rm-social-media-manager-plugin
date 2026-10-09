#!/usr/bin/env python3
"""What the customer typed in answer to the niche pick question (RMP-281, P2260).

Seen once: the list showed "1 ... 2 Birthday cake ... 3 ...", the customer typed `2`, and the model called
`choose_niche` with the id of option 1. The server only saw the model's id. So `session_stamp.py` now adds the
customer's own typed words to a `choose_niche` call as `customer_said`, and the SERVER reads them against the
options it showed (`niche_pick_judge.py`). Nothing is decided here -- this file only answers "which typed words,
if any, are a reply to the pick question?".

THE STALE RULE. A message typed BEFORE the pick question was shown is an answer to an earlier question (the live
run: a "2" typed for an earlier question was read as the pick). So the moment the question is shown (the planner's
`N8c` ask, or a `start_niche_pick` / `save_niche_research` / `choose_niche` reply that carries `question`) this
module remembers how many messages the customer had typed so far (`customer_upload_state.prompt_count`). Typed
words count only if the count has grown since. A click on the question (no typed message) never grows the count,
so nothing is stamped for it. No marker at all (the question was never seen to be shown) also stamps nothing:
today's behaviour.

The marker is written only when none is open, so a repeat poll of the same question (`next_actions` again, after
the customer already typed) cannot move it past their answer. `choose_niche` closes it.

State: one small file per chat with one writer per event; FAIL-SAFE like every sibling: nothing here may raise.
"""
from __future__ import annotations

import os
import pathlib
from typing import Any

import customer_upload_state as cus
import state_file_io

PICK_NODE = "N8c"
_MAX_SAID_CHARS = 300


def _marker_path(session_id: str) -> pathlib.Path:
    return pathlib.Path(os.environ.get("TMPDIR") or "/tmp") / f"rm-plugin-v2-pick-shown-{session_id}.txt"


def _marker(session_id: str) -> int | None:
    try:
        return int(_marker_path(session_id).read_text(encoding="utf-8").strip())
    except Exception:
        return None


def mark_shown(session_id: str) -> None:
    """The pick question was just shown. An already-open marker is kept (a repeat poll must not move it)."""
    try:
        if _marker(session_id) is not None:
            return
        state_file_io.write_atomic(_marker_path(session_id), str(cus.prompt_count(session_id)))
    except Exception:
        pass


def close(session_id: str) -> None:
    try:
        _marker_path(session_id).unlink()
    except Exception:
        pass


def customer_said(session_id: str) -> str:
    """The customer's last typed message, only if typed after the pick question was shown; otherwise ''."""
    try:
        shown_at = _marker(session_id)
        if shown_at is None or cus.prompt_count(session_id) <= shown_at:
            return ""
        return " ".join(cus.last_prompt(session_id).split())[:_MAX_SAID_CHARS]
    except Exception:
        return ""


def note_plan(session_id: str, plan: dict[str, Any]) -> None:
    """PostToolUse on a plan reply: the planner is asking the pick question (node N8c)."""
    try:
        ask = plan.get("ask")
        questions = ask.get("questions") if isinstance(ask, dict) else None
        if isinstance(questions, list) and any(isinstance(q, dict) and q.get("node") == PICK_NODE for q in questions):
            mark_shown(session_id)
    except Exception:
        pass


def note_reply(session_id: str, data: dict[str, Any] | None, *, closes: bool = False) -> None:
    """PostToolUse on a niche tool (`data` = its parsed reply): a reply that carries a `question` shows it (an open marker is
    kept); `closes` (choose_niche) first closes the open marker, so a re-asked question starts a fresh one."""
    try:
        if closes:
            close(session_id)
        if isinstance(data, dict) and isinstance(data.get("question"), dict):
            mark_shown(session_id)
    except Exception:
        pass
