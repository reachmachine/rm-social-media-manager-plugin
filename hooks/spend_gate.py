#!/usr/bin/env python3
"""The spend gate: a human's fresh "yes" is required before any of the six
credit-spending tools may run with `confirm=true` (RMP-23).

Reused from v1 (`.claude/skills/rm-social-media-manager/hooks/
spend-needs-human-yes.sh`) -- the founder's rule is to reuse that logic, not
rewrite it. Spec: `docs/plugin-v2/04-own-instagram-account.md`,
"Enforcement" -> "Spend gate". Called from `step_gate.decide`, LAST, so a
preview is only ever recorded once every other step rule already allowed
the call -- a denied preview must never authorise a later confirm.

CHANGED FROM v1 (full table in `step_gate.py`'s module docstring): one
gate, one state file. State lives under a new key, `spend_previews`, in the
SAME per-session file `connection_state.py`/`step_state.py` share -- read
via `cs.read_raw`/`cs.write_patch` directly, NOT `step_state.read_state`
(that function's shape is exact-equality-asserted in `test_step_state.py`;
a ninth key there would break every one of those tests for no benefit).
A workspace switch (`step_state.reset_for_new_workspace`) clears it too.

v1 FAILED OPEN when `prompt_id`/`session_id` was missing. v2 DENIES a
confirm when unsure: no `prompt_id`, no `session_id`, or a crash here
(caught by `connections_gate.main`'s top-level try/except) all deny a
confirm. A PREVIEW with no `prompt_id` is still allowed (nothing has been
charged), but records nothing, so a later confirm still has no entry to
match. Verified live 2026-09-24: `prompt_id` is on every hook payload on
Claude Code 2.1.281 (capture: `tests/fixtures/captures_step4_2026-09-24.
jsonl`), so this should not affect a real session.

A sub-agent (`agent_id` present) can never confirm -- it has no way to know
whether a human said yes mid-run.
"""
from __future__ import annotations

import hashlib
import json

import connection_state as cs
import deny_lines
import system_prompt_ids

GATED_SUFFIXES: frozenset[str] = frozenset({
    "run_pipeline",
    "run_pipeline_assist",
    "run_pipeline_by_category",
    "pull_data",
    "add_to_watchlist",
    "remove_competitor",
})

_NO_PREVIEW_REASON = "spend_no_preview"
_SAME_TURN_REASON = "spend_same_turn"
_ARGS_MISMATCH_REASON = "spend_args_mismatch"
_BACKGROUND_TASK_REASON = "spend_background_task"
_SUBAGENT_REASON = "spend_subagent"
_UNSURE_REASON = "spend_unsure"


def _deny(reason_id: str, **fill: object) -> dict:
    return deny_lines.deny_id(reason_id, **fill)


def args_hash(args: dict) -> str:
    if not isinstance(args, dict):
        args = {}
    cleaned = {
        key: value
        for key, value in args.items()
        # RMP-23, founder decision 6: `include_flagged` is OWNED by
        # `own_account_mismatch.check_include_flagged`, not this gate -- a
        # customer's yes to a flagged preview must still match its price
        # preview even though `include_flagged` flips False->True between
        # the two calls (the preview is denied outright if it were ever
        # sent True; see that module). RMP-175: `add_anyway` is OWNED by
        # `own_account_not_found.check_add_anyway` the same way -- a "yes"
        # to a not_found preview must still match its price preview even
        # though `add_anyway` flips False->True between the two calls.
        if key not in ("confirm", "dry_run", "preview_fingerprint", "include_flagged", "add_anyway")
    }
    blob = json.dumps(cleaned, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _load_previews(session_id: str) -> dict:
    previews = cs.read_raw(session_id).get("spend_previews")
    if not isinstance(previews, dict):
        return {}
    return {k: v for k, v in previews.items() if isinstance(k, str) and isinstance(v, dict)}


def _save_previews(session_id: str, previews: dict) -> None:
    cs.write_patch(session_id, {"spend_previews": previews})


def decide(payload: dict, tool_input: dict, session_id: str) -> dict | None:
    """None = allow. `tool_input` is the UNWRAPPED args
    (`payload_util.tool_args`). A preview records itself here (only reached
    once every other `step_gate` rule already allowed it); a confirm is
    judged here and, if allowed, its entry is removed -- one yes covers one
    spend."""
    tool_name = payload.get("tool_name")
    if not isinstance(tool_name, str) or cs.server_of(tool_name) != "reachmachine":
        return None
    if tool_name.rsplit("__", 1)[-1] not in GATED_SUFFIXES:
        return None

    if not isinstance(tool_input, dict):
        tool_input = {}
    confirm = tool_input.get("confirm") is True

    agent_id = payload.get("agent_id")
    if confirm and agent_id is not None:
        return _deny(_SUBAGENT_REASON)

    prompt_id = payload.get("prompt_id")
    prompt_id = prompt_id if isinstance(prompt_id, str) and prompt_id else None
    session_id = session_id if isinstance(session_id, str) and session_id else None

    if confirm and (prompt_id is None or session_id is None):
        return _deny(_UNSURE_REASON)

    if session_id is None:
        return None  # a preview with nowhere to record it is still free

    computed_hash = args_hash(tool_input)
    previews = _load_previews(session_id)

    if not confirm:
        if prompt_id is not None:
            entry = previews.get(tool_name)
            if entry is None or entry.get("args_hash") != computed_hash:
                previews[tool_name] = {"prompt_id": prompt_id, "args_hash": computed_hash}
                _save_previews(session_id, previews)
        return None

    if system_prompt_ids.is_system_prompt_id(session_id, prompt_id):
        return _deny(_BACKGROUND_TASK_REASON)  # RMP-24: a notification turn is never a human yes
    entry = previews.get(tool_name)
    if entry is None:
        return _deny(_NO_PREVIEW_REASON)
    if entry.get("prompt_id") == prompt_id:
        return _deny(_SAME_TURN_REASON)
    if entry.get("args_hash") != computed_hash:
        return _deny(_ARGS_MISMATCH_REASON)

    previews.pop(tool_name, None)
    _save_previews(session_id, previews)
    return None
