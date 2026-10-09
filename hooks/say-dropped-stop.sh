#!/usr/bin/env bash
# Stop hook (RMP-281): at the end of a turn, note an honest line the server
# handed over that was never said to the customer. Thin wrapper -- the logic
# lives in the sibling say_dropped.py. Prints nothing.
#
# FAIL-SAFE: must never block anything. No python -> exit 0, nothing saved.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cat | "$PY" "$DIR/say_dropped.py" stop
exit 0
