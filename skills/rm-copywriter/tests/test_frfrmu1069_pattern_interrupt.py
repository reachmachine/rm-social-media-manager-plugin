"""Falsifiable guards for p31 "Pattern-interrupt creative" (FRFRMU-1069),
copywriter half.

Part A (the matrix step) lives in `playbook/step-08-visual-recipe.md`
V.2b -- see the planner's own tests.

Standalone-runnable: `python test_frfrmu1069_pattern_interrupt.py`.
"""
from __future__ import annotations

import re
import sys

from _copywriter import SKILL_DIR, block_skeletons_text, pattern_interrupt_text, skill_text


def test_pattern_interrupt_file_exists() -> None:
    assert (SKILL_DIR / "pattern-interrupt.md").is_file()


def test_s28_shape_named() -> None:
    text = pattern_interrupt_text()
    assert "grab" in text.lower() and "curiosity gap" in text.lower()


def test_question_form_fallback_added() -> None:
    text = pattern_interrupt_text()
    assert "Are you tired of" in text
    assert "H.2b" in text


def test_meta_ads_out_of_scope() -> None:
    text = pattern_interrupt_text()
    assert "out of scope" in text.lower()
    assert "advisory only" in text.lower()


def test_prequalifies_is_a_hard_check() -> None:
    """Rule 3 target -- a cold-account reach reel that fails to prequalify
    must be a hard block, not advice."""
    text = pattern_interrupt_text()
    idx = text.rindex("check_prequalifies")
    nearby = re.sub(r"\s+", " ", text[idx: idx + 250])
    assert "hard" in nearby.lower()
    assert "cannot" in nearby.lower()


def test_fatigue_order_cites_1054() -> None:
    text = pattern_interrupt_text()
    assert "creative" in text.lower() and "FRFRMU-1054" in text


def test_visual_rationale_must_be_named_not_looks_good() -> None:
    text = pattern_interrupt_text()
    assert "check_visual_rationale_stated" in text


def test_block_skeletons_wires_pattern_interrupt() -> None:
    text = block_skeletons_text()
    assert "pattern-interrupt.md" in text
    assert "V.2b" in text


def test_skill_wires_pattern_interrupt_into_draft_pass() -> None:
    text = skill_text()
    assert "pattern-interrupt.md" in text
    assert "FRFRMU-1069" in text


_CHECKS = [
    ("pattern-interrupt.md exists", test_pattern_interrupt_file_exists),
    ("S28 shape named", test_s28_shape_named),
    ("question-form fallback added", test_question_form_fallback_added),
    ("Meta ads out of scope", test_meta_ads_out_of_scope),
    ("prequalifies is a hard check", test_prequalifies_is_a_hard_check),
    ("fatigue order cites FRFRMU-1054", test_fatigue_order_cites_1054),
    ("visual rationale must be named", test_visual_rationale_must_be_named_not_looks_good),
    ("block-skeletons.md wires pattern-interrupt.md", test_block_skeletons_wires_pattern_interrupt),
    ("SKILL.md wires pattern-interrupt.md in", test_skill_wires_pattern_interrupt_into_draft_pass),
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
