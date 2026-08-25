"""Falsifiable test for G372 / FRFRMU-364 — research how the niche's leaders
OPERATE commercially, not just how big the market is.

The gap: `WebSearch` was already granted to this skill and already used for
market-sizing (G233, PLAYBOOK Step 1, `/market-research`). Nothing looked at
how the niche's leading players actually run their business — offer, price,
promise, funnel — outside Instagram itself. This test guards the new PLAYBOOK
Step 1 bullet ("Niche commercial landscape (G372)") and the `/market-research`
command that points at it.

🔴 Hard boundary this test also guards (G332 / G364): the new step must NEVER
substitute for, or feed, Instagram account discovery. G332's guard has already
regressed once — G364 found it existed in one copy of the docs but never
reached the shipped plugin. So the new bullet must RESTATE the rule in its own
words, not just cite the gap number; a bare cross-reference is exactly the
kind of thing that goes stale silently.

Six checks, each isolated so a break in ONE piece of the new bullet fails only
the check that covers it:

1. The PLAYBOOK carries the G372 bullet at all.
2. Depth is bounded — "3-5 players", "quick scan", "teardown" (why not one).
3. Every finding needs a source and a date.
4. Output is labelled JUDGMENT, never DATA-DRIVEN.
5. G332 is restated in the bullet's own words, not just cross-referenced.
6. `/market-research` points at G372 and repeats the G332 boundary.

Standalone-runnable (the RAM guard blocks pytest on this box):
`python test_g372_niche_commercial_landscape.py`.
"""
from __future__ import annotations

import pathlib
import re
import sys

# Plugin root by marker-walk, never parent-counting (same reason as
# test_commands.py: fixed-depth path math broke on the last re-nesting).
_HERE = pathlib.Path(__file__).resolve()
_PLUGIN_ROOT = next(
    p for p in _HERE.parents if (p / ".claude-plugin" / "plugin.json").is_file()
)
_SKILL = _PLUGIN_ROOT / "skills" / "rm-content-planner"

_PLAYBOOK = _SKILL / "PLAYBOOK.md"
_MARKET_RESEARCH = _PLUGIN_ROOT / "commands" / "market-research.md"

# The literal marker the new bullet opens with.
_BULLET_MARKER = "Niche commercial landscape (G372)"

# How far past the marker to look. Generous on purpose: the PLAYBOOK is
# 1600+ lines, so a narrow window risks missing part of the bullet, but a
# window this size still cannot accidentally reach unrelated text elsewhere
# in the file.
_WINDOW_CHARS = 3000


def _flat(path: pathlib.Path) -> str:
    """Newlines collapsed to single spaces.

    Every phrase check below MUST use this. Markdown wraps prose at ~90
    columns, so a required phrase can be split across lines in the source —
    a raw regex over the unflattened text then reports the rule missing when
    it is right there (`test_commands.py`'s comment documents this biting a
    real check on `hooks.md`).
    """
    return " ".join(path.read_text(encoding="utf-8").split())


def _g372_section() -> str:
    """The new PLAYBOOK bullet's own text, isolated by the marker it opens
    with, so later checks cannot pass by matching unrelated text elsewhere
    in a 1600+ line file."""
    text = _flat(_PLAYBOOK)
    idx = text.find(_BULLET_MARKER)
    assert idx != -1, (
        f"PLAYBOOK.md is missing the '{_BULLET_MARKER}' bullet in Step 1 — "
        "G372's niche commercial landscape step is gone"
    )
    return text[idx : idx + _WINDOW_CHARS]


def test_playbook_carries_the_g372_bullet() -> None:
    # _g372_section() already asserts the marker exists; calling it here
    # makes that assertion this check's own failure, not a side effect of
    # another check running first.
    section = _g372_section()
    assert section, "PLAYBOOK.md G372 bullet resolved to an empty section"


def test_depth_is_bounded_to_a_quick_scan() -> None:
    section = _g372_section()
    assert "3-5 players" in section, (
        "G372 bullet no longer bounds the scan to 3-5 players — without a "
        "bound this risks becoming a multi-hour teardown by default"
    )
    assert re.search(r"quick scan", section, re.IGNORECASE), (
        "G372 bullet lost the 'quick scan' framing"
    )
    assert re.search(r"teardown", section, re.IGNORECASE), (
        "G372 bullet lost its explanation of why this is a quick scan and "
        "not a full competitive teardown"
    )


def test_every_finding_needs_a_source_and_a_date() -> None:
    section = _g372_section()
    assert re.search(r"source", section, re.IGNORECASE), (
        "G372 bullet no longer requires a source for each finding"
    )
    assert re.search(r"date", section, re.IGNORECASE), (
        "G372 bullet no longer requires a date for each finding"
    )


def test_output_is_labelled_judgment_never_data_driven() -> None:
    section = _g372_section()
    assert re.search(r"JUDGMENT", section), (
        "G372 bullet no longer labels its output JUDGMENT"
    )
    assert re.search(r"(?:never|not)\s+DATA-DRIVEN", section, re.IGNORECASE), (
        "G372 bullet no longer says the output is never/not DATA-DRIVEN — "
        "that label is reserved for real analysed-reel sample sizes"
    )


def test_g332_boundary_is_restated_not_just_referenced() -> None:
    """A bare 'G332' cross-reference is exactly what regressed once already
    (G364): the rule existed in one doc copy but never reached the shipped
    plugin. The bullet must restate the rule in its own words."""
    section = _g372_section()
    assert "G332" in section, "G372 bullet does not even reference G332"
    restated = re.search(
        r"never.{0,40}(find|name|surface).{0,40}Instagram accounts",
        section,
        re.IGNORECASE,
    )
    assert restated, (
        "G372 bullet mentions G332 but does not restate the rule in its own "
        "words — a bare cross-reference is exactly the kind of thing that "
        "goes stale silently (G364)"
    )


def test_market_research_command_points_at_g372_and_repeats_boundary() -> None:
    text = _flat(_MARKET_RESEARCH)
    # A generic "G372" search would still pass off the frontmatter
    # description alone, which mentions G372 too — this must anchor on the
    # actual step, not just any mention of the gap number anywhere in the
    # file, or deleting the step itself would leave this check green.
    step_marker = "leaders operate, briefly (G372)"
    assert step_marker in text, (
        "market-research.md is missing the G372 step under 'How to do it' — "
        "the file may still say G372 elsewhere (e.g. its description), but "
        "the actual step that points at PLAYBOOK's method is gone"
    )
    assert "G332" in text, (
        "market-research.md lost its G332 reference — the existing "
        "test_market_research_is_the_only_sanctioned_web_search check in "
        "test_commands.py also guards this, but it belongs here too since "
        "this file is specifically about G372"
    )
    boundary = re.search(
        r"never.{0,60}(accounts|find-competitors)", text, re.IGNORECASE
    )
    assert boundary, (
        "market-research.md no longer restates that web search may never be "
        "used to find or suggest Instagram accounts"
    )


_CHECKS = [
    ("PLAYBOOK carries the G372 bullet", test_playbook_carries_the_g372_bullet),
    ("depth is bounded to a quick scan", test_depth_is_bounded_to_a_quick_scan),
    ("every finding needs a source and a date",
     test_every_finding_needs_a_source_and_a_date),
    ("output is labelled JUDGMENT, never DATA-DRIVEN",
     test_output_is_labelled_judgment_never_data_driven),
    ("G332 boundary is restated, not just referenced",
     test_g332_boundary_is_restated_not_just_referenced),
    ("/market-research points at G372 and repeats the boundary",
     test_market_research_command_points_at_g372_and_repeats_boundary),
]


def main() -> int:
    # These docs contain emoji (the 🔴 prohibition marker). A failure message
    # quoting one must not die in Windows' cp1252 console before it prints.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    failed = 0
    for label, check in _CHECKS:
        try:
            check()
        except AssertionError as exc:
            failed += 1
            print(f"[FAIL] {label}: {exc}")
        else:
            print(f"[PASS] {label}")
    print(f"{len(_CHECKS) - failed}/{len(_CHECKS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
