#!/usr/bin/env python3
"""Step 6's "is a website read open right now" state (RMP-66).

Spec: docs/plugin-v2/06-website-and-business-knowledge.md, "Wave 2 design",
"Reading the site (plugin)". Three callers: `connection_state_cli.py`
(writes `handle_start`/`handle_finish` from the record entry -- NOT
`step_recorder.py`'s table, which P1668 owns), `website_upload.py` (reads
`open_read`/`same_site` before uploading a page), and `website_gate.py`
(reads the same two before allowing/denying a navigate).

STATE: one raw key, `website_read`, read/written straight through
`connection_state.read_raw`/`write_patch` -- same "kept out of
`step_state`'s asserted shape" pattern `step_recorder_revenue.py` uses for
`revenue_progress`. Shape: `{"read_id": str, "host": str}` while a read is
open, or the key absent/None once cleared. A missing, corrupt, or
wrong-shaped value reads as "no read open" (`open_read` returns `None`),
never a crash.

`start_website_read`'s JSON result carries `read_id` and `host` (the
normalized site host the backend computed) -- `handle_start` saves both
verbatim; the plugin never re-derives the host itself, so it can never
disagree with the server about what "same site" means.

FAIL-SAFE: nothing here may crash a hook, same convention as every sibling
module -- every function degrades to its safe default instead of raising.
"""
from __future__ import annotations

import json
from typing import Any
from urllib.parse import urlsplit

import connection_state as cs

_STATE_KEY = "website_read"
# RMP-179: the url a `browser_navigate` call was actually SENT, before any
# redirect the site itself makes -- separate key from `_STATE_KEY` so a
# malformed/missing value here can never affect `open_read`'s own shape.
_LAST_NAV_KEY = "website_last_navigate"
# RMP-184: how many times THIS session has navigated to each url within the
# CURRENT read -- separate key, same reason as `_LAST_NAV_KEY` above.
_ATTEMPTS_KEY = "website_navigate_attempts"
# The server decides this number (founder rule: the plugin only executes) and
# hands it back on `start_website_read` -- this is only the fallback for a
# server response from before that field existed.
DEFAULT_MAX_ATTEMPTS = 2
# Most sibling hosts remembered per read (a long list is not a real site).
MAX_ALLOWED_HOSTS = 10


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _normalize_host(host: str) -> str:
    host = host.strip().lower()
    if host.startswith("www."):
        host = host[len("www."):]
    return host


def same_site(url: Any, host: Any, allowed_hosts: Any = ()) -> bool:
    """True when `url`'s host matches `host` (`www.` and no-`www.` count as
    the same site), or one of `allowed_hosts` -- the hosts the SERVER listed
    in `browser_pages` (RMP-281: `book.brand.com` for a customer on
    `brand.com`; the server, not this plugin, decides what "same site"
    means). False for anything malformed, non-http(s), or with no hostname
    at all -- never raises."""
    if not isinstance(url, str) or not url or not isinstance(host, str) or not host:
        return False
    try:
        parsed = urlsplit(url)
    except Exception:
        return False
    if parsed.scheme not in ("http", "https"):
        return False
    if not parsed.hostname:
        return False
    wanted = {_normalize_host(host)}
    if isinstance(allowed_hosts, (list, tuple)):
        wanted.update(_normalize_host(h) for h in allowed_hosts if isinstance(h, str) and h)
    return _normalize_host(parsed.hostname) in wanted


def open_read(session_id: str) -> dict[str, Any] | None:
    """`{"read_id": str, "host": str, "max_attempts": int}` for this
    session's open read, or `None` once cleared, never started, or the state
    is corrupt. `max_attempts` (RMP-184) falls back to `DEFAULT_MAX_ATTEMPTS`
    when the saved state predates that field (an older server response, or a
    read started before this shipped)."""
    raw = cs.read_raw(session_id).get(_STATE_KEY)
    if not isinstance(raw, dict):
        return None
    read_id = raw.get("read_id")
    host = raw.get("host")
    max_attempts = raw.get("max_attempts")
    if not isinstance(max_attempts, int) or max_attempts < 1:
        max_attempts = DEFAULT_MAX_ATTEMPTS
    allowed = raw.get("allowed_hosts")
    allowed_hosts = [h for h in allowed if isinstance(h, str) and h] if isinstance(allowed, list) else []
    if isinstance(read_id, str) and read_id and isinstance(host, str) and host:
        return {"read_id": read_id, "host": host, "max_attempts": max_attempts, "allowed_hosts": allowed_hosts}
    return None


def handle_start(session_id: str, payload: dict) -> None:
    """PostToolUse on `start_website_read`: save `{read_id, host,
    max_attempts}` from the JSON result. A malformed result leaves any prior
    open read untouched -- it never manufactures a read out of a bad
    response. `max_attempts` (RMP-184, `browser_page_max_attempts` in the
    result) is optional -- absent for an older server, handled by
    `open_read`'s own fallback."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    read_id = data.get("read_id")
    host = data.get("host")
    max_attempts = data.get("browser_page_max_attempts")
    if isinstance(read_id, str) and read_id and isinstance(host, str) and host:
        state: dict[str, Any] = {"read_id": read_id, "host": host}
        if isinstance(max_attempts, int) and max_attempts >= 1:
            state["max_attempts"] = max_attempts
        cs.write_patch(session_id, {_STATE_KEY: state})


def handle_status(session_id: str, payload: dict) -> None:
    """PostToolUse on `wait_for_website_read` / `get_website_read_status`
    (RMP-281): remember the hosts of the `browser_pages` the SERVER just
    listed, so the browser may open a page on a sibling host of the same
    site (`book.brand.com`). Nothing is saved when no read is open or the
    result has no `browser_pages` -- the typed host alone stays allowed."""
    read = open_read(session_id)
    data = _parse_json_response(payload.get("tool_response"))
    pages = data.get("browser_pages") if data else None
    if read is None or not isinstance(pages, list):
        return
    hosts = list(read["allowed_hosts"])
    for page in pages:
        try:
            hostname = urlsplit(page).hostname if isinstance(page, str) else None
        except Exception:
            hostname = None
        if hostname and hostname not in hosts and len(hosts) < MAX_ALLOWED_HOSTS:
            hosts.append(hostname)
    state: dict[str, Any] = {k: read[k] for k in ("read_id", "host", "max_attempts")}
    state["allowed_hosts"] = hosts
    cs.write_patch(session_id, {_STATE_KEY: state})


def handle_finish(session_id: str) -> None:
    """PostToolUse on `finish_website_read`: close the open read. hooks.json
    only wires this tool name to `PostToolUse` (never `PostToolUseFailure`),
    so reaching this function already means the call succeeded."""
    cs.write_patch(session_id, {_STATE_KEY: None})


def record_navigate(session_id: str, read_id: str, url: str) -> None:
    """Remember the url a `browser_navigate` call was actually SENT (RMP-179)
    -- the PLANNED page, before any redirect the site itself makes. Called
    from `website_gate.py` on every navigate it ALLOWS while a read is open
    (never on a denied, off-site one -- that page is never read at all).
    Never raises; a malformed `read_id`/`url` is simply skipped."""
    if not isinstance(read_id, str) or not read_id or not isinstance(url, str) or not url:
        return
    cs.write_patch(session_id, {_LAST_NAV_KEY: {"read_id": read_id, "url": url}})


def last_navigate(session_id: str, read_id: str) -> str | None:
    """The most recently NAVIGATED url for THIS `read_id`, or `None` --
    a record left over from a different (older or newer) read_id never
    leaks across, same fail-safe convention as `open_read`."""
    raw = cs.read_raw(session_id).get(_LAST_NAV_KEY)
    if not isinstance(raw, dict) or raw.get("read_id") != read_id:
        return None
    url = raw.get("url")
    return url if isinstance(url, str) and url else None


def note_navigate_attempt(session_id: str, read_id: str, url: str) -> int:
    """Count one more attempt to navigate `url` within `read_id` (RMP-184) --
    returns the running total (1 on the first attempt). Keyed by the EXACT
    url string the reader was given (not normalized) -- good enough here,
    since `browser_pages` hands back the identical planned url every time,
    unlike the server's own full `normalize_page_url` matching.

    A count left over from a DIFFERENT (older or newer) `read_id` is
    discarded first, same convention as `last_navigate` -- a new read always
    starts counting from zero. Never raises; a malformed `read_id`/`url`
    counts as attempt 1 every time (fails toward "let it through" rather
    than crashing the hook or wedging a real url's own count at 1 forever).
    """
    if not isinstance(read_id, str) or not read_id or not isinstance(url, str) or not url:
        return 1
    raw = cs.read_raw(session_id).get(_ATTEMPTS_KEY)
    prior_counts = raw.get("counts") if isinstance(raw, dict) and raw.get("read_id") == read_id else None
    counts = dict(prior_counts) if isinstance(prior_counts, dict) else {}
    counts[url] = counts.get(url, 0) + 1
    cs.write_patch(session_id, {_ATTEMPTS_KEY: {"read_id": read_id, "counts": counts}})
    return counts[url]
