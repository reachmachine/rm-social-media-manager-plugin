#!/usr/bin/env bash
# PreToolUse hook (RMP-5), matchers:
#   mcp__plugin_rm-plugin-v2_(reachmachine|apify|playwright)__.*
#   Skill
#
# Thin wrapper. ALL the decision logic lives in the sibling
# connections_gate.py, EXCEPT the two things that must stay allowed even if
# python crashes: the probe calls themselves, and the connection-check
# skill. Those two are checked here in plain text, on the raw JSON, before
# python ever runs -- a missing python3 must never be able to trap them
# (spec: "Fail-safe direction").
#
# These plain-text checks are intentionally a little LOOSER than
# connections_gate.py's exact-match logic: they accept ANY plugin name in
# the probe/Skill tool names below, not just this one's, because without
# python this script cannot read plugin.json to find this plugin's own
# name (RMP-177's fix scopes hooks.json's own MATCHER, and connections_
# gate.py's Python parsing, to the real name -- both CAN read or embed it;
# this fallback text cannot). That looseness only matters in two narrow
# cases: the crash path (python missing), and a test driving this script
# directly, bypassing hooks.json's own matcher -- in real sessions,
# hooks.json's matcher already only ever hands this script OUR OWN
# plugin's tool names, so accepting a wider pattern here changes nothing
# real. Letting a differently-named plugin's identically-shaped probe or
# skill through during an already-degraded session is far safer than
# locking a customer out of the one thing that can unblock them. See
# connections_gate.py's module docstring and prompts/COMMS.md for the
# non-crash-path exact match, and the architect note about this trade-off.

INPUT="$(cat)"

_GENERIC_DENY='{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"[connections_unconfirmed]"}}'

# ":" with optional surrounding whitespace -- Claude Code's own hook payloads
# are compact (no spaces), but json.dumps()'s default output (used by this
# suite's own tests, and possibly by other future callers) inserts a space
# after every colon. Matching both keeps this from silently depending on one
# exact serializer's spacing.
_SEP='[[:space:]]*:[[:space:]]*'

_allow_if() {
  printf '%s' "$INPUT" | grep -qE "$1"
}

# reachmachine probe: get_billing_status takes no arguments, always counts.
if _allow_if "\"tool_name\"${_SEP}\"mcp__plugin_[^\"]*_reachmachine__get_billing_status\""; then
  exit 0
fi

# apify probe: exact runId only.
if _allow_if "\"tool_name\"${_SEP}\"mcp__plugin_[^\"]*_apify__get-actor-run\"" \
   && _allow_if "\"runId\"${_SEP}\"rmp-connection-probe-000\""; then
  exit 0
fi

# playwright probe: exact url only.
if _allow_if "\"tool_name\"${_SEP}\"mcp__plugin_[^\"]*_playwright__browser_navigate\"" \
   && _allow_if "\"url\"${_SEP}\"https://example\\.com/\""; then
  exit 0
fi

# browser_close is always allowed -- it cleans up the probe, it never
# reveals or spends anything.
if _allow_if "\"tool_name\"${_SEP}\"mcp__plugin_[^\"]*_playwright__browser_close\""; then
  exit 0
fi

# connection-check skill, any plugin name (see header comment on why).
if _allow_if "\"tool_name\"${_SEP}\"Skill\"" && _allow_if "\"skill\"${_SEP}\"[^\"]+:connection-check\""; then
  exit 0
fi

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
if ! "$PY" -c "" >/dev/null 2>&1; then
  # No python at all. Fails CLOSED: everything reaching this point (by the
  # matcher's own scope) is either a non-probe tool on our three servers or
  # a non-connection-check Skill call, and connections_gate.py's exact
  # ownership check cannot run without python -- deny with a generic reason
  # rather than guess.
  printf '%s\n' "$_GENERIC_DENY"
  exit 0
fi

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Capture BOTH python's stdout and its exit status. connections_gate.py's own
# main() already catches every exception it anticipates and prints a deny for
# those -- this is the second, independent layer for anything it could NOT
# anticipate (a crash at import time, a syntax error in a bad deploy, an
# interpreter-level failure): if python exits non-zero for ANY reason, deny.
# Never trust "no output" from a non-zero exit as if it meant allow --
# "no output" is only a real allow when python exited 0. Stderr (tracebacks)
# is discarded, never treated as the decision.
OUTPUT="$(printf '%s' "$INPUT" | "$PY" "$DIR/connections_gate.py" 2>/dev/null)"
STATUS=$?

if [ "$STATUS" -ne 0 ]; then
  printf '%s\n' "$_GENERIC_DENY"
  exit 0
fi

if [ -n "$OUTPUT" ]; then
  printf '%s\n' "$OUTPUT"
fi
exit 0
