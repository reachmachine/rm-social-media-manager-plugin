#!/usr/bin/env bash
# MessageDisplay hook (RMP-159/RMP-198). Logic lives in step1_silence.py.
# FAILS OPEN: python missing or crashing prints nothing, so the text shows as normal.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT="$("$PY" "$DIR/step1_silence.py" 2>/dev/null)"
if [ -n "$OUTPUT" ]; then
  printf '%s\n' "$OUTPUT"
fi
exit 0
