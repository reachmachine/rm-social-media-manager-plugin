#!/usr/bin/env bash
# PreToolUse hook (RMP-197 P3), matcher: WebSearch|WebFetch
#
# Thin wrapper. ALL the logic lives in the sibling niche_search_budget.py,
# which is a no-op for the overwhelming majority of calls (research not
# active this session) -- see that module's own docstring.
#
# No python -> exit 0 (allow), same fail-open direction as job-budget-gate.sh.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT="$("$PY" "$DIR/niche_search_budget.py" 2>/dev/null)"
if [ -n "$OUTPUT" ]; then
  printf '%s\n' "$OUTPUT"
fi
exit 0
