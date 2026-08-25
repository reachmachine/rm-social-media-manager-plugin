"""Falsifiable test for G226 — the two headless-safe scoping tools must be
allow-listed AND must not also sit in the deny-list.

Parses runner.py's source with ast instead of importing it, because runner.py
imports claude_agent_sdk at module top, which is not part of the backend test
environment.

Why both lists matter (not just the allow-list): runner.py's own safety-model
comment says `disallowed_tools` "holds in every permission mode, including
bypassPermissions" — it is a hard override on top of `allowed_tools`, which
only pre-approves. A tool that is in both `_RM_NONSPEND_TOOLS` (allow) and
`_RM_SPEND_OR_DESTRUCTIVE_TOOLS` (deny) is still denied at runtime. A test
that checks only the allow-list would go green on a fix that changes nothing
in practice — see prompts/COMMS.md, P1124 DISAGREE entry, 2026-08-09.
"""
from __future__ import annotations

import ast
import pathlib

_RUNNER = pathlib.Path(__file__).resolve().parent.parent / "runner.py"


def _load_list(name: str) -> list[str]:
    tree = ast.parse(_RUNNER.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == name
        ):
            return ast.literal_eval(node.value)
    raise AssertionError(f"{name} assignment not found in runner.py")


def _load_nonspend_tools() -> list[str]:
    return _load_list("_RM_NONSPEND_TOOLS")


def _load_deny_tools() -> list[str]:
    return _load_list("_RM_SPEND_OR_DESTRUCTIVE_TOOLS")


def test_set_data_selection_is_headless_allowed() -> None:
    tools = _load_nonspend_tools()
    assert "mcp__reachmachine__set_data_selection" in tools


def test_clear_data_selection_is_headless_allowed() -> None:
    tools = _load_nonspend_tools()
    assert "mcp__reachmachine__clear_data_selection" in tools


def test_set_data_selection_is_not_denied() -> None:
    """disallowed_tools overrides allowed_tools in every permission mode
    (runner.py's own comment). Being on the allow-list is not enough if the
    tool is also on the deny-list — it would still be blocked at runtime."""
    deny = _load_deny_tools()
    assert "mcp__reachmachine__set_data_selection" not in deny


def test_clear_data_selection_is_not_denied() -> None:
    deny = _load_deny_tools()
    assert "mcp__reachmachine__clear_data_selection" not in deny
