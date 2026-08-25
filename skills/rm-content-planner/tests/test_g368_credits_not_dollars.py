"""Falsifiable test for G368 / FRFRMU-360 — price everything in credits, never in dollars.

The bug: a live session told a customer "actual cost $4.83 (well under the $11 worst-case
estimate)". Customers pay Reach Machine in credits, never dollars, so that number is two
problems at once: (1) unverifiable — the customer has no dollar figure anywhere in their own
account to check it against, and (2) a margin leak — $4.83/570 reels is our internal COGS
(cost of goods sold), not what the customer was charged. Verified live: every existing pricing
rule (PLAYBOOK rules 5, 6, 6a, 6b) already speaks only in credits, but nothing forbade a dollar
figure. PLAYBOOK rule 6c is the fix — same shape as G339's rule 6a for "assist mode is a
discount, not free": a plain rule plus a test that fails if it, or its wiring into the
customer-facing commands, is ever removed.

Standalone-runnable (the RAM guard blocks pytest on this box):
`python test_g368_credits_not_dollars.py`.
"""
from __future__ import annotations

import pathlib
import re
import sys

# Plugin root by marker-walk, never parent-counting (same reason as test_commands.py and
# test_g339_assist_pricing_honesty.py: fixed-depth path math broke on the last re-nesting).
_HERE = pathlib.Path(__file__).resolve()
_PLUGIN_ROOT = next(
    p for p in _HERE.parents if (p / ".claude-plugin" / "plugin.json").is_file()
)
_SKILL = _PLUGIN_ROOT / "skills" / "rm-content-planner"

# Every file that can put a price in front of a customer — same set G339 uses.
_CUSTOMER_FACING = (
    _PLUGIN_ROOT / "commands" / "workflow_analyze.md",
    _PLUGIN_ROOT / "commands" / "workflow_plan.md",
    _PLUGIN_ROOT / "commands" / "watch-video.md",
    _SKILL / "PLAYBOOK.md",
    _SKILL / "SKILL.md",
    _SKILL / "README.md",
)

# The two command files that must cite rule 6c alongside 6/6a/6b.
_COMMANDS_CITING_RULES = (
    _PLUGIN_ROOT / "commands" / "watch-video.md",
    _PLUGIN_ROOT / "commands" / "workflow_analyze.md",
)

# A real (non-zero) dollar figure, or a bare currency-code/word mention. "$0" is exempt on
# purpose — SKILL.md's "invalid handles cost $0" is genuinely zero, not a margin leak.
_DOLLAR_RE = re.compile(
    r"\$\s*[1-9][\d,]*(?:\.\d+)?"  # $4.83, $11, $1,200
    r"|\bUSD\b"
    r"|\bin dollars\b"
    r"|\bin US dollars\b",
    re.IGNORECASE,
)

# A dollar mention only counts as an RM-pricing leak if it sits next to RM-pricing language.
# Without this, PLAYBOOK.md §G's own worked example — "I replaced a $2k hire with AI" — a
# CREATOR'S reel-idea example, nothing to do with what Reach Machine charges — trips the check.
# Confirmed against the live file: that line carries none of these words.
_PRICING_CONTEXT_RE = re.compile(
    r"credit|cost|charge|spend|hold|price|per reel|per run|worst-case", re.IGNORECASE
)

# An internal cost-accounting figure — never a customer's business. No context requirement:
# "COGS" itself is unambiguous, and no legitimate customer-facing use of the word exists today
# (confirmed empty against the live files before this fix).
_COGS_RE = re.compile(r"\bCOGS\b|\bcogs[- ]cents?\b", re.IGNORECASE)

# A line that FORBIDS the claim quotes it in order to forbid it — same idiom G339's test uses:
# these docs mark every prohibition with an uppercase NEVER or "never <verb>", so that idiom is
# the exemption, not a general "any negation nearby" rule. Extended with this rule's own verbs
# (convert/quote/translate/state) since "NEVER convert ... into USD" is how 6c phrases its ban.
_PROHIBITION_RE = re.compile(
    r"NEVER|never (?:tell|say|claim|promise|describe|convert|quote|translate|state)"
)


def _offending_lines(path: pathlib.Path, pattern: re.Pattern[str]) -> list[str]:
    return [
        f"{path.name}:{n}: {line.strip()}"
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if pattern.search(line) and not _PROHIBITION_RE.search(line)
    ]


def _rule_6c(path: pathlib.Path = _SKILL / "PLAYBOOK.md") -> str:
    """Rule 6c's own text — from the '6c.' marker up to the '7.' one."""
    text = path.read_text(encoding="utf-8")
    start = text.index("\n6c.")
    end = text.index("\n7.", start)
    return text[start:end]


def _dollar_pricing_offenders(path: pathlib.Path) -> list[str]:
    """Dollar figures that ALSO carry RM-pricing language on the same line — see
    _PRICING_CONTEXT_RE for why the context requirement exists."""
    return [
        f"{path.name}:{n}: {line.strip()}"
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if _DOLLAR_RE.search(line)
        and _PRICING_CONTEXT_RE.search(line)
        and not _PROHIBITION_RE.search(line)
    ]


def test_no_customer_facing_file_quotes_a_dollar_amount() -> None:
    offenders = [
        line
        for path in _CUSTOMER_FACING
        for line in _dollar_pricing_offenders(path)
    ]
    assert not offenders, (
        "a customer-facing file states a real dollar/currency figure next to pricing "
        "language — customers pay in credits, not dollars (G368/FRFRMU-360). Offending "
        "lines:\n  " + "\n  ".join(offenders)
    )


def test_no_customer_facing_file_mentions_cogs() -> None:
    offenders = [
        line
        for path in _CUSTOMER_FACING
        for line in _offending_lines(path, _COGS_RE)
    ]
    assert not offenders, (
        "a customer-facing file mentions COGS/cogs-cents — that is our internal cost "
        "accounting, never something a customer sees (G368/FRFRMU-360). Offending lines:\n  "
        + "\n  ".join(offenders)
    )


def test_rule_6c_bans_currency_conversion() -> None:
    rule = _rule_6c()
    assert re.search(r"\bcredit", rule, re.IGNORECASE), (
        "PLAYBOOK rule 6c no longer talks about credits at all"
    )
    assert re.search(r"NEVER", rule), (
        "PLAYBOOK rule 6c lost its explicit NEVER prohibition on currency conversion"
    )
    assert re.search(r"dollar|currency|USD|INR", rule, re.IGNORECASE), (
        "PLAYBOOK rule 6c no longer names dollars/currency as the thing it bans"
    )


def test_rule_6c_bans_cogs_specifically() -> None:
    rule = _rule_6c()
    assert re.search(r"\bCOGS\b", rule), (
        "PLAYBOOK rule 6c no longer names COGS explicitly — the original bug leaked a COGS "
        "figure ($4.83/570 reels), not just a converted currency amount, so the rule must ban "
        "both, not only currency conversion"
    )


def test_rule_6c_redirects_a_direct_dollar_question() -> None:
    rule = _rule_6c()
    assert re.search(r"prices in credits", rule, re.IGNORECASE), (
        "PLAYBOOK rule 6c no longer tells the assistant what to say when a human directly asks "
        "for a dollar figure — without this, 'never state a dollar number' has no fallback "
        "line and a session under-specified for this case reaches for a guess"
    )


def test_commands_cite_rule_6c() -> None:
    offenders = [
        path.name
        for path in _COMMANDS_CITING_RULES
        if "6c" not in path.read_text(encoding="utf-8")
    ]
    assert not offenders, (
        "these commands cite rules 2/6/6a/6b but not 6c, so a session following only the "
        "command file (not the full PLAYBOOK) never loads the credits-not-dollars rule: "
        + ", ".join(offenders)
    )


_CHECKS = [
    ("no customer-facing file quotes a dollar amount",
     test_no_customer_facing_file_quotes_a_dollar_amount),
    ("no customer-facing file mentions COGS",
     test_no_customer_facing_file_mentions_cogs),
    ("rule 6c bans currency conversion",
     test_rule_6c_bans_currency_conversion),
    ("rule 6c bans COGS specifically",
     test_rule_6c_bans_cogs_specifically),
    ("rule 6c redirects a direct dollar question",
     test_rule_6c_redirects_a_direct_dollar_question),
    ("watch-video.md and workflow_analyze.md cite rule 6c",
     test_commands_cite_rule_6c),
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
