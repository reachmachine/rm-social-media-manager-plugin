#!/usr/bin/env bash
# PreToolUse hook (RMP-194 part 4), matcher: Read|Bash|Glob.
#
# Thin wrapper. ALL the logic lives in the sibling customer_upload_gate.py,
# which FAILS OPEN (the opposite of connections-gate.sh) -- these are
# built-in tools, not this plugin's own, so a crash here must never brick an
# unrelated Read/Bash/Glob call in any session.
#
# No python -> exit 0 (allow), same fail-open direction.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT="$("$PY" "$DIR/customer_upload_gate.py" 2>/dev/null)"
if [ -n "$OUTPUT" ]; then
  printf '%s\n' "$OUTPUT"
fi
exit 0
