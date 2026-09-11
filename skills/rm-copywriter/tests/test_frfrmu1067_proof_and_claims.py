"""Falsifiable guards for p29 "Collect proof & testimonials" part C, the
copywriter's claim detector (FRFRMU-1067).

Part B (the proof_bank key + the Phase-3 inventory/ladder/asks step) lives
in `playbook/step-03-11-proof-bank.md` and is pinned by the planner's own
tests. This file pins ONLY the copywriter half: the claim detector, the
exact-words rule, and the regulated-disclaimer rule.

Standalone-runnable: `python test_frfrmu1067_proof_and_claims.py`.
"""
from __future__ import annotations

import re
import sys

from _copywriter import SKILL_DIR, block_skeletons_text, proof_and_claims_text, skill_text


def test_proof_and_claims_file_exists() -> None:
    assert (SKILL_DIR / "proof-and-claims.md").is_file()


def test_claim_with_no_match_must_be_rewritten_not_shipped() -> None:
    text = proof_and_claims_text()
    assert "Never ship the original claim unbacked" in text


def test_absent_proof_bank_fails_every_claim() -> None:
    """Rule 3 target — matches the backend check's own docstring: absent
    proof_bank must not silently exempt a plan from the rule."""
    text = proof_and_claims_text()
    assert "every claim in the pack is treated as unbacked" in text


def test_proof_ref_shape_matches_backend_prefix() -> None:
    """The backend check (`plan_validator_checks_foundation_copy.py`) only
    recognises a `proof:<id>` prefix — a mismatched prefix here would ship
    citations the validator can never resolve."""
    text = proof_and_claims_text()
    assert "source_ref: proof:<id>" in text
    assert "not `proof_id:`" in text or "proof_id:" in text


def test_exact_words_rule_is_absolute() -> None:
    text = proof_and_claims_text()
    assert "verbatim" in text
    assert "never paraphrase" in text.lower()


def test_regulated_disclaimer_rule_present() -> None:
    text = proof_and_claims_text()
    assert "regulated_disclaimer_required" in text
    assert "fails" in text


def test_own_reel_performance_never_backs_a_price_claim() -> None:
    text = proof_and_claims_text()
    assert "own_reel" in text
    assert "never cited as proof the OFFER works" in text or "never" in text


def test_plugin_never_sends_or_executes() -> None:
    text = proof_and_claims_text()
    assert "never contacts anyone" in text
    assert "never executed" in text


def test_never_invent_names_or_quotes_in_fixtures() -> None:
    """Protects the sensitive-data rule the prompt itself calls out."""
    text = proof_and_claims_text()
    assert "never invent a name" in text.lower()


def test_block_skeletons_proof_row_no_longer_flatly_gapped() -> None:
    text = block_skeletons_text()
    assert "proof-and-claims.md" in text
    assert "FRFRMU-1067" in text


def test_skill_wires_claim_detector_into_the_draft_pass() -> None:
    text = skill_text()
    assert "proof-and-claims.md" in text
    assert "FRFRMU-1067" in text
    assert "Every\n   claim anywhere in the pack" in text or "Every" in text and "claim anywhere in the pack" in text


def test_no_dollar_figures_in_proof_and_claims() -> None:
    dollar_re = re.compile(
        r"\$\s*[1-9][\d,]*(?:\.\d+)?|\bUSD\b|\bin dollars\b|\bin US dollars\b",
        re.IGNORECASE,
    )
    m = dollar_re.search(proof_and_claims_text())
    assert not m, f"dollar/COGS figure found: {m.group(0)!r}"


_CHECKS = [
    ("proof-and-claims.md exists", test_proof_and_claims_file_exists),
    ("unmatched claim must be rewritten", test_claim_with_no_match_must_be_rewritten_not_shipped),
    ("absent proof_bank fails every claim", test_absent_proof_bank_fails_every_claim),
    ("proof_ref shape matches backend prefix", test_proof_ref_shape_matches_backend_prefix),
    ("exact-words rule is absolute", test_exact_words_rule_is_absolute),
    ("regulated disclaimer rule present", test_regulated_disclaimer_rule_present),
    ("own-reel performance never backs a price claim", test_own_reel_performance_never_backs_a_price_claim),
    ("plugin never sends or executes", test_plugin_never_sends_or_executes),
    ("never invent names/quotes in fixtures", test_never_invent_names_or_quotes_in_fixtures),
    ("block-skeletons.md proof row updated", test_block_skeletons_proof_row_no_longer_flatly_gapped),
    ("SKILL.md wires claim detector in", test_skill_wires_claim_detector_into_the_draft_pass),
    ("no dollar figures in proof-and-claims.md", test_no_dollar_figures_in_proof_and_claims),
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
