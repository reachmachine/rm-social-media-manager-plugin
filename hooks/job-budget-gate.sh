#!/usr/bin/env bash
# PreToolUse hook (RMP-201 P4), matcher: WebSearch|mcp__plugin_rm-plugin-v2_(reachmachine|apify|playwright)__.*
#
# Thin wrapper. ALL the logic lives in the sibling job_budget_gate.py, which
# FAILS OPEN and returns instantly for the overwhelming majority of calls
# (anything not inside a subagent) -- see that module's own docstring.
#
# No python -> exit 0 (allow), same fail-open direction.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT="$("$PY" "$DIR/job_budget_gate.py" 2>/dev/null)"
if [ -n "$OUTPUT" ]; then
  printf '%s\n' "$OUTPUT"
fi
exit 0
