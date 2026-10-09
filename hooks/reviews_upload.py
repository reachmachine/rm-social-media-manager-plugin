#!/usr/bin/env python3
"""Uploads the Google reviews dataset the server-named actor produces,
straight from the generic Apify tools' own MCP results (RMP-190, RMP-202).

TOKEN COST, NOT AVOIDANCE (see backend/app/services/business_facts_reviews.
py's module docstring for the server-side half): an MCP tool's result always
lands in the model's context -- there is no path around that. What this
upload-hook pattern buys, same as `website_upload.py` does for `browser_
evaluate`, is that the model never has to RE-EMIT the dataset as another
tool call's arguments (which would double the cost and put the raw data in
the model's own visible output). The hook reads `tool_response` and POSTs it
straight to the server; the model says nothing about it.

RMP-202, TWO STEPS NOT ONE: every actor call now goes through the generic
`call-actor` tool, and Apify's own MCP server source confirms (apify-mcp-
server/src/tools/actors/call_actor.ts + .../actor_run_response.ts) that
`call-actor` returns run metadata -- `{"runId", "status", "storages":
{"datasets": {"default": {"id": ...}}}, "summary", "nextStep", ...}` -- NEVER
the dataset items themselves. A follow-up `get-dataset-items` call (using
that `datasetId`) is what actually returns them, as `{"datasetId", "items":
[...], "itemCount", ...}` (same source, get_dataset_items.ts). So this
module has two handlers, both wired in `tool_result_dispatch.py`:

  `handle_call_actor` -- PostToolUse on `call-actor`. No-op unless a reviews
  fetch is open AND this particular call named the Google-reviews actor;
  when both hold, records the run's dataset id (`reviews_read_state.
  set_dataset_id`) so the next handler can recognise the matching follow-up.

  `handle_dataset_items` -- PostToolUse on `get-dataset-items`. No-op unless
  a reviews fetch is open AND this call's `datasetId` matches the one the
  first handler recorded -- every OTHER dataset the session might separately
  fetch (a different actor's results) is left untouched. Uploads once both
  hold.

PARSING THE RESULT: `_extract_items` tries, in order: the flattened text as
a JSON array directly (an older/alternate shape, kept for tolerance), a JSON
object with an `items` list (the real `get-dataset-items` shape, confirmed
from source above), then the outermost `[` ... `]` slice inside the text
(covers a result wrapped in prose or a markdown fence) -- same tolerant-parse
convention as the server's own `business_facts_reviews_save.parse_dataset_
items`. Any other shape is silently skipped, never uploaded, never logged as
an error, same fail-safe convention as `website_upload.py`.

FAIL-SAFE: never raises, never blocks the tool call, never logs the upload
key or any review text -- only the outcome status.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

import connection_state as cs
import plugin_api
import reviews_read_state as rrs
import state_file_io
import transcript_cursor as tc

# RMP-202: the actor id itself, not a tool name -- `call-actor`'s `actor`
# input field is a plain string, no name-mangling (the "org/slug" -> "org--
# slug" conversion RMP-190 used to need was Apify's PER-ACTOR-TOOL naming
# convention, which no longer applies once every call goes through one
# shared generic tool). Must match `GOOGLE_REVIEWS_APIFY_ACTOR` in backend/
# app/core/config/business_facts.py -- the server names this same id in
# `start_reviews_fetch`'s `run_input["actor"]`.
GOOGLE_REVIEWS_ACTOR_ID = "compass/google-maps-reviews-scraper"

_LOG_FILENAME = "reviews_upload.log"
_LOG_MAX_LINES = 200
_TIMEOUT_S = 8.0
_UPLOAD_PATH = "/api/v1/plugin/google-reviews"
_MAX_ITEMS = 50


def _log(session_id: str, status: str) -> None:
    """One local debug line per attempt -- time, session id, status. NEVER
    the upload key or any review text. Capped at `_LOG_MAX_LINES` (trim the
    oldest), same convention as `website_upload._log`. Never raises."""
    ts = datetime.now(timezone.utc).isoformat()
    state_file_io.append_trimmed_line(tc.transcripts_dir() / _LOG_FILENAME, f"{ts} session={session_id} status={status}", _LOG_MAX_LINES)


def _extract_items(tool_response: Any) -> list[dict[str, Any]] | None:
    """A JSON array of dataset items out of the tool's flattened text, or
    `None` for anything that is not one. Tries a bare array, then a `{...,
    "items": [...]}` object (the real `get-dataset-items` shape, module
    docstring), then the outermost `[`...`]` slice as a last resort."""
    text = cs.flatten_response_text(tool_response)
    if not text:
        return None
    try:
        data = json.loads(text)
    except Exception:
        data = None
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        items = data.get("items")
        if isinstance(items, list):
            return items
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        data = json.loads(text[start:end + 1])
    except Exception:
        return None
    return data if isinstance(data, list) else None


def _run_response_dataset_id(tool_response: Any) -> str | None:
    """`storages.datasets.default.id` out of a `call-actor` RunResponse
    (module docstring). `None` for anything not shaped that way -- the exact
    wire shape has never been captured live (CLAUDE.md forbids a live plugin
    check), so this degrades to "no dataset id" rather than guessing."""
    text = cs.flatten_response_text(tool_response)
    if not text:
        return None
    try:
        data = json.loads(text)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    datasets = (data.get("storages") or {}).get("datasets")
    if not isinstance(datasets, dict):
        return None
    default = datasets.get("default")
    if not isinstance(default, dict):
        return None
    dataset_id = default.get("id")
    return dataset_id if isinstance(dataset_id, str) and dataset_id else None


def handle_call_actor(session_id: str, payload: dict) -> None:
    """`PostToolUse` on the generic `call-actor` tool (RMP-202). No-op
    unless a reviews fetch is open for this session AND this particular
    call named the Google-reviews actor -- every other actor `call-actor`
    might run (today, none; later, whatever a future flow adds) is left
    untouched. Records the run's dataset id for `handle_dataset_items`."""
    if rrs.open_fetch(session_id) is None:
        return
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict) or tool_input.get("actor") != GOOGLE_REVIEWS_ACTOR_ID:
        return
    dataset_id = _run_response_dataset_id(payload.get("tool_response"))
    if dataset_id:
        rrs.set_dataset_id(session_id, dataset_id)


def _post(session_id: str, fetch_id: str, upload_key: str, items: list[dict[str, Any]]) -> None:
    """One POST, the whole dataset (capped). Never raises -- every failure is
    logged and swallowed (module docstring). Break: remove this try/except
    and let the exception escape -> RED (Rule 3 test)."""
    api_url = plugin_api.api_url(_UPLOAD_PATH, "RM_GOOGLE_REVIEWS_API_URL")
    body = json.dumps({"fetch_id": fetch_id, "items": items[:_MAX_ITEMS]}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-RM-Upload-Key": upload_key,
        # RMP-57: Cloudflare blocks urllib's default "Python-urllib/3.x".
        "User-Agent": plugin_api.user_agent(),
    }
    request = urllib.request.Request(api_url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT_S) as resp:
            resp.read()
            _log(session_id, "sent")
    except urllib.error.HTTPError as exc:
        _log(session_id, f"http_{exc.code}")
    except Exception as exc:
        _log(session_id, f"error_{type(exc).__name__}")


def handle_dataset_items(session_id: str, payload: dict) -> None:
    """`PostToolUse` on `get-dataset-items` (RMP-202). No-op unless a
    reviews fetch is open, `handle_call_actor` recorded a pending dataset
    id for it, AND this call's `datasetId` matches that exact id -- any
    other dataset fetch this session makes is left untouched.

    RMP-25 (S6-B3): a genuinely EMPTY dataset (`items == []`, no Google
    Business listing found, or a listing with zero reviews) is now uploaded
    same as a non-empty one -- only `_extract_items` returning `None`
    (garbage, not a real parsed-JSON-array result at all) is skipped. Before
    this, `if not items:` treated the two exactly the same way, so the
    server never learned a fetch had genuinely completed with nothing to
    show -- `business_facts_reviews_save.save_sidecar` is the one place
    that tells "no listing" (permanent) apart from a real parse failure.
    Rule 3 break: revert to `if not items:` -> RED (a genuinely empty
    dataset would stop uploading again)."""
    fetch_id = rrs.open_fetch(session_id)
    if fetch_id is None:
        return
    pending = rrs.pending_dataset_id(session_id)
    if pending is None:
        return
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict) or tool_input.get("datasetId") != pending:
        return
    items = _extract_items(payload.get("tool_response"))
    if items is None:
        return
    upload_key = tc.read_cursor(session_id).get("upload_key")
    if not isinstance(upload_key, str) or not upload_key:
        return
    _post(session_id, fetch_id, upload_key, items)
