#!/usr/bin/env python3
"""Step 7's "is a customer file upload open right now" state (RMP-194 part 4).

Same shape as `website_read_state.py`: one raw key
(`customer_upload`), read/written through `connection_state.read_raw`/
`write_patch`, kept out of `step_state`'s asserted shape.

Callers: `customer_upload_dispatch.py` (writes `handle_start`/`handle_get_
done` from the record entry), `customer_file_upload.py` (reads `open_upload`/
`last_prompt`, writes `record_active_path` on a real send), and
`customer_upload_gate.py` (reads `active_path`).

Also holds `last_prompt` -- the customer's own last typed message, captured
by `capture_last_prompt.py`'s own UserPromptSubmit hook. This did NOT exist
before RMP-194: no earlier hook persisted a prompt's text across calls (only
`step_recorder.handle_typed_answer` reads `payload["prompt"]` live, within
the SAME UserPromptSubmit invocation). `customer_file_upload.py`'s path-in-
last-prompt guard needs it from a LATER, different hook call
(`send_customer_files`'s PostToolUse), so it has to be saved somewhere in
between -- this is that somewhere.

`last_prompt` gets its OWN file (`_last_prompt_path`), NOT a key inside
`connection_state`'s shared JSON file. Claude Code runs every hook matching
one event in parallel, and `connection_state.write_patch` is a read-merge-
write of ONE file -- `capture_last_prompt.py` (this ticket's new
UserPromptSubmit hook) now runs alongside `connection-reminder.sh` on every
single turn, and that script's own `step_recorder.handle_typed_answer` also
writes state on some turns (steps 2-5's typed-answer capture). Two hooks
racing a read-merge-write of the SAME file can silently drop whichever
wrote first -- a real "customer typed the path but the guard says not_typed"
bug, found in review. A dedicated file has exactly one writer, so there is
nothing to race.

FAIL-SAFE: nothing here may crash a hook -- every function degrades to its
safe default instead of raising, same convention as every sibling module.
"""
from __future__ import annotations

import json
import os
import pathlib
from typing import Any

import connection_state as cs
import state_file_io
from payload_util import tool_args

_STATE_KEY = "customer_upload"
# Bound how much of a prompt we keep -- a path is always short; this is just
# a sane ceiling against a customer pasting something huge.
_MAX_PROMPT_CHARS = 4000


def _last_prompt_path(session_id: str) -> pathlib.Path:
    """Same TMPDIR convention as `connection_state.state_path`, but its OWN
    file -- see the module docstring for why this must not share a file with
    any other writer."""
    tmp_dir = os.environ.get("TMPDIR") or "/tmp"
    return pathlib.Path(tmp_dir) / f"rm-plugin-v2-last-prompt-{session_id}.txt"


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def open_upload(session_id: str) -> dict[str, Any] | None:
    """`{"upload_id": str, "purpose": str, "topic": str|None, "refusals":
    dict}` for this session's open upload, or `None` once cleared, never
    started, or the state is corrupt."""
    raw = cs.read_raw(session_id).get(_STATE_KEY)
    if not isinstance(raw, dict):
        return None
    upload_id = raw.get("upload_id")
    if not isinstance(upload_id, str) or not upload_id:
        return None
    return raw


def handle_start(session_id: str, payload: dict) -> None:
    """`PostToolUse` on `start_customer_upload`: saves `upload_id`,
    `purpose`, `topic`, and the server-written `refusals` lines (RMP-76: the
    plugin only executes, never invents its own refusal wording)."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    upload_id = data.get("upload_id")
    if not isinstance(upload_id, str) or not upload_id:
        return
    args = tool_args(payload)
    refusals = data.get("refusals")
    cs.write_patch(session_id, {_STATE_KEY: {
        "upload_id": upload_id,
        "purpose": args.get("purpose"),
        "topic": args.get("topic"),
        "refusals": refusals if isinstance(refusals, dict) else {},
    }})


def handle_get_done(session_id: str, payload: dict) -> None:
    """`PostToolUse` on `get_customer_upload`: once the row is `done`,
    `failed`, or `not_found`, this upload is no longer "open" -- clears the
    gate and lets a later `start_customer_upload` open a fresh one."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    if data.get("status") in ("done", "failed", "not_found"):
        cs.write_patch(session_id, {_STATE_KEY: None})


def record_active_path(session_id: str, raw_path: str) -> None:
    """The path a REAL send just started for (guard already passed) --
    `customer_upload_gate.py` reads this back to deny `Read`/`Bash`/`Glob` on
    the same path while it is "sent for you, don't open it". No-op if no
    upload is open (a stale/late call can never invent one)."""
    current = open_upload(session_id)
    if current is None:
        return
    updated = dict(current)
    updated["active_path"] = raw_path
    cs.write_patch(session_id, {_STATE_KEY: updated})


def active_path(session_id: str) -> str | None:
    upload = open_upload(session_id)
    if upload is None:
        return None
    raw = upload.get("active_path")
    return raw if isinstance(raw, str) and raw else None


def _prompt_count_path(session_id: str) -> pathlib.Path:
    return _last_prompt_path(session_id).with_name(f"rm-plugin-v2-last-prompt-count-{session_id}.txt")


def prompt_count(session_id: str) -> int:
    """How many real typed messages this chat has had (RMP-281 P2260): lets a later hook ask "was anything typed AFTER
    point X?" without comparing clocks. One writer only (the UserPromptSubmit hook), so no lock is needed."""
    try:
        return int(_prompt_count_path(session_id).read_text(encoding="utf-8").strip() or 0)
    except Exception:
        return 0


def record_last_prompt(session_id: str, prompt_text: str) -> None:
    if not isinstance(prompt_text, str):
        return
    try:
        state_file_io.write_atomic(_last_prompt_path(session_id), prompt_text[:_MAX_PROMPT_CHARS])
        state_file_io.write_atomic(_prompt_count_path(session_id), str(prompt_count(session_id) + 1))
    except Exception:
        pass


def last_prompt(session_id: str) -> str:
    try:
        return _last_prompt_path(session_id).read_text(encoding="utf-8")
    except Exception:
        return ""
