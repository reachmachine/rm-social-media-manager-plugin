"""Falsifiable guards for p64 "Diagnose an underperforming reel" (FRFRMU-1076).

Supersedes qa-checklist.md's original 5-step flop order (FRFRMU-1065) --
this file is the single owner of the diagnosis. Fix the FIRST failing item
only, as one test; escalate to a rebuild only after a passing checklist and
a lagging re-test.

Standalone-runnable: `python test_frfrmu1076_flop_diagnosis.py`.
"""
from __future__ import annotations

import re
import sys

from _copywriter import SKILL_DIR, flop_diagnosis_text, qa_checklist_text, skill_text


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def test_flop_diagnosis_file_exists() -> None:
    assert (SKILL_DIR / "flop-diagnosis.md").is_file()


def test_eight_items_in_order() -> None:
    text = flop_diagnosis_text()
    items = (
        "Hook", "Offer clarity", "Reason to act now", "Emotional driver",
        "Bullets / value lines", "Price vs perceived value", "Visuals",
        "Proof",
    )
    positions = []
    for item in items:
        idx = text.index(item)
        positions.append(idx)
    assert positions == sorted(positions), "the 8 items are not in the card's order"


def test_each_item_requires_evidence_not_a_feeling() -> None:
    flat = _flat(flop_diagnosis_text()).lower()
    assert "one line of evidence" in flat
    assert '"the reel feels weak" is not a verdict' in flat


def test_trigger_is_lost_verdict_or_explicit_ask() -> None:
    flat = _flat(flop_diagnosis_text())
    assert "`lost`" in flop_diagnosis_text()
    assert "why did this flop" in flat.lower()


def test_cold_account_never_flagged_on_hour_1_views() -> None:
    flat = _flat(flop_diagnosis_text()).lower()
    assert "never flagged on hour-1 views" in flat


def test_item_3_never_fakes_scarcity() -> None:
    text = flop_diagnosis_text()
    idx = text.index("3. **Reason to act now**")
    section = text[idx: idx + 400]
    assert "never fake one" in section.lower() or "never a fake" in section.lower()


def test_fix_first_failure_only_one_test() -> None:
    flat = _flat(flop_diagnosis_text()).lower()
    assert "the first failure only" in flat or "fix the first" in flat
    assert "exactly one change" in flat or "exactly one item" in flat


def test_ledger_gap_is_labelled_not_invented() -> None:
    flat = _flat(flop_diagnosis_text())
    assert "[GAP: needs FRFRMU-1075 ledger key]" in flat, (
        "no labelled fallback for a missing FRFRMU-1075 ledger key -- the "
        "recipe must not invent a ledger shape"
    )


def test_reel_keeps_its_uid_and_history() -> None:
    flat = _flat(flop_diagnosis_text()).lower()
    assert "reel_uid" in flat
    assert "keeps its" in flat


def test_rebuild_only_after_passing_checklist_and_still_lagging() -> None:
    flat = _flat(flop_diagnosis_text()).lower()
    assert "every applicable item passes" in flat
    assert "the re-tested numbers still lag" in flat
    assert "the creator decides" in flat


def test_supersedes_qa_checklist_five_step_order() -> None:
    text = qa_checklist_text()
    flat = _flat(text)
    assert "SUPERSEDED by FRFRMU-1076" in flat
    assert "flop-diagnosis.md" in flat


def test_open_word_question_not_silently_resolved() -> None:
    flat = _flat(flop_diagnosis_text()).lower()
    assert "flopped" in flat and "`lost`" in flop_diagnosis_text()
    assert "not resolved here" in flat or "not resolved" in flat


def test_skill_wires_flop_diagnosis_in() -> None:
    text = skill_text()
    assert "flop-diagnosis.md" in text
    assert "FRFRMU-1076" in text


def test_no_dollar_figures_in_flop_diagnosis() -> None:
    dollar_re = re.compile(
        r"\$\s*[1-9][\d,]*(?:\.\d+)?|\bUSD\b|\bin dollars\b|\bin US dollars\b",
        re.IGNORECASE,
    )
    m = dollar_re.search(flop_diagnosis_text())
    assert not m, f"dollar/COGS figure found in flop-diagnosis.md: {m.group(0)!r}"


_CHECKS = [
    ("flop-diagnosis.md exists", test_flop_diagnosis_file_exists),
    ("eight items in the card's order", test_eight_items_in_order),
    ("each item requires evidence, not a feeling", test_each_item_requires_evidence_not_a_feeling),
    ("trigger is a lost verdict or explicit ask", test_trigger_is_lost_verdict_or_explicit_ask),
    ("cold account never flagged on hour-1 views", test_cold_account_never_flagged_on_hour_1_views),
    ("item 3 never fakes scarcity", test_item_3_never_fakes_scarcity),
    ("fix the first failure only, one test", test_fix_first_failure_only_one_test),
    ("ledger gap is labelled, not invented", test_ledger_gap_is_labelled_not_invented),
    ("reel keeps its uid and history", test_reel_keeps_its_uid_and_history),
    ("rebuild only after passing checklist + still lagging", test_rebuild_only_after_passing_checklist_and_still_lagging),
    ("supersedes qa-checklist's 5-step order", test_supersedes_qa_checklist_five_step_order),
    ("open word question stated, not resolved", test_open_word_question_not_silently_resolved),
    ("SKILL.md wires flop-diagnosis.md in", test_skill_wires_flop_diagnosis_in),
    ("no dollar figures in flop-diagnosis.md", test_no_dollar_figures_in_flop_diagnosis),
]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    failed = 0
    for label, check in _CHECKS:
        try:
            check()
        except (AssertionError, FileNotFoundError, ValueError) as exc:
            failed += 1
            print(f"[FAIL] {label}: {exc}")
        else:
            print(f"[PASS] {label}")
    print(f"{len(_CHECKS) - failed}/{len(_CHECKS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
