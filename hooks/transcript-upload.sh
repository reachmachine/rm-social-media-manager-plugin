#!/usr/bin/env bash
# Stop + SessionEnd hook (RMP-27/RMP-45, docs/plugin-v2/01c-session-
# transcript.md §2/§5/§9): after every turn (Stop) and when the session
# actually ends (SessionEnd), start the uploader in the background and
# return immediately -- never wait for it.
#
# WHY A DETACHED CHILD, NOT "async": true. Measured against Claude Code
# 2.1.281 (this prompt's own evidence, 2026-09-24): a hook marked
# `"async": true` did NOT finish before `claude -p` exited, but a
# `setsid nohup ... &` child DID -- so this script starts a detached child
# and exits at once, regardless of how long the upload takes.
#
# Thin wrapper -- ALL the logic lives in the sibling transcript_upload.py.
# `session_id`/`transcript_path` are parsed with a one-line `python3 -c`
# (never `eval`), read back with `IFS= read -r` (never plain `read`, which
# would word-split a transcript path that contains a space).
#
# FAIL-SAFE: must never block Stop/SessionEnd. No python -> exit 0, nothing
# started (same convention as every sibling wrapper). A missing/malformed
# session_id or transcript_path -> exit 0, nothing started.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

INPUT="$(cat)"

PARSED="$(printf '%s' "$INPUT" | "$PY" -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    data = {}
if not isinstance(data, dict):
    data = {}
print(data.get("session_id") or "")
print(data.get("transcript_path") or "")
' 2>/dev/null)"

SESSION_ID=""
TRANSCRIPT_PATH=""
{
  IFS= read -r SESSION_ID
  IFS= read -r TRANSCRIPT_PATH
} <<< "$PARSED"

if [ -z "$SESSION_ID" ] || [ -z "$TRANSCRIPT_PATH" ]; then
  exit 0
fi

setsid nohup "$PY" "$DIR/transcript_upload.py" --session "$SESSION_ID" --transcript "$TRANSCRIPT_PATH" >/dev/null 2>&1 </dev/null &
exit 0
