"""Falsifiable guards for p32 "Brief a hired writer" (FRFRMU-1070).

The plugin never hires, pays, contacts or evaluates people; it packages
foundation-key inputs into one Markdown brief a creator can hand to a human
writer, and it treats what comes back as a first draft, never final.

Standalone-runnable: `python test_frfrmu1070_writer_brief.py`.
"""
from __future__ import annotations

import re
import sys

from _copywriter import SKILL_DIR, skill_text, writer_brief_text


def test_writer_brief_file_exists() -> None:
    assert (SKILL_DIR / "writer-brief.md").is_file()


def test_seven_categories_present() -> None:
    text = writer_brief_text()
    categories = (
        "market / who they are", "benefits (what they get)",
        "payoffs (the transformation)", "motivation (why now)",
        "emotional impact", "reason to buy", "buy-now / limited bonus",
    )
    for cat in categories:
        assert cat in text, f"writer-brief.md is missing category {cat!r}"


def test_each_category_cites_a_foundation_key() -> None:
    text = writer_brief_text()
    for key in (
        "FRFRMU-1031", "FRFRMU-1049", "FRFRMU-1056", "FRFRMU-1041",
        "FRFRMU-1040", "FRFRMU-1055", "FRFRMU-1050", "FRFRMU-1052",
    ):
        assert key in text, f"writer-brief.md never cites {key!r}"


def test_unvetted_excludes_dossier_and_ladder_internals() -> None:
    flat = re.sub(r"\s+", " ", writer_brief_text())
    idx = flat.rindex("`audience: unvetted`")
    section = flat[idx: idx + 700]
    assert "competitor dossier" in section
    assert "value-ladder internals" in section
    assert "unreleased items" in section
    assert "declined" in section and "private" in section


def test_unvetted_filter_runs_before_assembly_not_a_redaction_pass() -> None:
    flat = re.sub(r"\s+", " ", writer_brief_text()).lower()
    assert "before the seven categories are assembled" in flat, (
        "the least-privilege ordering rule is gone -- a redaction-after-build "
        "brief can leak through a diff or a copy-paste"
    )


def test_paste_back_is_v1_author_external() -> None:
    flat = re.sub(r"\s+", " ", writer_brief_text())
    assert "author: external" in flat
    assert "v1" in flat and "v2" in flat
    assert "never ships raw" in flat


def test_paste_back_runs_block_truth_clone_qa_in_order() -> None:
    text = writer_brief_text()
    idx = text.index("## D. Paste-back")
    section = text[idx: idx + 1800]
    for step in ("Block check", "Truth check", "Near-clone check",
                 "seven-check QA pass"):
        assert step in section, f"paste-back section is missing {step!r}"
    # order: block before truth before clone before QA
    order = [section.index(s) for s in
             ("Block check", "Truth check", "Near-clone check", "seven-check QA")]
    assert order == sorted(order), "paste-back checks run out of order"


def test_audition_spec_is_one_slot_never_a_month() -> None:
    flat = re.sub(r"\s+", " ", writer_brief_text())
    assert "ONE reel's brief" in flat
    assert "never a whole month" in flat


def test_no_pii_or_hiring_stored() -> None:
    flat = writer_brief_text().lower()
    assert "never hires, pays, contacts" in flat or "never hires, pays" in flat
    assert "no pii" in flat or "no name, contact detail" in flat


def test_storage_key_shape() -> None:
    text = writer_brief_text()
    assert "writer_briefs__<plan_id>__<reel_uid>" in text


def test_validator_severities() -> None:
    text = writer_brief_text()
    idx = text.rindex("check_writer_brief_complete")
    nearby = re.sub(r"\s+", " ", text[idx: idx + 200])
    assert "warning" in nearby.lower()

    idx = text.rindex("check_unvetted_excludes")
    nearby = re.sub(r"\s+", " ", text[idx: idx + 200])
    assert "hard" in nearby.lower()

    idx = text.rindex("check_external_draft_qa")
    nearby = re.sub(r"\s+", " ", text[idx: idx + 200])
    assert "hard" in nearby.lower()


def test_gap_convention_used_for_missing_category() -> None:
    flat = re.sub(r"\s+", " ", writer_brief_text())
    assert "[GAP: needs <card>]" in flat


def test_skill_wires_writer_brief_in() -> None:
    text = skill_text()
    assert "writer-brief.md" in text
    assert "FRFRMU-1070" in text


def test_no_dollar_figures_in_writer_brief() -> None:
    dollar_re = re.compile(
        r"\$\s*[1-9][\d,]*(?:\.\d+)?|\bUSD\b|\bin dollars\b|\bin US dollars\b",
        re.IGNORECASE,
    )
    m = dollar_re.search(writer_brief_text())
    assert not m, f"dollar/COGS figure found in writer-brief.md: {m.group(0)!r}"


_CHECKS = [
    ("writer-brief.md exists", test_writer_brief_file_exists),
    ("seven categories present", test_seven_categories_present),
    ("each category cites a foundation key", test_each_category_cites_a_foundation_key),
    ("unvetted excludes dossier and ladder internals", test_unvetted_excludes_dossier_and_ladder_internals),
    ("unvetted filter runs before assembly", test_unvetted_filter_runs_before_assembly_not_a_redaction_pass),
    ("paste-back is v1 author:external", test_paste_back_is_v1_author_external),
    ("paste-back runs block/truth/clone/QA in order", test_paste_back_runs_block_truth_clone_qa_in_order),
    ("audition spec is one slot, never a month", test_audition_spec_is_one_slot_never_a_month),
    ("no PII or hiring stored", test_no_pii_or_hiring_stored),
    ("storage key shape", test_storage_key_shape),
    ("validator severities", test_validator_severities),
    ("[GAP] convention used for missing category", test_gap_convention_used_for_missing_category),
    ("SKILL.md wires writer-brief.md in", test_skill_wires_writer_brief_in),
    ("no dollar figures in writer-brief.md", test_no_dollar_figures_in_writer_brief),
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
