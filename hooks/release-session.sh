#!/usr/bin/env bash
# SessionEnd hook (RMP-79 part 3, docs/plugin-v2/08-one-chat-per-workspace.md
# "Design" step 4): release this chat's workspace lease when the session ends
# cleanly, so the workspace is free for another chat right away instead of
# waiting out the 15-minute lease TTL.
#
# Runs SYNCHRONOUSLY (unlike transcript-upload.sh's detached background
# child) — release_session.py's own HTTP call is capped at a 3-second
# timeout, so this never blocks SessionEnd for long, and there is nothing
# here worth surviving the process exiting early the way a multi-batch
# transcript upload is.
#
# Thin wrapper -- ALL the logic lives in the sibling release_session.py.
# `session_id` is parsed with a one-line `python3 -c` (never `eval`), read
# back with `IFS= read -r` (never plain `read`).
#
# FAIL-SAFE: must never block or error SessionEnd. No python -> exit 0,
# nothing run. A missing/malformed session_id -> exit 0, nothing run.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT="$(cat)"

SESSION_ID="$(printf '%s' "$INPUT" | "$PY" -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    data = {}
if not isinstance(data, dict):
    data = {}
print(data.get("session_id") or "")
' 2>/dev/null)"

if [ -z "$SESSION_ID" ]; then
  exit 0
fi

"$PY" "$DIR/release_session.py" --session "$SESSION_ID" >/dev/null 2>&1
exit 0
