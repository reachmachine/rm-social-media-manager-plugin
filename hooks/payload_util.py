#!/usr/bin/env python3
"""Unwraps a Reach Machine MCP tool's real input out of its `{"args": {...}}`
wrapper (RMP-5, RMP-7, RMP-10, RMP-20).

Found live on dev, 2026-09-23 (architect capture, verbatim). The model's
real `record_session_start` call:
    {"args": {"client_session_id": "c706f41e-...", "plugin_version": "2.0.0-dev.3",
              "results": {...}, "earlier_checks": []}}
Every hook in this plugin read `tool_input["client_session_id"]` etc.
directly -- one level too shallow -- so a correct call was denied as a
mismatch every time.

WHY IT IS WRAPPED: every Reach Machine tool is declared
`async def tool(args: SomeInput)` (e.g.
`backend/app/mcp/tools/workspace/tools_workspace_write.py:296`), and Claude
Code hands a Python-style tool's keyword arguments back inside that single
named parameter, `args`. Apify and Playwright tools declare their real
fields directly as top-level parameters (`runId`, `url`, ...), so those
arrive UNWRAPPED -- `tool_args` falls back to the flat value whenever the
wrapper is not there, so one call site works for every kind of tool, present
or future, without the caller having to know which kind it is looking at.

Used everywhere a hook reads a tool's input: `connection_state.judge_probe`,
`connections_gate.decide`, and `step_gate.decide` (the only three places
`tool_input` is ever pulled out of a hook payload -- see the module
docstrings there for the one-line justification at each remaining
`payload.get("tool_input")` that is NOT routed through this function,
because that tool is not a Reach Machine tool).
"""
from __future__ import annotations


# Claude Code sends its OWN messages through UserPromptSubmit too, with the message text as
# `prompt` -- e.g. "<task-notification>...</task-notification>" when a background agent
# finishes (live 2026-09-29, RMP-24 S5-B1: it was read as a customer's typed reply and used up
# step 5's one-time revenue guess before the customer typed anything).
_SYSTEM_PROMPT_TAGS = (
    "<task-notification", "<system-reminder", "<local-command", "<command-name", "<command-message",
)


def is_system_generated_prompt(prompt: object) -> bool:
    """True for a UserPromptSubmit `prompt` that Claude Code produced, not the customer."""
    return isinstance(prompt, str) and prompt.lstrip().casefold().startswith(_SYSTEM_PROMPT_TAGS)


def tool_args(payload: dict) -> dict:
    """`payload["tool_input"]["args"]` when that is itself a dict (every
    Reach Machine tool); otherwise `payload["tool_input"]` unchanged (Apify,
    Playwright, `Skill`, or any other flat tool); otherwise `{}` for a
    malformed or missing payload. Never raises -- same fail-safe direction
    as every other read in this plugin's hooks."""
    if not isinstance(payload, dict):
        return {}
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return {}
    args = tool_input.get("args")
    if isinstance(args, dict):
        return args
    return tool_input
