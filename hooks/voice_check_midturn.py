#!/usr/bin/env python3
"""The `PostToolUse` mid-turn voice scan (RMP-198).

STRUCTURAL GAP THIS CLOSES (prompts/COMMS.md, 2026-09-28 HEADS-UP): the
`Stop`-hook checker (`voice_check.py`, wired to `hooks.json`'s `Stop`
event) only ever fires once a whole turn ends with no tool call pending.
Live evidence showed a leaked line ("That's the 4th retry -- pass
accept_partial:true now.") and the `get_fact_tasks` tool call that followed
it were TWO CONTENT BLOCKS OF THE SAME ASSISTANT MESSAGE -- the customer's
chat surface renders text as it streams, so that line was already on
screen long before `Stop` (and the `Stop`-triggered note, delivered only on
the customer's NEXT full message) ever had a chance to react. This is the
THIRD recorded live leak of this exact shape (RMP-159 part 6, RMP-200,
RMP-198 2026-09-28) -- two rounds of "strengthen the skill wording" did not
hold, because the safety NET itself could not see the leak until it was
already too late to matter.

WHY `PostToolUse`, NOT `PreToolUse` (the prompt's own suggestion) -- do not
guess, verify: decoded this box's installed Claude Code build
(2.1.283, `/home/dev/.local/share/claude/versions/2.1.283`, the same
"decode the bundled zod schema" method RMP-78/P1612 used) via `strings`.
Its own bundled hook-output help text (`PDt()`, a debug dump of the exact
output shape per event) lists, verbatim:
    "for PreToolUse": {hookEventName, permissionDecision, permissionDecisionReason, updatedInput}
    "for PostToolUse": {hookEventName, additionalContext}
`PreToolUse`'s `hookSpecificOutput` has NO `additionalContext` field --
only `permissionDecision`/`permissionDecisionReason`/`updatedInput` (all
about ALLOWING or DENYING the pending call, not about steering the model's
own next words). `PostToolUse` is the one event that both (a) can see the
assistant message that triggered a tool call -- the transcript already has
it, since Claude Code writes a message before running any of its tool
calls -- AND (b) can deliver `additionalContext`, read by the model on its
very next turn. A `PreToolUse` hook here would therefore be able to log,
but never able to say anything back to the model -- strictly worse than
this file for the exact same read, so it was dropped rather than run
alongside.

FASTER THAN `Stop`, not a NEW code path: reuses `voice_check.check_message`
(same rules, same jargon.json) and `voice_check_log.append_entry` (same
log file, same 200-line cap) -- only the WHEN and the WHAT TEXT change.
`voice_check_transcript.last_assistant_message_blocks` returns the single
most recent assistant message's text blocks (the narration that led to
THIS tool call), not the whole turn -- see that function's own docstring.

DEDUPE: a message's own transcript uuid is stashed in the SAME per-session
state file `voice_check_block.py` uses (`connection_state.read_raw`/
`write_patch`), so a message with several `tool_use` blocks (parallel tool
calls) is scanned exactly once, not once per call.

FOUNDER RULE KEPT (RMP-159 part 5's own scoping, unchanged): still
log-only. This file never denies or alters the tool call it rides on --
`additionalContext` is a same-turn NUDGE for the model's next reply, not a
block; a genuine internal-name leak's `"block"` disposition (currently
always off, `voice_check_block.BLOCK_LEAKS_ENV`) is entirely
`voice_check.py`'s own concern, untouched by this file.

FAILS OPEN, same convention as `voice_check.py`: any crash, missing
transcript, or missing python means no output and no log entry -- this
scan must never be the reason a tool call's result fails to reach the
model.
"""
from __future__ import annotations

import json
import sys

import connection_state as cs
import voice_check as vc
import voice_check_transcript as vct

_SCANNED_UUID_KEY = "voice_midturn_scanned_uuid"


def _read_stdin_payload() -> dict | None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _already_scanned(session_id: str, uuid: str) -> bool:
    try:
        return cs.read_raw(session_id).get(_SCANNED_UUID_KEY) == uuid
    except Exception:
        return False


def _mark_scanned(session_id: str, uuid: str) -> None:
    try:
        cs.write_patch(session_id, {_SCANNED_UUID_KEY: uuid})
    except Exception:
        pass


def main() -> int:
    """The `PostToolUse` hook entry point. Always returns 0 -- fails open."""
    try:
        payload = _read_stdin_payload()
        if payload is None:
            return 0
        session_id = payload.get("session_id")
        if not isinstance(session_id, str) or not session_id:
            return 0
        transcript_path = payload.get("transcript_path")
        if not isinstance(transcript_path, str) or not transcript_path:
            return 0

        found = vct.last_assistant_message_blocks(transcript_path)
        if found is None:
            return 0
        uuid, blocks = found
        if not blocks:
            return 0
        if uuid is not None and _already_scanned(session_id, uuid):
            return 0
        if uuid is not None:
            _mark_scanned(session_id, uuid)

        problems = vc.check_message("\n\n".join(blocks))
        if not problems:
            return 0

        prompt_id = payload.get("prompt_id")
        vc.log_miss(session_id, prompt_id, problems, blocked=False, source="midturn")

        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PostToolUse",
                "additionalContext": vc.format_reason(problems),
            }
        }))
        return 0
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
