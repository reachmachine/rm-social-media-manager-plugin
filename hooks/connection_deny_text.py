#!/usr/bin/env python3
"""The customer-visible denial texts for step 1 (RMP-76, "hide the backend").

Claude Code prints a PreToolUse denial reason in the customer's terminal
("Error: PreToolUse:Skill hook error: <reason>") AND hands it to the model.
`PreToolUse` output has no model-only field (see prompts/COMMS.md,
2026-09-30), so every text here is plain customer words that also tell the
model what to do. Anything the model alone needs lives in
`connection_reminder_text.py` (a UserPromptSubmit line, which IS private).

No tool names, no "step N", no "hook/gate/pass/test run". The only command
named is `/mcp`, which the customer really types to sign in.

Split out of `connections_gate.py` to keep it under the 300-line limit.
"""
from __future__ import annotations

LABELS = {"reachmachine": "Reach Machine", "apify": "Apify", "playwright": "the browser"}
_SIGN_IN_NAMES = {"reachmachine": "reachmachine", "apify": "apify"}
_ORDER = ("reachmachine", "apify", "playwright")

# RMP-291 P2321: reason ids. The owner-language text is the server's (`deny_lines`); step 1 may run before any server
# reply exists, so with no map the customer sees the id and the values (names, the one command), never English prose.
GENERIC_DENY_REASON = "connections_unconfirmed"
RECORD_MISMATCH_REASON = "connections_record_mismatch"
ALL_CONNECTED_NOT_RECORDED_REASON = "connections_not_saved"   # all three connected, but the session is not saved yet
NAMES = {"reachmachine": "Reach Machine", "apify": "Apify", "playwright": "Playwright"}   # product names, not prose


def join_with_and(names: list[str]) -> str:
    """Oxford-comma join for 1, 2, or 3+ items -- never indexes past the
    list, so a caller can hand this any length, including 0."""
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + f", and {names[-1]}"


def missing_servers(state: dict) -> list[str]:
    """Server keys that have not passed, in a fixed order."""
    return [s for s in _ORDER if not state.get(s)]


def missing_reason(state: dict) -> tuple[str, dict]:
    """`(reason id, values)` for "step 1 is not open yet". `state` can miss 0, 1, 2 or 3 servers -- 0 happens when all three
    passed but the session was never recorded (P1611: the `missing[0]` crash this used to be)."""
    missing = missing_servers(state)
    if not missing:
        return ALL_CONNECTED_NOT_RECORDED_REASON, {}
    names = ", ".join(NAMES[s] for s in missing)
    sign_in = [_SIGN_IN_NAMES[s] for s in missing if s in _SIGN_IN_NAMES]
    if sign_in:
        return "connections_missing_sign_in", {"names": names, "command": "/mcp", "sign_in": ", ".join(sign_in)}
    return "connections_missing_wait", {"names": names}
