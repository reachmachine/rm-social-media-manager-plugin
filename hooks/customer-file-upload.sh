#!/usr/bin/env bash
# PostToolUse hook (RMP-194 part 4), matcher:
#   mcp__plugin_rm-plugin-v2_reachmachine__(start_customer_upload|send_customer_files|get_customer_upload)
#
# Thin wrapper. ALL the logic lives in the sibling customer_upload_dispatch.py.
# A SEPARATE hooks.json entry/script from record-connection-probe.sh on
# purpose -- connection_state_cli.py is already at the 300-line limit.
#
# FAIL-SAFE: this must never crash a tool call. No python -> exit 0.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$PY" "$DIR/customer_upload_dispatch.py"
exit 0
