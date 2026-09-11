"""Falsifiable guards for p27 "Polish & QA before it ships" (FRFRMU-1065).

Source card `marketing/rules/process-cards/p27-polish-qa-before-shipping.md`.
Core idea: a mandatory pre-ship pass, logged per check (the G650 principle
— "looks good" with no record is not a pass).

Standalone-runnable: `python test_frfrmu1065_qa_pass.py`.
"""
from __future__ import annotations

import re
import sys

from _copywriter import SKILL_DIR, correlation_table_text, qa_checklist_text, skill_text


def test_qa_checklist_file_exists() -> None:
    assert (SKILL_DIR / "qa-checklist.md").is_file()


def test_seven_checks_named() -> None:
    text = qa_checklist_text()
    for check in (
        "Mechanics", "Device / safe zones", "Scan path", "Muted watch",
        "Second eyes", "Outsider test", "The you-flip",
    ):
        assert check in text, f"check {check!r} missing"


def test_qa_record_shape_documented() -> None:
    text = qa_checklist_text()
    assert "qa.checks[] = {check, pass|fail|na, note}" in text


def test_safe_zone_numbers_in_one_config_block() -> None:
    text = qa_checklist_text()
    assert "SAFE_ZONE_CONFIG" in text
    # The actual VALUES must only be assigned once (inside the config
    # block) — the KEY NAMES may be referenced again in prose, but a second
    # numeric assignment (e.g. a stray "125" defined a second time) is the
    # drift this check exists to catch.
    for value in ("250", "320", "125"):
        assigned = re.findall(rf"[:=]\s*{value}\b", text)
        assert len(assigned) == 1, (
            f"{value!r} must be ASSIGNED exactly once (inside SAFE_ZONE_CONFIG), "
            f"found {len(assigned)} assignments"
        )


def test_critic_is_a_separate_subagent_never_the_author() -> None:
    text = qa_checklist_text()
    assert "SEPARATE Task subagent" in text
    assert "never the same run that drafted it" in text
    assert "{verdict, changes, no_findings_note}" in text


def test_outsider_test_never_silently_skipped() -> None:
    text = qa_checklist_text()
    assert "deferred" in text and "declined" in text and "substitute" in text
    assert "Never silently skipped" in text


def test_you_flip_exempts_story_beats_only() -> None:
    text = re.sub(r"\s+", " ", qa_checklist_text())
    assert "OUTSIDE story beats" in text
    assert "story_setup" in text and "story_turn" in text


def test_check_qa_record_no_fail_on_shippable() -> None:
    """Rule 3 target check."""
    text = qa_checklist_text()
    assert "check_qa_record" in text
    assert "none may be `fail`" in text


def test_flop_diagnosis_defers_to_1076_and_keeps_only_trigger() -> None:
    """Two owners for flop diagnosis is the exact risk the ticket calls
    out — this file must say ONE owner (1076), not implement its own
    five-step order."""
    text = qa_checklist_text()
    assert "SUPERSEDED by FRFRMU-1076" in text
    assert "does NOT implement a second diagnosis order here" in text
    assert "hand" in text.lower() and "off" in text.lower()


def test_flop_trigger_reads_lost_verdict() -> None:
    text = qa_checklist_text()
    assert "verdict is `lost`" in text
    assert "FRFRMU-1062" in text


def test_hook_history_no_longer_gapped_here_either() -> None:
    """FRFRMU-1060 shipped the ledger; this file now points at the real
    write recipe instead of the pre-1060 GAP marker."""
    text = qa_checklist_text()
    assert "FRFRMU-1060 not built" not in text
    assert "hook-variants.md" in text


def test_skill_wires_edit_pass_to_qa_checklist() -> None:
    text = skill_text()
    assert "qa-checklist.md" in text
    assert "FRFRMU-1065" in text


def test_no_dollar_figures_in_qa_checklist() -> None:
    dollar_re = re.compile(
        r"\$\s*[1-9][\d,]*(?:\.\d+)?|\bUSD\b|\bin dollars\b|\bin US dollars\b",
        re.IGNORECASE,
    )
    m = dollar_re.search(qa_checklist_text())
    assert not m, f"dollar figure found in qa-checklist.md: {m.group(0)!r}"


def test_correlation_table_still_intact_regression_guard() -> None:
    """Planner-touching regression guard for this ticket: 1065 must not
    have edited the correlation table it doesn't own."""
    text = correlation_table_text()
    assert "n_ways_mistakes | open_loop, warning" in text


_CHECKS = [
    ("qa-checklist.md exists", test_qa_checklist_file_exists),
    ("seven checks named", test_seven_checks_named),
    ("qa record shape documented", test_qa_record_shape_documented),
    ("safe-zone numbers in one config block", test_safe_zone_numbers_in_one_config_block),
    ("critic is a separate subagent", test_critic_is_a_separate_subagent_never_the_author),
    ("outsider test never silently skipped", test_outsider_test_never_silently_skipped),
    ("you-flip exempts story beats only", test_you_flip_exempts_story_beats_only),
    ("check_qa_record: no fail on shippable", test_check_qa_record_no_fail_on_shippable),
    ("flop diagnosis defers to 1076", test_flop_diagnosis_defers_to_1076_and_keeps_only_trigger),
    ("flop trigger reads lost verdict", test_flop_trigger_reads_lost_verdict),
    ("hook_history no longer gapped", test_hook_history_no_longer_gapped_here_either),
    ("SKILL.md wires edit pass to qa-checklist.md", test_skill_wires_edit_pass_to_qa_checklist),
    ("no dollar figures in qa-checklist.md", test_no_dollar_figures_in_qa_checklist),
    ("correlation table untouched regression guard", test_correlation_table_still_intact_regression_guard),
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
