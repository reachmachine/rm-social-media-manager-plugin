#!/usr/bin/env python3
"""update_creator_brief gate rules: private details, answer matching and
ordering (split from step_gate.py to stay under 300 lines, RMP-52).

`check_brief_private_details`: may only write a field whose text has nothing
left to hide (founder decision, RMP-59, 2026-09-25).

`check_fact_private_details`: `save_business_fact(source="customer", ...)` may
only carry customer text with nothing left to hide either -- same founder
decision, follow-up P1698 (P1683 covered the brief but missed this tool).
Shares `_redact_str`, the one small "would this string change" walker, with
`check_brief_private_details` instead of a second copy of the redact-and-
compare logic.

`check_brief_answers`: may only write a question step's `brief_key` with the
value the customer actually picked.

`check_brief_key_order`: may only write any step's `brief_key` (or its
follow_up's `brief_key`) if all earlier steps are finished (P1641, RMP-50).
"""
from __future__ import annotations

import json

import deny_lines
import step_order
import steps_manifest
import transcript_redaction

# RMP-291 P2320: reason ids; the owner-language texts come from the server (`deny_lines`).
_PRIVATE_DETAILS_REASON = "private_details_brief"
_FACT_PRIVATE_DETAILS_REASON = "private_details_fact"


def _redact_str(value: str) -> tuple[str, bool]:
    """The one shared "would this string change" check: `(redacted, changed)`
    for a single `str`, using the plugin's own `transcript_redaction.
    redact_text`. Both `check_brief_private_details` and
    `check_fact_private_details` call this instead of each running their own
    copy of `redact_text(value) != value`."""
    redacted = transcript_redaction.redact_text(value)
    return redacted, redacted != value


def _deny(text: str) -> dict:
    return deny_lines.deny(text)


def check_brief_private_details(tool_input: dict, session_id: str = "") -> dict | None:
    """`update_creator_brief` may only write a field whose text
    (`transcript_redaction.redact_text`, the plugin's own copy) has nothing
    left to hide -- checked for EVERY field in `fields`, whatever its key,
    before any other brief rule (founder decision, RMP-59, 2026-09-25: a
    phone/email/card must never leave the customer's machine, even in a
    saved brief field, not only in the session log RMP-27 already covers).

    Only a `str` value, or a list where every item is a `str`, is checked --
    any other shape (a number, a dict, `revenue_model`'s list of fixed option
    codes with nothing to hide) is left alone, same as the server's own
    `redact_value` (P1682). The deny reason is the full `fields` dict the
    agent sent, JSON-encoded, with only the redacted values swapped in and
    every other key of each entry kept exactly as sent -- so the agent can
    resend it verbatim."""
    fields = tool_input.get("fields")
    if not isinstance(fields, dict):
        return None
    resend = dict(fields)
    changed = False
    for key, entry in fields.items():
        if not isinstance(entry, dict):
            continue
        value = entry.get("value")
        if isinstance(value, str):
            redacted, item_changed = _redact_str(value)
            if item_changed:
                resend[key] = {**entry, "value": redacted}
                changed = True
        elif isinstance(value, list) and value and all(isinstance(v, str) for v in value):
            redacted_list = [_redact_str(v)[0] for v in value]
            if redacted_list != value:
                resend[key] = {**entry, "value": redacted_list}
                changed = True
    if not changed:
        return None
    shown = deny_lines.localize_markers(session_id, json.dumps(resend, ensure_ascii=False))   # hidden-detail words, owner language
    return _deny(deny_lines.reason(session_id, _PRIVATE_DETAILS_REASON, fields=shown))


def check_fact_private_details(tool_input: dict, session_id: str = "") -> dict | None:
    """`save_business_fact` may only carry customer text with nothing left to
    hide -- checked for `customer_words` (a `str`) and every `str` value
    inside every dict of `value["items"]`, whatever its key (`text`,
    `page_url`, `quote`, `price` -- `business_facts_models.FactItem`), before
    the call ever reaches the server (founder decision, RMP-59, 2026-09-25).

    Only `source == "customer"` is checked: `source == "website"` text was
    read off a public page, not typed by the customer, so it is never hidden
    here. A non-`str` item value (a number, `None`) is left alone, same as
    the server's own `redact_value` (P1697). The deny reason is the full
    `tool_input` the agent sent, JSON-encoded, with only the redacted strings
    swapped in and every other key kept exactly as sent -- so the agent can
    resend it verbatim."""
    if tool_input.get("source") != "customer":
        return None
    resend = dict(tool_input)
    changed = False

    customer_words = tool_input.get("customer_words")
    if isinstance(customer_words, str):
        redacted, item_changed = _redact_str(customer_words)
        if item_changed:
            resend["customer_words"] = redacted
            changed = True

    value = tool_input.get("value")
    if isinstance(value, dict):
        items = value.get("items")
        if isinstance(items, list):
            new_items = []
            items_changed = False
            for item in items:
                if not isinstance(item, dict):
                    new_items.append(item)
                    continue
                new_item = dict(item)
                for item_key, item_value in item.items():
                    if isinstance(item_value, str):
                        redacted, item_changed = _redact_str(item_value)
                        if item_changed:
                            new_item[item_key] = redacted
                            items_changed = True
                new_items.append(new_item)
            if items_changed:
                resend["value"] = {**value, "items": new_items}
                changed = True

    if not changed:
        return None
    shown = deny_lines.localize_markers(session_id, json.dumps(resend, ensure_ascii=False))
    return _deny(deny_lines.reason(session_id, _FACT_PRIVATE_DETAILS_REASON, args=shown))


def check_brief_answers(tool_input: dict, steps: list[dict], state: dict, session_id: str = "") -> dict | None:
    """`update_creator_brief` may only write a question step's `brief_key`
    with the value the customer actually picked -- checked for EVERY
    question step with a `brief_key`, regardless of step order, so a later
    re-answer (03-whose-account.md, "Changing the answer later") is
    protected the same way the first answer is."""
    fields = tool_input.get("fields")
    if not isinstance(fields, dict):
        return None
    for step in steps:
        brief_key = step.get("brief_key")
        if not isinstance(brief_key, str) or steps_manifest.answer_type(step) != "options":
            continue  # step 5's multi-select is checked by revenue_gate instead
        entry = fields.get(brief_key)
        if not isinstance(entry, dict):
            continue
        value = entry.get("value")
        if value != state["human_answers"].get(step["id"]):
            if step["id"] == "account_owner_type":
                return _deny(deny_lines.finish(session_id, step["id"]))
            return _deny(deny_lines.reason(session_id, "ask_customer_first"))
    return None


def check_brief_key_order(tool_input: dict, steps: list[dict], state: dict, session_id: str = "") -> dict | None:
    """`update_creator_brief` may only write any step's `brief_key` (or its follow_up's
    `brief_key`) if all earlier steps are finished (P1641, RMP-50). Checked for EVERY
    write, regardless of the value check (which runs first). The deny reason names the
    FIRST unfinished earlier step."""
    fields = tool_input.get("fields")
    if not isinstance(fields, dict):
        return None
    for step in steps:
        # Check both the step's own brief_key and any follow_up brief_key
        keys_to_check = []
        brief_key = step.get("brief_key")
        if isinstance(brief_key, str):
            keys_to_check.append((step["id"], brief_key))
        follow_up = steps_manifest.follow_up(step)
        if follow_up is not None:
            keys_to_check.append((step["id"], follow_up["brief_key"]))

        for step_id, key in keys_to_check:
            if key in fields:
                if not step_order.earlier_steps_done(steps, state, step_id):
                    first = step_order.first_unfinished(steps, state)
                    if first is not None:
                        return _deny(deny_lines.finish(session_id, first["id"]))
    return None
