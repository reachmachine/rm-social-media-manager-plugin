#!/usr/bin/env bash
# SessionStart hook (RMP-4), matchers: startup, resume, clear (three
# separate hooks.json entries, never one "a|b" matcher -- see v1's
# test_g369_sessionstart_hook.py for why a piped matcher is unsafe here).
#
# Every session starts closed: delete this session's connection-state file.
# Thin wrapper -- logic lives in the sibling connection_state.py (reset_state),
# reached through connection_state_cli.py; the same connection_state.py the
# recorder and P1596's gate both use.
#
# RMP-78: when the SessionStart `source` is "resume", connection_state_cli.py
# also prints an `additionalContext` line telling the agent its saved
# progress is gone -- `startup` and `clear` stay silent. This wrapper does
# not filter or redirect stdout, so that line passes straight through.
#
# FAIL-SAFE: a SessionStart hook must never block a session starting. If
# python3 (or python) is not on PATH, exit 0 and do nothing.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$PY" "$DIR/connection_state_cli.py" reset
exit 0
