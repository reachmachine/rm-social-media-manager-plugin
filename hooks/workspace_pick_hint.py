#!/usr/bin/env python3
"""The order a typed workspace number is read in (RMP-22, live 2026-09-29).

Live bug: the customer saw an UNNUMBERED workspace list, typed "1", and the
reply was "I'm not sure what '1' means. I never numbered my list." Worse, on
the next turn the model DID number a list -- but in its own order (last used
first, only 3 of 10 workspaces), so a typed "1" would have picked a different
workspace than the one printed next to "1".

A typed number is read against `workspace_options`, the order
`list_workspaces` returned (`answer_matcher._step_options`). So the one safe
rule is: the printed numbers must follow that exact order. This hook says so
in the same turn `list_workspaces` returns, listing the names in that order,
so the model does not have to remember a skill paragraph.

Only `additionalContext` for the model; it is never shown to the customer.
Never raises.
"""
from __future__ import annotations

import step_state


def message_for(session_id: str, payload: dict) -> str | None:
    if payload.get("hook_event_name") != "PostToolUse":
        return None
    tool_name = payload.get("tool_name")
    if not isinstance(tool_name, str) or not tool_name.endswith("__list_workspaces"):
        return None
    try:
        options = step_state.read_state(session_id)["workspace_options"]
    except Exception:
        return None
    names = [o.get("name") for o in options if isinstance(o.get("name"), str) and o.get("name")]
    if not names:
        return None
    order = "; ".join(f"{i}. {name}" for i, name in enumerate(names, start=1))
    return (
        "If AskUserQuestion is not in your tools, write the workspace question as a numbered "
        f"list, one line each, in exactly this order, none left out: {order}. Add one last "
        f"line, {len(names) + 1}. Another one (type the name). Never reorder, never skip a "
        "number, never leave the list unnumbered: the customer's typed number is read in this order."
    )
