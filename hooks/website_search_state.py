#!/usr/bin/env python3
"""Session-scoped record of whether `search_business_knowledge` is currently
working (RMP-72).

Live test, 2026-09-25: on dev there is no search model yet, so
`get_website_read_status` stayed pending and every `search_business_
knowledge` call came back `available: false`. Nothing stopped the agent
from still saving `online_shop = {is_shop: false}` and "not found" facts
sourced from the website, then ticking step 6 as `answered` -- both false
claims about a search that never actually ran.

STATE: ONE raw `connection_state` key, `search_available`
(`true`/`false`/absent). Absent means "no `search_business_knowledge` call
has come back yet this session" and reads as AVAILABLE -- the safe
default, so a save is never blocked before the first search has even run.
Same raw-key pattern as `website_mismatch.py`'s own `website_mismatch` key
(`step_state.py` is at the 300-line limit, so a new typed key there would
need a split first; this needs no new key at all).

NOT cleared on a workspace switch: whether search is up or down is a
property of THIS SESSION's search backend, not of one workspace's data --
`step_state.reset_for_new_workspace` leaves it alone, same as `voice_
check.py`'s own raw keys.

FAIL-SAFE: nothing here may crash a hook -- same convention as every
sibling module.
"""
from __future__ import annotations

import json
from typing import Any

import connection_state as cs
import deny_lines

_DENY_REASON = "search_down"


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _deny(reason_id: str, **fill: object) -> dict:
    return deny_lines.deny_id(reason_id, **fill)


def is_available(session_id: str) -> bool:
    """True unless a `search_business_knowledge` call has actually come
    back `available: false` this session. Missing/wrong-typed reads back as
    available -- see module docstring, "the safe default"."""
    value = cs.read_raw(session_id).get("search_available")
    return value is not False


def handle_search_business_knowledge(session_id: str, payload: dict) -> None:
    """PostToolUse: records THIS call's own `available` flag. Break: skip
    storing here -> RED (a website save would keep being allowed, and step
    6 would keep being ticked as answered, even while every search is
    coming back unavailable)."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    available = data.get("available")
    if not isinstance(available, bool):
        return
    cs.write_patch(session_id, {"search_available": available})


# RMP-96: `get_fact_tasks` uses the exact same `{"available": bool, ...}`
# shape `search_business_knowledge` does -- same handler, no duplicate.
handle_get_fact_tasks = handle_search_business_knowledge


def check_save_business_fact(tool_input: dict[str, Any], session_id: str) -> dict | None:
    """Delegated from `step_gate.py`. Only a website-sourced save is denied
    while search is down -- the customer's own words (`source: "customer"`)
    are never blocked by this check. Break: always return None -> RED (a
    website save would go through while search is known to be down)."""
    if tool_input.get("source") != "website":
        return None
    if is_available(session_id):
        return None
    return _deny(_DENY_REASON)
