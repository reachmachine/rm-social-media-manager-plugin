"""Falsifiable guards for p28 "Swipe file" (FRFRMU-1066), copywriter half.

Parts A/B (the `swipe` brief key + intake/KPI-review asks) live in
`playbook/step-01-intake-fields-2.md` and `playbook/step-12-after-the-save.md`
§4 -- see the planner's own tests.

Standalone-runnable: `python test_frfrmu1066_swipe_file.py`.
"""
from __future__ import annotations

import re
import sys

from _copywriter import SKILL_DIR, skill_text, swipe_file_text


def test_swipe_file_recipe_exists() -> None:
    assert (SKILL_DIR / "swipe-file.md").is_file()


def test_warm_up_reads_before_writing() -> None:
    text = swipe_file_text()
    assert "3-5 relevant entries" in text
    assert "reading pass, not a writing one" in text


def test_citation_shape_matches_proof_and_pattern_ref() -> None:
    text = swipe_file_text()
    assert "source_ref: swipe:<id>" in text
    assert "proof:<id>" in text  # named alongside for the shape-family comparison


def test_rm_library_never_duplicated_into_swipe() -> None:
    text = swipe_file_text()
    assert "never copied into `swipe`" in text or "never copied into" in text


def test_classic_label_is_human_only() -> None:
    """Rule 3 target -- the agent must never be able to set `classic: true`
    from view counts alone."""
    text = swipe_file_text()
    assert "The agent never sets `classic: true`" in text
    idx = text.rindex("classic: true` set")
    nearby = re.sub(r"\s+", " ", text[idx - 60: idx + 300])
    assert "**hard**" in nearby.lower() or "hard" in nearby.lower()
    assert "fails" in nearby


def test_no_verbatim_reuse_check_present() -> None:
    text = swipe_file_text()
    assert "check_no_verbatim_swipe_reuse" in text


def test_agent_never_writes_made_me_buy_on_creators_behalf() -> None:
    text = swipe_file_text()
    assert "made me buy" in text.lower()
    assert "never write" in text.lower() or "never writes" in text.lower()


def test_skill_wires_warm_up_into_the_workflow() -> None:
    text = skill_text()
    assert "swipe-file.md" in text
    assert "FRFRMU-1066" in text
    assert "Warm-up" in text


_CHECKS = [
    ("swipe-file.md exists", test_swipe_file_recipe_exists),
    ("warm-up reads before writing", test_warm_up_reads_before_writing),
    ("citation shape matches proof/pattern_ref", test_citation_shape_matches_proof_and_pattern_ref),
    ("RM library never duplicated into swipe", test_rm_library_never_duplicated_into_swipe),
    ("classic label is human-only, hard check", test_classic_label_is_human_only),
    ("no-verbatim-reuse check present", test_no_verbatim_reuse_check_present),
    ("agent never writes 'made me buy' for the creator", test_agent_never_writes_made_me_buy_on_creators_behalf),
    ("SKILL.md wires the warm-up into the workflow", test_skill_wires_warm_up_into_the_workflow),
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
