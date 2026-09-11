#!/usr/bin/env bash
# SessionStart hook (G369, widened by FRFRMU-985), matcher: startup AND resume.
#
# WHY THIS SCRIPT DOES ALMOST NOTHING: SessionStart fires before MCP servers
# finish connecting, so this cannot call get_creator_brief itself. Its only
# job is to make sure Claude checks planning_progress at the first NATURAL
# opportunity once tools ARE available -- the resume-check logic itself lives
# in rm-content-planner's PLAYBOOK.md (Step 1, rule 1 -- see P1414/FRFRMU-981).
# This is plain text to stdout, which Claude Code adds to context; exit 0
# always (this must never block a session start).
#
# FRFRMU-985 widened the matcher from "resume" only to "startup" AND "resume"
# -- two separate hooks.json SessionStart entries, both pointing at this same
# script (SessionStart's matcher checks against the "source" field, which is
# always exactly one of "startup"/"resume"/"clear"/"compact"/"fork" -- two
# single-value entries is the unambiguous way to cover two of those sources,
# verified against the installed Claude Code build's own source-value list
# rather than guessed). Why cover startup at all: planning_progress lives in
# the Creator Brief, which outlives any one Claude Code session -- a customer
# who opens a brand-new session ("startup") can still have an unfinished plan
# from days ago, and the old "resume"-only matcher only caught the case where
# they reopened the exact same conversation. FRFRMU-985 also reworded the
# instruction below for zero customer-facing noise: never interrupt the
# customer's actual first question, mention this at most once per session,
# and stay completely silent unless the saved record is genuinely live
# (status "in_progress" and updated within the last 14 days -- the same rule
# step-01-intake.md already enforces for FRFRMU-981, so both places agree).
#
# FRFRMU-310/G365 (admin-published skill-update notice): this was the
# anticipated second SessionStart check an earlier version of this comment
# named. It shipped -- but NOT here. It lives in SKILL.md's "Check for a
# published update (G365)" section, called on the first tool call of every
# content-planner run. See test_g365_skill_update_check.py, which explains
# why it belongs there and not in this hook: this hook still cannot call
# get_skill_version before MCP servers connect (widening the matcher above
# does not change that), and SKILL.md is already read on every invocation,
# resumed or fresh. Do not add a second, duplicate update-check here -- two
# places deciding whether an update is available could disagree.

echo "SESSION STARTED (new or resumed). Do NOT let this interrupt or delay whatever the customer asks first -- answer that first, normally, like any other session. Then, at the first natural opportunity (for example, the end of your first reply this session, or right before Step 1 if this session turns out to be about content planning) -- ONCE only, never repeated again later in this same session -- do this: if this account uses the Reach Machine content-planner skill (rm-content-planner), call get_creator_brief and read its planning_progress field. Only bring it up if planning_progress.status is exactly \"in_progress\" AND its updated_at is within the last 14 days. For anything else -- \"delivered\", \"abandoned\", a record older than 14 days, or a legacy record with no status field at all -- say nothing about it and move on as if it weren't there; that is not a bug, it is the record having nothing left to resume. When it DOES qualify, follow the resume-check instruction in that skill's PLAYBOOK Step 1 (playbook/step-01-intake.md): summarize where the plan left off in one line and ask the customer whether to continue, restart, or do something else -- never assume. If this session has nothing to do with content planning, or planning_progress isn't set at all, ignore all of this and proceed normally."

exit 0
