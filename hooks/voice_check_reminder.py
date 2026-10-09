#!/usr/bin/env python3
"""RMP-159 part 3: the per-turn narration reminder.

Root cause (live dev, 2026-09-26, on main @46b1861c5, AFTER part 1 and part
2 shipped): the shared voice-rules block inside each skill file is read
ONCE, then the model narrates on a later turn anyway -- "Hi! Let me quickly
check that Reach Machine is connected before we start.", "All three checks
passed. Closing the browser and recording the session now.", even a raw
internal field name in backticks ("`account_owner_type` isn't set yet, so I
need to ask."). A rule read once inside a skill is not enough for the
model.

`connection-reminder.sh` (the UserPromptSubmit hook) already re-prints
`voice_check.REMINDER_LINE` on EVERY customer turn (RMP-14/RMP-15) --
this module adds ONE more fixed line to that same channel. Printed
unconditionally, on every turn, not just while steps 1-6 setup is open:
the live examples show the leak happening throughout the session (the
"closing the browser" example is step 6, well past setup), so gating it
to "setup only" would leave the same leak everywhere else.

Kept out of `voice_check.py` and `connection_state_cli.py` on purpose --
both are already at the 300-line file cap, and this is a distinct concern
(what gets said every turn, not the jargon/paragraph rules or the
CLI dispatch table).

PostToolUse `additionalContext` (P1612's other delivery channel, used by
`connection_state_cli.py`'s `_cli_record`) was considered for this same
line and rejected: that path fires on every matched
`mcp__plugin_*_reachmachine__*` tool call, often several times in one
turn, so a fixed line there would cost N times what one line on
UserPromptSubmit costs (fires exactly once per customer turn). It would
also dilute the "next exact call" payload that channel exists to deliver.
See prompts/COMMS.md for the full note.
"""
from __future__ import annotations

import voice_check

NARRATION_REMINDER_LINE = (
    "Customer sees every word before tool calls too. Give only the "
    "question or result -- never mention checks, fields, tools, or next "
    "steps."
)


def print_turn_reminders(session_id: str) -> None:
    """Prints, in order: the simple-English line, this narration line, then
    any pending voice-miss note (RMP-49) -- at most 3 lines. Never raises:
    `voice_check.take_voice_note` already fails safe to `None`."""
    print(voice_check.REMINDER_LINE)
    print(NARRATION_REMINDER_LINE)
    note = voice_check.take_voice_note(session_id)
    if note:
        print(note)
