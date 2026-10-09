#!/usr/bin/env bash
# UserPromptSubmit hook (RMP-5). Covers slash commands and anything else the
# customer types directly, which never goes through the Skill tool -- so the
# PreToolUse gate alone would never remind them.
#
# Thin wrapper -- logic (all_passed, and RMP-7's record_session_start
# reminder payload) lives in connection_state.py / session_record.py,
# reached through connection_state_cli.py. Once step 1 is open, this same
# entry point also runs RMP-10/RMP-19's headless typed-answer fallback for
# question steps 2+ (step_recorder.py's handle_typed_answer), then RMP-9/
# RMP-18's own reminder of the exact next checklist/session-event call
# (checklist_recorder.py's build_step_reminder).
# Must NEVER block a prompt: always exits 0, printing at most one line.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$PY" "$DIR/connection_state_cli.py" reminder
exit 0
