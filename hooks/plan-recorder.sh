#!/usr/bin/env bash
# PostToolUse hook (RMP-201 P4), matcher:
# mcp__plugin_rm-plugin-v2_reachmachine__(next_actions|open_workspace|get_resume_checklist)
#
# Thin wrapper. All the logic lives in the sibling plan_recorder.py: writes
# the plan cache file and applies the tick-sync rule.
#
# FAIL-SAFE: must never crash a tool call. No python -> exit 0.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$PY" "$DIR/plan_recorder.py"
exit 0
