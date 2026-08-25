#!/usr/bin/env bash
# SessionStart hook (G369), matcher: resume.
#
# WHY THIS SCRIPT DOES ALMOST NOTHING: SessionStart fires before MCP servers
# finish connecting, so this cannot call get_creator_brief itself. Its only
# job is to make sure the FIRST thing Claude does, once tools ARE available,
# is the resume check that already lives in rm-content-planner's PLAYBOOK.md
# (Step 1, rule 1 — see P1414). This is plain text to stdout, which Claude
# Code adds to context; exit 0 always (this must never block a session start).
#
# Anchor point for G365 (FRFRMU-310, separate ticket, not built here): that
# ticket wants the same SessionStart hook to also check for a published skill
# update. If it lands later, add a second echo/check below rather than a
# second hook entry — one SessionStart hook is simpler to reason about than
# two competing ones.

echo "SESSION RESUMED. If this account uses the Reach Machine content-planner skill (rm-content-planner), before doing anything else call get_creator_brief and check its planning_progress field — if it is set, follow the resume-check instruction in that skill's PLAYBOOK.md Step 1 (summarize where the plan left off and ask the customer whether to continue, restart, or do something else — never assume). If planning_progress is not set, or this session has nothing to do with content planning, ignore this and proceed normally."

exit 0
