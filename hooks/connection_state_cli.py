#!/usr/bin/env python3
"""CLI entry point for step 1's three bash wrappers (RMP-3, RMP-4, RMP-5,
RMP-7, RMP-9, RMP-18): `record-connection-probe.sh` calls `record`,
`reset-connections.sh` calls `reset`, `connection-reminder.sh` calls
`reminder`.

Split out of `connection_state.py` when RMP-7 (docs/plugin-v2/01b-session-
log.md) added the `recorded` field, `expected_results`, and the local
queue: keeping the CLI here, importing the state library from
`connection_state.py` and the recording/queue logic from `session_record.py`
(step 1) and `checklist_recorder.py` (RMP-9/RMP-18's resume checklist),
holds every file under the 300-line limit.

P1612: `_cli_record` (the PostToolUse/PostToolUseFailure entry point) now
ALSO delivers "the next exact call" payload in the SAME turn, as
`hookSpecificOutput.additionalContext`, instead of waiting for the
UserPromptSubmit reminder on the customer's next message (found by the
dev sandbox, 2026-09-23: the model ran all three probes and correctly
refused to guess the payload). Verified against the installed Claude Code
2.1.281 build's own bundled zod schemas (decoded the binary the same way
P1605/P1607 did): BOTH `PostToolUse` and `PostToolUseFailure` declare
`hookSpecificOutput.additionalContext:o().optional()` as a plain optional
string, and the CLI's own bundled help text gives the exact JSON shape:
`{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext":
"Context injected back to model"}}`. `_print_additional_context` below
always echoes back the SAME `hook_event_name` this invocation received,
because Claude Code's output schema is a discriminated union keyed on that
literal -- printing the wrong one would not validate.

Two triggers, matching docs/plugin-v2/01b-session-log.md §3 and P1612's own
prompt:
  1. `_connection_check_message`: the probe that completes step 1's check
     (`session_record.check_complete`) -- may be a `PostToolUseFailure`
     (Apify's "not found" is a FAIL-shaped event that is a PASS signal, see
     `connection_state.judge_probe`). Checked only on a probe call.
  2. `_next_step_message`: whichever call `checklist_recorder.
     build_step_reminder` says is due right now, after `step_recorder.handle`
     has recorded this call's effect -- covers a confirmed
     `set_active_workspace` (-> `record_session_event`), a logged selection
     (-> `get_resume_checklist`), and a step pass (-> `record_checklist_step`).
     Checked only on a non-probe call (the two never overlap: a probe tool
     name is never one `step_recorder.handle` dispatches on).

The existing UserPromptSubmit reminder (`_cli_reminder`) keeps its exact
prior behaviour as a second channel -- it is only refactored, not changed,
to share the same text-building functions this file's PostToolUse delivery
now also calls (`session_record.build_reminder_text`, `checklist_recorder.
format_step_reminder`), so the two channels can never disagree.

FAIL-SAFE: none of these entry points may ever crash a tool call or a
prompt submission (same rule as before the split). `main` catches anything
unanticipated and always exits 0.
"""
from __future__ import annotations

import json
import sys
from typing import Any

import checklist_recorder as ckl
import connection_state as cs
import deny_lines
import probe_input_hint
import slim_tool_output
import session_record as sr
import step_recorder
import tool_result_dispatch
import connection_reminder_text
import voice_check_reminder
import workspace_pick_hint


def _read_stdin_payload() -> dict | None:
    try:
        raw = sys.stdin.read()
    except Exception:
        return None
    try:
        data = json.loads(raw)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _print_additional_context(
    event_name: Any, message: str | None, updated_output: Any = None,
) -> None:
    """P1612/RMP-78: the one place that prints
    `hookSpecificOutput.additionalContext`, for `_cli_record` (PostToolUse/
    PostToolUseFailure) and `_cli_reset` (SessionStart). `event_name` must be
    the SAME `hook_event_name` this invocation received -- Claude Code's
    output schema is a discriminated union keyed on that literal (see this
    module's docstring for the decoded-binary evidence, and RMP-78's own
    check that SessionStart uses the identical
    `{"hookSpecificOutput": {"hookEventName": ..., "additionalContext": ...}}`
    shape), so echoing anything else would not validate. Never raises;
    prints at most one JSON line."""
    if not message and updated_output is None:
        return
    if event_name not in ("PostToolUse", "PostToolUseFailure", "SessionStart"):
        return
    try:
        out: dict[str, Any] = {"hookEventName": event_name}
        if message:
            out["additionalContext"] = message
        if updated_output is not None and event_name == "PostToolUse":
            out["updatedToolOutput"] = updated_output  # RMP-76: slim_tool_output.py
        print(json.dumps({"hookSpecificOutput": out}))
    except Exception:
        pass


def _connection_check_message(session_id: str) -> str | None:
    """Trigger 1 (module docstring): only once this round's probing is
    `check_complete` and the session is not yet `recorded`."""
    state = cs.read_state(session_id)
    if not sr.check_complete(state) or state.get("recorded") is True:
        return None
    return sr.build_reminder_text(session_id)


def _next_step_message(session_id: str) -> str | None:
    """Trigger 2 (module docstring): whichever next call
    `checklist_recorder.build_step_reminder` says is due right now."""
    try:
        reminder = ckl.build_step_reminder(session_id)
    except Exception:
        return None
    if reminder is None:
        return None
    return ckl.format_step_reminder(reminder)


def _cli_record() -> int:
    """PostToolUse/PostToolUseFailure entry point. Never raises.

    P1612: also delivers "the next exact call" payload immediately, as
    `additionalContext` -- see this module's docstring."""
    payload = _read_stdin_payload()
    if payload is None:
        return 0
    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return 0
    event_name = payload.get("hook_event_name")

    tool_name = payload.get("tool_name")
    if isinstance(tool_name, str) and tool_name.endswith("__record_session_start"):
        try:
            sr.handle_record_session_start(session_id, payload)
        except Exception:
            pass
        deny_lines.capture_from_payload(session_id, payload)  # RMP-291 P2314: the lean stock-English map for the first gates (never raises)
        _print_additional_context(event_name, _next_step_message(session_id))
        return 0

    # RMP-66/RMP-190: session state for an open website read or reviews
    # fetch -- wired here (NOT step_recorder.py's table, which P1668 owns)
    # because it is session state, not a step tick. See tool_result_
    # dispatch.py's own docstring for the table this replaced.
    tool_result_dispatch.dispatch(session_id, tool_name, payload)

    # RMP-10, RMP-19: question steps 2+ (AskUserQuestion capture, and the
    # real tool results -- list_workspaces, set_active_workspace,
    # get_creator_brief, update_creator_brief). Mutually exclusive with the
    # probe-matching below -- none of these tool names look like a probe.
    try:
        step_recorder.handle(session_id, payload)
    except Exception:
        pass

    try:
        judged = cs.judge_probe(payload)
    except Exception:
        _print_additional_context(event_name, _next_step_message(session_id))
        return 0
    if judged is None:
        # RMP-48: when judged is None, check if there's a hint for wrapped input.
        hint = probe_input_hint.hint_for(payload)
        message = hint or workspace_pick_hint.message_for(session_id, payload) or _next_step_message(session_id)
        _print_additional_context(
            event_name, message, slim_tool_output.slimmed_output(session_id, payload),
        )
        return 0
    server, ok = judged
    cs.write_result(session_id, server, ok)
    try:
        sr.maybe_queue_check(session_id)
    except Exception:
        pass
    _print_additional_context(event_name, _connection_check_message(session_id))
    return 0


_RESUME_CONTEXT = (
    "This conversation was resumed. Earlier answers in this chat are not "
    "saved yet. Start again: run the connection check, ask which workspace, "
    "then continue from the checklist. Do not ask any step question before "
    "the workspace is chosen."
)


def _cli_reset() -> int:
    """SessionStart entry point. Never raises.

    RMP-78: a resumed session (`source == "resume"`) has its saved progress
    wiped by `cs.reset_state` above -- same as `startup`/`clear` -- but a
    resumed agent still THINKS it is mid-checklist (the chat history says
    so), so it must be told the state is gone. `startup` and `clear` stay
    silent: byte-identical to this hook's behaviour before RMP-78."""
    payload = _read_stdin_payload()
    if payload is None:
        return 0
    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return 0
    cs.reset_state(session_id)
    if payload.get("source") == "resume":
        _print_additional_context("SessionStart", _RESUME_CONTEXT)
    return 0


def _cli_reminder() -> int:
    """UserPromptSubmit entry point (RMP-5, RMP-7). Never raises, never
    blocks a prompt -- always returns 0, printing at most one line of
    context. While the probes have run but the session is not yet recorded
    (spec §6), that line is the exact `record_session_start` payload the
    model must copy.

    RMP-14/RMP-15: this hook only ever runs as THIS plugin's own
    UserPromptSubmit hook, so every call means the plugin is active in the
    session (docs/plugin-v2/00-voice.md, prompt step 5) -- print the voice
    reminder FIRST, before any of the branches below, so a caller looking
    for a specific payload's opening "{" (as every existing test here does)
    still finds it on whichever line prints next, not swallowed inside a
    JSON blob printed after it.

    RMP-49: also prints the pending voice note (if any) right after the
    reminder line, so it is delivered once. RMP-159 part 3:
    `voice_check_reminder.print_turn_reminders` now also prints the
    narration-reminder line between those two, on every turn."""
    payload = _read_stdin_payload()
    if payload is None:
        return 0
    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return 0
    voice_check_reminder.print_turn_reminders(session_id)
    if cs.all_passed(session_id):
        # Step 1 is open. RMP-10/RMP-19's headless typed-answer fallback for
        # whichever question step (2+) is current runs first, then RMP-9's
        # reminder: the exact next call the model must make to finish that
        # step (the session-event payload, then the checklist-tick payload)
        # -- same pattern as the record_session_start reminder below. Never
        # blocks the prompt either way.
        try:
            step_recorder.handle_typed_answer(session_id, payload)
        except Exception:
            pass
        text = _next_step_message(session_id)
        if text is not None:
            print(text)
        return 0

    text = _connection_check_message(session_id)
    if text is not None:
        print(text)
        return 0

    # RMP-76: model-only guidance lives here, not in the denial text.
    print(connection_reminder_text.build(cs.read_state(session_id), session_id))
    return 0


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else ""
    try:
        if mode == "record":
            return _cli_record()
        if mode == "reset":
            return _cli_reset()
        if mode == "reminder":
            return _cli_reminder()
    except Exception:
        # Fail-safe: none of these hooks may ever crash a tool call or a
        # prompt submission.
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
