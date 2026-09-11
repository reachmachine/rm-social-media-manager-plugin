"""Falsifiable guards for p34 "Trial closes" (FRFRMU-1072).

Planner untouched — this ticket only supplies wording; Gate 5 and CT.1/CT.2
are not edited (per this ticket's own execution plan).

Standalone-runnable: `python test_frfrmu1072_closes.py`.
"""
from __future__ import annotations

import re
import sys

from _copywriter import SKILL_DIR, block_skeletons_text, closes_text, skill_text


def test_closes_file_exists() -> None:
    assert (SKILL_DIR / "closes.md").is_file()


def test_all_sixteen_closes_present() -> None:
    text = closes_text()
    names = (
        "Money is Good", "Disposable Income", "Money Replenishes",
        "Break Old Habits", "Information Alone", "Money or Excuses",
        "Your Two Choices", "Their Two Choices", "Us vs. Them",
        "The Hand Hold", "Say Goodbye", "Now & Later", "Only Excuses",
        "Reluctant Hero", "If You Only Got", "Close Close",
    )
    for name in names:
        assert name in text, f"close {name!r} missing"


def test_first_yes_never_money() -> None:
    text = re.sub(r"\s+", " ", closes_text())
    assert "first yes is always about the problem or the dream — never money" in text


def test_micro_yes_density_bounds() -> None:
    text = closes_text()
    assert "at most ONE" in text
    assert "~1 per minute" in text


def test_shame_edged_closes_rewritten() -> None:
    """The original shaming forms must NOT appear -- only the rewritten
    our-voice versions."""
    text = closes_text()
    assert "good at making money, or good at making excuses" not in text.lower()
    assert "Which one do you want to be paying for in a year" in text


def test_classes_6_9_16_are_dm_restricted() -> None:
    """Rule 3 target -- the DM restriction on classes 6/9/16 is the open
    legal item's hard line."""
    text = closes_text()
    idx = text.rindex("check_closes_dm_restricted")
    nearby = re.sub(r"\s+", " ", text[idx: idx + 300])
    assert "hard" in nearby.lower()
    assert "6, 9, 16" in nearby or "6, 9" in nearby


def test_dm_allowed_false_on_the_three_restricted_rows() -> None:
    text = closes_text()
    # exactly 3 bold-false markers in the table (classes 6, 9, 16)
    assert text.count("**false**") == 3


def test_open_legal_item_stated_not_resolved() -> None:
    text = closes_text()
    assert "VERIFY WITH COUNSEL" in text or "counsel clears" in text.lower()
    assert "does not invent a resolution" in text.lower() or "does not attempt to resolve" in text.lower() or "never invent" in text.lower() or "does not invent" in text.lower()


def test_comfort_screen_cuts_never_reappear() -> None:
    text = closes_text()
    assert "closes_disabled_by_user" in text
    assert "never re-proposed" in text


def test_stack_mapping_cites_named_tickets() -> None:
    text = closes_text()
    assert "FRFRMU-1049" in text  # 15 -> stack If/All
    assert "FRFRMU-1043" in text  # 14 -> persona chair
    assert "FRFRMU-1031" in text  # 11 -> escape phrases


def test_gate5_stays_in_charge_no_widening() -> None:
    text = re.sub(r"\s+", " ", closes_text())
    assert "Gate 5" in text
    assert "never widens where a close is allowed" in text


def test_block_skeletons_wires_closes() -> None:
    text = block_skeletons_text()
    assert "closes.md" in text


def test_skill_wires_closes_into_draft_pass() -> None:
    text = skill_text()
    assert "closes.md" in text
    assert "FRFRMU-1072" in text


def test_no_dollar_figures_in_closes() -> None:
    dollar_re = re.compile(
        r"\$\s*[1-9][\d,]*(?:\.\d+)?|\bUSD\b|\bin dollars\b|\bin US dollars\b",
        re.IGNORECASE,
    )
    m = dollar_re.search(closes_text())
    assert not m, f"dollar/COGS figure found in closes.md: {m.group(0)!r}"


_CHECKS = [
    ("closes.md exists", test_closes_file_exists),
    ("all sixteen closes present", test_all_sixteen_closes_present),
    ("first yes never money", test_first_yes_never_money),
    ("micro-yes density bounds", test_micro_yes_density_bounds),
    ("shame-edged closes rewritten", test_shame_edged_closes_rewritten),
    ("classes 6/9/16 are DM-restricted (hard)", test_classes_6_9_16_are_dm_restricted),
    ("dm_allowed false on exactly the 3 restricted rows", test_dm_allowed_false_on_the_three_restricted_rows),
    ("open legal item stated, not resolved", test_open_legal_item_stated_not_resolved),
    ("comfort-screen cuts never reappear", test_comfort_screen_cuts_never_reappear),
    ("stack mapping cites named tickets", test_stack_mapping_cites_named_tickets),
    ("Gate 5 stays in charge, no widening", test_gate5_stays_in_charge_no_widening),
    ("block-skeletons.md wires closes.md", test_block_skeletons_wires_closes),
    ("SKILL.md wires closes.md in", test_skill_wires_closes_into_draft_pass),
    ("no dollar figures in closes.md", test_no_dollar_figures_in_closes),
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
