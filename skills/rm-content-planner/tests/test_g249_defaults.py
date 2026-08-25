"""Falsifiable test for G249 — the skill must default to assist mode and pin the reel
analysis to Sonnet.

Four things are checked, by reading the real skill files (no mocks):

1. `runner.py` runs the headless pipeline on Sonnet, and Opus is gone entirely.
2. `PLAYBOOK.md` rule 6a LEADS with assist mode instead of offering an even choice.
3. `PLAYBOOK.md` has a rule 6b that launches the `Agent` tool with `model: sonnet`.
4. `PLAYBOOK.md` never spells out the literal line `allowed-tools: Read, Write, Agent`.
   That line is the stale `github-marketing` fork's frontmatter. Pasting it into this
   branch's `SKILL.md` would silently delete six tool grants (WebFetch, WebSearch and
   four Playwright tools), so the PLAYBOOK must describe the change in words instead.

FRFRMU-124 adds four more, all guarding one founder rule: **these are defaults, not
locks — the customer must be able to reverse them.**

5. Rule 6a still tells the customer, out loud, that RM's own paid analysis is available
   on request.
6. Rule 6a still tells the assistant to fall back when the human explicitly asks.
7. Rule 6b says in words that its Sonnet pin is a default, not a lock.
8. `runner.py`'s model can be changed with `RM_SKILL_MODEL` without editing code.

Checks 1-4 all stayed green when the customer's opt-out sentence was deleted outright,
which turns the default into a lock. Check 5 exists because of that.

The other test files in this directory are pytest-style, so these are plain `test_*`
functions too. Unlike them, this file also runs standalone (`python test_g249_defaults.py`)
and prints one [PASS]/[FAIL] line per check, exiting non-zero if any check failed.
"""
from __future__ import annotations

import ast
import pathlib
import re
import sys

_SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent
_RUNNER = _SKILL_DIR / "runner.py"
_PLAYBOOK = _SKILL_DIR / "PLAYBOOK.md"

_SONNET_MODEL = "claude-sonnet-4-6"
_OPUS_MODEL = "claude-opus-4-8"

# The stale fork's frontmatter line. Must never appear in the PLAYBOOK.
_STALE_ALLOWED_TOOLS = "allowed-tools: Read, Write, Agent"


def _runner_text() -> str:
    return _RUNNER.read_text(encoding="utf-8")


def _playbook_text() -> str:
    return _PLAYBOOK.read_text(encoding="utf-8")


def _squash(text: str) -> str:
    """Collapse every run of whitespace to a single space.

    The PLAYBOOK hard-wraps its prose, so a sentence we want to match is often split
    across two lines with leading indentation. Without this, a substring check fails
    for the wrong reason.
    """
    return re.sub(r"\s+", " ", text)


def _rule_block(marker: str, next_marker: str) -> str:
    """Return the PLAYBOOK text from the line starting with `marker` up to (not
    including) the line starting with `next_marker`."""
    text = _playbook_text()
    start = re.search(rf"^{re.escape(marker)}", text, re.MULTILINE)
    assert start, f"rule {marker} not found in PLAYBOOK.md"
    rest = text[start.start():]
    end = re.search(rf"^{re.escape(next_marker)}", rest[1:], re.MULTILINE)
    return rest[: end.start() + 1] if end else rest


def test_runner_uses_sonnet_not_opus() -> None:
    """G249 — the headless runner's own reasoning is pinned to Sonnet."""
    text = _runner_text()
    # FRFRMU-124: the model id is no longer a bare literal — it is the fallback of an
    # os.getenv() call — so match the id itself, not the old `model="..."` spelling.
    assert _SONNET_MODEL in text, f"runner.py does not name {_SONNET_MODEL}"
    assert _OPUS_MODEL not in text, f"runner.py still mentions {_OPUS_MODEL}"


def test_rule_6a_defaults_to_assist_mode() -> None:
    """G249 — rule 6a recommends assist mode first; it no longer offers an even choice."""
    block = _rule_block("6a.", "6b.")
    assert "Default to assist mode" in block, (
        "rule 6a does not lead with 'Default to assist mode'"
    )
    assert "Offer the assist-vs-credits choice" not in block, (
        "rule 6a still carries the old even-choice wording"
    )


def test_rule_6b_pins_analysis_to_a_sonnet_subagent() -> None:
    """G249 — rule 6b names the Agent tool, a subagent_type, and the `sonnet` alias.

    The alias matters: the Agent tool's `model` parameter only accepts
    sonnet | opus | haiku | fable, not a full model id.
    """
    block = _rule_block("6b.", "7. ")
    assert "`Agent`" in block, "rule 6b does not name the Agent tool"
    assert "`subagent_type`" in block, "rule 6b does not set subagent_type"
    assert re.search(r"`model`:\s*`sonnet`", block), (
        "rule 6b does not set model to the `sonnet` alias"
    )


def test_playbook_never_quotes_the_stale_allowed_tools_line() -> None:
    """Guard against re-importing the stale github-marketing frontmatter.

    `allowed-tools: Read, Write, Agent` is that fork's line. On this branch it would
    drop WebFetch, WebSearch and four Playwright grants, so the PLAYBOOK must say
    'includes Agent' rather than quote a full replacement line.
    """
    assert _STALE_ALLOWED_TOOLS not in _playbook_text(), (
        f"PLAYBOOK.md quotes the stale frontmatter line: {_STALE_ALLOWED_TOOLS!r}"
    )


def test_rule_6a_still_offers_the_customer_the_other_option() -> None:
    """FRFRMU-124 — the default must stay a default, not become a lock.

    Rule 6a leads with assist mode, but it must keep telling the customer, out loud,
    that RM's own paid analysis is still available on request. Delete that sentence and
    the recommendation silently becomes a decision made for them. The four original
    checks in this file all stayed green through exactly that deletion, which is why
    this check exists.
    """
    block = _squash(_rule_block("6a.", "6b."))
    assert "If you'd rather I use RM's own analysis" in block, (
        "rule 6a no longer offers the customer RM's own analysis — the default has "
        "become a lock"
    )


def test_rule_6a_still_honours_an_explicit_request() -> None:
    """FRFRMU-124 — the assistant must obey the customer when they take the other option."""
    block = _squash(_rule_block("6a.", "6b."))
    assert "if the human explicitly asks for it" in block, (
        "rule 6a no longer tells the assistant to fall back when the human asks"
    )


def test_rule_6b_calls_sonnet_a_default_not_a_lock() -> None:
    """FRFRMU-124 — rule 6b must say in words that its Sonnet pin is changeable."""
    block = _squash(_rule_block("6b.", "7. "))
    assert "default, not a lock" in block, (
        "rule 6b does not say Sonnet is a default rather than a lock"
    )


def _runner_model_argument() -> ast.expr:
    """Return the AST node passed as `model=` to `ClaudeAgentOptions(...)` in runner.py.

    Read from the parsed syntax tree, NOT from the file's raw text. A plain substring
    check cannot tell live code from a comment: reverting the model line back to a
    hardcoded literal while leaving the explanatory comment in place left the string
    `RM_SKILL_MODEL` in the file, so a text-based test stayed green over code that had
    lost the override entirely. This is that same check, made falsifiable.
    """
    tree = ast.parse(_runner_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", None)
        if name != "ClaudeAgentOptions":
            continue
        for kw in node.keywords:
            if kw.arg == "model":
                return kw.value
        raise AssertionError("ClaudeAgentOptions(...) has no model= argument")
    raise AssertionError("runner.py never calls ClaudeAgentOptions(...)")


def test_runner_model_is_overridable() -> None:
    """FRFRMU-124 — the headless runner's model can be changed without editing code.

    The `model=` argument must literally be `os.getenv("RM_SKILL_MODEL", "<sonnet>")`:
    an env override with Sonnet as the fallback. A bare string literal there is a lock.
    """
    value = _runner_model_argument()
    assert isinstance(value, ast.Call), (
        "runner.py passes a hardcoded model= to ClaudeAgentOptions — the model is a "
        "lock, not a default"
    )
    func = value.func
    called = (
        f"{func.value.id}.{func.attr}"
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name)
        else getattr(func, "id", "?")
    )
    assert called == "os.getenv", f"model= is built by {called}(), not os.getenv()"
    args = [a.value for a in value.args if isinstance(a, ast.Constant)]
    assert args == ["RM_SKILL_MODEL", _SONNET_MODEL], (
        f"model= reads {args!r}; expected the RM_SKILL_MODEL override with "
        f"{_SONNET_MODEL!r} as the fallback"
    )
    assert _OPUS_MODEL not in _runner_text(), (
        f"runner.py still mentions {_OPUS_MODEL}"
    )


_CHECKS = [
    ("runner.py runs on Sonnet, no Opus left", test_runner_uses_sonnet_not_opus),
    ("PLAYBOOK rule 6a defaults to assist mode", test_rule_6a_defaults_to_assist_mode),
    ("PLAYBOOK rule 6b pins analysis to a Sonnet sub-agent",
     test_rule_6b_pins_analysis_to_a_sonnet_subagent),
    ("PLAYBOOK does not quote the stale allowed-tools line",
     test_playbook_never_quotes_the_stale_allowed_tools_line),
    ("PLAYBOOK rule 6a still offers the customer RM's own analysis",
     test_rule_6a_still_offers_the_customer_the_other_option),
    ("PLAYBOOK rule 6a still honours an explicit request",
     test_rule_6a_still_honours_an_explicit_request),
    ("PLAYBOOK rule 6b calls Sonnet a default, not a lock",
     test_rule_6b_calls_sonnet_a_default_not_a_lock),
    ("runner.py model is overridable via RM_SKILL_MODEL",
     test_runner_model_is_overridable),
]


def main() -> int:
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
