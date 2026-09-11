"""Falsifiable guards for p25 "Generate & test hooks", parts B-F (FRFRMU-1060).

Part A (the hidden-story hunt -> `hook_facts`) and the H.2 saturation count
stay with the planner (founder scope split, 2026-09-07). This file pins the
copywriter's half: permutation generators filled ONLY from `hook_facts`, the
truth check per element, `pays_off_at`, and the `hook_history` ledger write.

Standalone-runnable: `python test_frfrmu1060_hook_variants.py`.
"""
from __future__ import annotations

import re
import sys

from _copywriter import SKILL_DIR, hook_variants_text, qa_checklist_text, skill_text


def test_hook_variants_file_exists() -> None:
    assert (SKILL_DIR / "hook-variants.md").is_file()


def test_s29_permutation_shapes_named() -> None:
    text = hook_variants_text()
    assert "Unlikely Character" in text
    assert "Result + Timing" in text or "Result + Timing − Pain" in text


def test_permutation_shapes_filled_only_from_hook_facts() -> None:
    text = hook_variants_text()
    assert "hook_facts" in text
    assert "ONLY from `hook_facts`" in text or "ONLY from" in text


def test_truth_check_is_a_hard_line() -> None:
    """Rule 3 target — an invented element (no owned fact, no proof id) must
    be a hard fail, not a warning."""
    text = hook_variants_text()
    idx = text.rindex("check_hook_facts_true")  # its DEFINITION, in §G, not the §C forward-reference
    nearby = re.sub(r"\s+", " ", text[idx: idx + 400])
    assert "**hard" in nearby.lower(), (
        "check_hook_facts_true must say it is a hard check, or an invented "
        "number/person/timeframe silently ships"
    )
    assert "fails" in nearby


def test_owned_fact_or_proof_id_required() -> None:
    text = hook_variants_text()
    assert "owned_by_user: true" in text
    assert "proof:<id>" in text or "proof:" in text


def test_payoff_beat_documented() -> None:
    text = hook_variants_text()
    assert "pays_off_at" in text
    assert "check_hook_payoff" in text


def test_losers_never_deleted() -> None:
    text = hook_variants_text()
    assert "never deleted" in text or "Losers are never deleted" in text


def test_hook_history_shape_matches_backend() -> None:
    """The ledger entry shape documented here must match the fields the
    backend reserved-key checker requires, or a copy pack could write a
    shape the backend rejects at save time."""
    text = hook_variants_text()
    for field in (
        "cycle", "hook_id", "template", "result_vs_own_median", "verdict",
    ):
        assert field in text, f"hook_history field {field!r} not documented"
    for verdict in ("won", "held", "lost"):
        assert verdict in text


def test_hook_history_verdict_is_lost_not_flopped() -> None:
    """Matches the vocabulary already baked into qa-checklist.md/1062/1076
    (2026-09-07 open question, resolved here by following the merged
    convention rather than inventing a third word)."""
    text = hook_variants_text()
    assert "lost" in text
    assert "flopped" not in text


def test_skill_wires_hook_variants_into_the_draft_pass() -> None:
    text = skill_text()
    assert "hook-variants.md" in text
    assert "FRFRMU-1060" in text


def test_skill_no_longer_carries_the_hook_history_gap_marker() -> None:
    """Rule 3 target — before this ticket, SKILL.md said
    `[GAP: hook_history — FRFRMU-1060 not built]`. That marker must be gone
    now the key is shipped, or the agent will keep refusing to write real
    learning-loop data."""
    text = skill_text()
    assert "FRFRMU-1060 not built" not in text
    assert "hook_history" in text


def test_qa_checklist_no_longer_carries_the_hook_history_gap_marker() -> None:
    text = qa_checklist_text()
    assert "FRFRMU-1060 not built" not in text


_CHECKS = [
    ("hook-variants.md exists", test_hook_variants_file_exists),
    ("S29 permutation shapes named", test_s29_permutation_shapes_named),
    ("shapes filled only from hook_facts", test_permutation_shapes_filled_only_from_hook_facts),
    ("truth check is a hard line", test_truth_check_is_a_hard_line),
    ("owned fact or proof id required", test_owned_fact_or_proof_id_required),
    ("payoff beat documented", test_payoff_beat_documented),
    ("losers never deleted", test_losers_never_deleted),
    ("hook_history shape matches backend", test_hook_history_shape_matches_backend),
    ("hook_history verdict is lost, not flopped", test_hook_history_verdict_is_lost_not_flopped),
    ("SKILL.md wires hook-variants.md into the draft pass", test_skill_wires_hook_variants_into_the_draft_pass),
    ("SKILL.md GAP marker gone", test_skill_no_longer_carries_the_hook_history_gap_marker),
    ("qa-checklist.md GAP marker gone", test_qa_checklist_no_longer_carries_the_hook_history_gap_marker),
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
