"""Falsifiable test for G373 — "intake never asks the creator's own personal story."

The bug: Step 1's six-question positioning capture already asks for an
"origin / transformation story" (item 6) — but that question is a MARKET
question. It's the audience-facing proof-of-change ("here's my before/after,
trust me"), and it lives inside the `positioning` object that Step 7 later
validates against real data — skip it and the plan gets stamped "GENERIC".

The founder asked for something different, in his own words: "who are you?
why you started this and why this matters?" That's a PERSONAL question, not
a market one. It should never be graded as a hypothesis to prove, and
skipping it should never block the plan.

The fix, in `PLAYBOOK.md`:

1. a new, separate, explicitly optional bullet in Step 1 (between the
   Positioning bullet and the Funnel plumbing bullet) asking this exact
   question, saved to the Creator Brief under `personal_story` — never into
   the `positioning` object, so declining it never triggers the "GENERIC"
   stamp;
2. `personal_story` added to Step 1 rule 6's scored intake-completeness field
   list;
3. Step 8 Section 00's pinned identity reel now sources from `personal_story`
   first, falling back to the positioning transformation story;
4. Step 8 Section 00 now names a SECOND reel (objection-busting / Big Domino)
   that draws on the personal story, so a captured story isn't left unused.

CONTROL TESTS (the G175 lesson, see test_g370_dashboard_handoff.py /
test_g369_resume_and_progress.py): every block this file scopes its
assertions to is proved to exist and to be the right block FIRST, using text
that was already in the file before this fix. Without that, a typo in a
section marker would make every real assertion "pass" against an empty
string.

Standalone-runnable (the RAM guard blocks pytest on this box):
`python test_g373_personal_origin_story.py`.
"""
from __future__ import annotations

import pathlib
import re
import sys

# Plugin root by marker-walk, never parent-counting (same reason as
# test_commands.py / test_g369_resume_and_progress.py: fixed-depth path math
# broke on the last re-nesting).
_HERE = pathlib.Path(__file__).resolve()
_PLUGIN_ROOT = next(
    p for p in _HERE.parents if (p / ".claude-plugin" / "plugin.json").is_file()
)
_SKILL = _PLUGIN_ROOT / "skills" / "rm-content-planner"
_PLAYBOOK_MD = _SKILL / "PLAYBOOK.md"


def _squash(text: str) -> str:
    """Collapse newlines/indent so a sentence-scoped regex is not defeated by
    wherever the markdown source happens to wrap."""
    return " ".join(text.split())


def _step1_positioning_to_funnel_block() -> str:
    """Step 1's fields list, from the Positioning bullet start up to (but not
    including) the Funnel plumbing bullet start. Contains the six-question
    positioning capture AND (after the fix) the new personal-story bullet."""
    text = _PLAYBOOK_MD.read_text(encoding="utf-8")
    start = text.index("- **Positioning — a GATE")
    end = text.index("- **Funnel plumbing:**", start)
    return _squash(text[start:end])


def _positioning_six_items_block() -> str:
    """Just the numbered 1-6 sub-list inside the Positioning bullet (the
    origin/transformation-story question is item 6), up to 'Once you have
    real answers' where the numbered list ends. Used as a guard: this block
    must NEVER mention personal_story — proves the two questions stayed
    genuinely separate, not that item 6 got renamed."""
    text = _PLAYBOOK_MD.read_text(encoding="utf-8")
    start = text.index("1. Their one **ownable angle**")
    end = text.index("Once you have real answers", start)
    return _squash(text[start:end])


def _step1_rule6_block() -> str:
    """Step 1 rule 6 — 'Score the intake, and never guess silently (G225)' —
    up to the start of the next top-level paragraph ('Read the customer's
    website first')."""
    text = _PLAYBOOK_MD.read_text(encoding="utf-8")
    start = text.index("6. **Score the intake")
    end = text.index("**Read the customer's website first", start)
    return _squash(text[start:end])


def _step8_section00_block() -> str:
    """Step 8's Section 00 bullet (item 1 of the numbered list), from its
    heading up to the start of item 2 ('Section 00.5')."""
    text = _PLAYBOOK_MD.read_text(encoding="utf-8")
    start = text.index("1. **Section 00 — Foundation**")
    end = text.index("2. **Section 00.5", start)
    return _squash(text[start:end])


# --- the claims, as patterns and not as loose keywords -----------------------

_FOUNDER_WORDING_RE = re.compile(
    r"who are you\??\s*why did you start this", re.IGNORECASE
)


# --- CONTROL TESTS -----------------------------------------------------------
# These pass BEFORE and AFTER the fix on purpose. They prove each block below
# is the real block, so a failing real assertion means the instruction is
# missing — not that the marker string was mistyped and the block came back
# empty.

def test_control_step1_fields_block_is_the_real_block() -> None:
    block = _step1_positioning_to_funnel_block()
    assert len(block) > 500, f"Step 1 fields block looks empty/truncated: {block!r}"
    assert "origin / transformation story" in block, (
        "wrong block — missing the positioning item-6 origin/transformation-story question"
    )


def test_control_section00_block_is_the_real_block() -> None:
    block = _step8_section00_block()
    assert len(block) > 300, f"Section 00 block looks empty/truncated: {block!r}"
    assert "pinned first 3 reels" in block, "wrong block — missing the pinned-reels bullet"
    assert "HARD GUARD" in block, "wrong block — missing the HARD GUARD paragraph"


# --- THE REAL TESTS ----------------------------------------------------------

def test_personal_story_bullet_exists() -> None:
    block = _step1_positioning_to_funnel_block()
    assert "personal_story" in block, (
        "Step 1's fields list never mentions personal_story — the new bullet is missing"
    )


def test_personal_story_uses_the_founders_own_wording() -> None:
    block = _step1_positioning_to_funnel_block()
    assert _FOUNDER_WORDING_RE.search(block), (
        "the personal-story bullet doesn't use the founder's own wording — must ask, "
        "roughly, 'who are you? why did you start this ... why this matters' — a "
        "paraphrase that drops 'who are you' or 'why ... start this' doesn't count"
    )


def test_personal_story_bullet_is_optional_and_never_blocks() -> None:
    block = _step1_positioning_to_funnel_block().lower()
    assert "optional" in block, (
        "the personal-story bullet never says it's optional"
    )
    assert "never block" in block or "never blocks" in block, (
        "the personal-story bullet never says it must never block the plan"
    )


def test_personal_story_saved_separately_from_positioning_object() -> None:
    block = _step1_positioning_to_funnel_block()
    assert "personal_story" in block, "personal_story key missing from the block"
    assert re.search(r"never into the\s*`?positioning`?\s*object", block, re.IGNORECASE), (
        "the personal-story bullet doesn't explicitly say it's saved separately from, "
        "and never into, the positioning object"
    )


def test_positioning_six_items_never_mention_personal_story() -> None:
    """Guard: proves the market question (item 6) and the personal question
    stayed genuinely separate — a future edit that folds personal_story back
    into item 6 (instead of keeping it as its own bullet) must fail this."""
    block = _positioning_six_items_block()
    assert "personal_story" not in block, (
        "the positioning items 1-6 sub-list mentions personal_story — the personal "
        "question must live in its own separate bullet, not inside the market-facing "
        "positioning capture"
    )


def test_personal_story_added_to_step1_rule6_scored_fields() -> None:
    block = _step1_rule6_block()
    assert "personal_story" in block, (
        "Step 1 rule 6's scored intake-completeness field list never mentions "
        "personal_story"
    )


def test_section00_pinned_reel_sources_from_personal_story() -> None:
    block = _step8_section00_block()
    assert "personal_story" in block, (
        "Step 8 Section 00's pinned identity-reel instructions never mention "
        "sourcing from personal_story"
    )


def test_section00_names_a_second_reel_for_the_personal_story() -> None:
    block = _step8_section00_block()
    count = block.count("personal_story")
    assert count >= 2, (
        f"Step 8 Section 00 mentions personal_story only {count} time(s) — expected "
        "at least 2 (the pinned reel AND a second reel elsewhere in the calendar)"
    )
    assert (
        "objection-busting" in block.lower() or "big domino" in block.lower()
    ), (
        "Step 8 Section 00 doesn't name an objection-busting or Big Domino reel as "
        "the second use of the personal story"
    )


_CHECKS = [
    ("CONTROL: Step 1 fields block is the real block",
     test_control_step1_fields_block_is_the_real_block),
    ("CONTROL: Section 00 block is the real block",
     test_control_section00_block_is_the_real_block),
    ("personal-story bullet exists",
     test_personal_story_bullet_exists),
    ("personal-story bullet uses the founder's own wording",
     test_personal_story_uses_the_founders_own_wording),
    ("personal-story bullet is optional and never blocks the plan",
     test_personal_story_bullet_is_optional_and_never_blocks),
    ("personal-story bullet saved separately from the positioning object",
     test_personal_story_saved_separately_from_positioning_object),
    ("positioning items 1-6 never mention personal_story (guard)",
     test_positioning_six_items_never_mention_personal_story),
    ("personal_story added to Step 1 rule 6 scored fields",
     test_personal_story_added_to_step1_rule6_scored_fields),
    ("Section 00 pinned reel sources from personal_story",
     test_section00_pinned_reel_sources_from_personal_story),
    ("Section 00 names a second reel for the personal story",
     test_section00_names_a_second_reel_for_the_personal_story),
]


def main() -> int:
    # These docs contain emoji (the 🔴 prohibition marker elsewhere in the
    # file). A failure message quoting one must not die in Windows' cp1252
    # console before it prints.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    failed = 0
    for label, check in _CHECKS:
        try:
            check()
        except (AssertionError, ValueError) as exc:
            failed += 1
            print(f"[FAIL] {label}: {exc}")
        else:
            print(f"[PASS] {label}")
    print(f"{len(_CHECKS) - failed}/{len(_CHECKS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
