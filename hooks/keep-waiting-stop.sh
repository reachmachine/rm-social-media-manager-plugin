#!/usr/bin/env bash
# Stop hook (RMP-280, P2169): while step 10's research is still being built, keep the chat going instead of letting it
# end its turn with "say check again". Thin wrapper -- the logic is in keep_waiting_stop.py, the decision is the server's.
#
# FAIL-SAFE: must never trap a session. No python -> exit 0, nothing printed.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cat | "$PY" "$DIR/keep_waiting_stop.py"
exit 0
