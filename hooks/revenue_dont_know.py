#!/usr/bin/env python3
"""RMP-24 (S5-B6) -- "I don't know" for step 5's "what do you sell" free-text question.

Before this: an "I don't know" reply was captured VERBATIM as the customer's own
`revenue_description` (nothing filtered typed replies at all) -- a non-answer stored as
if it were the business's own words. Now: `answer_matcher.is_dont_know_reply` detects it
(P2233: the SERVER decides by meaning, in any language; no phrase list lives in the plugin),
and this module owns what happens next.

FLOW (never more than one gentle nudge): the FIRST "I don't know" bumps `count` to 1 and
saves nothing -- `checklist_recorder`'s own step-5 branch then reminds the model to ask
the one alternate phrasing ("What do people pay you for today -- even informally?") in
plain text, exactly like section 4's own question. The SECOND "I don't know" (`count`
reaching 2) closes step 5 honestly as `how="skipped"` -- never a third nudge, never an
invented description. A REAL answer in between (the normal `update_creator_brief` save)
naturally stops this module mattering at all: `build_follow_up_reminder` re-checks
`description_waiting` every time, which goes False the instant a real description saves.

STATE lives under ONE raw `connection_state` key, `revenue_dont_know_count` (read/written
via `connection_state.read_raw`/`write_patch` directly, same pattern as `step_recorder_
revenue.py`'s own `revenue_progress`). Shape, safe default for anything missing or
wrong-typed: a plain `int >= 0`. Cleared: on a fresh MCQ save (`step_recorder_revenue.
handle_brief_write`, a re-answer must start the "I don't know" count over too) and on
every workspace switch (`step_recorder_workspace.handle_set_active_workspace`).

FAIL-SAFE: nothing here may crash a hook -- same convention as every sibling module.
"""
from __future__ import annotations

from typing import Any

import connection_state as cs
import offer_lines
import step_state

STEP_ID = "revenue_model"
OFFER_ID = "revenue_description"   # P2361: the SERVER's follow-up line is `lines.dont_know_follow_up`
_MAX_ATTEMPTS = 2


def read_count(session_id: str) -> int:
    """The safe value, with the safe default (0) for anything missing or wrong-typed."""
    raw = cs.read_raw(session_id).get("revenue_dont_know_count")
    return raw if isinstance(raw, int) and not isinstance(raw, bool) and raw >= 0 else 0


def clear(session_id: str) -> None:
    cs.write_patch(session_id, {"revenue_dont_know_count": 0})


def handle_dont_know_reply(session_id: str) -> None:
    """Called from `step_recorder_revenue.capture_description_reply` the instant a typed
    reply is detected as "I don't know". Rule 3 target: drop the `count >= _MAX_ATTEMPTS`
    branch below and this never closes the step -- the customer would be asked the SAME
    gentle follow-up forever, one per "I don't know" reply, with no honest way out."""
    count = read_count(session_id) + 1
    if count >= _MAX_ATTEMPTS:
        # Same raw shape `step_recorder_revenue.py` writes under `revenue_progress` --
        # closes the step without ever going through that module (no import cycle: this
        # file must stay import-free of `step_recorder_revenue`, which itself calls INTO
        # this module on a fresh MCQ save).
        cs.write_patch(session_id, {
            "revenue_progress": {"model_saved": True, "description_saved": True, "words_to_log": None},
        })
        step_state.mark_step_passed(session_id, STEP_ID, "skipped")
        clear(session_id)
        return
    cs.write_patch(session_id, {"revenue_dont_know_count": count})


def build_follow_up_reminder(session_id: str, description_waiting: bool) -> dict[str, Any] | None:
    """The one-shot gentle follow-up, right after the FIRST "I don't know" -- `None` once
    it has already been asked (`count != 1`) or step 5 is no longer genuinely waiting on
    the description (a real answer saved, or the step closed some other way meanwhile).
    `description_waiting` is passed in (not recomputed here) to avoid this module needing
    to import `step_recorder_revenue` -- see the module docstring's "no import cycle" note."""
    if read_count(session_id) != 1 or not description_waiting:
        return None
    text = offer_lines.line(session_id, OFFER_ID, "dont_know_follow_up")
    if text is None:
        return None   # the server sent no follow-up line: say nothing of our own
    return {"instruction": f'Ask in plain text (not AskUserQuestion): "{text}" Then wait.'}
