"""Falsifiable test for G339 / FRFRMU-283 — assist mode is a DISCOUNT, not free.

The bug: every customer-facing file in this plugin told the user assist mode
"doesn't spend your RM credits" and was labelled "(free)". The live server does
charge for it. `backend/app/mcp/tools_pipeline_assist_write.py` states the two
real numbers plainly, and neither is zero:

  * the hold up front is the SAME size as a normal run, and
  * the FINAL charge is about HALF a normal run per reel.

So a customer approved a run they had been told was free and then watched their
balance drop. Founder decision 2026-08-19: say the discount, never say free, and
"it may become free in future" is allowed only as a maybe.

This test guards the wording in both directions:

1. NEGATIVE — no line that talks about assist mode may claim it is free, costs
   no credits, or carries no charge. Scoped to assist lines on purpose: the
   PLAYBOOK says "free" correctly about a dozen genuinely free read-only tools
   (`list_workspaces`, `remove_competitor`, `validate_content_plan`), and those
   must keep saying it.
2. POSITIVE — rule 6a must still carry BOTH numbers. Dropping the "hold is the
   same" half is the subtler lie: a creator short on credits would read "half
   price" and think they can afford to start, when the hold blocks them.
3. HEDGED — the future-free line must stay a maybe, never a promise.

Standalone-runnable (the RAM guard blocks pytest on this box):
`python test_g339_assist_pricing_honesty.py`.
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

# Every file that can put a price in front of a customer.
# Every file that can put a price in front of a customer. BOTH analysis entry
# points count: the workflow and the granular /watch-video command.
_CUSTOMER_FACING = (
    _PLUGIN_ROOT / "commands" / "workflow_analyze.md",
    _PLUGIN_ROOT / "commands" / "workflow_plan.md",
    _PLUGIN_ROOT / "commands" / "watch-video.md",
    _SKILL / "PLAYBOOK.md",
    _SKILL / "SKILL.md",
    _SKILL / "README.md",
)

# The commands whose frontmatter description quotes a price.
_PRICING_COMMANDS = ("workflow_analyze.md", "watch-video.md")

# A claim of zero cost. Each is a phrase that shipped, or its near neighbour.
_FREE_CLAIMS = (
    r"\(\s*free\s*\)",
    r"(?:does ?n[o']t|doesn't|will not|won't|never) spend (?:your |their |any )?RM credits",
    r"(?:costs?|spends?) no (?:RM )?credits",
    r"no[- ]credit path",
    r"at no charge",
    r"free of charge",
    r"is free\b",
    r"\bfor free\b",
)

_FREE_RE = re.compile("|".join(_FREE_CLAIMS), re.IGNORECASE)

# A line that FORBIDS the claim quotes the claim to forbid it — rule 6a's own
# "NEVER tell anyone assist mode is free" must not read as the bug it prevents.
# These docs mark every prohibition with an uppercase NEVER or "never tell",
# so that idiom is the exemption, not a general "any negation nearby" rule.
_PROHIBITION_RE = re.compile(r"NEVER|never (?:tell|say|claim|promise|describe)")

# The hold-is-the-same claim, as a CLAIM and not as two loose words. Rule 6a
# already says "does the same analysis" and "the same instructions" about
# unrelated things, so `"hold" in rule and "same" in rule` passes even after the
# real sentence is deleted — proven by a deliberate break. So require the two
# ideas inside ONE sentence: `[^.]` cannot cross a full stop.
_HOLD_SAME_RE = re.compile(
    r"(?:hold|held)[^.]{0,160}?(?:same|not smaller)"
    r"|(?:same|not smaller)[^.]{0,160}?(?:hold|held)",
    re.IGNORECASE,
)


def _assist_lines(path: pathlib.Path) -> list[tuple[int, str]]:
    """Lines that talk about assist mode — the only place a free claim is a bug."""
    return [
        (n, line)
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if re.search(r"assist", line, re.IGNORECASE)
        and not _PROHIBITION_RE.search(line)
    ]


def _rule_6a(path: pathlib.Path = _SKILL / "PLAYBOOK.md") -> str:
    """Rule 6a's own text — from the '6a.' marker up to the '6b.' one."""
    text = path.read_text(encoding="utf-8")
    start = text.index("\n6a.")
    end = text.index("\n6b.", start)
    return text[start:end]


def test_no_customer_facing_file_calls_assist_mode_free() -> None:
    offenders = [
        f"{path.name}:{n}: {line.strip()}"
        for path in _CUSTOMER_FACING
        for n, line in _assist_lines(path)
        if _FREE_RE.search(line)
    ]
    assert not offenders, (
        "assist mode is described as free, but the server charges about half a "
        "normal run (G339/FRFRMU-283). Offending lines:\n  " + "\n  ".join(offenders)
    )


def test_rule_6a_block_carries_no_free_claim_anywhere() -> None:
    """Line-scoped scanning is not enough on its own, and the original bug proves
    it: the shipped phrase "instead of RM credits, at no charge to them" sat on a
    line that never used the word "assist", so a per-line assist filter walked
    straight past it. Rule 6a is entirely about assist mode, so every line in the
    block counts — no keyword needed."""
    offenders = [
        line.strip()
        for line in _rule_6a().splitlines()
        if _FREE_RE.search(line) and not _PROHIBITION_RE.search(line)
    ]
    assert not offenders, (
        "PLAYBOOK rule 6a claims assist mode is free somewhere in the block:\n  "
        + "\n  ".join(offenders)
    )


def test_rule_6a_states_the_final_charge_is_about_half() -> None:
    rule = _rule_6a()
    assert re.search(r"half", rule, re.IGNORECASE), (
        "PLAYBOOK rule 6a no longer says the final charge is about HALF a normal "
        "run — that number is the whole reason to prefer assist mode"
    )
    assert re.search(r"not free", rule, re.IGNORECASE), (
        "PLAYBOOK rule 6a lost its explicit 'not free' — 'cheaper' on its own "
        "was read as free by every session that hit this"
    )


def test_rule_6a_states_the_up_front_hold_is_the_same() -> None:
    """The subtler half of the lie. Half-price on its own reads as 'a creator
    short on credits can still start it' — they cannot, the hold is full size."""
    # Newlines collapsed: the claim is wrapped across lines in the source, and a
    # sentence-scoped match must not be defeated by where the wrap happens to be.
    rule = " ".join(_rule_6a().split())
    assert _HOLD_SAME_RE.search(rule), (
        "PLAYBOOK rule 6a doesn't say IN ONE SENTENCE that the up-front hold is "
        "the same size as a normal run's. Without that, a creator who cannot "
        "afford the hold reads 'half price' and is told they can start anyway"
    )


def test_future_free_is_a_maybe_not_a_promise() -> None:
    """Founder allowed 'it might become free later'. A promise is still a lie."""
    rule = _rule_6a()
    if not re.search(r"free in future|become free", rule, re.IGNORECASE):
        return  # saying nothing about the future is fine
    assert re.search(r"may|might", rule, re.IGNORECASE), (
        "rule 6a talks about assist mode becoming free without hedging it — "
        "'may become free, not decided yet' is allowed, a promise is not"
    )
    assert re.search(r"not decided|isn't decided|never promise", rule, re.IGNORECASE), (
        "rule 6a mentions future-free without marking it undecided"
    )


def test_analyze_command_description_prices_assist_mode_honestly() -> None:
    """The frontmatter description is what a customer reads in the /help list,
    before any of the method text loads."""
    for name in _PRICING_COMMANDS:
        text = (_PLUGIN_ROOT / "commands" / name).read_text(encoding="utf-8")
        description = re.search(r"^description:.*$", text, re.MULTILINE)
        assert description, f"{name} has no description frontmatter"
        line = description.group(0)
        assert not _FREE_RE.search(line), f"{name} description calls assist free: {line}"
        assert re.search(r"half|not free", line, re.IGNORECASE), (
            f"{name} description doesn't price assist mode at all — it must say "
            "about half price / not free"
        )


_CHECKS = [
    ("no customer-facing file calls assist mode free",
     test_no_customer_facing_file_calls_assist_mode_free),
    ("rule 6a block carries no free claim anywhere",
     test_rule_6a_block_carries_no_free_claim_anywhere),
    ("rule 6a states the final charge is about half",
     test_rule_6a_states_the_final_charge_is_about_half),
    ("rule 6a states the up-front hold is the SAME",
     test_rule_6a_states_the_up_front_hold_is_the_same),
    ("future-free is a maybe, not a promise",
     test_future_free_is_a_maybe_not_a_promise),
    ("analyze command description prices assist honestly",
     test_analyze_command_description_prices_assist_mode_honestly),
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
