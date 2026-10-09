#!/usr/bin/env bash
# PostToolUse + PostToolUseFailure hook (RMP-3, RMP-4), matcher:
# mcp__plugin_rm-plugin-v2_(reachmachine|apify|playwright)__(get_billing_status|get-actor-run|browser_navigate|record_session_start|list_workspaces|set_active_workspace|get_creator_brief|update_creator_brief|record_session_event|get_resume_checklist|record_checklist_step|add_to_watchlist|refresh_competitor|start_website_read|finish_website_read|wait_for_website_read|browser_evaluate|get_website_read_status|save_business_fact|search_business_knowledge|get_next_fact_task|get_fact_tasks|save_business_facts)
# PLUS a separate PostToolUse-only entry for the built-in "AskUserQuestion"
# tool (RMP-10, RMP-19 -- question steps 2+, see step_recorder.py).
#
# start_website_read/finish_website_read/browser_evaluate (RMP-66) -- step
# 6's open website read and the page-upload hook -- are read here through
# connection_state_cli.py's own dispatch, not step_recorder.py's table.
#
# Thin wrapper. ALL the logic lives in the sibling connection_state.py /
# session_record.py / step_recorder.py / checklist_recorder.py, reached
# through connection_state_cli.py, so it can be unit-tested directly and
# P1596's connections-gate.sh can import the exact same state functions --
# never re-implemented twice. See connection_state.py's module docstring for
# the state file shape and the probe-matching rules, session_record.py for
# record_session_start / the local queue (RMP-7), step_recorder.py for the
# question-step tools and AskUserQuestion, and checklist_recorder.py for the
# resume checklist / session-event tools (RMP-9, RMP-18).
#
# FAIL-SAFE: this must never crash a tool call. If python3 (or python) is
# not on PATH, exit 0 and do nothing -- same pattern as v1's
# spend-needs-human-yes.sh.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$PY" "$DIR/connection_state_cli.py" record
exit 0
