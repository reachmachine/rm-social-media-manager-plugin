#!/usr/bin/env bash
# PreToolUse hook (RMP-257 P2041), matcher: WebSearch
#
# Thin wrapper. All the logic lives in the sibling hangouts_websearch.py, which is a no-op
# unless THIS job holds an open websearch run (step 8/9 research keeps its own rules).
# No python -> exit 0 (allow), same fail-open direction as niche-search-budget.sh.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT="$("$PY" "$DIR/hangouts_websearch.py" gate 2>/dev/null)"
if [ -n "$OUTPUT" ]; then
  printf '%s\n' "$OUTPUT"
fi
exit 0
