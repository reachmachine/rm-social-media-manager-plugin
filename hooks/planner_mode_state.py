#!/usr/bin/env python3
"""The one place the plugin remembers `PLANNER_MODE` (RMP-201 P4, design doc
§10 P4 scope line: "the plugin reads the mode from the server response;
`drive` enables it, anything else keeps today's behaviour exactly").

Lives in the SHARED `connection_state.py` file, not the separate plan-cache
file (`plan_cache.py`) -- on purpose. Design §4 G3 says the ordering gate
must fail OPEN when its cache is missing or corrupt, and that has to mean
something different from "mode unknown, behave exactly like today". Keeping
`planner_mode` in the file that survives independently of the plan cache
makes "mode == drive, but the plan cache is gone" a real, distinct,
testable condition -- if both lived in the same file, a missing file would
always read as "mode unknown" and the G3 fail-open path could never be
exercised.

Reset at `SessionStart` for free (`connection_state.reset_state` deletes
the whole file) -- a fresh session starts back at "mode unknown", the same
as every other flag `connection_state.py` owns.
"""
from __future__ import annotations

import connection_state as cs

DRIVE = "drive"

_KNOWN_MODES = frozenset({"off", "shadow", "drive"})


def record_mode(session_id: str, mode: object) -> None:
    """Stores `mode` when it is one of the three values the server can send
    (`app.config.PLANNER_MODE`'s own allowed set). Anything else (missing,
    malformed, a stale plugin talking to a pre-P4 backend) is silently
    ignored -- never invents a mode, never crashes a hook."""
    if isinstance(mode, str) and mode in _KNOWN_MODES:
        cs.write_patch(session_id, {"planner_mode": mode})


def is_drive(session_id: str) -> bool:
    """True only once the LAST response this session actually saw said
    `mode: "drive"`. `False` for `"off"`, `"shadow"`, or never having seen
    one at all -- the safe default that keeps every P4 behaviour dormant
    until the server itself turns the planner on.

    **Rule 3 target.** Change the `==` below to `!=` and every P4 gate/cache/
    guard would activate under `off`/`shadow` (today's default everywhere)
    instead of staying dormant -- `test_planner_mode_state.
    test_rule3_is_drive_only_true_for_the_literal_string` proves this."""
    return cs.read_raw(session_id).get("planner_mode") == DRIVE
