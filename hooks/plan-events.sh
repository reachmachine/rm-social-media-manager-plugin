#!/usr/bin/env bash
# PostToolUse hook (RMP-201 P4), matcher:
# mcp__plugin_rm-plugin-v2_(reachmachine|apify|playwright)__.*
#
# Thin wrapper. All the logic lives in the sibling plan_events.py: marks the
# plan cache dirty for any tool call OTHER than next_actions/open_workspace/
# get_resume_checklist (plan-recorder.sh's own job).
#
# FAIL-SAFE: must never crash a tool call. No python -> exit 0.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$PY" "$DIR/plan_events.py"
exit 0
