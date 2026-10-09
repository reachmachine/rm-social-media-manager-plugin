#!/usr/bin/env python3
"""Same-turn hint for a wrapped Apify or browser probe input (RMP-48).

Spec: docs/plugin-v2/01-connection-check.md, "Hand-test fix: flat probe
inputs".

Bug (found in founder's real session, 2026-09-24): the agent wrapped Apify and
browser inputs in `{"args": {...}}` exactly like Reach Machine tools, because
the SKILL.md never showed the input shape and never said these two tools are
flat. The hook still matched the wrapped call's inner value against the probe
id/url, and judged it broken -- so the agent told the customer "Apify ❌
broken, sign in again", twice, while the connection was fine.

This module delivers the correction in the same turn, as `additionalContext`.
`connection_state.py`'s own `judge_probe` returns `None` for these calls, so
they never write a broken result, and `connection_state_cli.py` prints this
hint instead of the next-step message.
"""
from __future__ import annotations

import connection_state as cs


def is_input_error(payload: dict) -> bool:
    """True when this is a PostToolUseFailure where the error text is "Invalid
    arguments...", the shape an MCP server returns when the tool input does not
    validate. (Case-insensitive, after stripping a leading "### Error" line if
    present.) An input mistake is not a connection result, even if the input
    looked flat -- the server never ran the call, so nothing was measured.
    Never raises."""
    if not isinstance(payload, dict):
        return False
    event = payload.get("hook_event_name")
    if event != "PostToolUseFailure":
        return False
    error = payload.get("error")
    if not isinstance(error, str):
        return False
    # Strip leading "### Error\n" if present (observed in real payloads).
    text = error
    if text.startswith("### Error\n"):
        text = text[len("### Error\n"):]
    return text.lower().startswith("invalid arguments")


def hint_for(payload: dict) -> str | None:
    """Returns the exact same-turn correction text when this is a
    PostToolUseFailure of the Apify `get-actor-run` or browser
    `browser_navigate` tool AND (the tool_input has a top-level "args" key OR
    `is_input_error` is true). Otherwise None. Never raises."""
    if not isinstance(payload, dict):
        return None
    event = payload.get("hook_event_name")
    if event != "PostToolUseFailure":
        return None
    tool_name = payload.get("tool_name")
    if not isinstance(tool_name, str):
        return None

    # Only these two tools.
    is_apify = tool_name.endswith("__get-actor-run")
    is_browser = tool_name.endswith("__browser_navigate")
    if not is_apify and not is_browser:
        return None

    # Needs a wrapped input OR an "Invalid arguments" error.
    tool_input = payload.get("tool_input")
    has_args_wrapper = isinstance(tool_input, dict) and "args" in tool_input
    if not has_args_wrapper and not is_input_error(payload):
        return None

    # Build the exact call from the spec constants, never a second hardcoded
    # copy of the values.
    if is_apify:
        example = f'{{"runId": "{cs.PROBE_RUN_ID}", "waitSecs": 0}}'
        tool = "get-actor-run"
    else:
        example = f'{{"url": "{cs.PROBE_URL}"}}'
        tool = "browser_navigate"

    return (
        f"That call failed because its input was wrong. The connection is fine. "
        f"Apify and the browser take flat inputs, with no \"args\" wrapper. "
        f"Call it again exactly like this: {tool} {example}. "
        f"Do not tell the customer anything is broken."
    )
