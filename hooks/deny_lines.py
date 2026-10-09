#!/usr/bin/env python3
"""Deny reasons the SERVER wrote in the owner's language (RMP-291 P2320).

WHY. A PreToolUse deny reason is shown to the customer, and a hook cannot translate (no model, a few seconds). So the
server sends `next_actions.deny_reasons = {reason_id: text}` already in the owner's language; PostToolUse keeps the map in
the plan cache (same file the hooks already read), and a gate shows `deny_reasons[reason_id]`. A `{hole}` in a text is
filled by the gate (`{fields}`, `{args}`).

NO MAP (an old session, the server down, the planner off): the gate shows a short LANGUAGE-NEUTRAL message, the reason id
plus the one action (the values it was given), never English prose. The plugin holds no English text for these.

FAIL-SAFE: nothing here may raise.
"""
from __future__ import annotations

import json
from typing import Any

import connection_state as cs
import plan_cache
import transcript_redaction

# The kinds of private detail the redactor hides. A refusal that shows the hidden text names the kind by a `redaction.<kind>` id.
REDACTION_KINDS = ("phone", "card", "email", "bank", "id_number", "secret")

# The reason ids the gates use. The server's registry (`plugin_say_stock`) must carry every one (a backend test pins it).
STEP_IDS = (
    "choose_workspace", "account_owner_type", "own_instagram_account", "revenue_model", "website",
    "business_review", "pick_niche", "dream_customer", "where_to_find",
)
REASON_IDS = frozenset({
    *(f"finish.{step}" for step in STEP_IDS), "finish.other",
    "manifest_outdated", "tick_not_done", "tick_server_done", "ask_instagram_first", "event_mismatch",
    "file_sent_for_you", "no_wait", "search_limit", "page_limit",
    "private_details_brief", "private_details_fact", "ask_customer_first",
    # RMP-291 P2321: the rest of the gates.
    "ask_account_right_first", "waiting_reply_1_or_2", "ask_fix_or_add_first", "add_wrong_handle", "competitor_add_unavailable",
    "pick_workspace", "workspace_pin", "session_mismatch", "fact_event_mismatch",
    "spend_no_preview", "spend_same_turn", "spend_args_mismatch", "spend_background_task", "spend_subagent", "spend_unsure",
    "repeat_call", "plan_stale", "revenue_wrong_pick", "ask_question_first", "revenue_words_mismatch",
    "actor_not_allowed", "job_limit", "search_down",
    "connections_unconfirmed", "connections_record_mismatch", "connections_not_saved",
    "connections_missing_sign_in", "connections_missing_wait",
    "stay_on_site", "page_tried_max", "scraper_started", "scraper_running", "page_order", "search_exact", "search_done",
    *(f"redaction.{kind}" for kind in REDACTION_KINDS),
})


_MARK = "_rm_reason"


def _map(session_id: str) -> dict[str, str]:
    try:
        return plan_cache.read_state(session_id)["deny_reasons"]
    except Exception:
        return {}


def neutral(reason_id: str, fill: dict[str, Any] | None = None) -> str:
    """The language-neutral message: the reason id plus the one action (the values the gate was given)."""
    parts = [f"[{reason_id}]"]
    for value in (fill or {}).values():
        parts.append(value if isinstance(value, str) else json.dumps(value))
    return " ".join(parts)


def reason(session_id: str, reason_id: str, **fill: Any) -> str:
    """The server's text for `reason_id` (holes filled), else the neutral message. Never raises."""
    try:
        text = _map(session_id).get(reason_id)
        if not isinstance(text, str) or not text.strip():
            return neutral(reason_id, fill)
        for key, value in fill.items():
            text = text.replace("{" + key + "}", value if isinstance(value, str) else json.dumps(value))
        return text
    except Exception:
        return neutral(reason_id, fill)


def finish(session_id: str, step_id: str) -> str:
    """"Let's finish <step> first." for a step the server worded; the server's generic line for any other step."""
    mapped = _map(session_id)
    if f"finish.{step_id}" in mapped:
        return reason(session_id, f"finish.{step_id}")
    if "finish.other" in mapped:
        return reason(session_id, "finish.other")
    return neutral(f"finish.{step_id}")


def deny_id(reason_id: str, **fill: Any) -> dict:
    """A refusal that carries a reason id (and the values to fill in), not a sentence. The gate does not know the session,
    so the neutral message is in the decision until `resolve` swaps in the server's text at the hook's one exit."""
    decision = deny(neutral(reason_id, fill))
    decision[_MARK] = {"id": reason_id, "fill": fill}
    return decision


def resolve(session_id: str, decision: Any) -> Any:
    """`decision` with the server's text (or the neutral message) for its reason id; any other decision is returned as it was.
    Always strips the private mark, so what is printed is a plain hook decision. Never raises."""
    try:
        if not isinstance(decision, dict) or _MARK not in decision:
            return decision
        mark = decision[_MARK]
        return deny(reason(session_id, mark["id"], **mark["fill"]))
    except Exception:
        return deny(neutral("hook_error"))


def localize_markers(session_id: str, text: str) -> str:
    """Swap the redactor's hidden-detail markers for the server's word (`redaction.<kind>`), else a neutral token
    (`[hidden:phone]`). The redaction RULES are untouched: this only changes what a refusal SHOWS."""
    try:
        for kind, marker in transcript_redaction.MARKERS.items():
            text = text.replace(marker, _map(session_id).get(f"redaction.{kind}") or f"[hidden:{kind}]")
    except Exception:
        pass
    return text


def deny(text: str) -> dict:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": text,
        }
    }


def capture_from_payload(session_id: str, payload: dict) -> None:
    """PostToolUse: keep a `deny_reasons` map a reply carried (top level or inside a nested `next_actions`). Never raises."""
    try:
        text = cs.flatten_response_text(payload.get("tool_response"))
        if '"deny_reasons"' not in text:
            return
        data = json.loads(text)
        found: dict[str, str] = {}
        for holder in (data.get("next_actions"), data):
            if isinstance(holder, dict) and isinstance(holder.get("deny_reasons"), dict):
                found.update({k: v for k, v in holder["deny_reasons"].items() if isinstance(k, str) and isinstance(v, str) and v.strip()})
        if found and data.get("deny_reasons_lang") == "en" and isinstance(data.get("deny_reasons"), dict):
            # P2314: the lean stock-English map for the first gates never replaces a line the owner-language map already gave.
            found = {k: v for k, v in found.items() if k not in _map(session_id)}
        if found:
            plan_cache.set_deny_reasons(session_id, found)
    except Exception:
        pass
