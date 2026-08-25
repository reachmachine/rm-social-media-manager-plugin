"""Falsifiable structural test for G410 — the mystery-shopper eval suite.

The gap (founder-picked approach, 2026-08-24): nothing audited the QUALITY of
the live conversation — the Rules Gate + critic audit the written plan, but a
rude, jargon-heavy, or gate-skipping conversation would ship undetected. The
fix is a `claude plugin eval` suite: scripted customer personas talk to the
agent and graders score the transcript against the plugin's own rules (G100,
G235, G237, G339, G371, G409, Rule 0, confirm-before-spend).

Running the evals spends real API tokens, so CI must NOT run them. This test
is the free structural guard instead: it fails when the suite's cases or the
graders that carry the safety-critical checks are deleted or gutted.

Checks:

1. All six mystery-shopper cases exist, each with a persona and graders.
2. Multi-turn cases carry a valid transcript.jsonl (parseable, ends on a
   user turn — the eval harness grades the agent's NEXT turn).
3. The spend-gate case keeps its confirm=true prohibition grader (min/max 0).
4. The rm-disconnected case keeps its no-improvised-plan graders.
5. The greeting case checks all four G371 beats (brand, cost, first move,
   plain-language judge).

Standalone-runnable: `python test_g410_eval_suite.py`.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

_HERE = pathlib.Path(__file__).resolve()
_PLUGIN_ROOT = next(
    p for p in _HERE.parents if (p / ".claude-plugin" / "plugin.json").is_file()
)
_EVALS = _PLUGIN_ROOT / "evals"

_CASES = {
    "greeting-first-reply": "single",
    "lost-user-menu": "multi",
    "impatient-founder": "multi",
    "agency-client": "multi",
    "spend-gate": "multi",
    "rm-disconnected": "single",
}


def _graders(case: str) -> dict[str, str]:
    gdir = _EVALS / case / "graders"
    return {
        f.name: " ".join(f.read_text(encoding="utf-8").split())
        for f in sorted(gdir.glob("*.md"))
    }


def test_all_six_cases_exist_with_personas_and_graders() -> None:
    for case, kind in _CASES.items():
        d = _EVALS / case
        assert d.is_dir(), f"eval case '{case}' is missing entirely"
        entry = d / ("prompt.md" if kind == "single" else "case.yaml")
        assert entry.is_file(), f"eval case '{case}' lost its {entry.name}"
        graders = list((d / "graders").glob("*.md"))
        assert len(graders) >= 2, (
            f"eval case '{case}' has {len(graders)} grader(s) — every "
            "mystery shopper needs at least an objective check and a judge"
        )


def test_multi_turn_transcripts_are_valid_and_end_on_user() -> None:
    for case, kind in _CASES.items():
        if kind != "multi":
            continue
        t = _EVALS / case / "transcript.jsonl"
        assert t.is_file(), f"'{case}' is multi-turn but has no transcript.jsonl"
        lines = [
            json.loads(line)
            for line in t.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        assert lines, f"'{case}' transcript.jsonl is empty"
        for obj in lines:
            assert obj.get("role") in ("user", "assistant") and obj.get(
                "content"
            ), f"'{case}' transcript has a malformed turn: {obj}"
        assert lines[-1]["role"] == "user", (
            f"'{case}' transcript must end on a USER turn — the harness "
            "replays history and grades the agent's next reply; ending on "
            "an assistant turn grades nothing"
        )


def test_spend_gate_keeps_the_confirm_true_prohibition() -> None:
    graders = _graders("spend-gate")
    prohibition = next(
        (g for g in graders.values() if '"confirm"' in g and "max: 0" in g),
        None,
    )
    assert prohibition, (
        "spend-gate lost its confirm=true prohibition grader (tool_used with "
        "max: 0) — that grader is the machine-checkable half of "
        "confirm-before-spend; the llm judge alone can miss a silent spend"
    )
    assert "min: 0" in prohibition, (
        "spend-gate confirm=true grader lost min: 0 — min/max 0 together "
        "mean 'must never be called'"
    )


def test_rm_disconnected_keeps_no_improvised_plan_graders() -> None:
    graders = _graders("rm-disconnected")
    joined = " ".join(graders.values())
    assert re.search(r"not_contains", joined), (
        "rm-disconnected lost its not_contains calendar grader — an "
        "improvised 'Week 1 / Day 1' plan must fail mechanically"
    )
    assert re.search(r"reconnect|connect it|settings", joined, re.IGNORECASE), (
        "rm-disconnected graders no longer require telling the user HOW to "
        "fix the connection (G235)"
    )


def test_greeting_checks_all_four_g371_beats() -> None:
    graders = _graders("greeting-first-reply")
    joined = " ".join(graders.values())
    for beat, needle in [
        ("brand name", "Reach Machine"),
        ("cost transparency", "credit"),
        ("one first move", "know-business"),
        ("plain-language judge", "type: llm"),
    ]:
        assert needle in joined, (
            f"greeting-first-reply graders lost the {beat} check "
            f"(expected '{needle}') — all four G371 beats must be graded"
        )


_CHECKS = [
    ("all six cases exist with personas and graders",
     test_all_six_cases_exist_with_personas_and_graders),
    ("multi-turn transcripts are valid and end on a user turn",
     test_multi_turn_transcripts_are_valid_and_end_on_user),
    ("spend-gate keeps the confirm=true prohibition",
     test_spend_gate_keeps_the_confirm_true_prohibition),
    ("rm-disconnected keeps the no-improvised-plan graders",
     test_rm_disconnected_keeps_no_improvised_plan_graders),
    ("greeting checks all four G371 beats",
     test_greeting_checks_all_four_g371_beats),
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
