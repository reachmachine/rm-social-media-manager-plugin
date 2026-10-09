#!/usr/bin/env python3
"""PostToolUse: marks the plan cache dirty (RMP-201 P4, design doc §3: "sets
a local `plan_dirty` flag, so the next prompt refreshes without a network
call").

BROAD ON PURPOSE. Design names `report_job` explicitly (it fires inside the
subagent), but any real save tool (`update_creator_brief`, `add_to_
watchlist`, `answer_business_review`, `save_business_facts`, `start_
reviews_fetch`, `finish_reviews_fetch`, ...) already calls the backend's own
`planner.notify` too (RMP-201 P2) -- the plugin has no cheap way to know
WHICH of those actually changed the plan, so marking dirty after ANY
Reach-Machine-family tool call is the safe direction: at worst, one harmless
extra `next_actions` call (free, no credits) slips past the repeat-call
guard; the harmful direction (denying a `next_actions` call after something
really did change) never happens.

EXCLUDES `next_actions`/`open_workspace`/`get_resume_checklist` -- those are
`plan_recorder.py`'s job (it CLEARS dirty, right after this same tool call).
Both hooks are wired to overlapping `hooks.json` matchers (see that file's
own comment); the suffix check below is what keeps them from fighting over
the same field on the same call."""
from __future__ import annotations

import json
import sys
from typing import Any

import plan_cache
import plan_recorder

_CLEARS_DIRTY = ("__next_actions", "__open_workspace", "__get_resume_checklist")


def handle(session_id: str, tool_name: Any, tool_response: Any = None) -> None:
    """Never raises. A response that carries a fresh plan (RMP-197 round 10b: the server just
    moved the plan and handed it over) is `plan_recorder.py`'s to record; marking it dirty
    here would undo that and bring back the "Call next_actions once" bounce."""
    if not isinstance(tool_name, str):
        return
    if any(tool_name.endswith(suffix) for suffix in _CLEARS_DIRTY):
        return
    try:
        if tool_response is not None and plan_recorder.embeds_plan(tool_response):
            return
    except Exception:
        pass
    try:
        plan_cache.mark_dirty(session_id)
    except Exception:
        pass


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    session_id = payload.get("session_id")
    if isinstance(session_id, str) and session_id:
        handle(session_id, payload.get("tool_name"), payload.get("tool_response"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
