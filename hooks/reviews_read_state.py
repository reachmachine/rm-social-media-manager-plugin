#!/usr/bin/env python3
"""Step 6's "is a Google reviews fetch open right now" state (RMP-190,
RMP-202).

Mirrors `website_read_state.py`'s pattern for website reads, much smaller:
there is no navigate URL to police, just an open `fetch_id` or none. Callers:
`tool_result_dispatch.py` (`handle_start`/`handle_finish` from the `start_
reviews_fetch`/`finish_reviews_fetch` record entries), and `reviews_upload.
py` (reads `open_fetch` before uploading a dataset, and `set_dataset_id`/
`pending_dataset_id` for the RMP-202 two-step flow below).

STATE: one raw key, `reviews_fetch`, read/written straight through
`connection_state.read_raw`/`write_patch` -- same pattern `website_read_
state.py` uses for `website_read`. Shape: `{"fetch_id": str, "dataset_id":
str}` while a fetch is open (`dataset_id` absent until `set_dataset_id` is
called), or the key absent/None once cleared or never started. A missing or
corrupt value reads as "no fetch open", never a crash.

RMP-202: the generic `call-actor` tool returns a run's dataset id, not its
items -- a follow-up `get-dataset-items` call is required (`reviews_upload.
py`'s module docstring). `set_dataset_id`/`pending_dataset_id` let the
upload hook tell THAT ONE follow-up apart from any other dataset fetch the
session might separately make.

FAIL-SAFE: nothing here may crash a hook, same convention as every sibling
module -- every function degrades to its safe default instead of raising.
"""
from __future__ import annotations

import json
from typing import Any

import connection_state as cs

_STATE_KEY = "reviews_fetch"
# RMP-194: separate raw key from `_STATE_KEY` above (module docstring's own
# "one raw key" pattern) -- whether section 8 has been REACHED this session
# at all, regardless of `available` true/false or whether a fetch ever
# opened. `step_recorder_website.website_tick_ready` reads this to hold
# step 6's own tick until the your-website skill's reviews question has had
# its turn.
_CONSENT_ASKED_KEY = "reviews_consent_asked"


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def open_fetch(session_id: str) -> str | None:
    """The open fetch_id for this session, or `None` once cleared, never
    started, or the state is corrupt."""
    raw = cs.read_raw(session_id).get(_STATE_KEY)
    if not isinstance(raw, dict):
        return None
    fetch_id = raw.get("fetch_id")
    return fetch_id if isinstance(fetch_id, str) and fetch_id else None


def handle_start(session_id: str, payload: dict) -> None:
    """`PostToolUse` on `start_reviews_fetch`: save `fetch_id` from the JSON
    result. A `{"available": false, ...}` result, or a malformed one, leaves
    any prior open fetch untouched -- it never manufactures a fetch out of a
    response that did not actually start one."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None or data.get("available") is False:
        return
    fetch_id = data.get("fetch_id")
    if isinstance(fetch_id, str) and fetch_id:
        cs.write_patch(session_id, {_STATE_KEY: {"fetch_id": fetch_id}})


def handle_finish(session_id: str) -> None:
    """`PostToolUse` on `finish_reviews_fetch`: close the open fetch. hooks.json
    only wires this tool name to `PostToolUse` (never `PostToolUseFailure`),
    so reaching this function already means the call succeeded."""
    cs.write_patch(session_id, {_STATE_KEY: None})


def set_dataset_id(session_id: str, dataset_id: str) -> None:
    """RMP-202: record which dataset the open reviews fetch's `call-actor`
    run produced, so `pending_dataset_id` can match the follow-up `get-
    dataset-items` call to it. No-op when no fetch is open for this session
    -- never manufactures a fetch out of a dataset id alone."""
    raw = cs.read_raw(session_id).get(_STATE_KEY)
    if not isinstance(raw, dict) or not isinstance(raw.get("fetch_id"), str):
        return
    cs.write_patch(session_id, {_STATE_KEY: {**raw, "dataset_id": dataset_id}})


def mark_consent_asked(session_id: str) -> None:
    """RMP-194: called from `tool_result_dispatch._handle_start_reviews_
    fetch` on EVERY `start_reviews_fetch` result, whatever it answers --
    the skill's section 8 always calls this tool once reached (module
    docstring, `handle_start`'s own "whatever it answers" convention), so
    merely being called is the one true signal section 8 has run this
    session."""
    cs.write_patch(session_id, {_CONSENT_ASKED_KEY: True})


def consent_asked(session_id: str) -> bool:
    """True once `mark_consent_asked` has run this session, else False --
    never raises on a missing/corrupt value."""
    return cs.read_raw(session_id).get(_CONSENT_ASKED_KEY) is True


def pending_dataset_id(session_id: str) -> str | None:
    """The dataset id `set_dataset_id` recorded for this session's open
    fetch, or `None` once cleared, never set, or the state is corrupt."""
    raw = cs.read_raw(session_id).get(_STATE_KEY)
    if not isinstance(raw, dict):
        return None
    dataset_id = raw.get("dataset_id")
    return dataset_id if isinstance(dataset_id, str) and dataset_id else None
