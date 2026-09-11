#!/usr/bin/env bash
# PreToolUse hook (FRFRMU-1152), matcher: apify--instagram-.*
#
# WHY THIS EXISTS: every Reach Machine MCP tool takes its input wrapped in an
# `args` box (`{"args": {...}}`), so an agent that has made ~40 RM calls learns
# "everything goes in args" and carries that habit into the four bundled Apify
# Instagram actors -- which declare their properties at the ROOT of the call
# and have no `args` property at all. On 2026-09-10 that produced a 100%
# failure on Step 2 (every plan, angles A/B/C/E): the agent sent the wrapped,
# stringified shape, got "root: must have required property 'hashtags'" back,
# retried the SAME wrong shape four times, then told the customer "the tooling
# itself is broken." Layer A (the playbook) teaches the right shape up front;
# this hook is the second line of defence that catches the mistake in the act,
# before a real customer session repeats it.
#
# WHAT IT DOES: reads the PreToolUse payload on stdin. If tool_input carries
# an `args` key and NONE of the real root keys (hashtags/search/usernames/
# directUrls), it denies the call and tells the agent to unwrap, in plain
# words that also say "this is not a tool fault, do not retry the wrapped
# shape and do not report the tool as broken." A bare, correctly-shaped call
# passes through with no output at all.
#
# FAILS OPEN: no python3/python on the machine -> exit 0 silently. Layer A
# (the playbook rule) still applies even when this hook cannot run. A broken
# guard must never block a legitimate call.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

CODE='
import json
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

tool_input = payload.get("tool_input")
if not isinstance(tool_input, dict) or "args" not in tool_input:
    sys.exit(0)

ROOT_KEYS = ("hashtags", "search", "usernames", "directUrls")
if any(key in tool_input for key in ROOT_KEYS):
    sys.exit(0)

raw = tool_input.get("args")
if isinstance(raw, str):
    try:
        unwrapped = json.loads(raw)
    except Exception:
        unwrapped = raw
else:
    unwrapped = raw

reason = (
    "This Apify actor takes its input at the ROOT of the call, as an object -- "
    "not inside Reach Machine'"'"'s `args` box, and never as a JSON string. "
    "Unwrapped payload: " + json.dumps(unwrapped) + ". "
    "This is not a tool fault; do not retry the wrapped shape and do not "
    "report the tool as broken."
)

json.dump(
    {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    },
    sys.stdout,
)
sys.stdout.write("\n")
'

"$PY" -c "$CODE"
exit 0
