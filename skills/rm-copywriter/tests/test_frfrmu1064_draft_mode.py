"""Falsifiable guards for p26 "Draft fast, block by block" (FRFRMU-1064).

Core idea (source card `marketing/rules/process-cards/p26-draft-fast-block-
by-block.md`): never start from a blank page — every asset is assembled
from blocks the foundation already filled; draft mode writes, edit mode
fixes, never mixed.

Standalone-runnable: `python test_frfrmu1064_draft_mode.py`.
"""
from __future__ import annotations

import sys

from _copywriter import SKILL_DIR, block_skeletons_text, skill_text


def test_block_skeletons_file_exists() -> None:
    assert (SKILL_DIR / "block-skeletons.md").is_file()


def test_all_five_asset_types_covered() -> None:
    text = block_skeletons_text()
    for heading in (
        "Reel script", "Carousel", "Caption", "Story sequence", "DM script",
    ):
        assert heading in text, f"missing skeleton for {heading!r}"


def test_every_block_names_a_default_source() -> None:
    """Every table row must point at a real card/brief-key reference, not a
    bare block name with nothing after it."""
    text = block_skeletons_text()
    # Spot-check the sourced blocks the ticket calls out by name.
    for needle in (
        "FRFRMU-1058", "FRFRMU-1059", "FRFRMU-1044", "FRFRMU-1043",
        "FRFRMU-1045", "FRFRMU-1049", "FRFRMU-1056", "FRFRMU-1055",
        "FRFRMU-1053", "FRFRMU-1052",
    ):
        assert needle in text, f"a block's default source {needle!r} is missing"


def test_never_cold_rule_present() -> None:
    text = block_skeletons_text()
    assert "cold draft" in text
    assert "[GAP: needs <card>]" in text


def test_ps_twin_is_mandatory() -> None:
    text = block_skeletons_text()
    assert "P.S. twin" in text
    assert "is not optional" in text


def test_mode_separation_rule_present() -> None:
    text = block_skeletons_text()
    assert "`mode: draft`" in text
    assert "never overwritten" in text or "v1 is never overwritten" in text


def test_beat_order_must_not_be_reordered() -> None:
    text = block_skeletons_text()
    assert "reorders the planner's beats" in text
    assert "fails" in text


def test_three_checks_documented() -> None:
    text = block_skeletons_text()
    for check in (
        "check_blocks_sourced", "check_mode_separation", "check_complete_draft",
    ):
        assert check in text, f"{check} not documented"


def test_check_blocks_sourced_is_hard_not_advisory() -> None:
    """Rule 3 target check — the source-ref-or-GAP rule must be a hard
    fail, not merely a suggestion."""
    text = block_skeletons_text()
    import re

    idx = text.index("check_blocks_sourced")
    nearby = re.sub(r"\s+", " ", text[idx: idx + 400])
    assert "**Hard**" in nearby, (
        "check_blocks_sourced must say it is a hard check near its "
        "definition, or a block with neither a source_ref nor a [GAP] "
        "silently ships"
    )
    assert "a block with neither fails" in nearby


def test_skill_wires_the_draft_pass_to_block_skeletons() -> None:
    text = skill_text()
    assert "block-skeletons.md" in text
    assert "FRFRMU-1064" in text
    assert "mode: draft" in text


_CHECKS = [
    ("block-skeletons.md exists", test_block_skeletons_file_exists),
    ("all 5 asset types covered", test_all_five_asset_types_covered),
    ("every block names a default source", test_every_block_names_a_default_source),
    ("never-cold rule present", test_never_cold_rule_present),
    ("P.S. twin mandatory", test_ps_twin_is_mandatory),
    ("mode-separation rule present", test_mode_separation_rule_present),
    ("beat order must not be reordered", test_beat_order_must_not_be_reordered),
    ("three checks documented", test_three_checks_documented),
    ("check_blocks_sourced is hard, not advisory", test_check_blocks_sourced_is_hard_not_advisory),
    ("SKILL.md wires the draft pass to block-skeletons.md", test_skill_wires_the_draft_pass_to_block_skeletons),
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
