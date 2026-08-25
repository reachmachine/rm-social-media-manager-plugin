"""Falsifiable test for G367 / FRFRMU-359 — poll, estimate, let the customer step away, and
absorb a stall instead of escalating it.

The bug: a real customer's run sat at 4/11 reels done for 10+ minutes. The assistant had no
instructions for that moment, so it improvised a 4-option menu ("keep waiting / stop+restart /
move on with partial / recommended") and asked the customer to choose. The founder's own words:
"if someone lacks patience... they feel 'what if i wait for 30 mins and if it does work ill waste
my time'." The backend (G341) already computes elapsed_s, stalled_for_s, and a calm friendly
message via get_pipeline_status — verified live in backend/app/mcp/tools_pipeline.py. Nothing in
PLAYBOOK.md told the skill to poll it, turn it into an ETA, say the customer can step away, or
trust the server's own calm message instead of inventing a menu. PLAYBOOK rule 6d is the fix —
same shape as G368's rule 6c and G339's rule 6a: a plain rule plus a test that fails if it, or its
wiring into the customer-facing commands, is ever removed.

Standalone-runnable (the RAM guard blocks pytest on this box):
`python test_g367_progress_and_waiting.py`.
"""
from __future__ import annotations

import pathlib
import re
import sys

# Plugin root by marker-walk, never parent-counting (same reason as test_commands.py and
# test_g368_credits_not_dollars.py: fixed-depth path math broke on the last re-nesting).
_HERE = pathlib.Path(__file__).resolve()
_PLUGIN_ROOT = next(
    p for p in _HERE.parents if (p / ".claude-plugin" / "plugin.json").is_file()
)
_SKILL = _PLUGIN_ROOT / "skills" / "rm-content-planner"
_PLAYBOOK = _SKILL / "PLAYBOOK.md"
_WATCH_VIDEO = _PLUGIN_ROOT / "commands" / "watch-video.md"
_WORKFLOW_ANALYZE = _PLUGIN_ROOT / "commands" / "workflow_analyze.md"

# The two command files that must cite rule 6d.
_COMMANDS_CITING_RULE_6D = (_WATCH_VIDEO, _WORKFLOW_ANALYZE)


def _rule_6d(path: pathlib.Path = _PLAYBOOK) -> str:
    """Rule 6d's own text — from the '6d.' marker up to the '7.' one."""
    text = path.read_text(encoding="utf-8")
    start = text.index("\n6d.")
    end = text.index("\n7.", start)
    return text[start:end]


def _while_it_runs_section(path: pathlib.Path = _WATCH_VIDEO) -> str:
    """watch-video.md's 'While it runs' section — from its heading to the next '##', or the
    end of the file if it's the last section."""
    text = path.read_text(encoding="utf-8")
    start = text.index("## While it runs")
    try:
        end = text.index("\n## ", start + 1)
    except ValueError:
        end = len(text)
    return text[start:end]


def test_get_pipeline_status_is_taught() -> None:
    count = _PLAYBOOK.read_text(encoding="utf-8").count("get_pipeline_status")
    assert count >= 1, (
        "PLAYBOOK.md never mentions get_pipeline_status (was 0 occurrences before the G367 "
        "fix) — nothing teaches the skill to poll the run it just dispatched"
    )


def test_rule_6d_exists_between_6c_and_7() -> None:
    rule = _rule_6d()
    assert rule.strip(), "PLAYBOOK rule 6d is empty or missing entirely"


def test_rule_6d_bans_self_estimated_time() -> None:
    rule = _rule_6d()
    assert re.search(r"elapsed_s", rule), (
        "PLAYBOOK rule 6d no longer names elapsed_s — the field the ETA must be computed from"
    )
    assert re.search(r"never (?:track|estimate)", rule, re.IGNORECASE), (
        "PLAYBOOK rule 6d mentions elapsed_s but no longer forbids guessing/tracking time "
        "yourself — the rule must actually ban self-estimated elapsed time, not just name the "
        "field"
    )


def test_rule_6d_says_step_away() -> None:
    rule = _rule_6d()
    assert re.search(r"step away", rule, re.IGNORECASE), (
        "PLAYBOOK rule 6d dropped the words 'step away' — this is the founder's own explicit "
        "ask (customers should not have to babysit a run)"
    )


def test_rule_6d_forbids_generic_menu() -> None:
    rule = _rule_6d()
    assert re.search(r"real choice", rule, re.IGNORECASE), (
        "PLAYBOOK rule 6d no longer talks about a 'real choice' — without this it gives no "
        "guidance on when asking the customer something is actually appropriate"
    )
    assert "keep waiting / stop" not in rule, (
        "PLAYBOOK rule 6d reintroduces the founder's actual bad-example 4-option menu style "
        "('keep waiting / stop...') as if it were guidance rather than the thing to avoid"
    )


def test_commands_cite_rule_6d() -> None:
    offenders = [
        path.name
        for path in _COMMANDS_CITING_RULE_6D
        if "6d" not in path.read_text(encoding="utf-8")
    ]
    assert not offenders, (
        "these commands should cite PLAYBOOK rule 6d so a session following only the command "
        "file (not the full PLAYBOOK) still loads the poll/ETA/step-away/stall rule: "
        + ", ".join(offenders)
    )


def test_watch_video_has_while_it_runs_pointer() -> None:
    section = _while_it_runs_section()
    assert re.search(r"rule 6d", section, re.IGNORECASE), (
        "watch-video.md's 'While it runs' section no longer points at PLAYBOOK rule 6d"
    )


def test_workflow_analyze_gained_a_while_it_runs_step() -> None:
    text = _WORKFLOW_ANALYZE.read_text(encoding="utf-8")
    assert re.search(r"rule 6d", text, re.IGNORECASE), (
        "workflow_analyze.md has no 'while it runs' step citing rule 6d — this command had "
        "NO such step at all before the G367 fix, so this is the falsifiable proof it was added"
    )


_CHECKS = [
    ("get_pipeline_status is taught in PLAYBOOK.md", test_get_pipeline_status_is_taught),
    ("rule 6d exists between 6c and 7", test_rule_6d_exists_between_6c_and_7),
    ("rule 6d bans self-estimated time", test_rule_6d_bans_self_estimated_time),
    ("rule 6d says 'step away'", test_rule_6d_says_step_away),
    ("rule 6d forbids a generic menu", test_rule_6d_forbids_generic_menu),
    ("watch-video.md and workflow_analyze.md cite rule 6d", test_commands_cite_rule_6d),
    ("watch-video.md's 'While it runs' points at rule 6d", test_watch_video_has_while_it_runs_pointer),
    ("workflow_analyze.md gained a 'while it runs' step", test_workflow_analyze_gained_a_while_it_runs_step),
]


def main() -> int:
    # These docs contain emoji (the 🔴 prohibition marker). A failure message quoting one must
    # not die in Windows' cp1252 console before it prints.
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
