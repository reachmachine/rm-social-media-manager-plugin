#!/usr/bin/env bash
# SessionStart hook (RMP-76 token pass 2): prints the shared voice + business-fact
# rules ONCE, as additionalContext. They used to be copied into six skill files,
# and every copy was paid for again on every later model call.
# Logic lives in session_rules.py. FAILS OPEN: python missing or crashing prints
# nothing and the session starts as normal.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$PY" "$DIR/session_rules.py" 2>/dev/null
exit 0
