#!/usr/bin/env bash
# UserPromptSubmit hook (RMP-194 part 4): saves the customer's own last
# typed message so a LATER PostToolUse hook (customer_file_upload.py) can
# check a file path against it. Thin wrapper -- all the logic lives in the
# sibling capture_last_prompt.py.
#
# FAIL-SAFE: must never block a prompt. No python -> exit 0, nothing saved.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cat | "$PY" "$DIR/capture_last_prompt.py"
exit 0
