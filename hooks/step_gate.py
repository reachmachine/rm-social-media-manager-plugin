#!/usr/bin/env python3
"""PreToolUse gate rules for question steps 2+ and the resume checklist
(RMP-9, RMP-10, RMP-18, RMP-19).

Spec: docs/plugin-v2/02-workspace-selection.md "Enforcement -- hooks, not
sentences", docs/plugin-v2/03-whose-account.md "The reusable question
step", and docs/plugin-v2/00-resume-checklist.md "The model cannot tick a
box it didn't earn". Called from `connections_gate.py` ONLY once step 1
(`connection_check`) is already open (`connection_state.all_passed` is
True) -- everything before that point is still step 1's own business.

GENERIC: reads `steps_manifest.py` for step order/kind/question/brief_key,
plus one small per-step allow-list of "which reachmachine tools are needed
to pass this step" (`_STEP_ALLOW` below) -- the one hard-coded piece the
spec allows. A later step's spec adds one line here, not a new gate.

GATE ORDERING NOW NEEDS A TICK, NOT JUST A PASS (RMP-9): `_first_unpassed`
only counts a step finished once `record_checklist_step("done")` was
accepted (`step_state.ticked`), except `connection_check` (RMP-7, built
before this rule existed) -- this is what makes "every step writes to
three places" (03-whose-account.md) a hook rule: `steps_passed` alone only
proves the Reach Machine write happened.

THE SPEND GATE (RMP-23): once every step rule above allows a call, `decide`
hands off to `spend_gate.decide` for the six credit-spending tools. Runs
LAST, so a preview denied here never reaches the spend gate and can never
authorise a confirm. `add_to_watchlist` ALSO gets `own_account_mismatch.
check_include_flagged` (founder decision 6).

**Drive-mode job bypass (RMP-201/RMP-76).** `_allowed_suffixes` below can be
SKIPPED for one call by `step_gate_plan.job_ordering_bypass` (a running
job's own tools) or `.early_allow` (a coarser session-wide fallback, same
"server proposed it early" bug class) -- see their own docstrings.

FAILS CLOSED like `connections_gate.py`: never raises on its own, and an
unexpected exception is caught by that module's top-level try/except.

SPLIT OUT (each kept under the 300-line limit): step 4's own-account rules
live in `step_gate_own_account.py`, resume-checklist rules in `step_gate_
checklist.py`, step 5's revenue rules in `step_gate_revenue.py`, workspace-
pin/pick rules in `step_gate_workspace.py`, cache-aware `_STEP_ALLOW`/
`_STEP_DENY_REASON` reads in `step_gate_rules.py`, `record_session_event`
rules in `step_gate_session_event.py`.

RMP-173 P3: `_STEP_ALLOW`/`_STEP_DENY_REASON` below are now the FALLBACK --
a cached session's `load_steps(session_id)` steps carry their own
`allow`/`deny_reason`, and `step_gate_rules.py` reads those first. Both
tables stay right here, unrenamed: a backend test AST-parses them by name.
"""
from __future__ import annotations

import connection_state as cs
import deny_lines
import own_account_mismatch
import own_account_not_found
from payload_util import tool_args
import spend_gate
import step_gate_brief as brief_gate
import step_gate_checklist as checklist_gate
import step_gate_own_account as own_account
import step_gate_plan
import step_gate_revenue as revenue_gate
import step_gate_rules
import step_gate_session_event
import step_gate_workspace as workspace_gate
import step_order
import step_recorder_revenue as revenue_recorder
import step_skip
import step_state
import steps_manifest
import website_mismatch
import website_search_state

# Tools whose whole job is to point the session at a (possibly different)
# workspace -- exempt from the pin check, and both checked the same way
# against the customer's own pick (RMP-76: `open_workspace` replaces the
# five calls after a pick with one -- see `step_gate_workspace.py`).
_WORKSPACE_PICKING_TOOLS = frozenset({"set_active_workspace", "open_workspace"})

# Tools each step ADDS to what is allowed while it is the current (not yet
# passed) step. Cumulative: once `account_owner_type` is current, everything
# `choose_workspace` allowed stays allowed too (spec: "additionally allow"),
# because "switch workspace" can happen at any later point.
_STEP_ALLOW: dict[str, set[str]] = {
    "choose_workspace": {
        "list_workspaces", "set_active_workspace", "open_workspace",
        # RMP-22: creating one IS a way to choose one -- and it stays allowed
        # at every later step (cumulative), so "make a new one" never forces
        # finishing steps in the old workspace first.
        "create_workspace",
        "record_session_event", "get_resume_checklist", "record_checklist_step",
        # RMP-201 P4: the 4 planner MCP tools, cumulative from here on --
        # matches agent_step_rules.STEPS["choose_workspace"]["allow"].
        "next_actions", "answer_question", "get_job", "report_job", "report_gap",  # RMP-281: report_gap at every step
    },
    "account_owner_type": {
        "get_creator_brief", "update_creator_brief",
        # RMP-26: facts from chat can be saved from step 3 on, not only at step 6.
        "get_business_facts", "save_business_fact",
        # RMP-156: `update_creator_brief` needs `skill_version`, and this is the
        # only tool that reports it -- without this line the very call RMP-156
        # tells the agent to make would be denied here with "Finish step 3 first."
        "get_skill_version",
    },
    "own_instagram_account": {
        "add_to_watchlist", "refresh_competitor", "record_session_event",
        # RMP-113: change the own account (rename vs a different business).
        "change_own_account",
    },
    "revenue_model": {
        "get_creator_brief", "update_creator_brief", "record_session_event",
        # RMP-95: `update_creator_brief` needs `skill_version`, and this is the only
        # tool that reports it -- without this line the very call RMP-95 tells the
        # agent to make would be denied here with "Finish step 5 first."
        "get_skill_version",
    },
    "website": {
        "start_website_read", "finish_website_read", "get_website_read_status",
        "wait_for_website_read", "get_next_fact_task", "skip_business_fact",  # RMP-76
        "search_business_knowledge", "get_business_facts", "save_business_fact",
        "get_fact_tasks", "save_business_facts",  # RMP-96
        "cancel_website_read",  # RMP-169
        "record_session_event",
        "start_reviews_fetch", "finish_reviews_fetch",  # RMP-190
        # RMP-193 part 1: section 6b's "your site is a shop" choice, and
        # sending a product-list export file (the shared upload primitive,
        # purpose="catalogue") -- both happen during step 6, before step 7.
        "choose_product_list_source",
        "start_customer_upload", "send_customer_files", "get_customer_upload",
        "sync_product_list",  # RMP-193 parts 2/3
    },
    # wait_for steps (7-10): parity rows only, see docs/plugin-v2/planner-notes/step_gate.md
    "business_review": {
        "get_business_review", "answer_business_review",
        "get_fact_tasks", "save_business_facts", "save_business_fact",
        "get_business_facts", "record_session_event",
        # RMP-194 P4/P2: "Add more" -> a customer document.
        "start_customer_upload", "send_customer_files", "get_customer_upload",
    },
    "pick_niche": {
        "start_niche_pick", "save_niche_research", "choose_niche",
        "get_business_facts", "record_session_event",
    },
    "dream_customer": {
        "start_dream_customer", "save_dream_customer", "get_dream_customer",
        "choose_main_persona", "get_business_facts", "record_session_event",
    },
    "where_to_find": {
        "get_hangouts", "save_hangout_keywords", "get_hangouts_work", "save_hangout_mentions",
        "answer_question", "record_session_event",
    },
}

def _deny(reason: str) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }


def _tool_suffix(tool_name: str) -> str:
    """The tool's own name, e.g. "list_workspaces" out of
    "mcp__plugin_rm-plugin-v2_reachmachine__list_workspaces"."""
    return tool_name.rsplit("__", 1)[-1]


def _allowed_suffixes(steps: list[dict], current: dict) -> set[str]:
    return step_gate_rules.allowed_suffixes(steps, current, _STEP_ALLOW)


def _decide_steps(payload: dict, session_id: str, tool_input: dict) -> dict | None:
    """None = allow. Called once step 1 is open (`tool_input` pre-unwrapped)."""
    tool_name = payload.get("tool_name")
    step_state.sync_connection_check(session_id)
    state = step_state.read_state(session_id)
    steps = steps_manifest.load_steps(session_id)
    suffix = _tool_suffix(tool_name)

    if suffix not in _WORKSPACE_PICKING_TOOLS:
        deny = workspace_gate.check_workspace_pin(tool_input, state)
        if deny is not None:
            return deny

    if suffix == "update_creator_brief":
        deny = brief_gate.check_brief_private_details(tool_input, session_id)
        if deny is not None:
            return deny
        deny = brief_gate.check_brief_answers(tool_input, steps, state, session_id)
        if deny is not None:
            return deny
        deny = brief_gate.check_brief_key_order(tool_input, steps, state, session_id)
        if deny is not None:
            return deny
        deny = revenue_gate.check_revenue_brief_write(
            tool_input, state, revenue_recorder.read_progress(session_id),
        )
        if deny is not None:
            return deny

    if suffix == "save_business_fact":
        deny = brief_gate.check_fact_private_details(tool_input, session_id)
        if deny is not None:
            return deny

    if suffix == "add_to_watchlist":
        deny = own_account.check_own_account_add(tool_input, state)
        if deny is not None:
            return deny
        deny = own_account_mismatch.check_include_flagged(tool_input, state)
        if deny is not None:
            return deny
        deny = own_account_not_found.check_add_anyway(tool_input, session_id)
        if deny is not None:
            return deny

    # RMP-72: a website-sourced save is denied while search is known to be
    # down this session -- see `website_search_state.py`'s own docstring.
    if suffix == "save_business_fact":
        deny = website_search_state.check_save_business_fact(tool_input, session_id)
        if deny is not None:
            return deny

    if suffix == "record_session_event":
        deny = step_gate_session_event.check_record_session_event(tool_input, state, session_id)
        if deny is not None:
            return deny

    if suffix == "get_resume_checklist":
        deny = checklist_gate.check_resume_checklist_manifest(tool_input, session_id)
        if deny is not None:
            return deny

    if suffix == "record_checklist_step":
        deny = checklist_gate.check_checklist_tick(tool_input, state, session_id)
        if deny is not None:
            return deny
        deny = website_mismatch.check_tick(tool_input, session_id)
        if deny is not None:
            return deny

    # RMP-201 P4: server gate map + repeat-call guard, dormant outside
    # drive mode -- see step_gate_plan.maybe_deny's own docstring.
    deny = step_gate_plan.maybe_deny(session_id, suffix, tool_input)
    if deny is not None:
        return deny

    current = step_order.first_unfinished(steps, state)
    if current is None or current["id"] == "connection_check":
        return None  # every known step passed (or manifest empty) -- nothing more to gate

    if suffix not in _allowed_suffixes(steps, current):
        if not step_gate_plan.job_ordering_bypass(payload, session_id, suffix):
            if not step_gate_plan.early_allow(session_id, suffix):
                return _deny(step_gate_rules.deny_reason(current, lambda step_id: deny_lines.finish(session_id, step_id)))

    if suffix in _WORKSPACE_PICKING_TOOLS:
        if suffix == "open_workspace":
            deny = workspace_gate.check_open_workspace_session(tool_input, session_id)
            if deny is not None:
                return deny
        return workspace_gate.check_workspace_pick(tool_input, state)

    # RMP-52: while skip_reoffer_pending, deny step 5 writes/ticks
    deny = step_skip.check_reoffer_gate(session_id, suffix, tool_input)
    if deny is not None:
        return deny

    return None


def decide(payload: dict, session_id: str) -> dict | None:
    """None = allow. Called only once step 1 is open. Runs the step rules
    first (`_decide_steps`); any deny there stops immediately, so a denied
    preview never reaches the spend gate. Once every step rule allows, the
    spend gate (RMP-23) has the last word for the six credit-spending
    tools -- see `spend_gate.py`."""
    tool_name = payload.get("tool_name")
    if not isinstance(tool_name, str):
        return None
    if cs.server_of(tool_name) != "reachmachine":
        return None  # this gate only restricts reachmachine tools

    # Only ever reached for reachmachine tools, so every input is wrapped
    # (RMP-5/RMP-10/RMP-20) -- see payload_util.tool_args.
    tool_input = tool_args(payload)

    deny = _decide_steps(payload, session_id, tool_input) or spend_gate.decide(payload, tool_input, session_id)
    return deny_lines.resolve(session_id, deny)   # RMP-291 P2321: a gate carries a reason id; show the server's words
