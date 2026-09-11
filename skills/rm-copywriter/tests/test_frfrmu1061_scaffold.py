"""Falsifiable guards for the rm-copywriter scaffold (FRFRMU-1061).

The founder's ask this ticket answers: "we already have a proven viral hook
and these are frameworks. how do we correlate it?" — plus "this plugin does
not have a copywriter [...] the scope stops until the content calendar is
ready. i wanted a copy writer agent as well."

These checks are deliberately grep/parse-based, matching the existing
`rm-content-planner/tests/` style (this skill is an agentic recipe read by
Claude, not executable business logic).

Standalone-runnable: `python test_frfrmu1061_scaffold.py`.
"""
from __future__ import annotations

import sys

from _copywriter import (
    AGENT_FILE,
    SKILL_DIR,
    agent_text,
    allowed_families_for,
    allowed_tools,
    correlation_table_text,
    frontmatter,
    parse_correlation_table,
    plugin_version,
    skill_text,
)


def test_agent_file_exists_with_copywriter_skill() -> None:
    assert AGENT_FILE.is_file(), f"missing {AGENT_FILE}"
    fm = frontmatter(agent_text())
    assert "name: copywriter" in fm
    assert "skills: [rm-copywriter]" in fm


def test_skill_files_exist() -> None:
    for name in ("SKILL.md", "VERSION", "correlation-table.md"):
        assert (SKILL_DIR / name).is_file(), f"missing {name}"


def test_skill_grants_agent_and_task_for_the_critic() -> None:
    tools = allowed_tools(skill_text())
    assert "Agent" in tools
    assert "Task" in tools


def test_approval_gate_sentence_present() -> None:
    """The founder's HEADS-UP (FRFRMU-1030 decision): draft ONLY approved reels."""
    text = skill_text()
    assert "drafts ONLY for reels whose `approval.status` is" in text
    assert '"approved"' in text
    assert "SKIPPED" in text
    assert "reel_uid` **plus** `version`" in text


def test_rejection_reason_codes_match_the_calendar_store() -> None:
    """These must be the EXACT codes plan_approval_store.py accepts, not the
    ticket's loose prose ("not my voice", "wrong CTA/offer")."""
    text = skill_text()
    for code in (
        "wrong_topic", "wrong_hook", "wrong_format", "wrong_cta_offer",
        "not_my_voice", "wrong_day_time", "other",
    ):
        assert code in text, f"reason code {code!r} missing from SKILL.md"


def test_storage_key_uses_reel_uid_and_version_not_slot_index() -> None:
    text = skill_text()
    assert "copy_pack__<plan_id>__<reel_uid>__v<version>" in text
    # save_copy_pack may be NAMED only as an explicit prohibition, never
    # presented as a tool the copywriter actually calls in v1.
    assert "Do not invent a" in text and "save_copy_pack` MCP tool" in text
    assert "update_creator_brief" in text, "v1 must write via the existing brief store"


def test_hook_history_no_longer_a_gap_now_shipped() -> None:
    """FRFRMU-1060 shipped the reserved key + the hook-variants.md ledger
    recipe. Updated from the original 'labelled as a gap' assertion, which
    pinned the pre-1060 state on purpose so nobody invented the key early."""
    text = skill_text()
    assert "FRFRMU-1060 not built" not in text
    assert "hook-variants.md" in text


def test_correlation_table_has_rows_for_every_planner_framework() -> None:
    table = parse_correlation_table()
    expected = {
        "how_to", "n_ways_mistakes", "warning_stop_doing", "unlikely_character",
        "result_minus_pain", "proven_method", "profitable_promise",
        "secret_telling", "us_vs_them", "myth_bust", "story_open",
        "shared_struggle_bridge",
    }
    missing = expected - set(table)
    assert not missing, f"correlation table missing rows: {missing}"


def test_framework_outside_table_is_illegal_for_the_subcategory() -> None:
    """Rule 3 target check. A `how_to` frame (legal only for shortcut/
    transformation) must NOT be a legal generator for an `open_loop` slot —
    that would be exactly the pattern swap the ticket calls out."""
    table = parse_correlation_table()
    allowed_for_open_loop = allowed_families_for("open_loop", table)
    assert "how_to" not in allowed_for_open_loop, (
        "a benefit-style frame (how_to) must not be legal for a "
        "curiosity-style subcategory (open_loop) — pattern swap"
    )
    assert allowed_for_open_loop == {"n_ways_mistakes", "secret_telling"}


def test_secret_telling_never_says_the_word_secret_as_wording() -> None:
    text = correlation_table_text()
    assert "NEVER the literal word" in text


def test_plugin_version_bumped_for_the_copywriter_wave() -> None:
    """The copywriter files are here → the plugin version must reflect it,
    or a `claude plugin update` never delivers them (mirrors
    rm-content-planner/tests/test_recipe_wave_version_bump.py's invariant)."""
    assert plugin_version() >= (1, 7, 0)


def test_no_dollar_figures_in_copywriter_files() -> None:
    """G368 / FRFRMU-360 — never quote a dollar figure or COGS to a creator.
    The planner's own guard only sweeps its own files; this is the
    copywriter's own copy of that rule (planner untouched, per the prompt).

    Sweeps every `.md` file under the skill dir BY GLOB, not a fixed list —
    so a future card ticket (e.g. FRFRMU-1064's block-skeletons.md,
    FRFRMU-1065's qa-checklist.md) is covered automatically the moment its
    file exists, instead of silently escaping the guard until someone
    remembers to add it here."""
    import re

    dollar_re = re.compile(
        r"\$\s*[1-9][\d,]*(?:\.\d+)?|\bUSD\b|\bin dollars\b|\bin US dollars\b",
        re.IGNORECASE,
    )
    checked = 0
    for path in sorted(SKILL_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        m = dollar_re.search(text)
        assert not m, f"dollar/COGS figure found in {path.name}: {m.group(0)!r}"
        checked += 1
    text = agent_text()
    m = dollar_re.search(text)
    assert not m, f"dollar/COGS figure found in copywriter.md: {m.group(0)!r}"
    assert checked >= 2, "expected at least SKILL.md + correlation-table.md to be swept"


_CHECKS = [
    ("agent file exists with copywriter skill", test_agent_file_exists_with_copywriter_skill),
    ("skill files exist", test_skill_files_exist),
    ("skill grants Agent + Task", test_skill_grants_agent_and_task_for_the_critic),
    ("approval gate sentence present", test_approval_gate_sentence_present),
    ("rejection reason codes match the store", test_rejection_reason_codes_match_the_calendar_store),
    ("storage key uses reel_uid + version", test_storage_key_uses_reel_uid_and_version_not_slot_index),
    ("hook_history no longer a gap", test_hook_history_no_longer_a_gap_now_shipped),
    ("correlation table has all rows", test_correlation_table_has_rows_for_every_planner_framework),
    ("framework outside table is illegal", test_framework_outside_table_is_illegal_for_the_subcategory),
    ("secret_telling never says 'secret'", test_secret_telling_never_says_the_word_secret_as_wording),
    ("plugin version bumped", test_plugin_version_bumped_for_the_copywriter_wave),
    ("no dollar figures in copywriter files", test_no_dollar_figures_in_copywriter_files),
]


def main() -> int:
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
