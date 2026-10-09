#!/usr/bin/env python3
"""Step reminder formatting (RMP-58: split from `checklist_recorder.py` to
keep it under 300 lines). Pure formatting: takes the dict from
`build_step_reminder` and returns the exact prose+JSON line."""
from __future__ import annotations

import json
from typing import Any


def format_step_reminder(reminder: dict[str, Any]) -> str | None:
    """The exact prose+JSON line for whatever `build_step_reminder` returned
    -- shared by the UserPromptSubmit reminder (`connection_state_cli.
    _cli_reminder`) and, since P1612, the IMMEDIATE PostToolUse delivery
    (`connection_state_cli._next_step_message`), so the two channels can
    never say something different. Returns None only if the payload cannot
    be serialised (never expected -- every field is a plain str/dict).
    Three shapes:
    {"call", "payload"} -> "call X with exactly this payload: {...}";
    {"call", "payload", "say"} -> the same, but first tells the model the
    exact line to say to the customer (P1649, RMP-53);
    {"instruction"} -> a plain instruction with no call (RMP-58 reoffer)."""
    try:
        instruction = reminder.get("instruction")
        if isinstance(instruction, str) and instruction:
            return "Reach Machine plugin: " + instruction
        payload_json = json.dumps(reminder["payload"])
        call = reminder["call"]
    except Exception:
        return None
    text = "Reach Machine plugin: "
    say = reminder.get("say")
    if isinstance(say, str) and say:
        text += 'first tell the customer exactly this line: "' + say + '" Then '
    text += "call " + call + " with exactly this payload: " + payload_json
    if call in ("get_resume_checklist", "open_workspace"):
        # RMP-54: the agent tried to Read/Bash steps.json four times.
        # RMP-76: open_workspace also carries the full manifest.
        text += " This payload is complete. Never read steps.json or any other plugin file."
    return text
