#!/usr/bin/env python3
"""Uploads a step 10 ("hangouts") scraper's dataset rows straight from the
Apify tools' own MCP results (RMP-218, P1776). Same idea as
`reviews_upload.py` (read its docstring for WHY a hook uploads instead of the
model re-typing the data) -- but step 10 runs several jobs at once, so every
piece of state here is keyed by the job's `agent_id`.

FOUR HANDLERS, all wired in `tool_result_dispatch.py`; each is a no-op
unless its own state matches, so they can run next to the reviews handlers:

  `handle_work_item` -- PostToolUse on `get_hangouts_work`. Remembers the
  job's `run.run_id` (the server's id for this scraper run) under
  `hangouts_upload:<safe agent_id>`. No `run_id` -> nothing recorded.

  `handle_call_actor` -- PostToolUse on `call-actor`. Only when this job has
  a recorded `run_id` AND the called `actor` is in THIS job's allow-list
  (`apify_actor_allowlist`): records the run's dataset id and a small, fixed
  set of cost/runtime fields (`run_meta`).

  `handle_get_actor_run` -- PostToolUse on `get-actor-run` (P1853). `call-actor`
  does NOT wait for the scraper (live: `READY`/`RUNNING` 8 times in 10). When
  the call's `runId` is this job's recorded Apify run, its newer `status` /
  `finishedAt` / usage replace the stored `run_meta`, so the upload carries
  the FINAL status. `hangouts_run_gate.py` (PreToolUse) uses the same record
  to refuse a second `call-actor` and a read of an unfinished dataset.

  `handle_dataset_items` -- PostToolUse on `get-dataset-items`. Only when the
  call's `datasetId` equals the recorded one: POSTs `{run_id, page, final,
  items, run_meta}` to the server with the `X-RM-Upload-Key` header.

BIG PAGES (P1860): when Claude Code hands over only a note that the page "exceeds maximum allowed tokens ...
saved to <file>", `hangouts_diverted_page.py` reads that file (path checks there) and the page goes the normal way.

PAGING: if the job fetched with `offset`/`limit`, `page = offset // limit`
and `final = len(items) < limit`; otherwise one page, `final = True`. After
the final page the recorded dataset id is cleared, so a re-fetch of the same
dataset cannot post twice.

FAIL-SAFE: never raises, never blocks the tool call, never logs the upload
key or any row content -- only the outcome status. Shapes below come from the
reviews capture (same Apify tools); the step-10 capture is pending.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

import apify_actor_allowlist as aal
import connection_state as cs
import hangouts_diverted_page as hdp
import plugin_api
from hangouts_pages import (  # noqa: F401  (re-exported: tests and the run gate use hu.*)
    _page_and_final, _reply_total, field_names, resume_fields,
)
import reviews_upload as ru
import state_file_io
import transcript_cursor as tc
from payload_util import tool_args

# ONE place for the work tool's suffix (P1778 builds the tool; it confirms the name).
HANGOUTS_WORK_SUFFIX = "__get_hangouts_work"

_STATE_PREFIX = "hangouts_upload"
_LOG_FILENAME = "hangouts_upload.log"
_LOG_MAX_LINES = 200
_TIMEOUT_S = 8.0  # same client timeout as reviews_upload.py
_UPLOAD_PATH = "/api/v1/plugin/hangouts/dataset"
_START_PATH = "/api/v1/plugin/hangouts/run-start"   # P1991: "this Apify run started", sent right after call-actor
# Server limits for this route (P1766): backend HANGOUT_UPLOAD_MAX_ITEMS and
# HANGOUT_UPLOAD_MAX_BYTES. A page is NEVER cut or split (the server de-duplicates
# by (run_id, page)); a page over either limit posts nothing.
_MAX_ITEMS = 5000
_MAX_BYTES = 5_000_000
# Cost/runtime fields copied from the `call-actor` result into `run_meta`.
_RUN_META_FIELDS = (
    "status", "startedAt", "finishedAt", "durationMillis",
    "usageTotalUsd", "usageUsd", "chargedEventCounts", "stats",
)
# The four statuses of a finished Apify run (the server refuses a final page without one).
FINAL_STATUSES = frozenset({"SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"})
_DIVERTED_MARKER = "exceeds maximum allowed tokens"


def _state_key(agent_id: Any) -> str:
    if isinstance(agent_id, str) and agent_id:
        return f"{_STATE_PREFIX}:{aal._safe(agent_id)}"
    return _STATE_PREFIX


def _read(session_id: str, agent_id: Any) -> dict[str, Any]:
    value = cs.read_raw(session_id).get(_state_key(agent_id))
    return value if isinstance(value, dict) else {}


def _log(session_id: str, status: str) -> None:
    ts = datetime.now(timezone.utc).isoformat()
    state_file_io.append_trimmed_line(
        tc.transcripts_dir() / _LOG_FILENAME, f"{ts} session={session_id} status={status}", _LOG_MAX_LINES,
    )


def _json_dict(tool_response: Any) -> dict[str, Any] | None:
    try:
        data = json.loads(cs.flatten_response_text(tool_response))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def handle_work_item(session_id: str, payload: dict) -> None:
    """`PostToolUse` on `get_hangouts_work`. Never raises."""
    try:
        data = _json_dict(payload.get("tool_response"))
        run = data.get("run") if data else None
        run_id = run.get("run_id") if isinstance(run, dict) else None
        if not isinstance(run_id, str) or not run_id:
            return
        resume = resume_fields(data.get("resume"))   # P1991: an Apify run already started for this server run
        known = _read(session_id, payload.get("agent_id"))
        if known.get("run_id") == run_id and (known.get("apify_run_id") or not resume):
            return   # the server hands the SAME open run again: keep what this job already started (P1853)
        record: dict[str, Any] = {"run_id": run_id, **resume}
        dataset = run.get("dataset")
        size = dataset.get("limit") if isinstance(dataset, dict) else None
        if isinstance(size, int) and not isinstance(size, bool) and size > 0:
            record["page_size"] = size   # the server's page size: hangouts_run_gate holds the job to it (P1862)
        fields = dataset.get("fields") if isinstance(dataset, dict) else None
        names = field_names(fields)
        if names:
            record["fields"] = ",".join(names)   # the server's exact fields, in its order (P1863)
        if isinstance(run.get("extract_names"), bool):
            record["extract_names"] = run["extract_names"]   # RMP-280: slim_scraper_output keeps rows whole when true
        cs.write_patch(session_id, {_state_key(payload.get("agent_id")): record})
    except Exception:
        pass


def _run_meta(tool_response: Any) -> dict[str, Any]:
    data = _json_dict(tool_response) or {}
    return {k: data[k] for k in _RUN_META_FIELDS if k in data}


def handle_call_actor(session_id: str, payload: dict) -> None:
    """`PostToolUse` on `call-actor`. Never raises."""
    try:
        agent_id = payload.get("agent_id")
        state = _read(session_id, agent_id)
        run_id = state.get("run_id")
        if not isinstance(run_id, str) or not run_id:
            return
        actor = tool_args(payload).get("actor")
        if not isinstance(actor, str) or actor not in aal.allowed_actor_ids(session_id, agent_id):
            return
        dataset_id = ru._run_response_dataset_id(payload.get("tool_response"))
        if not dataset_id:
            return
        apify_run_id = (_json_dict(payload.get("tool_response")) or {}).get("runId")
        record = {"run_id": run_id, "dataset_id": dataset_id, "run_meta": _run_meta(payload.get("tool_response"))}
        if isinstance(apify_run_id, str) and apify_run_id:
            record["apify_run_id"] = apify_run_id
        for key in ("page_size", "fields", "next_offset", "rows_posted", "extract_names"):
            if key in state:
                record[key] = state[key]
        cs.write_patch(session_id, {_state_key(agent_id): record})
        if "apify_run_id" in record:   # P1991: tell the server, so a restarted job resumes this run and never pays twice
            key = tc.read_cursor(session_id).get("upload_key")
            if isinstance(key, str) and key:
                _post(session_id, key, {"run_id": run_id, "apify_run_id": record["apify_run_id"],
                                        "dataset_id": dataset_id}, _START_PATH)
    except Exception:
        pass


def handle_get_actor_run(session_id: str, payload: dict) -> None:
    """`PostToolUse` on `get-actor-run` (P1853). No-op unless the `runId` is the one this job's `call-actor`
    started. Newer fields replace the stored ones; a field the result lacks never erases a stored one
    (usage often arrives only once the run is finished). Never raises."""
    try:
        agent_id = payload.get("agent_id")
        state = _read(session_id, agent_id)
        tracked = state.get("apify_run_id")
        if not (isinstance(tracked, str) and tracked) or tool_args(payload).get("runId") != tracked:
            return
        fresh = _run_meta(payload.get("tool_response"))
        if not isinstance(fresh.get("status"), str):
            return
        old = state.get("run_meta")
        merged = {**(old if isinstance(old, dict) else {}), **fresh}
        cs.write_patch(session_id, {_state_key(agent_id): {**state, "run_meta": merged}})
    except Exception:
        pass


def _api_url(path: str) -> str:
    """The server URL for `path`. Tests set RM_HANGOUTS_API_URL to a local fake server's URL: the other route
    is then that same server with `path` swapped in (never the real dev host from a unit test)."""
    override = os.environ.get("RM_HANGOUTS_API_URL")
    if override and path != _UPLOAD_PATH:
        return urllib.parse.urlunsplit(urllib.parse.urlsplit(override)._replace(path=path))
    return plugin_api.api_url(path, "RM_HANGOUTS_API_URL")


def _post(session_id: str, upload_key: str, body: dict[str, Any], path: str = _UPLOAD_PATH) -> bool:
    """One POST. Never raises -- every failure is logged (status only) and
    swallowed. Break: let the exception escape -> RED (Rule 3 test)."""
    api_url = _api_url(path)
    headers = {
        "Content-Type": "application/json",
        "X-RM-Upload-Key": upload_key,
        "User-Agent": plugin_api.user_agent(),
    }
    request = urllib.request.Request(api_url, data=json.dumps(body).encode("utf-8"), method="POST", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT_S) as resp:
            resp.read()
            _log(session_id, "sent")
            return True
    except urllib.error.HTTPError as exc:
        _log(session_id, f"http_{exc.code}")
    except Exception as exc:
        _log(session_id, f"error_{type(exc).__name__}")
    return False


def handle_dataset_items(session_id: str, payload: dict) -> None:
    """`PostToolUse` on `get-dataset-items`. Never raises."""
    try:
        agent_id = payload.get("agent_id")
        state = _read(session_id, agent_id)
        run_id, dataset_id = state.get("run_id"), state.get("dataset_id")
        if not (isinstance(run_id, str) and run_id and isinstance(dataset_id, str) and dataset_id):
            return
        args = tool_args(payload)
        if args.get("datasetId") != dataset_id:
            return
        reply = payload.get("tool_response")
        items = ru._extract_items(reply)
        if items is None:
            note = cs.flatten_response_text(reply)
            if _DIVERTED_MARKER not in note:
                return
            # Too big for the tool result (P1860): Claude Code saved the page to a file. Read it if the path is safe.
            reply = hdp.read_diverted_page(note, _MAX_BYTES)
            items = ru._extract_items(reply) if reply else None
            if items is None:
                _log(session_id, f"page_diverted run={run_id}")   # nothing is posted
                return
        upload_key = tc.read_cursor(session_id).get("upload_key")
        if not isinstance(upload_key, str) or not upload_key:
            return
        total = _reply_total(reply)
        rows_after = int(state.get("rows_posted") or 0) + len(items)
        page, final = _page_and_final(args, len(items), total, rows_after)
        meta = state.get("run_meta")
        if len(items) > _MAX_ITEMS:
            _log(session_id, f"page_too_large items={len(items)}")
            return
        body = {
            "run_id": run_id, "page": page, "final": final,
            "items": items, "run_meta": meta if isinstance(meta, dict) else {},
        }
        if total is not None:
            body["total_rows"] = total   # the server refuses a final page that has seen fewer rows (P1863)
        size = len(json.dumps(body).encode("utf-8"))
        if size > _MAX_BYTES:
            _log(session_id, f"page_too_large bytes={size}")
            return
        sent = _post(session_id, upload_key, body)
        if sent and not final:
            # P1863: the next read must start where this one ended (hangouts_run_gate checks it).
            nxt = int(state.get("next_offset") or 0) + len(items)
            cs.write_patch(session_id, {_state_key(agent_id): {**state, "next_offset": nxt, "rows_posted": rows_after}})
        if final:
            # Keep the Apify run id: a second call-actor for this run is still refused (hangouts_run_gate).
            done: dict[str, Any] = {"run_id": run_id}
            if isinstance(state.get("apify_run_id"), str):
                done["apify_run_id"] = state["apify_run_id"]
            if isinstance(state.get("extract_names"), bool):
                done["extract_names"] = state["extract_names"]   # RMP-280: the slim hook runs AFTER this clears the dataset id
            cs.write_patch(session_id, {_state_key(agent_id): done})
    except Exception:
        pass
