"""Falsifiable tests for G328 — the skill must analyse data per FUNNEL ROLE
(`reach` / `nurture` / `activation`), not once per plan goal.

Why: a Leads plan used to analyse only lead tags, then pattern its `reach` reels
off `hidden_gem` reels (low-view by definition) while stamping the receipt
"DATA-DRIVEN, reliability HIGH". These tests pin the three doc changes that fix
that: the Gate 7 wrong-slice check, the PLAYBOOK role→row mapping, and the
SKILL.md summary no longer telling the agent to pick one plan-level subset.

Plain-text/regex assertions on the skill's own files, matching the style of
`test_skill_frontmatter_tools.py` — no new dependencies.
"""
from __future__ import annotations

import pathlib
import re

_SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent


def _normalised(name: str) -> str:
    """File content with all whitespace collapsed, so line-wrap can't hide a phrase."""
    text = (_SKILL_DIR / name).read_text(encoding="utf-8")
    return " ".join(text.split())


def test_rules_gate_has_role_slice_check() -> None:
    """Gate 7 (data integrity) must contain the wrong-slice receipt check."""
    text = (_SKILL_DIR / "RULES_GATE.md").read_text(encoding="utf-8")
    m = re.search(r"## Gate 7\b(.*?)## Gate 8\b", text, re.DOTALL)
    assert m, "Gate 7 section not found (or Gate 8 heading missing) in RULES_GATE.md"
    gate7 = m.group(1)
    assert "Receipt slice matches funnel role" in gate7, (
        "Gate 7 is missing the G328 wrong-slice receipt check"
    )


def test_playbook_has_role_row_mapping() -> None:
    """PLAYBOOK Step 3 must map each funnel role to a row of the goal→tag table,
    and budget the union of those rows by the mix %."""
    text = _normalised("PLAYBOOK.md")
    assert "Apply the table PER FUNNEL ROLE, not once per plan (G328)" in text, (
        "PLAYBOOK is missing the per-funnel-role application rule"
    )
    assert '| `reach` (TOF) | ALWAYS the "Reach / awareness" row' in text, (
        "PLAYBOOK is missing the reach(TOF)→Reach-row table row"
    )
    assert "the UNION of those rows, budgeted by the mix %" in text, (
        "PLAYBOOK is missing the union-of-rows / mix-% budgeting phrase"
    )


def test_skill_summary_is_role_aware() -> None:
    """SKILL.md's Use-the-MCP bullet must instruct per-role subsets, and the old
    single plan-level instruction must be gone."""
    text = _normalised("SKILL.md")
    assert "each FUNNEL ROLE in the plan's mix needs" in text, (
        "SKILL.md is missing the role-aware analyse instruction"
    )
    assert "analyse the **GOAL-RELEVANT tag subset first**" not in text, (
        "SKILL.md still carries the old plan-level (goal-only) subset instruction"
    )
