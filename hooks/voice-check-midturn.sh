#!/usr/bin/env bash
# PostToolUse hook (RMP-198). Logic lives in the sibling voice_check_midturn.py.
#
# FAILS OPEN, same convention as voice-check.sh: a scanner must never be
# the reason a tool call's result fails to reach the model. Python
# missing/crashing falls straight through to `exit 0` with no output.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT="$("$PY" "$DIR/voice_check_midturn.py" 2>/dev/null)"
STATUS=$?

if [ "$STATUS" -eq 0 ] && [ -n "$OUTPUT" ]; then
  printf '%s\n' "$OUTPUT"
fi
exit 0
