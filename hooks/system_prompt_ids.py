#!/usr/bin/env python3
"""Remembers which `prompt_id`s belong to a prompt Claude Code made, not the customer
(RMP-24 money guard).

WHY: the spend gate treats "the customer said yes after the price" as "the confirm call has a
different `prompt_id` from the preview". A finished background agent arrives as a
`<task-notification>` UserPromptSubmit and starts a NEW `prompt_id` -- so preview -> agent
finishes -> notification turn -> `confirm: true` looked like a fresh human yes and charged
credits with no human at all. `capture_last_prompt.py` records those prompt_ids here;
`spend_gate.decide` then denies a confirm made in one of those turns.

Checked live (session d59f32e4, 2026-09-29 transcript): the notification's own row and the
tool results of the turn it starts carry the SAME promptId, and the next real customer message
has a different one -- so a tool call inside the notification turn shares the notification's id.

STATE: one raw key `system_prompt_ids` (a list of the last `_MAX_IDS` strings) in the shared
per-session state file. Reads fail closed for the guard's purpose in the only way that is safe
here: an unreadable state returns "not recorded", which is exactly today's behaviour. Never raises.
"""
from __future__ import annotations

import connection_state as cs

_KEY = "system_prompt_ids"
_MAX_IDS = 20


def _read(session_id: str) -> list[str]:
    raw = cs.read_raw(session_id).get(_KEY)
    if not isinstance(raw, list):
        return []
    return [v for v in raw if isinstance(v, str)]


def record(session_id: str, prompt_id: object) -> None:
    if not isinstance(prompt_id, str) or not prompt_id:
        return
    try:
        ids = [v for v in _read(session_id) if v != prompt_id]
        ids.append(prompt_id)
        cs.write_patch(session_id, {_KEY: ids[-_MAX_IDS:]})
    except Exception:
        pass


def is_system_prompt_id(session_id: str, prompt_id: object) -> bool:
    if not isinstance(prompt_id, str) or not prompt_id:
        return False
    try:
        return prompt_id in _read(session_id)
    except Exception:
        return False
