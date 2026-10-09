#!/usr/bin/env bash
# PostToolUse report_gap (RMP-281): a filed report ends the one-time reminder. Thin wrapper --
# the logic lives in the sibling report_pending.py.
#
# FAIL-SAFE: must never block anything. No python -> exit 0, nothing saved.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cat | "$PY" "$DIR/report_pending.py" mark
exit 0
