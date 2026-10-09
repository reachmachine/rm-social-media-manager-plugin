#!/usr/bin/env bash
# PostToolUse hook (RMP-201 drive-mode follow-up #2), matcher:
# mcp__plugin_rm-plugin-v2_reachmachine__(get_job|report_job)
#
# Thin wrapper. All the logic lives in the sibling job_tool_cache_record.py:
# caches (or clears) the drive-mode early-tool-access allow-list for the
# ONE subagent (`agent_id`) that just called get_job/report_job.
#
# FAIL-SAFE: must never crash a tool call. No python -> exit 0.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$PY" "$DIR/job_tool_cache_record.py"
exit 0
