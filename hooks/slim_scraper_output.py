#!/usr/bin/env python3
"""Short model copies of the big scraper results a step 10 background job never needs to re-read (RMP-280).

Every tool result stays in the job's context and is paid for again on every later call. The rows of
`get-dataset-items` (about 5 KB a page) and the run objects of `call-actor` / `get-actor-run` (about 3.8 KB
each) are already sent to the server by the upload hooks, which read the ORIGINAL payload, never this copy.
The job only needs the run id, the dataset id, the status and "is there another page".

Same mechanism as `slim_tool_output.py` (RMP-76): the caller prints the text as
`hookSpecificOutput.updatedToolOutput`. Slimming happens ONLY when
  - the call has an `agent_id` (a background job; main-chat calls stay whole), and
  - this job has a recorded run for the matching dataset / Apify run (the state `hangouts_upload` keeps), and
  - for dataset rows: the run says `extract_names` is false (otherwise the job must read the rows).
Any doubt, any parse trouble, any copy that is not shorter -> None (the model sees the full result).
Never raises. Never logs. Never touches state.
"""
from __future__ import annotations

import json
from typing import Any

import connection_state as cs
import hangouts_upload as hu
from payload_util import tool_args

# Kept from a `get-dataset-items` reply: the paging facts the job spec relies on ("No more pages" is in `nextStep`).
_PAGE_KEYS = ("datasetId", "itemCount", "totalItemCount", "offset", "limit", "summary", "nextStep")


def _default_dataset_id(data: dict) -> str | None:
    storages = data.get("storages")
    datasets = storages.get("datasets") if isinstance(storages, dict) else None
    default = datasets.get("default") if isinstance(datasets, dict) else None
    value = default.get("id") if isinstance(default, dict) else None
    return value if isinstance(value, str) and value else None


def _compact(obj: dict) -> str:
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


def slim_text(tool_short_name: str, text: str, *, extract_names: bool | None) -> str | None:
    """The short reply text for one tool, or None to leave the result whole."""
    try:
        data = json.loads(text)
        if not isinstance(data, dict):
            return None
        if tool_short_name == "get-dataset-items":
            if extract_names is not False or not isinstance(data.get("items"), list):
                return None
            out: dict[str, Any] = {k: data[k] for k in _PAGE_KEYS
                                   if isinstance(data.get(k), (str, int)) and not isinstance(data.get(k), bool)}
            out["items_received"] = len(data["items"])
        elif tool_short_name in ("call-actor", "get-actor-run"):
            keep = ("runId", "actorId", "status") if tool_short_name == "call-actor" else ("runId", "status")
            out = {k: data[k] for k in keep if isinstance(data.get(k), str)}
            dataset_id = _default_dataset_id(data)
            if dataset_id:
                out["datasetId"] = dataset_id
            if "runId" not in out or "status" not in out:
                return None
        else:
            return None
        slim = _compact(out)
        return slim if len(slim) < len(text) else None
    except Exception:
        return None


def apify_slim_text(session_id: str, payload: dict, short_name: str) -> str | None:
    """Guarded: the short text for a background job's own scraper result, or None."""
    try:
        agent_id = payload.get("agent_id")
        if not isinstance(agent_id, str) or not agent_id:
            return None
        state = hu._read(session_id, agent_id)
        if not (isinstance(state.get("run_id"), str) and state["run_id"]):
            return None
        text = cs.flatten_response_text(payload.get("tool_response"))
        args = tool_args(payload)
        if short_name == "get-dataset-items":
            dataset_id = state.get("dataset_id")
            # After the final page the upload hook (it runs first) clears `dataset_id`; the Apify run id stays.
            if args.get("datasetId") is None or not (
                dataset_id == args.get("datasetId") or (dataset_id is None and state.get("apify_run_id"))
            ):
                return None
        else:
            tracked = state.get("apify_run_id")
            if not (isinstance(tracked, str) and tracked) or json.loads(text).get("runId") != tracked:
                return None
            if short_name == "get-actor-run" and args.get("runId") != tracked:
                return None
        return slim_text(short_name, text, extract_names=state.get("extract_names"))
    except Exception:
        return None


def websearch_slim(response: Any, link_count: int) -> dict | None:
    """The model's copy of a job's `WebSearch` result: the same dict with `results` cut to one line saying how
    many links the hook sent to the server. The caller checks that this job has an open websearch run."""
    try:
        if not isinstance(response, dict) or not isinstance(response.get("results"), list):
            return None
        line = f"{link_count} links found; they were sent to the server. Nothing more to read."
        slim = {**response, "results": [line]}
        return slim if len(json.dumps(slim)) < len(json.dumps(response)) else None
    except Exception:
        return None
