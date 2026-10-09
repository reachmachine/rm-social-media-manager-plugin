#!/usr/bin/env python3
"""Customer lines the SERVER wrote, kept for the hooks (RMP-281 P2272).

WHY. A hook cannot translate: it has a few seconds and no model. So every line a customer sees in
steps 6-9 that a hook asks for (an offer, a "another website?" question, a re-offer) is written by
the server in the owner's language and arrives in the tool reply as `offers`:

    "offers": {"<offer id>": {"say": "<line>", "step": "<optional step id>",
                              "options": [{"id": "<neutral id>", "label": "<button>", "also": ["<typed words>"]}]}}

The hook shows the line exactly and matches an answer by the neutral option id, never by English
text. A typed reply matches a label, one of the server's `also` words, the id, or the option number
("1", "2"). `also` is how a Hindi "haan" or a Spanish "si" works without a word list in the plugin.
A reply value of `null` removes an offer. No offer from the server -> the hook says nothing (an
English owner gets the English from the server too; the plugin keeps no stock English here).

FAIL-SAFE: nothing here may raise.
"""
from __future__ import annotations

import json
import re
from typing import Any

import connection_state as cs
import plan_cache


def _clean_option(raw: Any) -> dict[str, Any] | None:
    if not isinstance(raw, dict):
        return None
    value = raw.get("id") if isinstance(raw.get("id"), str) else raw.get("value")
    label = raw.get("label")
    if not isinstance(value, str) or not value or not isinstance(label, str) or not label.strip():
        return None
    also = raw.get("also")
    words = [w for w in also if isinstance(w, str) and w.strip()] if isinstance(also, list) else []
    return {"value": value, "label": label, "also": words}


def clean_offer(raw: Any, *, allow_no_options: bool = False) -> dict[str, Any] | None:
    """A well-formed offer, or None. Needs a line and at least one option, unless `allow_no_options` (a typed
    question such as the Instagram handle or "what do you offer?" has a line and no buttons; RMP-281 P2356)."""
    if not isinstance(raw, dict):
        return None
    say = raw.get("say")
    options = [o for o in (_clean_option(x) for x in raw.get("options") or []) if o is not None]
    if not isinstance(say, str) or not say.strip() or not (options or allow_no_options):
        return None
    offer: dict[str, Any] = {"say": say, "options": options}
    if isinstance(raw.get("step"), str) and raw["step"]:
        offer["step"] = raw["step"]
    if isinstance(raw.get("lines"), dict):   # P2359: the offer's other fixed lines {line id: text with {holes}}
        offer["lines"] = {k: v for k, v in raw["lines"].items() if isinstance(k, str) and isinstance(v, str) and v.strip()}
    return offer


def offers_in_reply(data: Any) -> dict[str, Any]:
    """The `offers` dict of a reply: at the top, or inside a nested `next_actions`."""
    if not isinstance(data, dict):
        return {}
    found: dict[str, Any] = {}
    for holder in (data.get("next_actions"), data):
        if isinstance(holder, dict) and isinstance(holder.get("offers"), dict):
            found.update(holder["offers"])
    return found


def capture_from_payload(session_id: str, payload: dict) -> None:
    """PostToolUse: keep any `offers` the tool reply carried. Never raises."""
    try:
        text = cs.flatten_response_text(payload.get("tool_response"))
        if '"offers"' not in text:
            return
        offers = offers_in_reply(json.loads(text))
        if offers:
            plan_cache.merge_offers(session_id, offers)
    except Exception:
        pass


def get(session_id: str, offer_id: str, *, allow_no_options: bool = False) -> dict[str, Any] | None:
    try:
        return clean_offer(plan_cache.read_state(session_id)["offers"].get(offer_id), allow_no_options=allow_no_options)
    except Exception:
        return None


def line(session_id: str, offer_id: str, line_id: str, **holes: str) -> str | None:
    """One fixed non-button line of an offer (`offers.<id>.lines.<line id>`), its `{holes}` filled from `holes`.
    None when the server sent no such line, or a hole is left unfilled: the caller then says nothing of its own
    (the plugin holds no English stock; the server sends English for English or unknown owners). Never raises."""
    try:
        offer = get(session_id, offer_id, allow_no_options=True)
        text = (offer or {}).get("lines", {}).get(line_id)
        if not isinstance(text, str):
            return None
        for key, value in holes.items():
            text = text.replace("{" + key + "}", str(value))
        return None if re.search(r"\{[a-z_]+\}", text) else text
    except Exception:
        return None


def labels_text(offer: dict[str, Any]) -> str:
    return " / ".join(f'"{o["label"]}"' for o in offer["options"])


def ask_instruction(offer: dict[str, Any]) -> dict[str, str]:
    """The reminder every offer hook returns: ask the server's line with the server's buttons."""
    return {"instruction": f'Ask the customer with AskUserQuestion: "{offer["say"]}" Options: {labels_text(offer)}'}


def match(offer: dict[str, Any] | None, text: str) -> str | None:
    """The option id a typed reply means, or None. Label, `also` word, id or option number only."""
    if offer is None or not isinstance(text, str):
        return None
    key = text.strip().casefold()
    if not key:
        return None

    def hits_of(word: str) -> set[str]:
        if word.isdecimal():
            word = str(int(word))  # Devanagari / Arabic-Indic digits ("२") pick the option number too
        return {opt["value"] for number, opt in enumerate(offer["options"], start=1)
                if word in {n.strip().casefold() for n in [opt["label"], opt["value"], str(number), *opt["also"]]}}

    hits = hits_of(key) or hits_of(key.rstrip(".!?।…").strip())   # "Yes!" / "yes." / "२." mean the same without the stop (P2361)
    return next(iter(hits)) if len(hits) == 1 else None


def match_clicked(offer: dict[str, Any] | None, label: str) -> str | None:
    """A clicked button echoes its label: label or id only (a bare "1" is typing, not a click)."""
    if offer is None or not isinstance(label, str):
        return None
    key = label.strip().casefold()
    hits = {o["value"] for o in offer["options"] if key in {o["label"].strip().casefold(), o["value"].casefold()}}
    return next(iter(hits)) if len(hits) == 1 else None


def find_by_question(session_id: str, question_text: str) -> tuple[str, dict[str, Any]] | None:
    """The step-bound offer whose line is exactly `question_text` (the question a customer just answered)."""
    try:
        for offer_id, raw in plan_cache.read_state(session_id)["offers"].items():
            offer = clean_offer(raw)
            if offer is not None and offer.get("step") and offer["say"] == question_text:
                return offer_id, offer
    except Exception:
        pass
    return None


def find_for_step(session_id: str, step_id: str) -> tuple[str, dict[str, Any]] | None:
    """The offer bound to `step_id` (a step's own question carried by the server), if any."""
    try:
        for offer_id, raw in plan_cache.read_state(session_id)["offers"].items():
            offer = clean_offer(raw)
            if offer is not None and offer.get("step") == step_id:
                return offer_id, offer
    except Exception:
        pass
    return None
