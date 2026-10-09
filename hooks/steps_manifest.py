#!/usr/bin/env python3
"""Loads and validates `plugins/rm-plugin-v2/steps.json` (RMP-10, RMP-12,
RMP-19).

Spec: docs/plugin-v2/00-resume-checklist.md, "Where the list of steps
lives." `step_gate.py` and `step_recorder.py` both read the step order,
`kind`, and (for a fixed-option question step) `question`/`brief_key` from
here, instead of hard-coding step 3's shape anywhere -- step 2
(`choose_workspace`) has neither `question` nor `brief_key`: its options
come from the live `list_workspaces` result instead, held in
`step_state.py`'s `workspace_options`.

FAIL-SAFE, same direction as `connection_state.py`: a missing or malformed
`steps.json` must never crash a hook. `load_steps` returns an empty list --
callers already treat "no steps" as "nothing more to check" (the FAILING
CLOSED, when it happens, is `step_gate.py`'s job, by denying whatever it
cannot positively allow -- never this module's).
"""
from __future__ import annotations

import json
import pathlib
from typing import Any

import steps_localize
import steps_manifest_from_rules

_MANIFEST_PATH = pathlib.Path(__file__).resolve().parent.parent / "steps.json"

REQUIRED_STEP_KEYS = ("id", "number", "title", "kind")


def manifest_path() -> pathlib.Path:
    return _MANIFEST_PATH


def _load_raw() -> dict[str, Any] | None:
    try:
        raw = _MANIFEST_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def manifest_version() -> int:
    """Read-only lookup used by `public_manifest` -- 1 for anything missing
    or malformed, same fail-safe direction as `load_steps`."""
    data = _load_raw()
    version = data.get("manifest_version") if data else None
    return version if isinstance(version, int) else 1


def load_steps(session_id: str | None = None) -> list[dict[str, Any]]:
    """The steps as THIS owner sees them: `_load_stock_steps`, with the server's translated lines for steps 2-5 laid
    over the question and button text (RMP-281 P2356, `steps_localize.py`). Ids, values and order never change."""
    steps = _load_stock_steps(session_id)
    return steps if session_id is None else steps_localize.apply(session_id, steps)


def _load_stock_steps(session_id: str | None = None) -> list[dict[str, Any]]:
    """Every well-formed step entry, sorted by `number`. A step missing a
    required key, or one that collides on `id`/`number` with an earlier
    entry, is silently dropped rather than trusted half-shaped.

    RMP-173 P2: when `session_id` is given, this SESSION's own cached
    server rules (`step_rules_cache.cached_rules`, mapped to this exact
    shape by `steps_manifest_from_rules`) win over the bundled `steps.json`
    -- the server is the source of truth once it has spoken. Falls back to
    the bundle below when nothing is cached yet, the cache is corrupt, or
    no `session_id` was given at all (every call site not yet updated to
    pass one, per RMP-173's "P3 replaces the hardcoded hook tables" scope
    cut -- see that module's own docstring)."""
    if session_id is not None:
        cached = steps_manifest_from_rules.load_from_cache(session_id)
        if cached is not None:
            return cached
    data = _load_raw()
    if data is None:
        return []
    steps = data.get("steps")
    if not isinstance(steps, list):
        return []

    seen_ids: set[str] = set()
    seen_numbers: set[int] = set()
    result: list[dict[str, Any]] = []
    for step in steps:
        if not isinstance(step, dict) or not all(k in step for k in REQUIRED_STEP_KEYS):
            continue
        step_id = step.get("id")
        number = step.get("number")
        if not isinstance(step_id, str) or not step_id or step_id in seen_ids:
            continue
        if not isinstance(number, int) or number in seen_numbers:
            continue
        seen_ids.add(step_id)
        seen_numbers.add(number)
        result.append(step)
    result.sort(key=lambda s: s["number"])
    return result


def step_by_id(steps: list[dict[str, Any]], step_id: str) -> dict[str, Any] | None:
    for step in steps:
        if step.get("id") == step_id:
            return step
    return None


def question_options(step: dict[str, Any]) -> list[dict[str, str]]:
    """`[{value, label}]` from a step's own fixed `question.options` (step 3
    onward). Step 2 has none here -- its options are the live workspace
    list, read from `step_state.py`'s `workspace_options` instead."""
    question = step.get("question")
    if not isinstance(question, dict):
        return []
    options = question.get("options")
    if not isinstance(options, list):
        return []
    result: list[dict[str, str]] = []
    for opt in options:
        if (
            isinstance(opt, dict)
            and isinstance(opt.get("value"), str)
            and isinstance(opt.get("label"), str)
        ):
            result.append({"value": opt["value"], "label": opt["label"]})
    return result


def question_text(step: dict[str, Any]) -> str | None:
    """A question step's own fixed `question.text` (P1615, RMP-10, RMP-19):
    the exact wording `AskUserQuestion` must use, and the ONLY thing an
    answer is matched back to (`answer_matcher.step_for_question_text`) --
    never step order. `choose_workspace` has one too now (its options stay
    the live workspace list, held in `step_state.py`), so a re-answer
    ("switch workspace") maps to the right step even long after it first
    passed. None for a step with no fixed question text at all."""
    question = step.get("question")
    if not isinstance(question, dict):
        return None
    text = question.get("text")
    return text if isinstance(text, str) and text else None


_KNOWN_ANSWER_TYPES = ("handle", "multi_options")


def answer_type(step: dict[str, Any]) -> str:
    """"handle" or "multi_options" when the step's `question.answer_type`
    is exactly one of those; otherwise "options" (every step that leaves
    `answer_type` unset, and any unrecognised value). Never raises."""
    question = step.get("question")
    if not isinstance(question, dict):
        return "options"
    value = question.get("answer_type")
    return value if value in _KNOWN_ANSWER_TYPES else "options"


def follow_up(step: dict[str, Any]) -> dict[str, str] | None:
    """`{id, text, brief_key}` from a step's `follow_up` block when all
    three are non-empty strings AND `answer_type == "free_text"`;
    otherwise None. Never raises.

    Step 5 (docs/plugin-v2/05-how-you-make-money.md) is the first step with
    a second, free-text question -- the MCQ ("How does this business make
    money?") is the step's own `question`; the description question
    ("what do you offer, and to whom?") lives here instead, so `public_
    manifest` (below) can keep leaving it out without a second exemption."""
    follow = step.get("follow_up")
    if not isinstance(follow, dict):
        return None
    if follow.get("answer_type") != "free_text":
        return None
    result: dict[str, str] = {}
    for key in ("id", "text", "brief_key"):
        value = follow.get(key)
        if not isinstance(value, str) or not value:
            return None
        result[key] = value
    return result


def skip_question(step: dict[str, Any]) -> dict[str, Any] | None:
    """The skip question from a step's `skip.question` block: `{text,
    options}` if both present and well-formed, else None (RMP-52). Used by
    `step_skip.py` for the in-flow skip question and by the skill.
    `options` is `[{value, label}]` -- same shape as
    `question_options`."""
    skip = step.get("skip")
    if not isinstance(skip, dict):
        return None
    question = skip.get("question")
    if not isinstance(question, dict):
        return None
    text = question.get("text")
    if not isinstance(text, str) or not text:
        return None
    options = question.get("options")
    if not isinstance(options, list):
        return None
    result_options = []
    for opt in options:
        if (
            isinstance(opt, dict)
            and isinstance(opt.get("value"), str)
            and isinstance(opt.get("label"), str)
        ):
            result_options.append({"value": opt["value"], "label": opt["label"]})
    if not result_options:
        return None
    return {"text": text, "options": result_options}


def reoffer_question(step: dict[str, Any]) -> dict[str, Any] | None:
    """The reoffer question from a step's `skip.reoffer` block: `{text,
    options}` if both present and well-formed, else None (RMP-52). Used by
    `step_skip.py` for the later-session reoffer question and by the skill."""
    skip = step.get("skip")
    if not isinstance(skip, dict):
        return None
    reoffer = skip.get("reoffer")
    if not isinstance(reoffer, dict):
        return None
    text = reoffer.get("text")
    if not isinstance(text, str) or not text:
        return None
    options = reoffer.get("options")
    if not isinstance(options, list):
        return None
    result_options = []
    for opt in options:
        if (
            isinstance(opt, dict)
            and isinstance(opt.get("value"), str)
            and isinstance(opt.get("label"), str)
        ):
            result_options.append({"value": opt["value"], "label": opt["label"]})
    if not result_options:
        return None
    return {"text": text, "options": result_options}


def public_manifest() -> dict[str, Any]:
    """The exact `steps_manifest` payload `get_resume_checklist` must be
    called with (00-resume-checklist.md, "one file, owned by the plugin"):
    only the four wire fields per step (`id`, `number`, `title`, `kind`) --
    never `question`/`brief_key`, which are this plugin's own business, not
    the server's. `step_gate.py` denies any `get_resume_checklist` call
    whose `steps_manifest` does not match this exactly, so the server always
    holds the true list."""
    return {
        "manifest_version": manifest_version(),
        "steps": [
            {"id": s["id"], "number": s["number"], "title": s["title"], "kind": s["kind"]}
            for s in load_steps()
        ],
    }
