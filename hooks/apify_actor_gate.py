#!/usr/bin/env python3
"""PreToolUse cost/permission gate for the generic Apify `call-actor` tool
(RMP-202).

Called from `connections_gate.py`'s `_decide`, only for a `call-actor` call,
only once step 1 (the connection check) is already open -- see that
module's own docstring for where this plugs in.

`call-actor` can run ANY actor on the customer's own Apify account. Before
RMP-202, the plugin.json URL listed one MCP tool per actor
(`apify--instagram-scraper`, `compass--google-maps-reviews-scraper`, ...),
so the tool name itself was the safety boundary -- picking a tool already
fixed which actor ran. Moving every call to one shared generic tool removes
that boundary, so this gate replaces it: `tool_input["actor"]` must be one
of the actor ids `apify_actor_allowlist.allowed_actor_ids` cached for THIS
session (or, for a background job that has its own list, THAT job -- RMP-218)
from a server tool result (today, only `start_reviews_fetch`). Any
other actor id -- typo, hallucination, or a genuine attempt to run something
the server never approved -- is denied with a plain reason, never a stack
trace and never "why".

FAILS CLOSED like every other check `connections_gate.py` runs: a missing,
non-string `actor`, or an actor id absent from an empty/unreadable
allow-list, is denied. Nothing here ever allows by omission.
"""
from __future__ import annotations

import apify_actor_allowlist
import deny_lines
import hangouts_run_gate

_DENY_REASON = "actor_not_allowed"


def _deny() -> dict:
    return deny_lines.deny_id(_DENY_REASON)


def check_call_actor(tool_input: dict, session_id: str, agent_id: str | None = None) -> dict | None:
    """None = allow. `tool_input["actor"]` must be a non-empty string
    present in this caller's cached allow-list (a background job's own list
    when it has one, else the session list -- `apify_actor_allowlist`). Break: always `return None`
    (skip the check entirely) -> RED (Rule 3 test: an actor id the server
    never named must be denied, not silently run)."""
    actor = tool_input.get("actor")
    if not isinstance(actor, str) or not actor:
        return _deny()
    if actor not in apify_actor_allowlist.allowed_actor_ids(session_id, agent_id):
        return _deny()
    return hangouts_run_gate.check_call_actor(session_id, agent_id)   # P1853: one call-actor per issued run
