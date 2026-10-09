#!/usr/bin/env python3
"""Maps a cached server `rules` step (RMP-173 P2) onto the exact step-dict
shape `steps_manifest.py`'s own readers (`question_options`, `question_text`,
`answer_type`, `follow_up`, `skip_question`, `reoffer_question`) already
expect from the bundled `steps.json` -- split out of `steps_manifest.py` to
keep it under the 300-line limit, same "split when it grows" precedent as
`step_gate_own_account.py`.

FIELD MAPPING (`backend/app/services/agent_step_rules.py`'s wire shape ->
`plugins/rm-plugin-v2/steps.json`'s own shape):
  id/n/title/kind      -> id/number/title/kind (`n` is the only renamed key)
  q{text, type, opts}  -> question{text, answer_type, options} (`type` is
                          always copied straight into `answer_type` --
                          `steps_manifest.answer_type` already treats
                          anything outside {"handle","multi_options"} as
                          "options", so a literal "options" value there is
                          harmless)
  follow_up{...,type}  -> follow_up{...,answer_type} (same rename; `type`
                          is always the literal "free_text" for every real
                          follow-up today, matching what `steps_manifest.
                          follow_up` requires)
  skip{q, reoffer}     -> skip{question, reoffer} (each inner `{text, opts}`
                          -> `{text, options}`; `type` is dropped -- neither
                          `skip_question` nor `reoffer_question` reads it)
  allow/deny_reason    -> allow/deny_reason (RMP-173 P3): copied through
                          unchanged onto the mapped step ONLY when well-formed
                          (`allow` a list of non-empty strings, `deny_reason`
                          a non-empty string) -- omitted entirely otherwise,
                          same "drop what doesn't map" rule as every other
                          field here. `step_gate_rules.py` reads these two
                          keys with `dict.get`, so a step with no `allow` key
                          (every BUNDLED step, which never carries one) reads
                          exactly like "nothing cached for this step" and
                          falls back to `step_gate.py`'s own `_STEP_ALLOW`/
                          `_STEP_DENY_REASON` tables -- the key's mere
                          presence is the cache-vs-bundle signal, no separate
                          flag needed.
  wait_for               -> wait_for (RMP-194 gap fix, 2026-09-27): copied
                          through unchanged when a non-empty string. LIVE BUG
                          this fixes, found on dev @bc17e1f9c: a real customer
                          session always reaches step 7 through THIS cached
                          path (any session that ever called `open_workspace`/
                          `get_resume_checklist` -- every real session past
                          step 2), and this function used to drop `wait_for`
                          on the floor even though the server's own wire
                          payload (`agent_step_rules.rules_payload`) already
                          sends it. `step_order.first_unfinished`'s
                          `step.get("wait_for")` check then saw nothing, so
                          `business_review` was NEVER skipped in ordering once
                          cached -- it looked like a normal blocking step the
                          moment step 6 ticked, and `step_gate.py` denied
                          every other tool with "Finish step 7 first." while
                          step 7 was not even ready. The BUNDLED `steps.json`
                          path (used only when nothing is cached, e.g. most
                          existing tests) never had this bug -- it already
                          carries `wait_for` verbatim from disk. Rule 3: drop
                          the `wait_for` block below -> RED (`test_load_
                          steps_cache_maps_wait_for` in test_step_rules_
                          cache.py, and the end-to-end `test_step_gate_order.
                          test_business_review_wait_for_never_blocks_other_
                          tools_from_cache`).

FAIL-SAFE, same direction as `steps_manifest.load_steps`: a step that fails
to map (missing/wrong-typed required field) is silently dropped, exactly
like a malformed bundled entry -- never trusted half-shaped, never crashes.
"""
from __future__ import annotations

from typing import Any

import step_rules_cache

# RMP-201 P0 (2026-09-27): shape parity, closing the exact bug class the
# `wait_for` gap was. Every key `agent_step_rules.STEPS`/`rules_payload()`
# can put on a step must be named here -- either as one `_step_from_rule`
# below actually copies, or (if genuinely never needed on the plugin side)
# in `_IGNORED_RULE_KEYS`. `test_step_rules_cache.py`'s shape-parity test
# reads `agent_step_rules.STEPS` directly (loaded by file path, no `app.*`
# imports needed) and fails the moment a real key is missing from BOTH sets
# -- so a future new server field can never again be silently dropped here
# the way `wait_for` was. Rule 3: remove "wait_for" from this set -> RED.
_HANDLED_RULE_KEYS = frozenset({
    "id", "n", "title", "kind", "q", "brief_key", "follow_up", "skip",
    "allow", "deny_reason", "wait_for",
})
_IGNORED_RULE_KEYS: frozenset[str] = frozenset()

_REQUIRED_STEP_KEYS = ("id", "n", "title", "kind")


def _options_from_opts(opts: Any) -> list[dict[str, str]]:
    if not isinstance(opts, list):
        return []
    return [
        {"value": opt["value"], "label": opt["label"]}
        for opt in opts
        if isinstance(opt, dict) and isinstance(opt.get("value"), str) and isinstance(opt.get("label"), str)
    ]


def _question_from_rule(q: Any) -> dict[str, Any] | None:
    if not isinstance(q, dict):
        return None
    text = q.get("text")
    if not isinstance(text, str) or not text:
        return None
    question: dict[str, Any] = {"text": text, "answer_type": q.get("type")}
    options = _options_from_opts(q.get("opts"))
    if options:
        question["options"] = options
    return question


def _follow_up_from_rule(follow: Any) -> dict[str, Any] | None:
    if not isinstance(follow, dict):
        return None
    result: dict[str, Any] = {}
    for key in ("id", "text", "brief_key"):
        value = follow.get(key)
        if not isinstance(value, str) or not value:
            return None
        result[key] = value
    result["answer_type"] = follow.get("type")
    return result


def _skip_side_from_rule(side: Any) -> dict[str, Any] | None:
    if not isinstance(side, dict):
        return None
    text = side.get("text")
    options = _options_from_opts(side.get("opts"))
    if not isinstance(text, str) or not text or not options:
        return None
    return {"text": text, "options": options}


def _skip_from_rule(skip: Any) -> dict[str, Any] | None:
    if not isinstance(skip, dict):
        return None
    question = _skip_side_from_rule(skip.get("q"))
    reoffer = _skip_side_from_rule(skip.get("reoffer"))
    if question is None or reoffer is None:
        return None
    return {"question": question, "reoffer": reoffer}


def _step_from_rule(rule: Any) -> dict[str, Any] | None:
    if not isinstance(rule, dict) or not all(k in rule for k in _REQUIRED_STEP_KEYS):
        return None
    step_id, number, title, kind = rule.get("id"), rule.get("n"), rule.get("title"), rule.get("kind")
    if not isinstance(step_id, str) or not step_id:
        return None
    if not isinstance(number, int) or isinstance(number, bool):
        return None
    if not isinstance(title, str) or not title or not isinstance(kind, str) or not kind:
        return None
    step: dict[str, Any] = {"id": step_id, "number": number, "title": title, "kind": kind}

    question = _question_from_rule(rule.get("q"))
    if question is not None:
        step["question"] = question

    brief_key = rule.get("brief_key")
    if isinstance(brief_key, str) and brief_key:
        step["brief_key"] = brief_key

    follow_up = _follow_up_from_rule(rule.get("follow_up"))
    if follow_up is not None:
        step["follow_up"] = follow_up

    skip = _skip_from_rule(rule.get("skip"))
    if skip is not None:
        step["skip"] = skip

    allow = rule.get("allow")
    if isinstance(allow, (list, tuple)) and all(isinstance(a, str) and a for a in allow):
        step["allow"] = list(allow)

    deny_reason = rule.get("deny_reason")
    if isinstance(deny_reason, str) and deny_reason:
        step["deny_reason"] = deny_reason

    # RMP-201 P0 / RMP-194 gap fix (2026-09-27): see the module docstring's
    # "wait_for" row -- without this, a cached `business_review` step never
    # carries `wait_for`, and `step_order.first_unfinished` treats it as a
    # normal blocking step the instant it is cached.
    wait_for = rule.get("wait_for")
    if isinstance(wait_for, str) and wait_for:
        step["wait_for"] = wait_for

    return step


def load_from_cache(session_id: str) -> list[dict[str, Any]] | None:
    """The cached server rules for this session, mapped onto the bundled
    step-dict shape and sorted by `number` -- `None` when nothing is cached,
    or when every entry in it fails to map (full corruption). A step that
    individually fails to map is dropped, same as a malformed bundled
    entry, and does not by itself trigger the bundle fallback."""
    rules = step_rules_cache.cached_rules(session_id)
    if rules is None:
        return None
    raw_steps = rules.get("steps")
    if not isinstance(raw_steps, list):
        return None

    seen_ids: set[str] = set()
    seen_numbers: set[int] = set()
    result: list[dict[str, Any]] = []
    for rule in raw_steps:
        step = _step_from_rule(rule)
        if step is None:
            continue
        if step["id"] in seen_ids or step["number"] in seen_numbers:
            continue
        seen_ids.add(step["id"])
        seen_numbers.add(step["number"])
        result.append(step)

    if not result:
        return None
    result.sort(key=lambda s: s["number"])
    return result
