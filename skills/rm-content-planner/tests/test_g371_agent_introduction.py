"""Falsifiable test for G371 — the agent never introduces itself.

The bug in plain words: agents/social-media-manager.md was written entirely TO
THE MODEL ("You are..., you MUST invoke...") with nothing addressed to the
customer — no branding, no plain-English description, no first move, no cost
line. Materially worse since 2026-08-19: the plugin went from 4 to 18 commands,
so a customer never told what exists cannot find 14 of them.

Wording is the founder/CMO's call (still pending) — this test does not police
exact phrasing. It polices STRUCTURE: that the four required pieces exist, that
the introduction fires once per session and not on every turn, that the
existing content-plan routing rule survives unchanged, and that the file stays
inside its token/word budget so this fix does not repeat the growth the
register already flagged (~338 -> ~920 tok before this fix existed).

Standalone-runnable (the RAM guard blocks pytest on this box):
`python test_g371_agent_introduction.py`.
"""
from __future__ import annotations

import pathlib
import re
import sys

# Plugin root by marker-walk, never parent-counting (same reason as
# test_commands.py / test_g339 / test_g366: fixed-depth path math broke on a
# past re-nesting).
_HERE = pathlib.Path(__file__).resolve()
_PLUGIN_ROOT = next(
    p for p in _HERE.parents if (p / ".claude-plugin" / "plugin.json").is_file()
)
_AGENT = _PLUGIN_ROOT / "agents" / "social-media-manager.md"
_KNOW_BUSINESS_CMD = _PLUGIN_ROOT / "commands" / "know-business.md"

_WORD_BUDGET = 480


def _flat(text: str) -> str:
    """Markdown hard-wraps at ~90 chars — match against whitespace-collapsed
    text so a sentence split across lines still counts as one sentence."""
    return " ".join(text.split())


def _read() -> str:
    return _AGENT.read_text(encoding="utf-8")


def test_control_the_file_under_test_is_the_real_one() -> None:
    """If the marker-walk landed somewhere wrong, every other check below would
    fail (or pass) for a reason that has nothing to do with G371."""
    assert _AGENT.is_file(), f"{_AGENT} does not exist — wrong plugin root?"
    assert _AGENT.stat().st_size > 200, f"{_AGENT} is suspiciously empty"
    assert "rm-content-planner" in _read(), (
        "social-media-manager.md has no rm-content-planner reference — this is "
        "not the file this test thinks it is"
    )


def test_introduction_fires_on_the_first_reply() -> None:
    flat = _flat(_read())
    assert re.search(r"first reply", flat, re.IGNORECASE), (
        "no instruction to open the FIRST reply with a greeting — G371's whole "
        "point is that nothing currently talks to the customer at all"
    )
    assert re.search(r"do not repeat|only once|once per session", flat, re.IGNORECASE), (
        "the introduction instruction never says to give it ONCE per session — "
        "without this the agent could repeat a full branded greeting every turn"
    )


def test_introduction_names_the_brand() -> None:
    flat = _flat(_read())
    assert "Reach Machine" in flat, (
        "the introduction never names the Reach Machine brand — the whole gap "
        "is that nothing is addressed to the customer, starting with who this is"
    )


def test_introduction_explains_what_it_does_in_plain_terms() -> None:
    flat = _flat(_read())
    assert re.search(r"content plan", flat, re.IGNORECASE), (
        "the introduction never says, in plain terms, what this agent does"
    )
    assert re.search(r"hooks|structures|posting calendar", flat, re.IGNORECASE), (
        "the introduction names 'a content plan' but never says concretely "
        "what that means (hooks, structures, a posting calendar)"
    )


def test_introduction_gives_one_obvious_first_move() -> None:
    flat = _flat(_read())
    assert "/rm-social-media-manager:know-business" in flat, (
        "the introduction never points to a concrete first command — a "
        "customer told 'tell me about your business' with no command still "
        "has no obvious first move"
    )
    # Regression guard: the command this points to must actually exist, or the
    # 'obvious first move' is a dead link.
    assert _KNOW_BUSINESS_CMD.is_file(), (
        f"{_KNOW_BUSINESS_CMD} does not exist — the introduction's first move "
        "points at a command that isn't shipped"
    )


def test_introduction_states_the_cost_honestly() -> None:
    flat = _flat(_read())
    assert re.search(r"\bfree\b", flat, re.IGNORECASE), (
        "the introduction never says most of this is free to explore"
    )
    assert re.search(r"\bcredit", flat, re.IGNORECASE), (
        "the introduction never mentions Reach Machine credits — a customer "
        "reads 'free' with nothing telling them anything ever costs"
    )
    assert re.search(r"\bask\b", flat, re.IGNORECASE), (
        "the introduction never says it asks before spending — 'free... but "
        "some things cost' with no ask-first promise is the G339-shaped trap"
    )


def test_original_routing_rule_still_present_unchanged() -> None:
    """This fix is additive. The rule that sends every content-plan request
    into the rm-content-planner skill must survive character-for-character —
    breaking it would be a NEW, worse bug hiding behind a nicer greeting."""
    flat = _flat(_read())
    assert "you MUST invoke the `/rm-social-media-manager:rm-content-planner`" in flat, (
        "the original routing instruction was changed or removed — "
        "content-plan requests must still be forced through the skill"
    )
    assert re.search(r"Do not improvise a plan", flat, re.IGNORECASE), (
        "the 'do not improvise, do not skip the skill' guard was lost"
    )


def test_file_stays_within_word_budget() -> None:
    words = len(_read().split())
    assert words <= _WORD_BUDGET, (
        f"social-media-manager.md is {words} words, over the {_WORD_BUDGET}-word "
        "budget — the register already flagged this file's always-on cost "
        "growing once; this fix must not repeat that"
    )


_CHECKS = [
    ("CONTROL: the file under test is the real shipped one",
     test_control_the_file_under_test_is_the_real_one),
    ("introduction fires on the first reply, once per session",
     test_introduction_fires_on_the_first_reply),
    ("introduction names the Reach Machine brand",
     test_introduction_names_the_brand),
    ("introduction explains what it does in plain terms",
     test_introduction_explains_what_it_does_in_plain_terms),
    ("introduction gives one obvious first move, and it exists",
     test_introduction_gives_one_obvious_first_move),
    ("introduction states the cost honestly",
     test_introduction_states_the_cost_honestly),
    ("original routing rule still present, unchanged",
     test_original_routing_rule_still_present_unchanged),
    ("file stays within its word budget",
     test_file_stays_within_word_budget),
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
