#!/usr/bin/env python3
"""PostToolUse recorder + gate check for `save_business_fact` (RMP-68, RMP-72).

Spec: docs/plugin-v2/06-website-and-business-knowledge.md, "Wave 2 design"
-> "Facts from chat". `save_business_fact` is allowed from step 3 on
(P1668, RMP-26, `step_gate.py`'s `_STEP_ALLOW`) -- this module only logs a
CUSTOMER-sourced save as a `business_fact_saved` session event, the same
"one exact call, then check it against what actually happened" shape step
5's `revenue_described` flow uses (`step_recorder_revenue.py` /
`step_gate_revenue.py`). Kept in ONE file here (recorder + gate check
together) because both halves are small -- unlike revenue's two-question
flow, there is nothing else for this feature to split.

RMP-72 (live test, 2026-09-25): a customer who gives 3 facts in one message
gets 3 saves in a row. The OLD single-slot `pending_fact_event` key could
only ever remember the LAST one -- the earlier two `record_session_event`
calls the model then made were denied as "That doesn't match what actually
happened", so 2 of the customer's 3 facts were never logged. Fix: the
pending state is now a LIST, `pending_fact_events` (raw `connection_state`
key), oldest first, capped at `_MAX_PENDING` items (oldest dropped past
that, same "never grow the state file forever" rule as the queue file in
`session_record.py`). A new save of a field ALREADY pending replaces that
field's item rather than adding a second one -- there is only ever one
truthful `{field, version}` owed per field at a time.

FLOW: every `save_business_fact(source="customer", ...)` call that actually
`saved` (never a `kept_customer_value` conflict, and never `source=
"website"`) is appended to (or replaces its field's slot in) the pending
list for this session. `pending_event_reminder` (wired into
`checklist_recorder.build_step_reminder` via `priority_reminders.py`, the
SAME channel step 5's `revenue_described` reminder uses, both immediate
PostToolUse delivery and the UserPromptSubmit fallback) hands the model the
OLDEST pending item's exact `record_session_event` call plus its `say`
line, one at a time, until `check_event` sees THAT item's exact
`{field, version}` pair come back and `handle_record_session_event_
dispatch` removes exactly that one item -- the other pending items are
untouched and get their own turn next.

BACK-COMPAT: a session already in flight when this shipped may still have
the OLD single-slot `pending_fact_event` key on disk and nothing under the
new list key yet. `read_pending_list` reads that old key ONCE, as a list of
one, whenever the new key is absent -- so an in-progress save from before
the fix is never silently dropped.

FAIL-SAFE: nothing here may crash a hook -- same convention as every
sibling module.
"""
from __future__ import annotations

import json
from typing import Any

import connection_state as cs
import deny_lines
from payload_util import tool_args

FACT_EVENT_KIND = "business_fact_saved"
_EVENT_MISMATCH_REASON = "fact_event_mismatch"
_MAX_PENDING = 20


def _parse_json_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _deny(reason_id: str, **fill: object) -> dict:
    return deny_lines.deny_id(reason_id, **fill)


def _validate_item(raw: Any) -> dict[str, Any] | None:
    """The safe `{field, version, say}` shape, or None for anything missing
    or wrong-typed -- same fail-safe direction as every read in this
    plugin's hooks."""
    if not isinstance(raw, dict):
        return None
    field = raw.get("field")
    version = raw.get("version")
    if not isinstance(field, str) or not field or not isinstance(version, int):
        return None
    say = raw.get("say")
    return {"field": field, "version": version, "say": say if isinstance(say, str) else ""}


def read_pending_list(session_id: str) -> list[dict[str, Any]]:
    """Every fact event this session owes a `business_fact_saved` log for,
    oldest first. Reads the new list key; when that is absent, falls back
    ONCE to the old single-slot key (see module docstring, "BACK-COMPAT"),
    read as a list of one. Wrong-typed entries are dropped, never crash the
    caller."""
    raw = cs.read_raw(session_id)
    items = raw.get("pending_fact_events")
    if isinstance(items, list):
        return [v for v in (_validate_item(i) for i in items) if v is not None]
    old = _validate_item(raw.get("pending_fact_event"))
    return [old] if old is not None else []


def read_pending(session_id: str) -> dict[str, Any] | None:
    """The OLDEST pending item, or None -- what `pending_event_reminder`
    hands over one at a time, same "one at a time" rule as before this
    fix, just no longer limited to remembering only the LAST save."""
    items = read_pending_list(session_id)
    return items[0] if items else None


def _write_list(session_id: str, items: list[dict[str, Any]]) -> None:
    cs.write_patch(session_id, {"pending_fact_events": items})


def handle_save_business_fact(session_id: str, payload: dict) -> None:
    """PostToolUse. A customer-sourced save that actually saved (not a
    kept-customer-value conflict, and never a website save -- neither one
    is something the customer needs told back to them as "recorded") is
    appended to the pending list, replacing that field's own item if one is
    already pending. Break: skip storing here -> RED (no reminder is ever
    handed over, so `record_session_event` is never called and the fact
    never appears in the session log)."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None or data.get("saved") is not True or data.get("kept_customer_value") is True:
        return
    tool_input = tool_args(payload)  # RMP-5/RMP-10/RMP-20: see payload_util.tool_args
    if tool_input.get("source") != "customer":
        return
    field = data.get("field")
    version = data.get("version")
    say = data.get("say")
    if not isinstance(field, str) or not field or not isinstance(version, int):
        return
    items = [i for i in read_pending_list(session_id) if i["field"] != field]
    items.append({"field": field, "version": version, "say": say if isinstance(say, str) else ""})
    if len(items) > _MAX_PENDING:
        items = items[-_MAX_PENDING:]
    _write_list(session_id, items)


def handle_save_business_facts(session_id: str, payload: dict) -> None:
    """PostToolUse recorder for the batch `save_business_facts` call
    (RMP-96), the same pending-list flow `handle_save_business_fact` uses
    for one field at a time. Called from `step_recorder_website.handle_
    save_business_facts`, which owns the step-6 tick side of this same
    response.

    P1733 (RMP-96 follow-up, live batch chat 2026-09-25): P1731 queued one
    event per SAVED field regardless of source, so one `save_business_facts`
    call made the model place 7 separate `record_session_event` calls --
    each a full model turn, and most of what was left of the fact loop's
    cost. A website-sourced fact is already stored on the server with its
    own source, page URL, quote and version, so the session-log event adds
    nothing the customer or we need. Restored: nothing is queued for a
    `source: "website"` item, the same rule `handle_save_business_fact`
    above has always followed for the single-fact path.

    The batch tool's own schema (`BatchFactInput.source`, `tool_schemas_
    fact_tasks.py`) allows `source: "customer"` items too, and the backend
    passes that straight through to `business_facts.save_fact` -- so a
    customer-sourced field saved through this batch call still queues
    exactly like one saved through `save_business_fact`. The `results` list
    carries no source of its own, so the saved field names are matched
    against `source: "customer"` entries in the call's own `facts` input.

    Break 1: queue website items again (drop the customer-only filter) ->
    RED (a batch save of purely-website facts would queue events again).
    Break 2: stop queueing customer items too (return unconditionally) ->
    RED (a customer-sourced batch save would queue no event, unlike a
    single `save_business_fact` call for the same field)."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None:
        return
    results = data.get("results")
    if not isinstance(results, list):
        return
    tool_input = tool_args(payload)
    facts = tool_input.get("facts")
    if not isinstance(facts, list):
        return
    customer_fields = {
        f["field"] for f in facts
        if isinstance(f, dict) and f.get("source") == "customer"
        and isinstance(f.get("field"), str) and f["field"]
    }
    if not customer_fields:
        return
    items = read_pending_list(session_id)
    for result in results:
        if not isinstance(result, dict) or result.get("status") != "saved":
            continue
        field = result.get("field")
        if not isinstance(field, str) or field not in customer_fields:
            continue
        items = [i for i in items if i["field"] != field]
        items.append({"field": field, "version": 1, "say": ""})
    if len(items) > _MAX_PENDING:
        items = items[-_MAX_PENDING:]
    _write_list(session_id, items)


def pending_event_reminder(session_id: str, state: dict[str, Any]) -> dict[str, Any] | None:
    """The exact `record_session_event` payload owed for the OLDEST pending
    fact, with its `say` line (`step_reminder_format.format_step_reminder`'s
    `{call, payload, say}` shape) -- None once the list is empty, or before
    a workspace is chosen (nothing to attach `workspace_id` to yet)."""
    workspace = state["workspace"]
    pending = read_pending(session_id)
    if pending is None or workspace is None:
        return None
    reminder: dict[str, Any] = {
        "call": "record_session_event",
        "payload": {
            "client_session_id": session_id, "kind": FACT_EVENT_KIND,
            "workspace_id": workspace["id"],
            "detail": {"field": pending["field"], "version": pending["version"]},
        },
    }
    if pending["say"]:
        reminder["say"] = pending["say"]
    return reminder


def check_event(tool_input: dict[str, Any], session_id: str) -> dict | None:
    """For `record_session_event(kind="business_fact_saved")` -- called from
    `step_gate_session_event.check_record_session_event`, AFTER the workspace itself
    already matched. Allowed when `detail` equals ANY pending item's
    `{field, version}` -- not only the oldest one, so a model that logs
    them out of order (all three saves happened before any of the three
    events came back) still gets every one accepted. The explicit "list
    empty" check matters the same way `step_gate_revenue.
    check_revenue_described_event`'s `words is None` check does: without
    it, a model sending a made-up `detail` when nothing is pending would
    still need SOME real mismatch to be denied, rather than being denied on
    the much simpler "nothing is owed" ground. Break: always allow -> RED (a
    fabricated field/version, or a stale/already-cleared one, would be
    accepted as truthful)."""
    items = read_pending_list(session_id)
    if not items:
        return _deny(_EVENT_MISMATCH_REASON)
    detail = tool_input.get("detail")
    expected = [{"field": i["field"], "version": i["version"]} for i in items]
    if detail not in expected:
        return _deny(_EVENT_MISMATCH_REASON)
    return None


def handle_record_session_event_dispatch(session_id: str, payload: dict) -> None:
    """`record_session_event`'s dispatch entry for `business_fact_saved` --
    removes exactly the ONE matching pending item once the server actually
    accepted THIS EXACT event (never unconditionally, and never more than
    one item): a denied or unrelated call must never remove anything, or a
    real fact-saved event would be lost and never logged. The other pending
    items (from the customer's other facts in the same message) are left
    alone and get their own reminder next. Break: clear the whole list
    unconditionally -> RED (a denied/mismatched call would still drop every
    pending reminder, silently dropping the others)."""
    data = _parse_json_response(payload.get("tool_response"))
    if data is None or data.get("recorded") is not True:
        return
    tool_input = tool_args(payload)
    if tool_input.get("kind") != FACT_EVENT_KIND:
        return
    detail = tool_input.get("detail")
    if not isinstance(detail, dict):
        return
    field = detail.get("field")
    version = detail.get("version")
    items = read_pending_list(session_id)
    remaining = [i for i in items if not (i["field"] == field and i["version"] == version)]
    if len(remaining) == len(items):
        return  # nothing matched -- never touch the list on a mismatch
    _write_list(session_id, remaining)
