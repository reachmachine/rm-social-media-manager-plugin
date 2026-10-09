#!/usr/bin/env bash
# PostToolUse AND PostToolUseFailure hook (RMP-257 P2041), matcher: WebSearch. The payload's
# hook_event_name tells the two apart.
#
# Thin wrapper. All the logic lives in the sibling hangouts_websearch.py: it posts the links of
# an issued search to the server, and is a no-op unless THIS job holds an open websearch run.
# FAIL-SAFE: must never crash a tool call. No python -> exit 0.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$PY" "$DIR/hangouts_websearch.py" record 2>/dev/null   # RMP-280: stdout may carry updatedToolOutput
exit 0
