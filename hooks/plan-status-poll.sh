#!/usr/bin/env bash
# UserPromptSubmit hook (RMP-201 P4): polls GET /api/v1/plugin/plan-status,
# dormant outside drive mode. Thin wrapper -- all the logic (gate, throttle,
# timeout, fail-safe) lives in the sibling plan_status_poll.py.
#
# FAIL-SAFE: must never block a prompt. No python -> exit 0, nothing polled.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$PY" "$DIR/plan_status_poll.py"
exit 0
