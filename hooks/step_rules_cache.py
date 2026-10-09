#!/usr/bin/env python3
"""Caches the server's step rules for this session (RMP-173 P2).

Spec: RMP-173 Jira design comment, "Plugin side" -- "A PostToolUse recorder
caches `rules` via `cs.write_patch` into the session's connection-state
file. It survives workspace switches and is reset at SessionStart (one
fetch per session)."

`open_workspace` and `get_resume_checklist` both now accept `rules_version`
and always return it, returning a `rules` body too only when the caller's
own version is older (`backend/app/services/agent_step_rules.py`,
RMP-173 P1). This module is the plugin-side half: `maybe_cache_rules` reads
whatever a successful call to either tool returned and stores it; `steps_
manifest.load_steps` (RMP-173 P2's merge point) reads it back through
`cached_rules`, preferring it over the bundled `steps.json`.

SAME FILE, NEW KEYS: `step_rules`/`step_rules_version` live in the same
per-session state file `connection_state.py` and `step_state.py` already
share -- `write_patch` merges onto it, so this can never stomp a sibling
writer's own keys, and vice versa.

SURVIVES A WORKSPACE SWITCH ON PURPOSE: `step_state.reset_for_new_workspace`
clears only workspace-scoped progress; the funnel's own wording/options are
session-wide, not workspace-scoped, so re-fetching them on every switch
would waste the very round-trip this cache exists to avoid. Cleared at
SessionStart instead, when `connection_state.reset_state` deletes the whole
file (`reset-connections.sh`).

VALIDATION, same fail-safe direction as `steps_manifest.load_steps`: a
malformed `rules` body is never trusted half-shaped. `_valid_rules` checks
the top-level shape (`{"steps": [...], "extra_q": {...}}`) and that every
step carries its four required wire keys before anything is written or
read back -- a corrupt cache reads as "nothing cached", never as a crash.
"""
from __future__ import annotations

import json
from typing import Any

import connection_state as cs

# The two tools whose JSON response may carry `rules_version`/`rules`
# (`backend/app/services/agent_step_rules.py`'s `rules_for_client`).
CACHED_TOOLS = ("open_workspace", "get_resume_checklist")

_REQUIRED_STEP_KEYS = ("id", "n", "title", "kind")


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _valid_rules(rules: Any) -> bool:
    """The shape `agent_step_rules.rules_payload()` sends: a `steps` list
    (non-empty, every entry carrying its four required wire keys) and an
    `extra_q` dict. Never raises."""
    if not isinstance(rules, dict):
        return False
    steps = rules.get("steps")
    if not isinstance(steps, list) or not steps:
        return False
    for step in steps:
        if not isinstance(step, dict) or not all(k in step for k in _REQUIRED_STEP_KEYS):
            return False
    return isinstance(rules.get("extra_q"), dict)


def maybe_cache_rules(session_id: str, payload: dict) -> None:
    """Reads a successful `open_workspace`/`get_resume_checklist` response
    and updates the cache: `step_rules_version` whenever the response
    carries an int `rules_version` (always, per the tools' own contract --
    this keeps the cached version current even on a call that returns no
    `rules` body because the client was already up to date), and
    `step_rules` only when `rules` is present AND well-formed. A malformed
    `rules` body writes nothing for it, leaving whatever was already cached
    (or the bundled fallback) in place -- never overwritten with garbage."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    patch: dict[str, Any] = {}
    version = data.get("rules_version")
    if isinstance(version, int) and not isinstance(version, bool):
        patch["step_rules_version"] = version
    rules = data.get("rules")
    if rules is not None and _valid_rules(rules):
        patch["step_rules"] = rules
    if patch:
        cs.write_patch(session_id, patch)


def cached_rules(session_id: str) -> dict[str, Any] | None:
    """The cached `rules` body for this session, or `None` when never
    cached, cleared (SessionStart), or corrupt -- `steps_manifest.load_steps`
    falls back to the bundled `steps.json` in every one of those cases."""
    raw = cs.read_raw(session_id)
    rules = raw.get("step_rules")
    return rules if _valid_rules(rules) else None


def cached_rules_version(session_id: str) -> int:
    """The `rules_version` this session already has cached, or 0 for a
    fresh session -- sent back to the server on every `open_workspace`/
    `get_resume_checklist` call so it never re-downloads rules the plugin
    already has (RMP-173 design comment)."""
    raw = cs.read_raw(session_id)
    version = raw.get("step_rules_version")
    return version if isinstance(version, int) and not isinstance(version, bool) else 0
