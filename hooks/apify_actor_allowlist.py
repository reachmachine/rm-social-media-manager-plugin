#!/usr/bin/env python3
"""Per-session cache of which Apify actor ids the server named for the
CURRENT task (RMP-202).

Every actor run now goes through the ONE generic `call-actor` tool
(`plugin.json`'s Apify server exposes only `?tools=call-actor`, so the same
URL never has to change when a new actor is added -- see `plugin.json`'s own
history). `call-actor` can run ANY actor on the customer's own Apify account
(RMP-190's module docstring: the customer's account pays, our server holds
no token for it). Before this module, the SAFETY BOUNDARY was the tool name
itself -- one named tool per actor, so the model could only ever call the
actor the tool name already fixed. That boundary is gone once every call
goes through one shared tool name, so this cache is the replacement:
`apify_actor_gate.py`'s PreToolUse check denies any `call-actor` call whose
`actor` is not in the list recorded here for this session.

RECORDED FROM: a reachmachine tool's own JSON result, when it carries an
`allowed_actor_ids` list -- today, only `start_reviews_fetch` (RMP-190)
returns one. A later server tool that hands back its own actor id (a future
Instagram flow, say) needs no new gate code -- only a new `tool_result_
dispatch.py` wiring line that calls `record_from_tool_result` too.

STATE: raw keys read/written through `connection_state.read_raw`/`write_patch`
-- the same per-session JSON store `reviews_read_state.py` uses for
`reviews_fetch`. Shape of each: `{"actor_ids": [str, ...]}`, or the key
absent once nothing has named an allow-list yet.

  `_STATE_KEY` -- the SESSION list, written by a result that carries no
  `agent_id` (the main chat: reviews flow, step 9). Behaviour unchanged.

  `_STATE_KEY:<safe agent_id>` -- a PER-JOB list (RMP-218, P1776). Step 10
  runs several background jobs at once; if they all wrote the one session key,
  each new server answer would wipe the previous job's list and the gate would
  block its scraper (plan edge E38). A result that arrives WITH an `agent_id`
  writes ONLY its own key, so it can never touch the session list either.

READ FALLBACK (`allowed_actor_ids(session_id, agent_id)`): an agent that HAS
its own key is allowed only that list (a corrupt own key denies everything --
it does not fall back). An agent that never recorded a key gets the session
list, exactly as before this change, so no flow that works today breaks.

FAIL-SAFE ON WRITE, FAILS CLOSED ON READ -- the opposite of most siblings
here, and deliberately so: a malformed or missing cache on the read side
must deny every actor id, never allow by omission. `record_from_tool_result`
itself never raises (same convention as `reviews_read_state.handle_start`):
a response with no `allowed_actor_ids` list, or a malformed one, leaves any
prior allow-list untouched rather than clearing it or crashing the hook.
"""
from __future__ import annotations

import json
import re
from typing import Any

import connection_state as cs

_STATE_KEY = "apify_allowed_actors"


def _safe(agent_id: str) -> str:
    """Same rule as `job_tool_cache._safe`."""
    return re.sub(r"[^A-Za-z0-9_-]", "_", agent_id)


def _state_key(agent_id: Any) -> str:
    if isinstance(agent_id, str) and agent_id:
        return f"{_STATE_KEY}:{_safe(agent_id)}"
    return _STATE_KEY


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def record_from_tool_result(session_id: str, payload: dict) -> None:
    """`PostToolUse` on a reachmachine tool whose JSON result MAY carry an
    `allowed_actor_ids` list. No-op (leaves any prior allow-list untouched)
    when the result is not JSON, is not a dict, or has no list of strings
    under that key -- never manufactures an allow-list out of a response
    that did not actually set one."""
    try:
        data = _parse_json_response(payload.get("tool_response"))
        if data is None:
            return
        actor_ids = data.get("allowed_actor_ids")
        run = data.get("run")
        if actor_ids is None and isinstance(run, dict):
            # `get_hangouts_work` (P1778) nests it: `run.allowed_actor_ids`.
            actor_ids = run.get("allowed_actor_ids")
        if not isinstance(actor_ids, list) or not actor_ids:
            return
        if not all(isinstance(a, str) and a for a in actor_ids):
            return
        cs.write_patch(session_id, {_state_key(payload.get("agent_id")): {"actor_ids": actor_ids}})
    except Exception:
        pass


def _list_at(raw: dict, key: str) -> list[str]:
    value = raw.get(key)
    if not isinstance(value, dict):
        return []
    actor_ids = value.get("actor_ids")
    if not isinstance(actor_ids, list):
        return []
    return [a for a in actor_ids if isinstance(a, str)]


def allowed_actor_ids(session_id: str, agent_id: str | None = None) -> list[str]:
    """The cached allow-list for this caller, or `[]` once cleared, never
    set, or the state is corrupt. An empty list denies every actor id --
    FAILS CLOSED (module docstring), never "allow" by omission. An
    `agent_id` that has its own key reads ONLY that key; one that never
    recorded a key reads the session list (module docstring)."""
    try:
        raw = cs.read_raw(session_id)
        own_key = _state_key(agent_id)
        if own_key != _STATE_KEY and own_key in raw:
            return _list_at(raw, own_key)
        return _list_at(raw, _STATE_KEY)
    except Exception:
        return []
