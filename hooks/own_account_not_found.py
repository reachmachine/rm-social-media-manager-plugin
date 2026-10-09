#!/usr/bin/env python3
"""RMP-175 -- reverses founder decision 1 (2026-09-24, 04-own-instagram-
account.md) for the customer's OWN account only: "a typo is the customer's
cost, no backend change, no 'couldn't find it' flow." Live bug, 2026-09-26,
proved that wrong for step 4 specifically -- @natgeotravell (a typo) came
back verdict "passed"/niche_fit "unclear" with every check "unknown", and
the confirmed add silently charged the customer with no numbers and no
warning at all. Competitor adds keep founder decision 1 unchanged (see
`backend/app/mcp/_ingest_authenticity_screen.py`'s own docstring -- the
server only ever applies this to the entry matching `self_handle`).

THE SERVER decides (RMP-76): `add_to_watchlist`'s own-account-only preview
now returns `screened[0].verdict == "not_found"` when Instagram returned
neither a follower nor a post count for the handle
(`backend/app/mcp/_no_profile_data.py`). This module is the ONE place that
turns that into: state (this session knows a not-found handle is pending),
a gate (`add_anyway=true` is earned only by a real "Add it anyway" to
EXACTLY that handle), and the AskUserQuestion/typed-reply capture for the
"Fix the spelling" / "Add it anyway" question. Same SHAPE as step 4's own
`own_account_mismatch.py` (RMP-23, founder decision 6) / `website_mismatch.
py` (RMP-66) -- copied structure, not code.

STATE lives under ONE raw `connection_state` key, `own_account_not_found`
(read/written via `connection_state.read_raw`/`write_patch` directly, kept
OUT of `step_state.read_state`'s own typed shape -- `step_state.py` is at
the 300-line limit, so a new key there would need a split first; this needs
no new key at all, same reasoning as `website_mismatch.py`'s own
docstring). Shape, safe defaults for anything missing or wrong-typed:
    {"pending": {"handle": str, "reason": str} | None,
     "answer": "fix" | "add_anyway" | None}

No session-event kind of its own (unlike RMP-23/RMP-66's `..._shown`/
`..._answered` pairs) -- out of scope for this bug fix; a real add still
writes the ordinary `own_instagram_account` step-done event exactly as
before. Flagged as a follow-up in prompts/COMMS.md.

FAIL-SAFE: nothing here may crash a hook -- same convention as every
sibling module.
"""
from __future__ import annotations

from typing import Any

import connection_state as cs
import deny_lines
import offer_lines
import step_gate_own_account as own_account_gate

OFFER_ID = "instagram_not_found"   # P2361: the SERVER's question and buttons (ids `fix` / `add_anyway`); the plugin holds no words

_ASK_FIRST_REASON = "ask_fix_or_add_first"
_MAX_REASON_LEN = 200

_DEFAULT_STATE: dict[str, Any] = {"pending": None, "answer": None}


def _deny(reason_id: str, **fill: object) -> dict:
    return deny_lines.deny_id(reason_id, **fill)


def read_state(session_id: str) -> dict[str, Any]:
    """The safe shape, with the safe default for anything missing or
    wrong-typed."""
    raw = cs.read_raw(session_id).get("own_account_not_found")
    result = dict(_DEFAULT_STATE)
    if not isinstance(raw, dict):
        return result
    pending = raw.get("pending")
    handle_ok = isinstance(pending, dict) and isinstance(pending.get("handle"), str) and pending.get("handle")
    if handle_ok and isinstance(pending.get("reason"), str):
        result["pending"] = {"handle": pending["handle"], "reason": pending["reason"]}
    if raw.get("answer") in ("fix", "add_anyway"):
        result["answer"] = raw["answer"]
    return result


def _save(session_id: str, state: dict[str, Any]) -> None:
    cs.write_patch(session_id, {"own_account_not_found": state})


def clear(session_id: str) -> None:
    """A workspace switch, or a fresh handle typed for step 4, clears
    whatever not-found handle applied to the OLD handle/workspace -- same
    per-workspace rule `own_account_mismatch.clear_on_new_handle` already
    applies to the mismatch pair."""
    _save(session_id, dict(_DEFAULT_STATE))


clear_on_new_handle = clear


# --------------------------------------------------------------- the gate --

def check_add_anyway(tool_input: dict[str, Any], session_id: str) -> dict | None:
    """`add_to_watchlist`'s `add_anyway=true` skip (RMP-175) is earned only
    by a real "Add it anyway" to EXACTLY the handle the preview just told
    the customer it could not find -- never on a preview, never without a
    stored pending handle, never for a different handle, never without
    `answer == "add_anyway"`. Same shape as `own_account_mismatch.
    check_include_flagged`."""
    if tool_input.get("add_anyway") is not True:
        return None
    if tool_input.get("confirm") is not True:
        return _deny(_ASK_FIRST_REASON)
    state = read_state(session_id)
    pending = state["pending"]
    if pending is None:
        return _deny(_ASK_FIRST_REASON)
    if own_account_gate.normalize_handle(tool_input.get("self_handle")) != pending["handle"]:
        return _deny(_ASK_FIRST_REASON)
    if state["answer"] != "add_anyway":
        return _deny(_ASK_FIRST_REASON)
    return None


# ------------------------------------------------------------- detection --

def note_preview_result(session_id: str, tool_input: dict[str, Any], data: dict[str, Any]) -> None:
    """Called from the PostToolUse recorder after an own-account-only
    preview (`requires_confirmation: true`) returns. Sets the pending
    not-found handle when the `screened` entry for the typed handle has
    `verdict == "not_found"`; any other preview result clears it (a fixed
    typo followed by a clean preview must never leave a stale pending
    handle behind)."""
    handles = tool_input.get("handles")
    self_handle = own_account_gate.normalize_handle(tool_input.get("self_handle"))
    if not isinstance(handles, list) or len(handles) != 1 or not isinstance(self_handle, str) or not self_handle:
        return
    if own_account_gate.normalize_handle(handles[0]) != self_handle:
        return
    screened = data.get("screened")
    entry = next(
        (e for e in screened if isinstance(e, dict)
         and own_account_gate.normalize_handle(e.get("handle")) == self_handle),
        None,
    ) if isinstance(screened, list) else None
    if entry is None or entry.get("verdict") != "not_found":
        clear(session_id)
        return
    reasons = entry.get("reasons")
    reason = "; ".join(r for r in reasons if isinstance(r, str)) if isinstance(reasons, list) else ""
    reason = reason[:_MAX_REASON_LEN] or "Instagram did not return a follower or post count for this handle."
    _save(session_id, {"pending": {"handle": self_handle, "reason": reason}, "answer": None})


# --------------------------------------------------- typed/clicked answer --

def try_capture_ask_user_answer(session_id: str, question_text: str, label: str) -> bool:
    """True if this WAS our own not-found question (the server's line, `offers.instagram_not_found.say`) -- caller must not
    also run normal step matching in that case, whether or not the label actually resolved to fix/add_anyway."""
    offer = offer_lines.get(session_id, OFFER_ID)
    if offer is None or question_text != offer["say"]:
        return False
    _try_capture(session_id, offer_lines.match_clicked(offer, label))
    return True


def try_capture_typed_answer(session_id: str, message: str) -> bool:
    """True only if this typed reply WAS captured as the not-found answer --
    caller must skip normal step matching in that case. Unlike the
    `AskUserQuestion` path, an unrelated typed reply must still fall through
    to normal matching. Matched by the server's option id, label, `also` words or option number."""
    return _try_capture(session_id, offer_lines.match(offer_lines.get(session_id, OFFER_ID), message))


def _try_capture(session_id: str, answer: str | None) -> bool:
    """`answer` is the server's option id (`fix` / `add_anyway`), or None when the reply meant neither."""
    state = read_state(session_id)
    if state["pending"] is None or state["answer"] is not None:
        return False
    if answer not in ("fix", "add_anyway"):
        return False
    _save(session_id, {**state, "answer": answer})
    return True
