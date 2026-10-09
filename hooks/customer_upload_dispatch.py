#!/usr/bin/env python3
"""PostToolUse dispatcher for the three customer-upload tools (RMP-194 part
4): `start_customer_upload`, `send_customer_files`, `get_customer_upload`.

A SEPARATE dispatcher/hooks.json entry from `connection_state_cli.py` on
purpose -- that file is already at the 300-line limit, and none of these
three tools appear in any step's allow-list until RMP-194's step-7 part (P1)
lands, so they need no `_next_step_message`/checklist wiring at all today.

FAIL-SAFE: never crashes a tool call. Prints at most one
`hookSpecificOutput.additionalContext` line (a refusal from
`customer_file_upload.handle`); everything else is a silent side-effect
(session-state writes).
"""
from __future__ import annotations

import json
import sys

import customer_file_upload
import customer_upload_path_guard as guard
import customer_upload_state as cus
from payload_util import tool_args


def _print_additional_context(event_name, message: str | None) -> None:
    if not message:
        return
    if event_name not in ("PostToolUse", "PostToolUseFailure"):
        return
    try:
        print(json.dumps({
            "hookSpecificOutput": {"hookEventName": event_name, "additionalContext": message}
        }))
    except Exception:
        pass


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
    tool_name = payload.get("tool_name")
    if not isinstance(tool_name, str):
        return 0
    event_name = payload.get("hook_event_name")

    try:
        if tool_name.endswith("__start_customer_upload"):
            cus.handle_start(session_id, payload)
            if tool_args(payload).get("purpose") == "business_doc":
                guard.ensure_files_folder(customer_file_upload.base_dir(payload))
        elif tool_name.endswith("__send_customer_files"):
            message = customer_file_upload.handle(session_id, payload)
            _print_additional_context(event_name, message)
        elif tool_name.endswith("__get_customer_upload"):
            cus.handle_get_done(session_id, payload)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
