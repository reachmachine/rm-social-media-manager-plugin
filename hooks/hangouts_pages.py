#!/usr/bin/env python3
"""Pure page helpers for the step 10 upload hook (RMP-218). Split out of `hangouts_upload.py` (P1991) to keep it under
300 lines. No state, no I/O: `hangouts_upload` re-exports these names, so `hu.field_names` etc. still work."""
from __future__ import annotations

import json
from typing import Any

import connection_state as cs


def field_names(fields: Any) -> list[str]:
    """The field names of a `fields` value: a comma string ("a, b") or a list. Order kept, blanks dropped."""
    parts = fields if isinstance(fields, list) else (fields.split(",") if isinstance(fields, str) else [])
    return [p.strip() for p in parts if isinstance(p, str) and p.strip()]


def _reply_total(tool_response: Any) -> int | None:
    """The row count Apify's own reply says the whole dataset holds (`totalItemCount`), or None. `itemCount` is
    only the rows on THIS page, so it is never used: offset + itemCount would always look like the end."""
    try:
        data = json.loads(cs.flatten_response_text(tool_response))
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    value = data.get("totalItemCount")
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def _page_and_final(args: dict[str, Any], count: int, total: int | None = None,
                    rows_after: int | None = None) -> tuple[int, bool]:
    """(page number, is this the last page). A page is final when it is short or empty, or when the rows
    posted so far (`rows_after`, this page included) reach the reply's own row total (P1858). Never because the
    page "touches the last row": a job that jumps to the last offset has NOT read the rows before it (P1863).
    Without `rows_after` the old offset + count is used (pure callers only)."""
    offset, limit = args.get("offset"), args.get("limit")
    if not (isinstance(limit, int) and not isinstance(limit, bool) and limit > 0):
        return 0, True
    has_offset = isinstance(offset, int) and not isinstance(offset, bool) and offset >= 0
    start = offset if has_offset else 0
    reaches_total = total is not None and (start + count if rows_after is None else rows_after) >= total
    return start // limit, count < limit or reaches_total


def resume_fields(resume: Any) -> dict[str, Any]:
    """P1991: the state a job takes from the server's `resume` block (an Apify run already started for this server
    run). Empty when the block is missing or not whole: a half-trusted block must not seed anything."""
    if not isinstance(resume, dict):
        return {}
    apify_run_id, dataset_id = resume.get("apify_run_id"), resume.get("dataset_id")
    offset, rows = resume.get("next_offset"), resume.get("rows_posted")
    whole = (isinstance(apify_run_id, str) and apify_run_id and isinstance(dataset_id, str) and dataset_id
             and all(isinstance(n, int) and not isinstance(n, bool) and n >= 0 for n in (offset, rows)))
    return ({"apify_run_id": apify_run_id, "dataset_id": dataset_id, "next_offset": offset, "rows_posted": rows}
            if whole else {})
