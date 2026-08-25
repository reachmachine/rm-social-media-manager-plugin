"""Falsifiable test for G365 — "the admin publish-a-skill-update screen is inert for real
customers." Admin UI, admin API, and the get_skill_version/get_skill_bundle MCP tools were all
built (G113/FRFRMU-115) but only ever called from runner.py (headless, engineering-only) and
tests/ — grepping SKILL.md + PLAYBOOK.md + every command found ZERO update checks, so a published
version never reached a plugin customer.

The fix, in SKILL.md only:
1. a new "Check for a published update" section, the literal first instruction in the file, that
   calls get_skill_version every run and tells the creator (once, plainly) to run
   `claude plugin update` when a newer version exists;
2. a cross-reference from the existing G113 "check your copy isn't stale" section, which is the
   REACTIVE half (detected mid-run from validate_content_plan's checks_run count) — this file adds
   the PROACTIVE half (checked before Step 1 even starts).

Deliberately does NOT touch hooks/hooks.json or hooks/session-resume-check.sh (the G369
SessionStart hook) — verified live that hook fires before MCP servers connect and only on the
"resume" matcher, so it cannot make this call and would miss every fresh session. SKILL.md itself
is read on every invocation, resumed or fresh, by which point MCP tools are already callable (the
file already assumes this for get_creator_brief in Step 1).

CONTROL TESTS (the G175 lesson, see test_g370_dashboard_handoff.py): the real block below is
proved to be the right block FIRST, using text that was already in the file before this fix —
without that, a typo in a section marker would make every real assertion "pass" against an empty
string.

Standalone-runnable (the RAM guard blocks pytest on this box):
`python test_g365_skill_update_check.py`.
"""
from __future__ import annotations

import pathlib
import re
import sys

# Plugin root by marker-walk, never parent-counting (plugin-creator memory:
# fixed-depth path math is exactly what broke on the last re-nesting).
_HERE = pathlib.Path(__file__).resolve()
_PLUGIN_ROOT = next(
    p for p in _HERE.parents if (p / ".claude-plugin" / "plugin.json").is_file()
)
_SKILL = _PLUGIN_ROOT / "skills" / "rm-content-planner"
_SKILL_MD = _SKILL / "SKILL.md"


def _squash(text: str) -> str:
    """Collapse newlines/indent so a sentence-scoped regex is not defeated by
    wherever the markdown source happens to wrap."""
    return " ".join(text.split())


def _control_before_block() -> str:
    """The pre-existing ADHD-tone paragraph that must immediately precede the new
    section. Pre-existing text, unchanged by this fix — proves the file's
    landmark structure is intact before trusting the block below."""
    text = _SKILL_MD.read_text(encoding="utf-8")
    start = text.index("**Talk to the creator the way you'd talk to someone with ADHD")
    end = text.index("## Check for a published update", start)
    return _squash(text[start:end])


def _update_check_section() -> str:
    """The new G365 section, from its heading up to the pre-existing
    'First, read the method' line that must still follow it."""
    text = _SKILL_MD.read_text(encoding="utf-8")
    start = text.index("## Check for a published update")
    end = text.index("**First, read the method:**", start)
    return _squash(text[start:end])


def _g113_section_head() -> str:
    """First ~400 chars of the G113 section — enough to hold the new
    cross-reference sentence without pulling in the whole long section."""
    text = _SKILL_MD.read_text(encoding="utf-8")
    start = text.index("## Skill version — check your copy isn't stale (G113)")
    return _squash(text[start:start + 500])


# --- CONTROL TESTS ------------------------------------------------------------

def test_control_before_block_is_the_real_block() -> None:
    block = _control_before_block()
    assert len(block) > 100, f"ADHD-tone paragraph looks empty/truncated: {block!r}"
    assert "ADHD" in block, "wrong block — no ADHD reference"
    assert "PLAYBOOK Step 1, rule 2" in block, "wrong block — missing its own closing reference"


# --- THE REAL TESTS ------------------------------------------------------------

def test_update_check_section_exists_right_after_the_adhd_paragraph() -> None:
    # If the heading isn't there at all, .index() inside _update_check_section()
    # raises ValueError — that IS the RED failure for a deleted section.
    section = _update_check_section()
    assert len(section) > 300, f"update-check section looks empty/truncated: {section!r}"


def test_calls_get_skill_version_with_the_right_skill_id() -> None:
    section = _update_check_section()
    assert "get_skill_version" in section, (
        "the section never names get_skill_version — nothing would ever check for a "
        "published update"
    )
    assert "rm-content-planner" in section, (
        "the section never names skill_id rm-content-planner"
    )


def test_tells_the_customer_the_real_update_command() -> None:
    section = _update_check_section()
    assert "claude plugin update" in section, (
        "the section never tells the creator to run `claude plugin update` — the ONLY "
        "supported way this skill gets updated (register G365, option b)"
    )


def test_never_self_installs_via_get_skill_bundle() -> None:
    """Guards against someone 'fixing' this into option (c) later — self-writing the
    bundle is the exact thing the register rejected (two writers, same files)."""
    section = _update_check_section()
    assert "get_skill_bundle" not in section, (
        "the section calls out get_skill_bundle — this skill must never fetch or "
        "install the update itself, only tell the creator to run `claude plugin update`"
    )


def test_carves_out_headless_runner_runs() -> None:
    section = _update_check_section()
    assert "runner.py" in section, (
        "the section never names runner.py as the headless carve-out"
    )
    assert re.search(r"headless", section, re.IGNORECASE), (
        "the section never says 'headless' — runner.py already does its own "
        "check-and-repair and would waste a redundant call here"
    )


def test_never_blocks_or_repeats_the_message() -> None:
    section = _update_check_section()
    assert re.search(r"once per session", section, re.IGNORECASE), (
        "the section doesn't say 'once per session' — without this, a naive read "
        "could re-nag the creator on every turn"
    )
    assert re.search(r"never (let it )?block", section, re.IGNORECASE), (
        "the section doesn't say the check must never block the run — a version "
        "check must never be able to delay or interrupt a customer's plan"
    )


def test_a_failed_tool_call_stays_silent_to_the_customer() -> None:
    section = _update_check_section()
    assert "report_gap" in section, (
        "the section never says to log a failed version check with report_gap"
    )
    assert re.search(r"say nothing to the creator", section, re.IGNORECASE), (
        "the section doesn't say to stay silent to the creator when the tool call "
        "itself fails — THE AUDIENCE RULE (G134) is that our infra problems never "
        "reach the client"
    )


def test_g113_section_cross_references_g365() -> None:
    head = _g113_section_head()
    assert "G365" in head, (
        "the G113 'check your copy isn't stale' section doesn't cross-reference "
        "G365 — a reader would not know the reactive and proactive checks are "
        "related"
    )
    assert "REACTIVE" in head and "PROACTIVE" in head, (
        "the G113 section cross-reference doesn't distinguish reactive (this "
        "section, mid-run) from proactive (G365, before Step 1)"
    )


_CHECKS = [
    ("CONTROL: ADHD-tone paragraph is the real preceding block",
     test_control_before_block_is_the_real_block),
    ("update-check section exists right after the ADHD paragraph",
     test_update_check_section_exists_right_after_the_adhd_paragraph),
    ("calls get_skill_version with skill_id rm-content-planner",
     test_calls_get_skill_version_with_the_right_skill_id),
    ("tells the customer to run `claude plugin update`",
     test_tells_the_customer_the_real_update_command),
    ("never self-installs via get_skill_bundle",
     test_never_self_installs_via_get_skill_bundle),
    ("carves out headless runner.py runs",
     test_carves_out_headless_runner_runs),
    ("never blocks the run, never repeats the message",
     test_never_blocks_or_repeats_the_message),
    ("a failed tool call stays silent to the customer",
     test_a_failed_tool_call_stays_silent_to_the_customer),
    ("G113 section cross-references G365",
     test_g113_section_cross_references_g365),
]


def main() -> int:
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
