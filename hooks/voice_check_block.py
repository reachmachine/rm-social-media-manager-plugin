#!/usr/bin/env python3
"""RMP-159 part 5 (2026-09-26): "Block and rewrite" for a genuine internal-
name leak. Founder decision (QUESTIONS-FOR-FOUNDER-PART5 item 5): when the
`Stop` checker finds a leaked INTERNAL name (a `voice/jargon.json`
`internal_terms` row -- a tool name, or a field key like `revenue_model`,
`revenue_description`, `account_owner_type`), the AI must rewrite that
reply, not just get a note on the next turn.

RMP-159 part 6 (2026-09-26): a live test of part 5 found the block does not
achieve its goal -- the customer had ALREADY seen the leaked line before
`Stop` fires (Claude Code streams text as it's written; a `Stop` hook can
only affect what the model writes NEXT, never un-show what is already on
screen), and the forced rewrite costs one whole extra model turn per leak
for no visible benefit. Founder's call: turn the block off by default and
fix the actual leaks at their source (server-side `say` lines, skill
wording) instead -- see the individual skill files and
`backend/app/services/creator_brief_field_rules.py`. THE CODE STAYS: a
single switch, `BLOCK_LEAKS_ENV`, gates the whole decision so this can be
re-enabled later without rebuilding it. Everything below this switch
(`first_blockable_leak`, the loop guard) is dormant while it is off, but
must keep working the moment it is turned back on -- do not delete it.

Split out of `voice_check.py` (already at the 300-line cap) and out of
`voice_check_internal.py` (the raw-hit scanner) on purpose -- this module
owns ONE decision: block or don't, and how to say so.

SCOPE (while re-enabled). Only a genuine internal name/field/tool leak
blocks. The RMP-159 parts 2-4 narration markers ("now checking", "closing
the browser", "so I need to ask", ...) are `kind == "internal"` too (same
jargon.json list, same checker), but the founder scoped the block to real
internal-name leaks only ("generic 'doing it now' narration stays log-only
unless it contains an internal term") -- those rows carry `"block": false`
in jargon.json, and `voice_check_internal.internal_term_hits_in_line`
already turned that into each problem's `leak` flag. Plain jargon
(`avoid_terms`) and paragraph-length problems never block either,
unchanged from RMP-49.

HOW THE BLOCK WORKS. Claude Code's `Stop` hook can print
`{"decision": "block", "reason": "..."}` on stdout: the model then keeps
going and writes a NEW reply, using `reason` as its instruction. It cannot
un-show text already on screen -- this is a forced correction for what the
model says NEXT, not an edit of what it already said. The reason is
deliberately ONE short line (it goes straight into the model's context on
every leak): which term leaked, plus "rewrite in plain words, don't
mention it" -- no explanation, no repeat of the leaked sentence.

LOOP GUARD, two layers, both must agree to skip re-blocking:
  1. `stop_hook_active` (the payload's own field, true when Claude Code is
     ALREADY continuing because of an earlier Stop-hook block this turn) --
     the primary guard, needs no state of ours.
  2. A backup for when `stop_hook_active` is absent/false for any reason:
     `mark_blocked` stamps `voice_blocked_prompt` with this turn's
     `prompt_id` in the session state the moment we block; `should_block`
     refuses to block again for the SAME `prompt_id`. Needed because a
     forced continuation's transcript still contains the original leaked
     text block (the synthetic block-reason line is not a REAL customer
     message, so `voice_check_transcript`'s boundary never moves past it)
     -- without a guard, the SAME leak would be found and re-blocked on
     every subsequent `Stop` of the same turn, forever.
A second leak inside the rewrite itself is logged (`blocked=False`) like
any other miss, not blocked a second time -- at most one forced rewrite
per turn.
"""
from __future__ import annotations

import os
from typing import Any

import connection_state as cs

_BLOCKED_PROMPT_KEY = "voice_blocked_prompt"

# RMP-159 part 6: off by default -- set to "1"/"true"/"yes" (any case) to
# turn the block back on. Read at call time (not cached at import), so a
# test can flip it with `monkeypatch.setenv` in the same process AND a
# subprocess test (`run_hook`'s `env = dict(os.environ)` already forwards
# whatever the parent test process has set).
BLOCK_LEAKS_ENV = "RM_VOICE_BLOCK_LEAKS_ENABLED"


def blocking_enabled() -> bool:
    return os.environ.get(BLOCK_LEAKS_ENV, "").strip().lower() in {"1", "true", "yes"}


def first_blockable_leak(problems: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The first problem that is a genuine internal-name leak (`kind ==
    "internal"` AND `leak` is true) -- `None` if there is none."""
    for problem in problems:
        if problem.get("kind") == "internal" and problem.get("leak"):
            return problem
    return None


def format_block_reason(problem: dict[str, Any]) -> str:
    """One short line: which term leaked, and the fix. Token-optimal on
    purpose -- no explanation, no repeat of the leaked sentence."""
    term = problem.get("term") or "an internal term"
    return f'You said "{term}" -- rewrite that line in plain words, do not mention it.'


def should_block(payload: dict[str, Any], problems: list[dict[str, Any]], session_id: str) -> dict[str, Any] | None:
    """The problem to block on, or `None` to fall through to the normal
    log-only path. Never blocks a second time for the same turn (see the
    module docstring's two-layer loop guard). RMP-159 part 6: returns
    `None` unconditionally unless `BLOCK_LEAKS_ENV` is on -- the default,
    now, is always log-only."""
    if not blocking_enabled():
        return None
    if payload.get("stop_hook_active") is True:
        return None
    leak = first_blockable_leak(problems)
    if leak is None:
        return None
    prompt_id = payload.get("prompt_id")
    if prompt_id is not None:
        try:
            if cs.read_raw(session_id).get(_BLOCKED_PROMPT_KEY) == prompt_id:
                return None
        except Exception:
            pass
    return leak


def mark_blocked(session_id: str, prompt_id: Any) -> None:
    """Records that this exact turn already forced one rewrite (see
    `should_block`'s backup guard). Never raises."""
    if prompt_id is None:
        return
    try:
        cs.write_patch(session_id, {_BLOCKED_PROMPT_KEY: prompt_id})
    except Exception:
        pass
