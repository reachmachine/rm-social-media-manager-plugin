"""Falsifiable test for G234 (and G233, G246, added by later prompts in this sprint) — SKILL.md's
`allowed-tools:` frontmatter must grant the tools its own PLAYBOOK steps assume are available.

Parses the frontmatter as plain text (it's a single `key: value` scalar line, not a YAML list —
matching this file's existing style), because SKILL.md's frontmatter is not valid standalone YAML
on its own (the description field uses a multi-line `>-` block) and a full YAML parser is not a
project dependency here.
"""
from __future__ import annotations

import pathlib
import re

_SKILL_MD = pathlib.Path(__file__).resolve().parent.parent / "SKILL.md"


def _allowed_tools() -> list[str]:
    text = _SKILL_MD.read_text(encoding="utf-8")
    m = re.search(r"^allowed-tools:\s*(.+)$", text, re.MULTILINE)
    assert m, "allowed-tools: line not found in SKILL.md frontmatter"
    return [t.strip() for t in m.group(1).split(",")]


def test_webfetch_is_granted() -> None:
    """G234 — the PLAYBOOK's website-reading step assumes WebFetch is allowed."""
    assert "WebFetch" in _allowed_tools()


def test_read_and_write_still_granted() -> None:
    """Regression guard — don't lose the original two tools while adding new ones."""
    tools = _allowed_tools()
    assert "Read" in tools
    assert "Write" in tools


def test_websearch_is_granted() -> None:
    """G233 — the PLAYBOOK's TAM-research step assumes WebSearch is allowed."""
    assert "WebSearch" in _allowed_tools()


def test_playwright_fallback_tools_are_granted() -> None:
    """G246 — the PLAYBOOK's website-reading fallback (Step 1) assumes these four
    Playwright tools are allowed: navigate, snapshot, wait_for, close."""
    tools = _allowed_tools()
    for tool in (
        "mcp__playwright__browser_navigate",
        "mcp__playwright__browser_snapshot",
        "mcp__playwright__browser_wait_for",
        "mcp__playwright__browser_close",
    ):
        assert tool in tools, f"{tool} missing from allowed-tools"
