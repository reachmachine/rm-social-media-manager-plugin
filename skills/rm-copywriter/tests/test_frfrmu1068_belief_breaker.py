"""Falsifiable guards for p30 "Thirsty content" (FRFRMU-1068), copywriter half.

Part A (the `m_type` field + default order rule) lives in
`playbook/step-03-10-false-beliefs-map.md` §7 — see the planner's own tests.

Standalone-runnable: `python test_frfrmu1068_belief_breaker.py`.
"""
from __future__ import annotations

import re
import sys

from _copywriter import SKILL_DIR, belief_breaker_text, block_skeletons_text, skill_text


def test_belief_breaker_file_exists() -> None:
    assert (SKILL_DIR / "belief-breaker.md").is_file()


def test_names_the_m_and_belief_row() -> None:
    text = belief_breaker_text()
    assert "item_id" in text
    assert "mistake, misconception, or myth" in text


def test_no_evidence_no_debunk() -> None:
    text = belief_breaker_text()
    assert "no evidence, no debunk" in text.lower()


def test_domain_claims_ask_user_once() -> None:
    text = re.sub(r"\s+", " ", belief_breaker_text())
    assert "ONE ask-user question" in text
    assert "actually false in your field" in text


def test_thirst_test_stops_before_the_method() -> None:
    text = belief_breaker_text()
    assert "stops before the METHOD" in text or "stop before the METHOD" in text


def test_method_given_flag_blocks_shippable_and_is_hard() -> None:
    """Rule 3 target -- the method_given block must be a hard rule, or a
    belief-breaker that spills the method for free ships anyway."""
    text = belief_breaker_text()
    idx = text.rindex("method_given")  # its DEFINITION, in the Validator section
    nearby = re.sub(r"\s+", " ", text[idx - 100: idx + 300])
    assert "hard" in nearby.lower()
    assert "cannot" in nearby.lower() and "shippable" in nearby.lower()


def test_enemy_rule_never_a_named_person() -> None:
    text = belief_breaker_text()
    assert "never a named person" in text


def test_no_staged_demo_results() -> None:
    text = belief_breaker_text()
    assert "no staged results" in text.lower()


def test_next_step_never_the_backend_rung() -> None:
    text = re.sub(r"\s+", " ", belief_breaker_text())
    assert "never the backend rung" in text


def test_block_skeletons_wires_belief_breaker() -> None:
    text = block_skeletons_text()
    assert "belief-breaker.md" in text
    assert "m_type" in text


def test_skill_wires_belief_breaker_into_draft_pass() -> None:
    text = skill_text()
    assert "belief-breaker.md" in text
    assert "FRFRMU-1068" in text


_CHECKS = [
    ("belief-breaker.md exists", test_belief_breaker_file_exists),
    ("names the M and belief row", test_names_the_m_and_belief_row),
    ("no evidence, no debunk", test_no_evidence_no_debunk),
    ("domain claims ask-user once", test_domain_claims_ask_user_once),
    ("thirst test stops before the method", test_thirst_test_stops_before_the_method),
    ("method_given flag is hard, blocks shippable", test_method_given_flag_blocks_shippable_and_is_hard),
    ("enemy rule: never a named person", test_enemy_rule_never_a_named_person),
    ("no staged demo results", test_no_staged_demo_results),
    ("next step never the backend rung", test_next_step_never_the_backend_rung),
    ("block-skeletons.md wires belief-breaker.md", test_block_skeletons_wires_belief_breaker),
    ("SKILL.md wires belief-breaker.md in", test_skill_wires_belief_breaker_into_draft_pass),
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
