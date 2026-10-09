#!/usr/bin/env bash
# PostToolUse AskUserQuestion (RMP-201): the model asked the customer something,
# so a pending server question counts as shown. Thin wrapper -- the logic lives
# in the sibling ask_dropped.py.
#
# FAIL-SAFE: must never block anything. No python -> exit 0, nothing saved.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cat | "$PY" "$DIR/ask_dropped.py" mark
exit 0
