#!/usr/bin/env python3
"""PreToolUse hard search/fetch budget for step 8's research pass (RMP-197
P3, design section 3): "A hard search budget, enforced by the plugin rather
than by the prompt." Matches BOTH `WebSearch` and `WebFetch` (the design
text focuses on WebSearch, but `pick_your_niche.md`'s own rules give
WebFetch its OWN separate budget for confirming a competitor price on its
exact page -- both need a hard stop, not just a prompt request).

A no-op unless the `niche_research_active` session flag is set --
`activate()`/`deactivate()` below are called by `step_recorder_niche.py`'s
PostToolUse handlers, never from here. The two budgets (search vs webfetch)
come from the SERVER's own `start_niche_pick`/`save_niche_research` payload
(`search_budget.max`/`webfetch_budget.max`) -- never hardcoded here, so a
founder-changed budget (RMP-197 round 6 already raised both once) needs no
plugin release to take effect.

FAIL-SAFE, same convention as `job_budget_gate.py`: a crash here must never
brick a real tool call, and this hook denies only the ONE tool call that
would cross the budget, never every call after that -- the model can still
call `save_niche_research` to close out with whatever it has.
"""
from __future__ import annotations

import json
import sys

import connection_state as cs
import deny_lines

_ACTIVE_KEY = "niche_research_active"
_SEARCH_MAX_KEY = "niche_search_max"
_SEARCH_USED_KEY = "niche_search_used"
_WEBFETCH_MAX_KEY = "niche_webfetch_max"
_WEBFETCH_USED_KEY = "niche_webfetch_used"

_DEFAULT_SEARCH_MAX = 30
_DEFAULT_WEBFETCH_MAX = 20

_TOOL_BUDGET_KEYS = {
    "WebSearch": (_SEARCH_MAX_KEY, _SEARCH_USED_KEY, "search_limit"),
    "WebFetch": (_WEBFETCH_MAX_KEY, _WEBFETCH_USED_KEY, "page_limit"),
}


def activate(session_id: str, search_max: object, webfetch_max: object) -> None:
    """Turns the budget window on. Only sets the MAX values if this is the
    FIRST activation this window (an already-active session keeps its
    running `*_used` counts) -- `save_niche_research`/`start_niche_pick` can
    both re-show `stage:"research"` on repeated polls without resetting a
    count already in progress."""
    state = cs.read_raw(session_id)
    if state.get(_ACTIVE_KEY) is True:
        return
    cs.write_patch(session_id, {
        _ACTIVE_KEY: True,
        _SEARCH_MAX_KEY: search_max if isinstance(search_max, int) else _DEFAULT_SEARCH_MAX,
        _SEARCH_USED_KEY: 0,
        _WEBFETCH_MAX_KEY: webfetch_max if isinstance(webfetch_max, int) else _DEFAULT_WEBFETCH_MAX,
        _WEBFETCH_USED_KEY: 0,
    })


def deactivate(session_id: str) -> None:
    cs.write_patch(session_id, {_ACTIVE_KEY: False})


def _deny(reason_id: str, session_id: str = "") -> dict:
    return deny_lines.deny(deny_lines.reason(session_id, reason_id))   # RMP-291 P2320: the text is the server's


def decide(payload: dict) -> dict | None:
    """None = allow. Never raises -- see module docstring."""
    tool_name = payload.get("tool_name")
    budget_keys = _TOOL_BUDGET_KEYS.get(tool_name)
    if budget_keys is None:
        return None

    session_id = payload.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return None

    state = cs.read_raw(session_id)
    if state.get(_ACTIVE_KEY) is not True:
        return None

    max_key, used_key, deny_reason = budget_keys
    max_value = state.get(max_key)
    if not isinstance(max_value, int):
        max_value = _DEFAULT_SEARCH_MAX if tool_name == "WebSearch" else _DEFAULT_WEBFETCH_MAX
    used = state.get(used_key)
    used = used + 1 if isinstance(used, int) else 1

    if used > max_value:
        return _deny(deny_reason, session_id)
    cs.write_patch(session_id, {used_key: used})
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    try:
        result = decide(payload)
    except Exception:
        return 0
    if result is not None:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
