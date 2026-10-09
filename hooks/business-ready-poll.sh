#!/usr/bin/env bash
# UserPromptSubmit hook (RMP-194 P2): polls GET /api/v1/plugin/business-ready
# so the plugin learns step 7 is ready with no model tokens spent. Thin
# wrapper -- all the logic (gate, throttle, timeout, fail-safe) lives in the
# sibling business_ready_poll.py.
#
# FAIL-SAFE: must never block a prompt. No python -> exit 0, nothing polled.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cat | "$PY" "$DIR/business_ready_poll.py"
exit 0
