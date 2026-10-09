#!/usr/bin/env python3
"""Model-only step 1 guidance (RMP-76, "hide the backend").

A PreToolUse denial is shown to the customer, so its text
(`connection_deny_text.py`) must be plain customer words. The instructions
only the model should see live here instead, in a UserPromptSubmit line: that
event's `additionalContext` reaches the model and is not shown as an error.

Covers what used to be stuffed into the denial text ("Redo only: X", "Apify
says the test run is not found. That is a pass.") and the customer asking to
carry on without Apify (live run CO, 2026-10-01): step 1 needs Apify, and the
answer says why and how to connect it. Never skip the check.
"""
from __future__ import annotations

import connection_deny_text as deny_text
import offer_lines

_OFFER = "connection_check"   # the SERVER's lines (RMP-281 P2359): `needs_signin` with {server}, `browser_missing`, ...
_SIGN_IN_SERVERS = {"reachmachine": "reachmachine", "apify": "apify"}


def _connect_line(session_id: str, server: str) -> str | None:
    """The server's own line telling the customer how to connect `server`, in the owner's language."""
    if server in _SIGN_IN_SERVERS:
        return offer_lines.line(session_id, _OFFER, "needs_signin", server=_SIGN_IN_SERVERS[server])
    return offer_lines.line(session_id, _OFFER, "browser_missing")


def build(state: dict, session_id: str = "") -> str:
    """One line for the model while step 1 is not open. `state` is the
    connection state (`connection_state.read_state`)."""
    missing = deny_text.missing_servers(state)
    parts = ["Reach Machine plugin: step 1 (connection check) has not passed yet in this session."]
    if missing:
        names = deny_text.join_with_and([deny_text.LABELS[s] for s in missing])
        parts.append(f"Redo only the check for {names}; the others already passed.")
        lines = [ln for ln in (_connect_line(session_id, s) for s in missing) if ln]
        if lines:
            parts.append("Tell the customer, exactly as given: " + " ".join(lines))
        else:
            parts.append(
                "Tell the customer how to connect it in their own language: type /mcp, "
                "choose the server and log in, then say check again."
            )
    if not state.get("apify"):
        parts.append(
            "Apify's reply that the test run was not found means Apify IS connected; "
            "never report it as a failure."
        )
        apify = offer_lines.line(session_id, _OFFER, "apify_needed", server="apify")   # P2361: the server's own line for this case
        parts.append(
            "If the customer asks to carry on without Apify, do not skip or work around the check. "
            + (f"Tell them exactly: {apify}" if apify else "In their own language, tell them to type /mcp, choose apify and log in, then say check again.")
        )
    parts.append("Run the connection-check skill before anything else.")
    return " ".join(parts)
