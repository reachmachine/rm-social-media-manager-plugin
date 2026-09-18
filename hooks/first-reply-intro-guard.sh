#!/usr/bin/env bash
# SubagentStop hook (FRFRMU-1513 layer 3), matcher: social-media-manager.
#
# WHY THIS EXISTS: agents/social-media-manager.md's session-start rule says
# the FIRST reply of every session must open with the founder's exact
# FRFRMU-363 sentence, verbatim. A live smoke test (2026-09-15) found the
# agent skipping it and jumping straight into a data question instead --
# nothing errored, nothing logged it, so it could ship broken indefinitely.
# Layers 1-2 (the eval case + the publish-time gate) catch this before a
# release ships. This layer catches it AT RUNTIME, but only when the agent
# runs as a subagent -- the shape a smoke test or an `Agent`-tool invocation
# uses. A customer running `claude --agent social-media-manager` directly is
# a MAIN session, which has no scoped hook to fire here (a plain `Stop` hook
# is not scoped to this agent and would force this sentence into every
# unrelated session that has the plugin installed) -- layers 1-2 are the net
# for that path. See FRFRMU-1513 comment 15712 for why `SubagentStop` (not
# `Stop`) is the only hook Claude Code lets us scope this way.
#
# VERIFIED AGAINST THE INSTALLED BUILD (2026-09-16, "read it from the build,
# don't guess" -- same approach test_g369_sessionstart_hook.py documents):
# grepping the installed Claude Code 2.1.261 bundle confirms (a)
# `SubagentStop`'s payload schema carries `stop_hook_active`, `agent_id`,
# `agent_transcript_path`, `agent_type` (all strings/bool -- so the loop
# guard below is real, not a guess), and (b) hook matchers are compared as
# an unanchored substring/regex test (`matcher.split("|")`, then tested
# against the field, never plain equality) -- so matcher "social-media-manager"
# fires whether the runtime reports the bare agent name or the
# plugin-qualified form ("rm-social-media-manager:social-media-manager").
#
# WHAT IT DOES: reads the SubagentStop payload on stdin. If stop_hook_active
# is true, or the transcript already holds more than one "spoken" assistant
# turn (a turn with real text, not just thinking/tool-use), it stays silent
# -- this only ever checks the FIRST reply, once. Otherwise it reads that
# first reply's text and blocks (asking Claude to revise) unless it opens
# with the founder's exact sentence.
#
# FAILS OPEN: no python3/python, unreadable transcript, or any parse error
# -> exit 0 silently. A broken guard must never block a subagent from
# finishing, and layers 1-2 still apply even when this cannot run.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

CODE='
import json
import re
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

if not isinstance(payload, dict):
    sys.exit(0)

# Loop guard: never re-block a reply we already sent back for revision.
if payload.get("stop_hook_active"):
    sys.exit(0)

transcript_path = payload.get("agent_transcript_path")
if not transcript_path:
    sys.exit(0)

try:
    with open(transcript_path, encoding="utf-8") as fh:
        lines = fh.readlines()
except Exception:
    sys.exit(0)

# FRFRMU-363, verbatim -- agents/social-media-manager.md is the source of
# truth; this string must stay identical to it and to
# skills/rm-content-planner/tests/test_g371_agent_introduction.py'"'"'s
# _FOUNDER_SENTENCE (a static test cross-checks the two never drift apart).
FOUNDER_SENTENCE = "I am your IG Algorithm Reverse Engineering Assistant from Reach Machine. I reverse engineer IG and build a content strategy so you can get Views, Followers, Leads and sales in shortest time possible."


def flat(text):
    return " ".join(text.split())


def spoken_text(entry):
    """The real text of an assistant turn, or None if it has none (a
    thinking-only or tool-use-only turn is not a "reply" yet)."""
    if entry.get("type") != "assistant":
        return None
    message = entry.get("message") or {}
    if message.get("role") != "assistant":
        return None
    parts = []
    for block in message.get("content") or []:
        if isinstance(block, dict) and block.get("type") == "text":
            text = block.get("text")
            if text:
                parts.append(text)
    joined = "".join(parts).strip()
    return joined or None

spoken_turns = []
for raw in lines:
    raw = raw.strip()
    if not raw:
        continue
    try:
        entry = json.loads(raw)
    except Exception:
        continue
    if not isinstance(entry, dict):
        continue
    text = spoken_text(entry)
    if text:
        spoken_turns.append(text)

# Only ever check the FIRST spoken reply, and only once it exists.
if len(spoken_turns) != 1:
    sys.exit(0)

first_reply = flat(spoken_turns[0]).lstrip("\"\x27“‘")
anchor = flat(FOUNDER_SENTENCE)

if first_reply.lower().startswith(anchor.lower()):
    sys.exit(0)

reason = (
    "Your first reply must open with the founder-approved sentence, "
    "verbatim, before anything else: \"" + FOUNDER_SENTENCE + "\" "
    "Prepend it and keep the rest of your reply (FRFRMU-363, FRFRMU-1513)."
)
json.dump({"decision": "block", "reason": reason}, sys.stdout)
sys.stdout.write("\n")
'

"$PY" -c "$CODE"
exit 0
