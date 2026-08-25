"""Falsifiable test for G408 — the SaaS codebase-dossier intake.

The gap (founder request, 2026-08-24): for a software/SaaS subject, the two
normal intake sources routinely undersell the product — owners forget or
under-explain their own features, and public sites lag what's actually built.
The fix: Step 1 offers the creator a copy-paste prompt
(`PRODUCT_DOSSIER_PROMPT.md`) to run in their OWN codebase's AI coding agent,
which writes back a plain-English product dossier. The dossier is saved to the
Creator Brief under `product_dossier` and the creator re-runs the SAME prompt
as the product grows, so strategy updates stay current.

Seven checks, each isolated so a break in ONE piece fails only the check that
covers it:

1. `PRODUCT_DOSSIER_PROMPT.md` exists and carries a fenced prompt block.
2. The prompt forbids code/secrets and requires the NOT YET PUBLIC marker.
3. The PLAYBOOK Step 1 carries the G408 block at all.
4. The block is an OFFER, never a requirement.
5. The dossier is labelled never DATA-DRIVEN (§I stays reserved for
   analysed-reel medians).
6. The block persists to the Creator Brief `product_dossier` key AND carries
   the re-run/staleness refresh rule.
7. SKILL.md references the prompt file (the operating contract must load it).

Standalone-runnable (the RAM guard blocks pytest on this box):
`python test_g408_product_dossier.py`.
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
_SKILL_MD = _SKILL / "SKILL.md"
_DOSSIER_PROMPT = _SKILL / "PRODUCT_DOSSIER_PROMPT.md"

# The literal marker the new PLAYBOOK block opens with.
_BLOCK_MARKER = "Offer the codebase dossier (G408)"

# Window past the marker. Generous on purpose (same sizing rationale as
# test_g372): wide enough to hold the whole block, narrow enough not to reach
# unrelated Step 1 text.
_WINDOW_CHARS = 3500


def _flat(path: pathlib.Path) -> str:
    """Newlines collapsed to single spaces — markdown wraps prose at ~90
    columns, so a required phrase can be split across lines in the source."""
    return " ".join(path.read_text(encoding="utf-8").split())


def _g408_section() -> str:
    text = _flat(_PLAYBOOK)
    idx = text.find(_BLOCK_MARKER)
    assert idx != -1, (
        f"PLAYBOOK.md is missing the '{_BLOCK_MARKER}' block in Step 1 — "
        "G408's codebase-dossier intake step is gone"
    )
    return text[idx : idx + _WINDOW_CHARS]


def test_dossier_prompt_file_exists_with_fenced_prompt() -> None:
    assert _DOSSIER_PROMPT.is_file(), (
        "PRODUCT_DOSSIER_PROMPT.md is missing from the skill folder — the "
        "creator has nothing to copy-paste into their own dev agent"
    )
    raw = _DOSSIER_PROMPT.read_text(encoding="utf-8")
    assert "```" in raw, (
        "PRODUCT_DOSSIER_PROMPT.md has no fenced block — the PLAYBOOK tells "
        "the agent to hand over 'the fenced block in that file' verbatim"
    )
    flat = " ".join(raw.split())
    assert "product-dossier.md" in flat, (
        "the prompt no longer names the output file (product-dossier.md)"
    )
    assert re.search(r"Features and benefits", flat), (
        "the prompt lost its 'Features and benefits' section — the whole "
        "point is surfacing every user-facing feature, including unmarketed "
        "ones"
    )


def test_prompt_forbids_secrets_and_marks_unreleased() -> None:
    flat = _flat(_DOSSIER_PROMPT)
    assert re.search(r"NEVER include.{0,120}secrets", flat, re.IGNORECASE), (
        "the prompt no longer forbids code/keys/secrets in the dossier — "
        "without this rule the creator's agent may paste sensitive material "
        "into a marketing document"
    )
    assert "NOT YET PUBLIC" in flat, (
        "the prompt lost the 'NOT YET PUBLIC' marker for unreleased items — "
        "the SMM side relies on that marker to keep roadmap out of the "
        "calendar"
    )


def test_playbook_carries_the_g408_block() -> None:
    section = _g408_section()
    assert section, "PLAYBOOK.md G408 block resolved to an empty section"
    assert "PRODUCT_DOSSIER_PROMPT.md" in section, (
        "the G408 block no longer points at PRODUCT_DOSSIER_PROMPT.md — the "
        "agent won't know where the verbatim prompt lives"
    )


def test_block_is_an_offer_never_a_requirement() -> None:
    section = _g408_section()
    assert re.search(r"Never REQUIRE it", section, re.IGNORECASE), (
        "the G408 block lost its 'Never REQUIRE it' rule — a creator with no "
        "dev agent must be able to just continue the normal conversation"
    )
    assert re.search(r"not a blocker", section, re.IGNORECASE), (
        "the G408 block no longer says a missing dossier is not a blocker"
    )


def test_dossier_is_never_data_driven() -> None:
    section = _g408_section()
    assert re.search(r"never\s+DATA-DRIVEN", section, re.IGNORECASE), (
        "the G408 block no longer labels the dossier never DATA-DRIVEN — "
        "that label is reserved for real analysed-reel sample sizes (§I)"
    )


def test_block_persists_and_refreshes_the_dossier() -> None:
    section = _g408_section()
    assert "update_creator_brief" in section, (
        "the G408 block no longer persists the dossier via "
        "update_creator_brief"
    )
    assert "product_dossier" in section, (
        "the G408 block lost the `product_dossier` brief key — later "
        "sessions can't find the dossier to reuse or refresh"
    )
    assert re.search(r"re-?run", section, re.IGNORECASE), (
        "the G408 block lost the re-run rule — the whole update mechanism is "
        "the creator re-running the SAME prompt as the product grows"
    )
    assert re.search(r"stale", section, re.IGNORECASE), (
        "the G408 block no longer checks the brief's stale flag before "
        "planning on an old dossier"
    )


def test_skill_md_references_the_prompt_file() -> None:
    flat = _flat(_SKILL_MD)
    assert "PRODUCT_DOSSIER_PROMPT.md" in flat, (
        "SKILL.md never mentions PRODUCT_DOSSIER_PROMPT.md — the operating "
        "contract must tell the agent the file exists, or only PLAYBOOK "
        "readers ever find it"
    )
    assert "G408" in flat, (
        "SKILL.md lost its G408 reference for the codebase-dossier step"
    )


_CHECKS = [
    ("PRODUCT_DOSSIER_PROMPT.md exists with a fenced prompt",
     test_dossier_prompt_file_exists_with_fenced_prompt),
    ("prompt forbids secrets and marks unreleased items",
     test_prompt_forbids_secrets_and_marks_unreleased),
    ("PLAYBOOK carries the G408 block",
     test_playbook_carries_the_g408_block),
    ("block is an offer, never a requirement",
     test_block_is_an_offer_never_a_requirement),
    ("dossier is labelled never DATA-DRIVEN",
     test_dossier_is_never_data_driven),
    ("block persists and refreshes the dossier",
     test_block_persists_and_refreshes_the_dossier),
    ("SKILL.md references the prompt file",
     test_skill_md_references_the_prompt_file),
]


def main() -> int:
    # These docs contain emoji. A failure message quoting one must not die in
    # Windows' cp1252 console before it prints.
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
