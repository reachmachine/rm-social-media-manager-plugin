#!/usr/bin/env python3
"""Cache-aware allow/deny lookups for `step_gate.py` (RMP-173 P3).

Spec: RMP-173 Jira design comment, "Plugin side" -- "`_STEP_ALLOW` /
`_STEP_DENY_REASON`, the step_skip ids, the revenue follow-up and the
hardcoded question texts all move to the server rules." This module is the
`_STEP_ALLOW`/`_STEP_DENY_REASON` half of that: `step_gate.py` still OWNS
both tables (by name, as literal dicts) -- a backend transcription test
(`backend/tests/unit/test_agent_step_rules.py`) AST-parses them there, and
several plugin tests read them directly
(`step_gate._STEP_ALLOW["website"]`, etc.) -- so this module never renames or
relocates them. What moves here is the READ: once a step carries its own
`allow`/`deny_reason` (only true for a step that came from the session's
cached server rules, mapped by `steps_manifest_from_rules.py` -- see that
module's own docstring for why the key's mere presence is the signal), that
value wins over the matching hardcoded table entry. A step from the bundled
`steps.json` never carries either key, so it always falls through to the
table -- same behaviour as before P3, unchanged.

Split out of `step_gate.py` to keep it under the 300-line limit (same
"split when it grows" precedent as `step_gate_own_account.py` and
`step_gate_workspace.py`). Takes the hardcoded tables as arguments rather
than importing `step_gate` itself, so there is no import cycle.

FAIL-SAFE, same direction as `steps_manifest.load_steps`: a step whose
`allow` is present but the wrong shape, or whose `deny_reason` is present
but empty/non-string, was already dropped by `steps_manifest_from_rules.
_step_from_rule` before it ever reaches here -- this module only ever sees
"key present and well-formed" or "key absent", never "key present but bad".
"""
from __future__ import annotations

from typing import Any, Callable


def allowed_suffixes(
    steps: list[dict[str, Any]], current: dict[str, Any], fallback: dict[str, set[str]],
) -> set[str]:
    """Cumulative union of every tool suffix allowed up to and including
    `current`'s step number (RMP-9's "additionally allow" rule, unchanged).
    `connection_check` is skipped -- it never appears in `fallback` and
    never carries `allow` either, same as before P3."""
    allowed: set[str] = set()
    for step in steps:
        if step["id"] == "connection_check":
            continue
        if step["number"] > current["number"]:
            continue
        allow = step.get("allow")
        if allow is not None:
            allowed |= set(allow)
        else:
            allowed |= fallback.get(step["id"], set())
    return allowed


def deny_reason(current: dict[str, Any], fallback: Callable[[str], str]) -> str:
    """The refusal for the step `current`: `fallback(step id)`, the line the SERVER wrote in the owner's language
    (`deny_lines.finish`, RMP-291 P2320). The English `deny_reason` a cached server rule may also carry is NOT shown: the
    plugin shows no English a hook cannot translate. Rule 3: return `current["deny_reason"]` first -> the Spanish test goes RED."""
    return fallback(current["id"])
