#!/usr/bin/env python3
"""Session-state side effects keyed by MCP tool name suffix (RMP-66/RMP-190/
RMP-202).

Split out of `connection_state_cli.py`'s `_cli_record` (which was at the
300-line limit) so a new tool-name entry never has to fight that file's cap
again. Table, not one `if` per tool: `_TABLE` maps a `tool_name.endswith()`
suffix to the handler it feeds `(session_id, payload)` to.

This is session state (an open website read, an open reviews fetch), NOT a
step tick -- `step_recorder.py`'s table (P1668) owns step ticks instead.
`dispatch` runs EVERY entry whose suffix matches (not just the first), same
as the three `if` blocks it replaces -- a tool name could in principle match
more than one entry, and none of today's entries actually overlap. Never
raises: each handler's exception is swallowed on its own, so one broken
table entry can never stop another from running, same fail-safe convention
as every caller here.

RMP-202: every actor call now goes through the ONE generic `call-actor`
tool instead of one named tool per actor (RMP-190's `compass--google-maps-
reviews-scraper` suffix match, removed) -- see `apify_actor_allowlist.py`'s
module docstring for why that changed, and `reviews_upload.py`'s for how it
reshapes the upload flow. Apify's own MCP server confirms (source:
apify-mcp-server/src/tools/actors/call_actor.ts and .../actor_run_response.
ts) that `call-actor` returns run metadata plus a `storages.datasets.
default.id`, NEVER the dataset items themselves -- a follow-up `get-
dataset-items` call is required, so BOTH tool names need a table entry:
`call-actor` records which dataset the open reviews fetch's run produced,
and `get-dataset-items` uploads once that exact dataset comes back.

`__start_reviews_fetch` now feeds TWO independent effects
(`reviews_read_state.handle_start`, which is the only one for `finish_
reviews_fetch` too, and `apify_actor_allowlist.record_from_tool_result`,
RMP-202's allow-list cache) through `_handle_start_reviews_fetch` below --
one `_TABLE` entry can only hold one callable, and each effect is wrapped in
its OWN try/except there so one raising can never stop the other, the same
guarantee `dispatch`'s per-entry loop gives entries that don't share a key.
"""
from __future__ import annotations

from typing import Any, Callable

import apify_actor_allowlist
import hangouts_upload
import hangouts_websearch
import deny_lines
import offer_lines
import reviews_read_state
import reviews_upload
import website_read_state
import website_upload


def _handle_start_reviews_fetch(session_id: str, payload: dict) -> None:
    """Three effects of a `start_reviews_fetch` result: the open-fetch state
    (RMP-190), the actor-allowlist cache (RMP-202), and the RMP-194
    "section 8 has been reached" marker -- the LAST one runs unconditionally
    (never inside the other two's own success path), since the skill calls
    this tool whatever it answers (`reviews_read_state.mark_consent_asked`'s
    own docstring). Each wrapped in its own try/except -- see module
    docstring."""
    try:
        reviews_read_state.handle_start(session_id, payload)
    except Exception:
        pass
    try:
        apify_actor_allowlist.record_from_tool_result(session_id, payload)
    except Exception:
        pass
    try:
        reviews_read_state.mark_consent_asked(session_id)
    except Exception:
        pass


def _run_each(session_id: str, payload: dict, *handlers: Callable[[str, dict], None]) -> None:
    """Run every handler, each in its OWN try/except (one raising never stops
    the next) -- the reviews handler and the step 10 hangouts handler share
    the two generic Apify tool names (RMP-218, P1776); each is a no-op
    unless its own state matches."""
    for handler in handlers:
        try:
            handler(session_id, payload)
        except Exception:
            pass


def _handle_call_actor(session_id: str, payload: dict) -> None:
    _run_each(session_id, payload, reviews_upload.handle_call_actor, hangouts_upload.handle_call_actor)


def _handle_dataset_items(session_id: str, payload: dict) -> None:
    _run_each(session_id, payload, reviews_upload.handle_dataset_items, hangouts_upload.handle_dataset_items)


def _handle_get_actor_run(session_id: str, payload: dict) -> None:
    _run_each(session_id, payload, hangouts_upload.handle_get_actor_run)   # P1853: the run's newer status


def _handle_hangouts_work(session_id: str, payload: dict) -> None:
    """Step 10's work item: the job's per-job allow-list (one actor) plus the
    run id the later upload needs. No-op until P1778 builds the tool."""
    _run_each(
        session_id, payload,
        apify_actor_allowlist.record_from_tool_result, hangouts_upload.handle_work_item,
        hangouts_websearch.handle_work_item,   # RMP-257 P2041: a websearch run's issued searches
    )


_TABLE: dict[str, Callable[[str, dict], None]] = {
    "__start_website_read": lambda sid, payload: website_read_state.handle_start(sid, payload),
    "__wait_for_website_read": lambda sid, payload: website_read_state.handle_status(sid, payload),
    "__get_website_read_status": lambda sid, payload: website_read_state.handle_status(sid, payload),
    "__finish_website_read": lambda sid, payload: website_read_state.handle_finish(sid),
    "__browser_evaluate": lambda sid, payload: website_upload.handle(sid, payload),
    "__start_reviews_fetch": _handle_start_reviews_fetch,
    "__finish_reviews_fetch": lambda sid, payload: reviews_read_state.handle_finish(sid),
    "__call-actor": _handle_call_actor,
    "__get-dataset-items": _handle_dataset_items,
    "__get-actor-run": _handle_get_actor_run,
    hangouts_upload.HANGOUTS_WORK_SUFFIX: _handle_hangouts_work,
    # RMP-205: step 9's `start_dream_customer` is the SECOND server tool
    # (after `start_reviews_fetch`) that can hand back its own
    # `allowed_actor_ids` -- exactly the extension point `apify_actor_
    # allowlist.py`'s own docstring names ("needs no new gate code -- only
    # a new tool_result_dispatch.py wiring line"). No-op when the result
    # carries no such list (module docstring).
    "__start_dream_customer": lambda sid, payload: apify_actor_allowlist.record_from_tool_result(sid, payload),
}


def dispatch(session_id: str, tool_name: Any, payload: dict) -> None:
    """Run every `_TABLE` entry whose suffix matches `tool_name`. Never
    raises. Break: `return` on the first match instead of continuing the
    loop -> RED (Rule 3 test: a tool name crafted to match two entries would
    only run one)."""
    if not isinstance(tool_name, str):
        return
    offer_lines.capture_from_payload(session_id, payload)  # RMP-281 P2272: server-written offer lines (never raises)
    deny_lines.capture_from_payload(session_id, payload)  # RMP-291 P2320: server-written deny reasons (never raises)
    for suffix, handler in _TABLE.items():
        if tool_name.endswith(suffix):
            try:
                handler(session_id, payload)
            except Exception:
                pass
