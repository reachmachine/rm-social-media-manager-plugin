#!/usr/bin/env python3
"""Stamps every allowed Reach Machine call with this chat's own id (RMP-79
part 2, `docs/plugin-v2/08-one-chat-per-workspace.md`, "1. The plugin
stamps every Reach Machine call with the chat id"). Called from
`connections_gate.decide`, last, after the real allow/deny/ask decision is
already made.

WHY: the MCP transport is stateless and two Claude Code windows can share
one OAuth token, so the server cannot tell which chat a call came from
without help. The plugin's hook `session_id` is the one thing that IS
unique per chat. Once the server reads it (P1737, not part of this file),
each chat gets its own workspace instead of the last window to pick
winning for everyone.

CONFIRMED AGAINST THE OFFICIAL HOOK REFERENCE (code.claude.com/docs/en/
hooks, "PreToolUse decision control", read 2026-09-25) before writing this:
- `updatedInput` REPLACES THE WHOLE `tool_input` object -- "Replaces the
  entire input object, so include unchanged fields alongside modified
  ones." It is NOT a deep merge, so every original argument has to be
  copied across here, not just the one being added.
- `updatedInput` can sit next to any `permissionDecision` ("allow" or
  "ask"), or next to none at all -- omitting `permissionDecision` leaves
  the tool's normal permission handling untouched and only rewrites the
  arguments. That is what "not denied" means below: this file never turns
  a previously-unopinionated allow into an explicit one, it only adds
  `updatedInput`. It can never be combined with "deny" (a denied call
  never runs), so a denied decision is returned completely unchanged.

Every Reach Machine tool's real input sits under `tool_input["args"]`
(`payload_util.tool_args`); a genuinely no-arg tool such as
`list_workspaces` sends `tool_input: {}`, no `args` key at all -- either
way `tool_args` always returns a dict (its own docstring), so
`{**original_args, "client_session_id": sid}` wrapped back in
`{"args": ...}` produces the right shape for both cases.

Apify and Playwright calls are untouched -- the server-side reader
(design doc, point 2) only ever looks at a Reach Machine call's own body.

No `session_id` (missing, not a string, or empty) means never stamp: the
server's own validator would reject an empty `client_session_id` outright,
and a hook payload with nothing chat-scoped to attach is strictly safer
left alone than sent a value the server would refuse.
"""
from __future__ import annotations

from connection_state import server_of
import customer_upload_state as cus
import niche_pick_said

# RMP-281 P2356: the first Reach Machine calls of a session. The server learns the owner's language from the customer's
# own words, so steps 1-5 can be asked in it before any free-text answer exists.
FIRST_MESSAGE_TOOLS = ("__record_session_start", "__list_workspaces", "__open_workspace", "__get_resume_checklist")
_MAX_FIRST_MESSAGE_CHARS = 300


def _is_denied(decision: dict | None) -> bool:
    if not isinstance(decision, dict):
        return False
    hook_out = decision.get("hookSpecificOutput")
    return isinstance(hook_out, dict) and hook_out.get("permissionDecision") == "deny"


def _stamp_customer_said(args: dict, session_id: str) -> None:
    """RMP-281 P2260: `choose_niche` carries the customer's own typed words, so the server reads the pick from them and
    never has to trust the model's number-to-id mapping. The field is the hook's alone: whatever the model sent is
    dropped, and nothing is stamped unless the customer typed AFTER the pick question was shown (`niche_pick_said`)."""
    args.pop("customer_said", None)
    said = niche_pick_said.customer_said(session_id)
    if said:
        args["customer_said"] = said


def _stamp_first_message(args: dict, session_id: str) -> None:
    """RMP-281 P2356: `first_message` is the hook's alone. Whatever the model sent is dropped; what is stamped is the
    customer's last REAL typed prompt (`capture_last_prompt.py` never records a hook-injected or task-notification
    text), up to 300 characters. Nothing typed yet -> no field at all."""
    args.pop("first_message", None)
    try:
        said = " ".join(cus.last_prompt(session_id).split())[:_MAX_FIRST_MESSAGE_CHARS]
    except Exception:
        said = ""
    if said:
        args["first_message"] = said


def apply(tool_name: str, original_args: dict, session_id: object, decision: dict | None) -> dict | None:
    """Returns `decision` unchanged for anything that is not an allowed
    Reach Machine call. Otherwise returns a new dict carrying every field
    `decision` already had (an `ask`/`allow` from `spend_gate`, its reason,
    ...) plus `updatedInput` -- the model's own `client_session_id`, if it
    sent one, is always overwritten with the hook's real value."""
    if server_of(tool_name) != "reachmachine":
        return decision
    if not isinstance(session_id, str) or not session_id:
        return decision
    if _is_denied(decision):
        return decision

    args = original_args if isinstance(original_args, dict) else {}
    updated_input = {"args": {**args, "client_session_id": session_id}}
    if tool_name.endswith("__choose_niche"):
        _stamp_customer_said(updated_input["args"], session_id)
    if tool_name.endswith(FIRST_MESSAGE_TOOLS):
        _stamp_first_message(updated_input["args"], session_id)

    if decision is None:
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "updatedInput": updated_input,
            }
        }

    hook_out = dict(decision.get("hookSpecificOutput") or {})
    hook_out["updatedInput"] = updated_input
    merged = dict(decision)
    merged["hookSpecificOutput"] = hook_out
    return merged
