#!/usr/bin/env bash
# Stop hook (RMP-14, RMP-15). Logic lives in the sibling voice_check.py.
#
# FAILS OPEN, deliberately the OPPOSITE of connections-gate.sh: a voice
# checker must never be the reason a customer's reply gets stuck. So unlike
# the gate, this wrapper does NOT turn "python crashed" or "python missing"
# into a block -- both cases fall straight through to `exit 0` with no
# output, which Claude Code reads as "let the reply through unchanged."

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT="$("$PY" "$DIR/voice_check.py" 2>/dev/null)"
STATUS=$?

if [ "$STATUS" -eq 0 ] && [ -n "$OUTPUT" ]; then
  printf '%s\n' "$OUTPUT"
fi
exit 0
