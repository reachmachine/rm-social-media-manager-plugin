#!/usr/bin/env python3
"""RMP-23 step-4 gate rules -- split out of `step_gate.py` to stay under the
300-line file limit, same "split when it grows" precedent as
`checklist_recorder.py`/`step_recorder.py` (RMP-9).

Spec: `docs/plugin-v2/04-own-instagram-account.md`, "Enforcement". Each
function here returns a ready `_deny(...)` dict or `None` (allow), exactly
like every check function in `step_gate.py` itself -- `_decide_steps` just
calls straight through.
"""
from __future__ import annotations

from typing import Any

import deny_lines

_ADD_WRONG_HANDLE_REASON = "add_wrong_handle"
_COMPETITOR_ADD_REASON = "competitor_add_unavailable"
_PICK_WORKSPACE_REASON = "pick_workspace"
_EVENT_MISMATCH_REASON = "event_mismatch"


def _deny(reason_id: str, **fill: object) -> dict:
    return deny_lines.deny_id(reason_id, **fill)


def normalize_handle(handle: Any) -> Any:
    """Compare handles the way the server does (architect review of P1620):
    `tools_watchlist_add_write.py` strips a leading `@` and lower-cases
    before it matches a handle against `self_handle`. The stored answer
    (`human_answers["own_instagram_account"]`) is already in this exact
    shape (`answer_matcher.extract_handle` lower-cases it, P1618), so
    normalizing only the INCOMING value here is enough to compare like for
    like. Returns non-strings (e.g. `None`, a missing field) unchanged --
    never raises, same fail-safe convention as every function in this
    module. `step_recorder_own_account.py`'s success handler imports this
    same function so both sides of the comparison agree."""
    if not isinstance(handle, str):
        return handle
    return handle.strip().lstrip("@").lower()


def check_own_account_add(tool_input: dict[str, Any], state: dict[str, Any]) -> dict | None:
    """`add_to_watchlist` during/after step 4 may only add EXACTLY the
    handle the customer typed for step 4 (`human_answers
    ["own_instagram_account"]`) -- never a competitor, never a different
    handle. Mirrors `step_gate._check_workspace_pick`'s "only the human's
    own pick" shape. The caller runs this unconditionally whenever the tool
    is `add_to_watchlist`, even after step 4 has passed -- a LATER,
    self-authorised add attempt with a different handle must still be
    denied, same as `_check_brief_answers` runs regardless of step order.

    RMP-186: `self_handle` is the ONLY signal `AddToWatchlistInput` gives for
    "this is the customer's own account, not a competitor" (backend/app/mcp/
    schemas/tool_schemas_ingest_watchlist.py -- "leave unset for an ordinary
    competitor add"). A call with no `self_handle` at all is therefore a
    COMPETITOR add, which plugin v2's onboarding (steps 1-6) does not offer
    yet -- checked FIRST, before the own-account pin below, so a competitor
    add gets the true reason instead of the misleading own-account one (live
    dev, 2026-09-26: the model filled that gap with an invented "needs a
    separate sign-in" story).

    Known limit, not changed here: this pins EVERY `add_to_watchlist` call
    to the customer's own typed handle, even after step 4 -- correct today
    (no later step adds competitors). The future step that adds competitors
    must relax this rule for its own step."""
    self_handle = tool_input.get("self_handle")
    if not isinstance(self_handle, str) or not self_handle.strip():
        return _deny(_COMPETITOR_ADD_REASON)
    picked = state["human_answers"].get("own_instagram_account")
    handles = tool_input.get("handles")
    if not isinstance(handles, list):
        return _deny(_ADD_WRONG_HANDLE_REASON)
    normalized_handles = [normalize_handle(h) for h in handles]
    if normalized_handles != [picked] or normalize_handle(self_handle) != picked:
        return _deny(_ADD_WRONG_HANDLE_REASON)
    return None


def check_profile_refreshed_event(tool_input: dict[str, Any], state: dict[str, Any]) -> dict | None:
    """`record_session_event(kind="profile_refreshed")` is truthful only --
    the `detail` sent must equal what the plugin's own hook just saw in a
    REAL `refresh_competitor` result (`state["last_refresh"]`), never a
    value the model could invent. The explicit `last is None` check
    matters: without it, a model sending `detail: null` (or omitting it)
    when no refresh ever happened would pass a bare `None != None`
    comparison (which is `False`), i.e. be wrongly ALLOWED. Caller
    (`step_gate_session_event.check_record_session_event`) has already checked the
    workspace itself matches before reaching here."""
    workspace = state["workspace"]
    if workspace is None:
        return _deny(_PICK_WORKSPACE_REASON)
    last = state["last_refresh"]
    if last is None or tool_input.get("detail") != last:
        return _deny(_EVENT_MISMATCH_REASON)
    return None
