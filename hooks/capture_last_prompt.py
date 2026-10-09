#!/usr/bin/env python3
"""UserPromptSubmit hook: saves the customer's own last typed message
(RMP-194 part 4).

Nothing before this saved a prompt's text ACROSS hook calls --
`step_recorder.handle_typed_answer` only reads `payload["prompt"]` live,
inside the SAME UserPromptSubmit invocation. `customer_file_upload.py`'s
path guard needs it later, from a different hook (`send_customer_files`'s
PostToolUse), so it has to live in the shared session-state file in between
-- see `customer_upload_state.py`'s own docstring for the fuller "why".

Standalone (own `hooks.json` entry, own tiny `.sh` wrapper) rather than
folded into `connection_state_cli.py`'s `_cli_reminder` -- that file is
already at the 300-line limit.

Never blocks a prompt, never prints anything (this hook has nothing to say
to the model) -- purely a side-effecting state write.
"""
from __future__ import annotations

import json
import sys

import customer_turn_release
import customer_upload_state as cus
import payload_util
import system_prompt_ids


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return 0
    prompt = payload.get("prompt")
    if isinstance(prompt, str) and payload_util.is_system_generated_prompt(prompt):
        system_prompt_ids.record(session_id, payload.get("prompt_id"))  # spend_gate denies a confirm here
    elif isinstance(prompt, str):
        try:
            cus.record_last_prompt(session_id, prompt)
        except Exception:
            pass
        customer_turn_release.release(session_id)  # a real customer turn frees a held question (RMP-201)
    return 0


if __name__ == "__main__":
    sys.exit(main())
