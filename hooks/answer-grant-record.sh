#!/usr/bin/env bash
# PostToolUse hook (RMP-201/RMP-76 live bug, 2026-09-28), matcher:
# mcp__plugin_rm-plugin-v2_reachmachine__answer_question
#
# Thin wrapper. All the logic lives in the sibling answer_grant_record.py:
# grants early tool-call access to whatever `_STEP_ALLOW` step the reply's
# own `next_tool` belongs to (the server's own "call this next" instruction).
#
# FAIL-SAFE: must never crash a tool call. No python -> exit 0.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$PY" "$DIR/answer_grant_record.py"
exit 0
