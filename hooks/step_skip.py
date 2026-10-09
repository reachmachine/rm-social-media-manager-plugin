#!/usr/bin/env python3
"""Step 4 (RMP-52, RMP-281 S4-7): "We don't use Instagram" is FINAL (`how="no_instagram"`), never
re-offered. An older `how="skipped"` record is re-offered once per session; step 5 saves are denied
while that re-offer is pending. Split from checklist_recorder.py and step_gate.py. Fails safe."""
from __future__ import annotations

from typing import Any

import answer_matcher
import connection_state as cs
import deny_lines
import offer_lines
import step_skip_typed
import step_state
import steps_manifest

_REOFFER_GATE_REASON = "ask_instagram_first"


def _is_skip_reoffer_pending(session_id: str) -> bool:
    """Read skip_reoffer_pending from raw state. Pattern: same as
    step_recorder_revenue.read_progress, kept OUT of step_state.read_state."""
    raw = cs.read_raw(session_id).get("skip_reoffer_pending")
    return raw if isinstance(raw, bool) else False


def _was_reoffer_handled(session_id: str) -> bool:
    raw = cs.read_raw(session_id).get("skip_reoffer_handled")
    return raw if isinstance(raw, bool) else False


def _set_skip_reoffer_pending(session_id: str) -> None:
    cs.write_patch(session_id, {"skip_reoffer_pending": True})


def _clear_skip_reoffer_pending(session_id: str) -> None:
    cs.write_patch(session_id, {"skip_reoffer_pending": False, "skip_reoffer_handled": True})


def _note_skipped_this_session(session_id: str) -> None:
    """RMP-52 (live 2026-09-28): skipped in THIS session -> re-offer at the NEXT one only.
    State is wiped at every session start, so the flag lives for one session."""
    cs.write_patch(session_id, {"skip_made_this_session": True})


def _skipped_this_session(session_id: str) -> bool:
    return cs.read_raw(session_id).get("skip_made_this_session") is True


def _match_option_label(label: str, options: list[dict[str, str]]) -> str | None:
    """Simple exact match of label against options list. Returns the value
    if exactly one option matches, else None. Pure; never raises."""
    label_lower = label.strip().casefold()
    matches = [opt["value"] for opt in options if opt.get("label", "").strip().casefold() == label_lower]
    return matches[0] if len(matches) == 1 else None


def _close_step_no_instagram(session_id: str, value: str) -> None:
    """Step 4 passed as `no_instagram` (final, never re-offered). `value == "skip"` is an older server's question."""
    if value == "skip":
        step_state.mark_step_passed(session_id, "own_instagram_account", "skipped")
        _note_skipped_this_session(session_id)
    else:
        step_state.mark_step_passed(session_id, "own_instagram_account", "no_instagram")
    step_state.clear_human_answer(session_id, "own_instagram_account")  # no typed handle is left for the gate


def handle_skip_answer(
    session_id: str, question_text: str, answer_label: str, state: dict[str, Any]
) -> bool:
    """Checks if the answer is to the skip question. If so, processes it and
    returns True (indicating the answer was consumed). Otherwise returns
    False (the answer belongs to a different question).

    "We don't use Instagram" -> step 4 marked passed with how="no_instagram", the
    stored handle answer (if any) is cleared. "Yes, I'll add it" ->
    nothing happens (step 4 continues normally)."""
    steps = steps_manifest.load_steps(session_id)
    step = steps_manifest.step_by_id(steps, "own_instagram_account")
    if step is None:
        return False

    skip_q = steps_manifest.skip_question(step)
    if skip_q is None:
        return False
    if question_text != skip_q["text"]:
        return False

    # The answer is to the skip question. Match it to an option.
    matched_value = _match_option_label(answer_label, skip_q["options"])
    if matched_value is None:
        return True  # Malformed answer, but still consumed

    if matched_value in ("no_instagram", "skip"):
        _close_step_no_instagram(session_id, matched_value)

    return True


def _typed_value(
    typed: str, question: dict[str, Any], words: dict, transcript_path: str | None,
    session_id: str = "", offer_id: str = "",
) -> str | None:
    """Exact label always; a number or short word only while this question is
    the one the assistant just asked (RMP-281 P2187, step_skip_typed.py). The
    server's own `also` words for the offer count too (P2359): a Spanish "ahora no"."""
    value = _match_option_label(typed, question["options"])
    if value is None and step_skip_typed.question_pending(transcript_path, question["text"]):
        value = offer_lines.match(offer_lines.get(session_id, offer_id), typed) if offer_id else None
        if value is None:
            value = step_skip_typed.match_loose(typed, question["options"], words)
    return value


def handle_skip_answer_typed(
    session_id: str, typed_answer: str, state: dict[str, Any], transcript_path: str | None = None
) -> bool:
    """Headless typed fallback for the skip question. The exact label, or (when
    the question is pending) "1" / "skip" -> no_instagram. A bare "yes" never matches.
    Returns True if the answer was consumed, False if it doesn't match."""
    steps = steps_manifest.load_steps(session_id)
    step = steps_manifest.step_by_id(steps, "own_instagram_account")
    skip_q = steps_manifest.skip_question(step) if step is not None else None
    if skip_q is None:
        return False

    matched_value = _typed_value(typed_answer, skip_q, step_skip_typed.SKIP_WORDS, transcript_path, session_id, "skip_instagram")
    if matched_value is None:
        return False
    if matched_value in ("no_instagram", "skip"):
        _close_step_no_instagram(session_id, matched_value)
    return True


def maybe_set_reoffer_pending(session_id: str, state: dict[str, Any]) -> None:
    """Called from `checklist_recorder.handle_get_resume_checklist` when a
    workspace-kind done step is found. If the step is `own_instagram_account`
    with `how == "skipped"`, and the flag is not yet set, set it. Idempotent
    -- called on every checklist read, but only sets the flag once per
    session."""
    if _is_skip_reoffer_pending(session_id) or _was_reoffer_handled(session_id):
        return  # Already set or already answered this session
    if _skipped_this_session(session_id):
        return  # RMP-52: skipped just now -- ask again at the NEXT session only

    steps = steps_manifest.load_steps(session_id)
    step = steps_manifest.step_by_id(steps, "own_instagram_account")
    if step is None or steps_manifest.skip_question(step) is None:
        return  # Step 4 has no skip block

    step_id = "own_instagram_account"
    if step_id in state["steps_passed"] and state["steps_passed"][step_id] == "skipped":
        if step_id in state["ticked"]:
            _set_skip_reoffer_pending(session_id)


def build_reoffer_reminder(session_id: str, state: dict[str, Any]) -> dict[str, Any] | None:
    """Returns the reoffer question reminder if `skip_reoffer_pending` is
    True, else None. Format matches `checklist_recorder.build_step_reminder`:
    `{"instruction": <prose>}`. Called from
    `checklist_recorder.build_step_reminder` AFTER the mismatch reminder but
    BEFORE all other reminders, so it appears at the same-turn prompt."""
    if not _is_skip_reoffer_pending(session_id):
        return None

    steps = steps_manifest.load_steps(session_id)
    step = steps_manifest.step_by_id(steps, "own_instagram_account")
    if step is None:
        return None

    reoffer_q = steps_manifest.reoffer_question(step)
    if reoffer_q is None:
        return None

    # Format the instruction with the exact question text and options
    options_text = " / ".join(f'"{opt["label"]}"' for opt in reoffer_q["options"])
    return {
        "instruction": (
            f'Ask the customer with AskUserQuestion: "{reoffer_q["text"]}" '
            f'Options: {options_text}'
        )
    }


def handle_reoffer_answer(
    session_id: str, question_text: str, answer_label: str, state: dict[str, Any]
) -> bool:
    """Checks if the answer is to the reoffer question. If so, processes it
    and returns True. Otherwise returns False.

    "Yes, add it now" -> step 4 unpassed and unticked, flag cleared.
    "Not now" -> flag cleared, step 4 stays ticked."""
    if not _is_skip_reoffer_pending(session_id):
        return False

    steps = steps_manifest.load_steps(session_id)
    step = steps_manifest.step_by_id(steps, "own_instagram_account")
    if step is None:
        return False

    reoffer_q = steps_manifest.reoffer_question(step)
    if reoffer_q is None:
        return False
    if question_text != reoffer_q["text"]:
        return False

    matched_value = _match_option_label(answer_label, reoffer_q["options"])
    if matched_value is None:
        return True  # Malformed answer, but still consumed

    if matched_value == "add":
        # "Yes, add it now" -> unmark step 4 and clear the flag
        step_state.unmark_step_passed(session_id, "own_instagram_account")
        step_state.unmark_ticked(session_id, "own_instagram_account")

    # Both "add" and "later" clear the flag
    _clear_skip_reoffer_pending(session_id)
    return True


def handle_reoffer_answer_typed(
    session_id: str, typed_answer: str, state: dict[str, Any], transcript_path: str | None = None
) -> bool:
    """Headless typed fallback for the reoffer question. Returns True if the
    answer was consumed."""
    if not _is_skip_reoffer_pending(session_id):
        return False

    steps = steps_manifest.load_steps(session_id)
    step = steps_manifest.step_by_id(steps, "own_instagram_account")
    reoffer_q = steps_manifest.reoffer_question(step) if step is not None else None
    if reoffer_q is None:
        return False

    matched_value = _typed_value(typed_answer, reoffer_q, step_skip_typed.REOFFER_WORDS, transcript_path, session_id, "instagram_reoffer")
    if matched_value is None:
        return False

    if matched_value == "add":
        step_state.unmark_step_passed(session_id, "own_instagram_account")
        step_state.unmark_ticked(session_id, "own_instagram_account")
    _clear_skip_reoffer_pending(session_id)
    return True


def try_capture_ask_user_answer(session_id: str, question_text: str, label: str) -> bool:
    """Entry point for AskUserQuestion answers. Reads state itself, tries
    reoffer then skip (same order `step_recorder.py` used before). Returns
    True if either consumed the answer -- caller must not run normal step
    matching in that case. Pattern: same shape as `own_account_mismatch.
    try_capture_ask_user_answer`, so one place handles both."""
    state = step_state.read_state(session_id)
    if handle_reoffer_answer(session_id, question_text, label, state):
        return True
    if handle_skip_answer(session_id, question_text, label, state):
        return True
    return False


def try_capture_typed_answer(session_id: str, message: str, transcript_path: str | None = None) -> bool:
    """Entry point for typed (headless) answers. Reads state itself, tries
    reoffer then skip. Returns True only if one of them consumed the message
    -- caller must skip normal step matching in that case. An unrelated typed
    reply falls through (False), exactly like the mismatch path."""
    state = step_state.read_state(session_id)
    if handle_reoffer_answer_typed(session_id, message, state, transcript_path):
        return True
    if handle_skip_answer_typed(session_id, message, state, transcript_path):
        return True
    return False


def check_reoffer_gate(session_id: str, tool_suffix: str, tool_input: dict) -> dict | None:
    """While `skip_reoffer_pending`, denies step 5's `update_creator_brief`
    writes for step 5's brief keys and `record_checklist_step` ticks for step
    5. Returns a deny dict or None (allow).

    Called from `step_gate._decide_steps` after all other checks but before
    the spend gate."""
    if not _is_skip_reoffer_pending(session_id):
        return None

    if tool_suffix == "update_creator_brief":
        fields = tool_input.get("fields") if isinstance(tool_input, dict) else None
        if not isinstance(fields, dict):
            return None
        # Check if any step 5 brief key is being written
        if "revenue_model" in fields or "revenue_description" in fields:
            return deny_lines.deny_id(_REOFFER_GATE_REASON)

    if tool_suffix == "record_checklist_step":
        step_id = tool_input.get("step_id") if isinstance(tool_input, dict) else None
        if step_id == "revenue_model":
            return deny_lines.deny_id(_REOFFER_GATE_REASON)

    return None
