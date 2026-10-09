#!/usr/bin/env bash
# UserPromptSubmit hook (RMP-281): one plain line for the model when the report_gap call the server handed
# over was not made. Thin wrapper -- the logic lives in the sibling report_pending.py.
#
# FAIL-SAFE: must never block a prompt. No python -> exit 0, nothing printed.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cat | "$PY" "$DIR/report_pending.py" remind
exit 0
