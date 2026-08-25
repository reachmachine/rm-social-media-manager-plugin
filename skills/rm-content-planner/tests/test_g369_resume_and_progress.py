"""Falsifiable test for G369 — "the content planner had no durable progress state."

The bug: if a customer closed the session mid-plan, nothing survived except what
was already saved via `submit_content_plan`, `update_creator_brief` or
`update_business_profile`. On restart, the skill started cold at Step 1 and
re-asked questions it already had answers to. The founder's own words: "in
halfway when i closed the session and restarted the skill kept asking me
different weird question without understanding any of the previous context."
And: "setup a hook where skill consider updates, then sync to previous session
and gives the next steps for user to proceed and let user decide the
direction."

The register's suggested fix (`record_content_plan_run`) does not work —
checked against the live tool schema, it requires a `plan_id` that only exists
AFTER `submit_content_plan` has already returned one (Step 11/12), so it
cannot record progress for Steps 1-10, exactly the part that gets lost.

The fix, in two places in `PLAYBOOK.md`:

1. a new "Progress checkpoints" subsection (right after the step-order spine)
   telling the skill to call `update_creator_brief` with a `planning_progress`
   field after every step 1-11, skipped on headless (`runner.py`) runs;
2. a new bullet in Step 1 rule 1 telling the skill to ASK the creator what to
   do with unfinished progress it finds — never silently resume, never
   silently restart. This is the founder's explicit instruction ("let user
   decide the direction"), not a convenience default.

CONTROL TESTS (the G175 lesson, see test_g370_dashboard_handoff.py): every
block this file scopes its assertions to is proved to exist and to be the
right block FIRST, using text that was already in the file before the fix.
Without that, a typo in a section marker would make every real assertion
"pass" against an empty string.

Standalone-runnable (the RAM guard blocks pytest on this box):
`python test_g369_resume_and_progress.py`.
"""
from __future__ import annotations

import pathlib
import re
import sys

# Plugin root by marker-walk, never parent-counting (same reason as
# test_commands.py / test_g370_dashboard_handoff.py: fixed-depth path math
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


def _checkpoints_section() -> str:
    """The new 'Progress checkpoints' subsection, from its heading up to the
    next top-level (`## `) heading (which is 'Step 1')."""
    text = _PLAYBOOK_MD.read_text(encoding="utf-8")
    start = text.index("## Progress checkpoints")
    end = text.index("\n## ", start + 1)
    return _squash(text[start:end])


def _step_order_spine() -> str:
    """The existing numbered 1-7 list of what Steps 1-12 cover — used to prove
    the checkpoints section landed in the right place (right after it)."""
    text = _PLAYBOOK_MD.read_text(encoding="utf-8")
    start = text.index("## The method — the step order (the spine)")
    end = text.index("## Progress checkpoints", start)
    return _squash(text[start:end])


def _step1_rule1_block() -> str:
    """Step 1's rule 1 — 'Load what's already known FIRST' — up to the start
    of rule 2 ('Ask CONVERSATIONALLY')."""
    text = _PLAYBOOK_MD.read_text(encoding="utf-8")
    start = text.index("1. **Load what's already known FIRST")
    end = text.index("2. **Ask CONVERSATIONALLY", start)
    return _squash(text[start:end])


# --- the claims, as patterns and not as loose keywords -----------------------

_RESUME_BULLET_RE = re.compile(r"Unfinished session\? Ask, never assume", re.IGNORECASE)
_ALWAYS_ASK_RE = re.compile(r"always ask", re.IGNORECASE)
# The concrete way "never silently resume/restart" stays true if someone edits
# this file later: the block must never say it CAN silently resume/continue.
_SILENT_CONTINUE_RE = re.compile(r"silently (resume|continue)", re.IGNORECASE)


# --- CONTROL TESTS -----------------------------------------------------------
# These pass BEFORE and AFTER the fix on purpose (except where noted). They
# prove each block below is the real block, so a failing real assertion means
# the instruction is missing — not that the marker string was mistyped and the
# block came back empty.

def test_control_step_order_spine_is_the_real_block() -> None:
    block = _step_order_spine()
    assert len(block) > 200, f"step-order spine looks empty/truncated: {block!r}"
    assert "Step 12" in block, "wrong block — no reference to Step 12"
    assert "Capture" in block, "wrong block — missing the 'Capture' spine item"


def test_control_step1_rule1_is_the_real_block() -> None:
    block = _step1_rule1_block()
    assert len(block) > 300, f"Step 1 rule 1 block looks empty/truncated: {block!r}"
    assert "get_creator_brief" in block, "wrong block — no get_creator_brief call"
    assert "get_business_profile" in block, "wrong block — no get_business_profile call"


# --- THE REAL TESTS ----------------------------------------------------------

def test_checkpoints_section_exists_right_after_the_spine() -> None:
    # If the section heading isn't there at all, this raises ValueError from
    # .index() inside _checkpoints_section() — that IS the RED failure for a
    # deleted section, so we don't need a separate try/except here.
    section = _checkpoints_section()
    assert len(section) > 200, f"Progress checkpoints section looks empty/truncated: {section!r}"


def test_checkpoints_section_mentions_update_creator_brief_and_the_field() -> None:
    section = _checkpoints_section()
    assert "update_creator_brief" in section, (
        "the Progress checkpoints section never says to call update_creator_brief — "
        "that is the only tool that can persist progress before a plan_id exists"
    )
    assert "planning_progress" in section, (
        "the Progress checkpoints section never names the planning_progress field"
    )


def test_checkpoints_section_does_not_suggest_record_content_plan_run() -> None:
    """Guards against someone 'fixing' this back to the broken suggestion later.
    record_content_plan_run requires a plan_id that only exists after
    submit_content_plan — it cannot record progress for Steps 1-10."""
    section = _checkpoints_section()
    assert "record_content_plan_run" not in section, (
        "the Progress checkpoints section mentions record_content_plan_run — "
        "that tool needs a plan_id that doesn't exist until Step 11/12 and "
        "cannot be used for this"
    )


def test_checkpoints_section_carves_out_headless_runs() -> None:
    section = _checkpoints_section()
    assert re.search(r"headless", section, re.IGNORECASE), (
        "the Progress checkpoints section never mentions 'headless' — the "
        "skip-on-headless carve-out is missing, so runner.py would spend an "
        "extra tool call nobody is coming back to use"
    )
    assert "runner.py" in section, (
        "the Progress checkpoints section doesn't name runner.py as the "
        "headless entry point"
    )


def test_step1_rule1_has_the_resume_check_bullet() -> None:
    block = _step1_rule1_block()
    assert _RESUME_BULLET_RE.search(block), (
        "Step 1 rule 1 is missing the G369 resume-check bullet — a returning "
        "creator with unfinished planning_progress is never told about it"
    )


def test_step1_resume_bullet_always_asks_and_never_silently_resumes() -> None:
    block = _step1_rule1_block()
    assert _ALWAYS_ASK_RE.search(block), (
        "Step 1's resume-check bullet doesn't say 'Always ask' (or equivalent) — "
        "the founder's instruction was 'let user decide the direction', not a "
        "silent default"
    )
    assert not _SILENT_CONTINUE_RE.search(block), (
        "Step 1's resume-check bullet contains language matching "
        "'silently (resume|continue)' — it must never be OK to silently "
        "resume or continue without asking"
    )


def test_step1_resume_bullet_covers_all_three_choices() -> None:
    """'pick up from there', 'start over', 'something else' — the creator must
    be able to choose any of the three, not just resume-or-restart."""
    block = _step1_rule1_block().lower()
    for phrase in ("pick up from there", "start over", "something else"):
        assert phrase in block, (
            f"Step 1's resume-check bullet never mentions the choice "
            f"{phrase!r} — the creator must be free to choose any of the "
            f"three outcomes, not just resume or restart"
        )


_CHECKS = [
    ("CONTROL: step-order spine is the real block",
     test_control_step_order_spine_is_the_real_block),
    ("CONTROL: Step 1 rule 1 is the real block",
     test_control_step1_rule1_is_the_real_block),
    ("checkpoints section exists right after the spine",
     test_checkpoints_section_exists_right_after_the_spine),
    ("checkpoints section mentions update_creator_brief and planning_progress",
     test_checkpoints_section_mentions_update_creator_brief_and_the_field),
    ("checkpoints section does not suggest record_content_plan_run",
     test_checkpoints_section_does_not_suggest_record_content_plan_run),
    ("checkpoints section carves out headless runs",
     test_checkpoints_section_carves_out_headless_runs),
    ("Step 1 rule 1 has the resume-check bullet",
     test_step1_rule1_has_the_resume_check_bullet),
    ("Step 1 resume bullet always asks, never silently resumes",
     test_step1_resume_bullet_always_asks_and_never_silently_resumes),
    ("Step 1 resume bullet covers all three choices",
     test_step1_resume_bullet_covers_all_three_choices),
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
        except (AssertionError, ValueError) as exc:
            failed += 1
            print(f"[FAIL] {label}: {exc}")
        else:
            print(f"[PASS] {label}")
    print(f"{len(_CHECKS) - failed}/{len(_CHECKS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
