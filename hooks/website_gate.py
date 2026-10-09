#!/usr/bin/env python3
"""Off-site guard for step 6's website read (RMP-66).

Spec: docs/plugin-v2/06-website-and-business-knowledge.md, "Wave 2 design",
"Reading the site (plugin)", "Off-site guard". Wired from
`connections_gate.py`, for the playwright server's `browser_navigate` only,
AFTER that file's own step-1 checks (`_is_probe_call`, `browser_close`) --
the step 1 connection probe's fixed `PROBE_URL` navigate is allowed there
before this module ever runs, so it is never subject to this guard.

While no website read is open (`website_read_state.open_read` returns
`None`), this changes nothing -- every `browser_navigate` call navigates
freely, exactly as before RMP-66.

FAILS TOWARD ALLOW only when no read is open (that is the correct behaviour,
not a fail-open bug): `website_read_state.open_read`'s own fail-safe already
treats a missing/corrupt state as "no read open", so this module needs no
extra try/except of its own to stay non-crashing.
"""
from __future__ import annotations

from typing import Any

import deny_lines
import website_read_state as wrs


def _deny(reason_id: str, **fill: object) -> dict:
    return deny_lines.deny_id(reason_id, **fill)


def check_navigate(tool_input: dict, session_id: str) -> dict[str, Any] | None:
    """None = allow. Denies a `browser_navigate` whose `url` leaves the open
    read's own site, OR (RMP-184) one already tried `read["max_attempts"]`
    times this read -- the server decides that number (founder rule: the
    plugin only executes), see `website_read_state.open_read`.

    RMP-179: an ALLOWED navigate also records its own url via
    `website_read_state.record_navigate` -- the PLANNED page, before any
    redirect the site makes. `website_upload.py` reads it back and sends it
    to the server as `requested_url`, so an upload can still be matched to
    its planned page even when the browser ends up somewhere else entirely.
    A denied navigate (off-site, or over the attempt cap) never happens, so
    it is never recorded.

    RMP-184: a page whose `browser_evaluate` keeps failing to load (site
    error, timeout, or the reader's own "if a page fails to load ... move
    on" instruction) never reaches `website_upload.py` at all, so nothing
    server-side ever retires it -- the read's `browser_pages` list keeps
    handing it straight back, and the reader keeps re-navigating it (the
    live incident this fixes: one url opened 7 times, luisazhou.com). This
    cap stops the WASTE (no more page loads once a url is over its limit);
    the read itself still finishes honestly once its time budget ends --
    see ``website_runner._finish``'s own sweep for that.
    """
    read = wrs.open_read(session_id)
    if read is None:
        return None
    url = tool_input.get("url")
    if not wrs.same_site(url, read["host"], read["allowed_hosts"]):
        return _deny("stay_on_site", host=read["host"])
    attempts = wrs.note_navigate_attempt(session_id, read["read_id"], url)
    if attempts > read["max_attempts"]:
        return _deny("page_tried_max", times=read["max_attempts"])
    wrs.record_navigate(session_id, read["read_id"], url)
    return None
