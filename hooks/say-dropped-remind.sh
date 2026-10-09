#!/usr/bin/env bash
# UserPromptSubmit hook (RMP-281): one plain reminder line when the previous
# turn never said the honest line the server handed over. Thin wrapper -- the
# logic lives in the sibling say_dropped.py.
#
# FAIL-SAFE: must never block a prompt. No python -> exit 0, nothing printed.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cat | "$PY" "$DIR/say_dropped.py" remind
exit 0
