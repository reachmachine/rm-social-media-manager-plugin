#!/usr/bin/env python3
"""Step 5 recorder rules: "how you make money" (P1627, RMP-38).

Spec: docs/plugin-v2/05-how-you-make-money.md, "What the recorder does" (flow, 1-6) and "Capturing
the customer's words". Split out of `step_recorder.py`/`checklist_recorder.py` to keep both under
the 300-line limit, same "split when it grows" precedent as `step_recorder_own_account.py`.

STATE: kept OUT of `step_state.read_state`'s shape (exact-equality-asserted in
`test_step_state.py`) -- lives under one raw key, `revenue_progress`, read/written straight
through `connection_state.read_raw`/`write_patch`, same pattern as `spend_gate.py`'s
`spend_previews`. Shape, safe defaults for anything missing or wrong-typed:
    {"model_saved": bool, "description_saved": bool, "words_to_log": str | None}
`step_state.reset_for_new_workspace` clears it on every switch. A re-answer (a fresh
`revenue_model` save after step 5 already passed) un-passes and un-ticks the step, same
"changing the answer later" rule P1615 gave steps 2-4.

RMP-281 ("not earning yet"): `NOT_EARNING_VALUE` is still the one exclusive pick, but it no longer
closes step 5 on the model save alone. Every pick, this one included, saves the model with
`description_saved: False`, so the "what do you offer, and to whom?" question is asked and the
customer's next typed message is taken as the description. Must match
`agent_step_rules.NOT_EARNING_VALUE` (backend) exactly.

FAIL-SAFE: nothing here may crash a hook -- same convention as every sibling module.
"""
from __future__ import annotations

import json
import os
from typing import Any

import answer_matcher
import connection_state as cs
import fact_events
from payload_util import tool_args
import revenue_dont_know
import step_order
import step_recorder_own_account as own_account_recorder
import step_state
import steps_manifest
import transcript_redaction
import website_mismatch

REVENUE_STEP_ID = "revenue_model"
REVENUE_DESCRIPTION_KEY = "revenue_description"
# = server safety limit (P1624): a technical abuse cap, never a product rule (founder: no
# character cap on the customer's own words).
_MAX_WORDS = int(os.environ.get("RMP_CUSTOMER_WORDS_MAX_CHARS", "10000"))

_DEFAULT_PROGRESS: dict[str, Any] = {
    "model_saved": False, "description_saved": False, "words_to_log": None,
}


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def read_progress(session_id: str) -> dict[str, Any]:
    """The safe shape, with the safe default for anything missing or wrong-typed."""
    raw = cs.read_raw(session_id).get("revenue_progress")
    result = dict(_DEFAULT_PROGRESS)
    if isinstance(raw, dict):
        for flag in ("model_saved", "description_saved"):
            if isinstance(raw.get(flag), bool):
                result[flag] = raw[flag]
        words = raw.get("words_to_log")
        if isinstance(words, str) and words:
            result["words_to_log"] = words
    return result


def _save_progress(session_id: str, progress: dict[str, Any]) -> None:
    cs.write_patch(session_id, {"revenue_progress": progress})


def description_waiting(steps: list[dict], state: dict, progress: dict) -> bool:
    """True when: the revenue step exists in `steps`; every earlier step is finished (using
    the SAME definition the order gate uses: step 1 via `steps_passed`, later steps via
    `ticked`, P1641, RMP-50); `progress["model_saved"]` is True; `progress["description_saved"]`
    is False. Rule 3 break (b): drop the `model_saved` check and a reply before the MCQ is even
    saved would be read as the description."""
    step = steps_manifest.step_by_id(steps, REVENUE_STEP_ID)
    if step is None:
        return False
    return (
        step_order.earlier_steps_done(steps, state, REVENUE_STEP_ID)
        and progress["model_saved"]
        and not progress["description_saved"]
    )


def capture_description_reply(session_id: str, prompt_text: str) -> None:
    """UserPromptSubmit only. The latest reply wins while `description_waiting` -- called with the
    ORIGINAL `prompt_text` (not the casefolded `message`), so the words logged later keep the
    customer's real case. Rule 3 break (c): capture from the casefolded message instead and the
    logged words lose their case."""
    steps = steps_manifest.load_steps(session_id)
    state = step_state.read_state(session_id)
    progress = read_progress(session_id)
    if not description_waiting(steps, state, progress):
        return
    reply = answer_matcher.free_text_reply(prompt_text, max_chars=_MAX_WORDS)
    if reply is None:
        return
    if answer_matcher.is_dont_know_reply(session_id, reply):  # RMP-24 (S5-B6)
        revenue_dont_know.handle_dont_know_reply(session_id)
        return
    step_state.set_human_answer(session_id, REVENUE_DESCRIPTION_KEY, reply)


def handle_brief_read(session_id: str, fields: dict) -> None:
    """Already known: `revenue_model` a non-empty list of known option values AND
    `revenue_description` a non-empty string -> `already_known`, ONLY if the step is not already
    passed AND `progress["model_saved"]` is False -- a re-answer in progress must never be closed
    by the OLD description still in the brief. Rule 3 break (d): drop the `model_saved` guard and
    an in-progress re-answer would be silently closed by the stale brief.

    RMP-281: every pick, "not earning yet" included, needs a saved description to count as known."""
    steps = steps_manifest.load_steps(session_id)
    step = steps_manifest.step_by_id(steps, REVENUE_STEP_ID)
    if step is None:
        return
    state = step_state.read_state(session_id)
    if REVENUE_STEP_ID in state["steps_passed"] or read_progress(session_id)["model_saved"]:
        return
    model_entry = fields.get("revenue_model")
    model_value = model_entry.get("value") if isinstance(model_entry, dict) else None
    allowed = {opt["value"] for opt in steps_manifest.question_options(step)}
    model_ok = bool(model_value) and isinstance(model_value, list) and all(
        isinstance(v, str) and v in allowed for v in model_value
    )
    description_entry = fields.get(REVENUE_DESCRIPTION_KEY)
    description_value = description_entry.get("value") if isinstance(description_entry, dict) else None
    if model_ok and isinstance(description_value, str) and description_value:
        step_state.mark_step_passed(session_id, REVENUE_STEP_ID, "already_known")


def handle_brief_write(session_id: str, fields: dict) -> None:
    """Called only after a `saved: true` result. Uses the progress as it was BEFORE this call."""
    progress = read_progress(session_id)
    state = step_state.read_state(session_id)

    description_entry = fields.get(REVENUE_DESCRIPTION_KEY)
    description_value = description_entry.get("value") if isinstance(description_entry, dict) else None
    stored_description = state["human_answers"].get(REVENUE_DESCRIPTION_KEY)
    if (
        isinstance(description_value, str) and description_value and progress["model_saved"]
        and isinstance(stored_description, str) and stored_description
    ):
        _save_progress(session_id, {
            "model_saved": True, "description_saved": True,
            # RMP-59: private details are hidden BEFORE the words leave this machine.
            "words_to_log": transcript_redaction.redact_text(
                stored_description, home=os.path.expanduser("~"),
            ),
        })
        step_state.clear_human_answer(session_id, REVENUE_DESCRIPTION_KEY)

    model_entry = fields.get("revenue_model")
    model_value = model_entry.get("value") if isinstance(model_entry, dict) else None
    stored_model = state["human_answers"].get("revenue_model")
    if (
        isinstance(model_value, list) and isinstance(stored_model, list)
        and len(model_value) == len(set(model_value)) and set(model_value) == set(stored_model)
    ):
        step_state.clear_human_answer(session_id, "revenue_model")
        step_state.clear_human_answer(session_id, REVENUE_DESCRIPTION_KEY)
        # A re-answer (this step already passed) starts step 5 over -- a no-op the first time.
        step_state.unmark_step_passed(session_id, REVENUE_STEP_ID)
        step_state.unmark_ticked(session_id, REVENUE_STEP_ID)
        revenue_dont_know.clear(session_id)  # RMP-24: a fresh MCQ save starts the "I don't know" count over too
        _save_progress(session_id, {
            "model_saved": True, "description_saved": False, "words_to_log": None,
        })


def handle_revenue_described_event(session_id: str, payload: dict) -> None:
    """`recorded: true`, `kind == "revenue_described"`, workspace matches, `detail ==
    {"customer_words": progress["words_to_log"]}` (and `words_to_log` is not None) -> clear the
    slot, mark step 5 passed `how: "answered"`."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None or data.get("recorded") is not True:
        return
    tool_input = tool_args(payload)
    if tool_input.get("kind") != "revenue_described":
        return
    state = step_state.read_state(session_id)
    workspace = state["workspace"]
    if workspace is None or tool_input.get("workspace_id") != workspace["id"]:
        return
    progress = read_progress(session_id)
    words = progress["words_to_log"]
    if words is None or tool_input.get("detail") != {"customer_words": words}:
        return
    _save_progress(session_id, {**progress, "words_to_log": None})
    step_state.mark_step_passed(session_id, REVENUE_STEP_ID, "answered")


def pending_event_reminder(session_id: str, state: dict) -> dict[str, Any] | None:
    """The exact `record_session_event` payload owed once the description is saved but the words
    are not yet logged; None once logged or before a workspace is chosen."""
    workspace = state["workspace"]
    words = read_progress(session_id)["words_to_log"]
    if words is None or workspace is None:
        return None
    return {
        "call": "record_session_event",
        "payload": {
            "client_session_id": session_id, "kind": "revenue_described",
            "workspace_id": workspace["id"], "detail": {"customer_words": words},
        },
    }


def handle_record_session_event_dispatch(session_id: str, payload: dict) -> None:
    """`record_session_event`'s single dispatch entry in `step_recorder.py`'s table -- moved here
    (not left as a small helper there) only to keep that file under the 300-line limit. Runs the
    step-4 dispatcher, this step's own handler, AND (RMP-68) the facts-from-chat dispatcher; each
    checks its own `kind`, so nothing here needs to know which one matched."""
    own_account_recorder.handle_record_session_event_dispatch(session_id, payload)
    handle_revenue_described_event(session_id, payload)
    fact_events.handle_record_session_event_dispatch(session_id, payload)
    website_mismatch.handle_record_session_event_dispatch(session_id, payload)
