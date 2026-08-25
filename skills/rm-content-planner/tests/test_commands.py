"""Falsifiable test for the plugin's slash commands.

Design (founder decision 2026-08-19, superseding the earlier 4-command design):
FOUR end-to-end **workflows** keep the `workflow_` prefix, and FOURTEEN granular
commands do one action each, so a step can be re-run without redoing a plan.

Guards the rules that keep that surface safe:

1. Exactly the approved set exists — adding or dropping a command is a founder
   decision, not drift.
2. Money gates hold. Every RM-spending command carries confirm-before-spend
   language; every read-only command carries BOTH a never-spend rule and a
   never-call-Apify rule.
3. Apify is the user's OWN bill, which RM cannot see or cap, so only the two
   commands that legitimately search Instagram may touch it.
4. `delete-competitors` warns that removal can permanently destroy an analysed
   library, and needs a named explicit yes.
5. Web search is allowed for MARKET SIZING only (G233) and never as a substitute
   for real competitor discovery (G332).
6. Thin wrappers, one source of truth — every command defers to the PLAYBOOK,
   and nothing here edits PLAYBOOK.md.

Also guards the advisor-flagged trap: command files must NOT hardcode an MCP tool
prefix. Plugin-bundled MCP tools resolve under `mcp__plugin_<plugin>_<server>__*`
for installed customers, so commands name tools bare and let Claude resolve them.

Standalone-runnable (the RAM guard blocks pytest on this box):
`python test_commands.py`.
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
_COMMANDS = _PLUGIN_ROOT / "commands"

_WORKFLOWS = {
    "workflow_plan.md",
    "workflow_insights.md",
    "workflow_research.md",
    "workflow_analyze.md",
}

# Commands that may spend RM credits. Each needs the confirm gate.
_SPEND = {
    "workflow_research.md",
    "workflow_analyze.md",
    "find-competitors.md",
    "pull-data.md",
    "watch-video.md",
}

# Commands that must never spend and never touch Apify.
_READ_ONLY = {
    "workflow_insights.md",
    "hooks.md",
    "cta.md",
    "structures.md",
    "strategy.md",
    "our-patterns.md",
    "show-competitors.md",
    "switch-workspace.md",
    "know-business.md",
    "market-research.md",
    "check-classifications.md",
}

# Destructive: spends nothing, but can erase data.
_DESTRUCTIVE = {"delete-competitors.md"}

# The only commands allowed to drive Apify: the two that legitimately reach the
# skill's Step 2 discovery. workflow_plan runs the WHOLE method, so it includes
# Step 2; workflow_analyze does not, and must refuse Apify like any other command.
_MAY_USE_APIFY = {
    "find-competitors.md",
    "workflow_research.md",
    "workflow_plan.md",
}

_EXPECTED = _WORKFLOWS | _SPEND | _READ_ONLY | _DESTRUCTIVE

# Any hardcoded MCP prefix is wrong — the customer-install prefix differs.
_MCP_PREFIX = re.compile(r"mcp__[a-z0-9_-]+__")


def _read(name: str) -> str:
    return (_COMMANDS / name).read_text(encoding="utf-8")


def _flat(name: str) -> str:
    """Newlines collapsed to single spaces.

    Every phrase check below MUST use this. Markdown wraps prose at ~90 columns, so
    a required phrase like "never call Apify" is regularly split as "never call\\n
    Apify" — a raw regex then reports the rule missing when it is right there. A
    deliberate break proved it: hooks.md carried the rule and still failed.
    """
    return " ".join(_read(name).split())


def test_exactly_the_approved_commands_exist() -> None:
    found = {p.name for p in _COMMANDS.glob("*.md")}
    assert found == _EXPECTED, (
        f"commands/ has {sorted(found)}, expected exactly {sorted(_EXPECTED)} — "
        "adding or dropping a command is a founder decision, not drift"
    )


def test_every_command_has_description_frontmatter() -> None:
    for name in sorted(_EXPECTED):
        text = _read(name)
        assert text.startswith("---"), f"{name} has no frontmatter block"
        assert re.search(r"^description:", text, re.MULTILINE), (
            f"{name} frontmatter has no description"
        )


def test_no_command_hardcodes_an_mcp_prefix() -> None:
    """Plugin-bundled MCP tools get the mcp__plugin_<plugin>_<server>__ prefix on
    customer installs, so ANY hardcoded prefix silently points at nothing."""
    for name in sorted(_EXPECTED):
        hit = _MCP_PREFIX.search(_read(name))
        assert not hit, (
            f"{name} hardcodes the MCP prefix {hit.group(0)!r} — name tools bare"
        )


def test_every_command_defers_to_the_playbook() -> None:
    """One source of truth: the method lives in the PLAYBOOK, not in 18 copies."""
    for name in sorted(_EXPECTED - {"workflow_plan.md"}):
        assert "PLAYBOOK" in _read(name), f"{name} never defers to the PLAYBOOK"
    assert "rm-social-media-manager:rm-content-planner" in _read("workflow_plan.md"), (
        "workflow_plan.md does not invoke the skill"
    )


def test_spend_commands_keep_the_confirm_gate() -> None:
    for name in sorted(_SPEND):
        text = _flat(name)
        assert "confirm=true" in text, f"{name} never mentions confirm=true"
        assert re.search(r"explicit yes", text, re.IGNORECASE), (
            f"{name} lost the wait-for-an-explicit-yes language"
        )


def test_read_only_commands_refuse_to_spend() -> None:
    for name in sorted(_READ_ONLY):
        text = _flat(name)
        assert re.search(r"[Nn]ever call (a )?spend", text), (
            f"{name} lost its never-spend rule"
        )


def test_only_discovery_commands_may_touch_apify() -> None:
    """Apify bills the USER's own Apify account. RM's credit ceiling and
    confirm-before-spend cannot see or stop it, so every other command must
    explicitly refuse it."""
    for name in sorted(_EXPECTED - _MAY_USE_APIFY):
        text = _flat(name)
        assert re.search(r"never call Apify", text, re.IGNORECASE), (
            f"{name} does not refuse Apify — an unguarded Apify call spends the "
            "user's own money outside every gate we control"
        )


def test_apify_commands_gate_the_users_own_money() -> None:
    for name in sorted(_MAY_USE_APIFY):
        text = _flat(name)
        if "Apify" not in text:
            continue
        assert re.search(r"own (money|Apify account)", text, re.IGNORECASE), (
            f"{name} drives Apify without saying it spends the user's OWN money"
        )


def test_find_competitors_refuses_the_web_search_substitute() -> None:
    """G332: a generic web search is not a substitute for real discovery, and the
    shipped plugin lost this guard once already."""
    text = _flat("find-competitors.md")
    assert "G332" in text, "find-competitors.md lost the G332 reference"
    assert re.search(r"web search", text, re.IGNORECASE), (
        "find-competitors.md never mentions the web-search substitute it must refuse"
    )
    assert re.search(r"\bstop\b", text, re.IGNORECASE), (
        "find-competitors.md must STOP when it cannot search, not degrade silently"
    )


def test_market_research_is_the_only_sanctioned_web_search() -> None:
    text = _flat("market-research.md")
    assert "G233" in text and "G332" in text, (
        "market-research.md must cite G233 (sizing is allowed) AND G332 (finding "
        "accounts is not) — without both, the boundary is guesswork"
    )


def test_delete_competitors_warns_about_permanent_data_loss() -> None:
    text = _flat("delete-competitors.md")
    assert re.search(r"last workspace", text, re.IGNORECASE), (
        "delete-competitors.md does not explain the last-holder case, which is the "
        "one that erases an analysed library for good"
    )
    assert re.search(r"permanent", text, re.IGNORECASE), (
        "delete-competitors.md never says the loss is permanent"
    )
    assert re.search(r"explicit yes", text, re.IGNORECASE), (
        "delete-competitors.md lost its explicit-yes gate"
    )


def test_switch_workspace_reconfirms_the_handle() -> None:
    """G223 is still open: the Instagram handle is account-wide, not per-workspace,
    so an easy switch silently carries the previous client's handle."""
    text = _flat("switch-workspace.md")
    assert "G223" in text, "switch-workspace.md lost the G223 reference"
    assert "get_business_profile" in text, (
        "switch-workspace.md does not re-read the profile after switching"
    )


def test_watch_video_prices_assist_mode_honestly() -> None:
    """G339: the plugin told customers assist mode was free. It is about half."""
    text = _flat("watch-video.md")
    assert re.search(r"not free", text, re.IGNORECASE), (
        "watch-video.md must say assist mode is NOT free"
    )
    assert re.search(r"half", text, re.IGNORECASE), (
        "watch-video.md must say the final charge is about half a normal run"
    )
    assert re.search(r"SAME", text), (
        "watch-video.md must say the up-front hold is the SAME as a normal run"
    )


def test_playbook_was_not_edited_for_the_commands() -> None:
    """The commands are wrappers — the method lives in PLAYBOOK.md only. The
    PLAYBOOK must not name any command, or the method would depend on the
    wrapper layer."""
    playbook = (
        _PLUGIN_ROOT / "skills" / "rm-content-planner" / "PLAYBOOK.md"
    ).read_text(encoding="utf-8")
    for marker in ("/rm-social-media-manager:", "commands/"):
        assert marker not in playbook, (
            f"PLAYBOOK.md references {marker!r} — the method must not depend on "
            "the command wrappers"
        )


_CHECKS = [
    ("exactly the approved commands exist", test_exactly_the_approved_commands_exist),
    ("every command has description frontmatter",
     test_every_command_has_description_frontmatter),
    ("no command hardcodes an MCP prefix", test_no_command_hardcodes_an_mcp_prefix),
    ("every command defers to the PLAYBOOK", test_every_command_defers_to_the_playbook),
    ("spend commands keep the confirm gate", test_spend_commands_keep_the_confirm_gate),
    ("read-only commands refuse to spend", test_read_only_commands_refuse_to_spend),
    ("only discovery commands may touch Apify",
     test_only_discovery_commands_may_touch_apify),
    ("Apify commands gate the user's own money",
     test_apify_commands_gate_the_users_own_money),
    ("find-competitors refuses the web-search substitute (G332)",
     test_find_competitors_refuses_the_web_search_substitute),
    ("market-research is the only sanctioned web search (G233)",
     test_market_research_is_the_only_sanctioned_web_search),
    ("delete-competitors warns about permanent data loss",
     test_delete_competitors_warns_about_permanent_data_loss),
    ("switch-workspace re-confirms the handle (G223)",
     test_switch_workspace_reconfirms_the_handle),
    ("watch-video prices assist mode honestly (G339)",
     test_watch_video_prices_assist_mode_honestly),
    ("PLAYBOOK was not edited for the commands",
     test_playbook_was_not_edited_for_the_commands),
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
