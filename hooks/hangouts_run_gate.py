#!/usr/bin/env python3
"""PreToolUse rules for a step 10 job's Apify runs (RMP-218, P1853).

Live, `call-actor` did not wait for the scraper: it came back `READY` or `RUNNING`. A Haiku job then (a) called
`call-actor` again with the same input (3 paid runs, 1 counted by the server) and (b) read the dataset while the
scraper was still starting (0 rows, uploaded as the final page, "empty"). Prose in the job steps is not enough, so
the two rules are enforced here, from the record `hangouts_upload.py` keeps per job (`agent_id`):

* `check_call_actor`  -- this job's current server run already started a scraper: deny, point at `get-actor-run`.
* `check_dataset_items` -- the dataset is this job's and its run has not reached a final status: deny.

Both return None (allow) for every call that is not this job's own run, and never raise: a crash here must not
brick an unrelated tool call, so any error allows (the server refuses an unfinished final page anyway).
"""
from __future__ import annotations

import deny_lines
import hangouts_upload as hu

# Apify's MCP server rejects waitSecs above 45 (its WAIT_SECS_MAX); 45 is the longest single wait.
POLL_WAIT_SECS = 45


def _deny(reason_id: str, **fill: object) -> dict:
    return deny_lines.deny_id(reason_id, **fill)   # RMP-291 P2321: the server's words, shown at the hook's exit


def _poll_action(run_id: object) -> str:
    """The one action, as data: which call to make and with what."""
    return f"get-actor-run runId={run_id} waitSecs={POLL_WAIT_SECS}"


def check_call_actor(session_id: str, agent_id: str | None) -> dict | None:
    try:
        apify_run_id = hu._read(session_id, agent_id).get("apify_run_id")
        if isinstance(apify_run_id, str) and apify_run_id:
            return _deny("scraper_started", action=_poll_action(apify_run_id))
    except Exception:
        pass
    return None


def check_dataset_items(tool_input: dict, session_id: str, agent_id: str | None) -> dict | None:
    try:
        state = hu._read(session_id, agent_id)
        dataset_id = state.get("dataset_id")
        if not (isinstance(dataset_id, str) and dataset_id) or tool_input.get("datasetId") != dataset_id:
            return None
        meta = state.get("run_meta")
        status = meta.get("status") if isinstance(meta, dict) else None
        if status in hu.FINAL_STATUSES:
            return _paging_denial(tool_input, state)
        return _deny("scraper_running", action=_poll_action(state.get("apify_run_id", "")))
    except Exception:
        return None


def _paging_denial(tool_input: dict, state: dict) -> dict | None:
    """P1862 + P1863: hold the job to the server's own fields, page size and NEXT offset.

    P1862: a job switched from limit 1 to limit 10, the hook numbered pages `offset // limit`, and the server threw
    44 paid profiles away as duplicates. P1863: with page size 1 every offset is a "multiple", so a Haiku job read
    offsets 0-2, cut `fields` to `username`, then jumped to the last row: 42 paid profiles were never read.

    Fields are compared as an UNORDERED set of names (the server's order is for show, Apify returns the same rows
    either way). Offset must be exactly `next_offset`, the rows already posted."""
    size = state.get("page_size")
    if not (isinstance(size, int) and not isinstance(size, bool) and size > 0):
        return None
    want = hu.field_names(state.get("fields"))
    next_offset = state.get("next_offset")
    next_offset = next_offset if isinstance(next_offset, int) and not isinstance(next_offset, bool) else 0
    fields_ok = not want or set(hu.field_names(tool_input.get("fields"))) == set(want)
    offset = tool_input.get("offset")
    if fields_ok and tool_input.get("limit") == size and isinstance(offset, int) and not isinstance(offset, bool) \
            and offset == next_offset:
        return None
    fields_part = f", fields {','.join(want)}" if want else ""
    return _deny("page_order", action=f"offset {next_offset}, limit {size}{fields_part}")
