"""Falsifiable guards for p24 "Bullets (Feature + Benefit + Meaning)"
(FRFRMU-1059), copywriter half.

Ownership moved from the planner to the copywriter (founder decision,
2026-09-07) -- the planner only marks WHICH beats carry value
(`carries_value_lines: true`); see
`rm-content-planner/tests/test_frfrmu1059_value_lines_flag.py` for that half.

Standalone-runnable: `python test_frfrmu1059_bullet_recipe.py`.
"""
from __future__ import annotations

import re
import sys

from _copywriter import SKILL_DIR, block_skeletons_text, bullet_recipe_text, skill_text


def test_bullet_recipe_file_exists() -> None:
    assert (SKILL_DIR / "bullet-recipe.md").is_file()


def test_formula_stated() -> None:
    text = bullet_recipe_text()
    assert "so you can" in text
    assert "which means" in text


def test_why_drill_is_three_deep() -> None:
    text = bullet_recipe_text()
    assert "×3" in text or "three times" in text
    assert "THIRD answer is the meaning" in text


def test_overproduce_then_cut_ratio() -> None:
    text = bullet_recipe_text()
    assert "2×" in text or "2x" in text.lower()
    assert "10-12" in text and "5-6" in text


def test_honesty_screen_on_meaning_clause() -> None:
    text = bullet_recipe_text()
    assert "never lose a client again" in text  # the bad example
    assert "evenings are yours again" in text  # the good example


def test_spread_check_is_warning_not_hard_fail() -> None:
    text = bullet_recipe_text()
    idx = text.index("check_bullets_spread")
    nearby = re.sub(r"\s+", " ", text[idx: idx + 200])
    assert "warning" in nearby.lower()


def test_three_layers_check_is_hard() -> None:
    """Rule 3 target -- a two-layer line (no meaning) must be a hard fail."""
    text = bullet_recipe_text()
    idx = text.index("check_bullets_three_layers")
    nearby = re.sub(r"\s+", " ", text[idx: idx + 300])
    assert "**hard" in nearby.lower()
    assert "fails" in nearby


def test_planner_owns_which_beats_never_the_copywriter() -> None:
    text = bullet_recipe_text()
    assert "never decides WHICH beats" in text


def test_block_skeletons_wires_flag_conditional() -> None:
    text = block_skeletons_text()
    assert "carries_value_lines" in text
    assert "bullet-recipe.md" in text


def test_skill_wires_bullet_recipe_into_draft_pass() -> None:
    text = skill_text()
    assert "bullet-recipe.md" in text
    assert "FRFRMU-1059" in text


_CHECKS = [
    ("bullet-recipe.md exists", test_bullet_recipe_file_exists),
    ("F+B+M formula stated", test_formula_stated),
    ("why-drill is three deep", test_why_drill_is_three_deep),
    ("overproduce-then-cut ratio", test_overproduce_then_cut_ratio),
    ("honesty screen on meaning clause", test_honesty_screen_on_meaning_clause),
    ("spread check is a warning", test_spread_check_is_warning_not_hard_fail),
    ("three-layers check is hard", test_three_layers_check_is_hard),
    ("planner owns which beats", test_planner_owns_which_beats_never_the_copywriter),
    ("block-skeletons.md wires flag", test_block_skeletons_wires_flag_conditional),
    ("SKILL.md wires bullet-recipe.md", test_skill_wires_bullet_recipe_into_draft_pass),
]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    failed = 0
    for label, check in _CHECKS:
        try:
            check()
        except (AssertionError, FileNotFoundError) as exc:
            failed += 1
            print(f"[FAIL] {label}: {exc}")
        else:
            print(f"[PASS] {label}")
    print(f"{len(_CHECKS) - failed}/{len(_CHECKS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
