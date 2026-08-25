"""Falsifiable test for G409 — the agent routes NON-planning asks too.

The gap (founder-confirmed, 2026-08-24): the agent definition routed ONLY
planning requests to the rm-content-planner skill. A user who opened with
anything else — "why did my reel flop?", "who am I tracking?" — got no
guidance at all, and nothing anywhere told them the plugin's other commands
exist beyond the greeting's single `know-business` pointer. Friendliness
depended entirely on the user discovering 18 slash commands on their own.

The fix: a compact routing section in `agents/social-media-manager.md` that
maps common intents to the plugin's commands, plus a lost-user rule — show a
short menu grouped free vs spends-credits and end with ONE recommended next
step.

Four checks, each isolated:

1. The agent file carries the G409 routing section at all.
2. Every command the routing table names exists as a real command file —
   the table must never point at a command that was renamed or deleted.
3. The lost-user rule survives: menu, free-vs-credits grouping, ONE next step.
4. The section forbids improvising instead of routing.

Standalone-runnable: `python test_g409_intent_routing.py`.
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
_AGENT = _PLUGIN_ROOT / "agents" / "social-media-manager.md"
_COMMANDS_DIR = _PLUGIN_ROOT / "commands"

_SECTION_MARKER = "Route it (G409)"


def _flat() -> str:
    """Newlines collapsed to single spaces — markdown wraps prose, so a
    required phrase can be split across lines in the source."""
    return " ".join(_AGENT.read_text(encoding="utf-8").split())


def _g409_section() -> str:
    text = _flat()
    idx = text.find(_SECTION_MARKER)
    assert idx != -1, (
        f"social-media-manager.md is missing the '{_SECTION_MARKER}' section "
        "— G409's non-planning intent routing is gone"
    )
    return text[idx:]


def test_agent_carries_the_g409_routing_section() -> None:
    section = _g409_section()
    assert section, "G409 section resolved to empty text"


def test_every_routed_command_exists() -> None:
    """Backtick-quoted names in the G409 section are command references.
    Each must exist as commands/<name>.md — a routing table pointing at a
    renamed or deleted command sends the user to a dead end, which is the
    exact opposite of what this section is for."""
    section = _g409_section()
    named = set(re.findall(r"`([a-z0-9_-]+)`", section))
    assert len(named) >= 8, (
        f"G409 section names only {len(named)} commands ({sorted(named)}) — "
        "the routing table has been gutted; it must cover intake, insights, "
        "competitors, analysis and data at minimum"
    )
    missing = sorted(
        n for n in named if not (_COMMANDS_DIR / f"{n}.md").is_file()
    )
    assert not missing, (
        f"G409 routing table names commands with no command file: {missing} "
        "— either the command was renamed/deleted (fix the table) or the "
        "table has a typo"
    )


def test_lost_user_gets_a_menu_and_one_next_step() -> None:
    section = _g409_section()
    assert re.search(r"\bmenu\b", section, re.IGNORECASE), (
        "G409 section lost the lost-user menu rule"
    )
    assert re.search(r"free.{0,30}credits", section, re.IGNORECASE), (
        "G409 menu no longer groups commands free vs spends-credits — cost "
        "transparency is part of the greeting's promise and must carry "
        "through here"
    )
    assert re.search(r"ONE recommended next step", section), (
        "G409 section no longer ends the menu with ONE recommended next "
        "step — a bare menu offloads the choice back onto the user"
    )


def test_section_forbids_improvising() -> None:
    section = _g409_section()
    assert re.search(r"never improvise", section, re.IGNORECASE), (
        "G409 section no longer forbids improvising instead of routing"
    )


_CHECKS = [
    ("agent carries the G409 routing section",
     test_agent_carries_the_g409_routing_section),
    ("every routed command exists as a command file",
     test_every_routed_command_exists),
    ("lost user gets a menu and ONE next step",
     test_lost_user_gets_a_menu_and_one_next_step),
    ("section forbids improvising",
     test_section_forbids_improvising),
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
