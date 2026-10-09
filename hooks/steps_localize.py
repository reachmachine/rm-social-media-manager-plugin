#!/usr/bin/env python3
"""Steps 2-5 in the owner's own language (RMP-281 P2356, half P).

`steps.json` keeps the English question and button text of steps 2-5 (marked `server_text`): that is the STOCK an English
owner's server sends too. For any other owner the SERVER sends the same lines translated, as `offers` (see
`offer_lines.py`), keyed by these ids:

    choose_workspace      step 2 question (no buttons: the workspace names are the options)
    account_owner_type    step 3 question + `own` / `client`
    own_instagram_account step 4 question (typed handle, no buttons)
    skip_instagram        step 4 skip question + `no_instagram` / `add`
    instagram_reoffer     step 4 re-offer question (a "skipped" step 4, a later session) + `add` / `later`
    revenue_model         step 5 question + the five revenue values
    revenue_description   step 5 follow-up question (typed, no buttons)

`apply` lays those lines over the loaded steps: ONLY the `text` of a question and the `label` of an option change.
Every `value` (the neutral id), the order, and the step ids stay as in `steps.json`, so every hook that matches an answer
by question text or by label (`answer_matcher`, `step_skip`, `step_recorder_revenue`) works in any language without
holding a word of English of its own. No offer, or an English owner (stock == steps.json): returned unchanged.

FAIL-SAFE: reads the plan cache only (no model, no network); any problem returns `steps` untouched.
"""
from __future__ import annotations

import copy
from typing import Any

import plan_cache

# offer id -> (step id, where in the step it goes)
OFFER_SLOTS: dict[str, tuple[str, str]] = {
    "choose_workspace": ("choose_workspace", "question"),
    "account_owner_type": ("account_owner_type", "question"),
    "own_instagram_account": ("own_instagram_account", "question"),
    "skip_instagram": ("own_instagram_account", "skip"),
    "instagram_reoffer": ("own_instagram_account", "reoffer"),   # P2359: the later-session "add it now?" question
    "revenue_model": ("revenue_model", "question"),
    "revenue_description": ("revenue_model", "follow_up"),
}


def _text(offer: Any) -> str | None:
    say = offer.get("say") if isinstance(offer, dict) else None
    return say if isinstance(say, str) and say.strip() else None


def _relabel(block: dict[str, Any], offer: dict[str, Any]) -> None:
    """New labels by option id; an option the offer does not name keeps its English label."""
    labels = {}
    for opt in offer.get("options") or []:
        if isinstance(opt, dict) and isinstance(opt.get("id"), str) and isinstance(opt.get("label"), str) and opt["label"].strip():
            labels[opt["id"]] = opt["label"]
    for opt in block.get("options") or []:
        if isinstance(opt, dict) and opt.get("value") in labels:
            opt["label"] = labels[opt["value"]]


def _apply_one(step: dict[str, Any], slot: str, offer: dict[str, Any]) -> None:
    text = _text(offer)
    if text is None:
        return
    skip = step.get("skip", {})
    block = skip.get("question") if slot == "skip" else skip.get("reoffer") if slot == "reoffer" else step.get(slot)
    if not isinstance(block, dict):
        return
    block["text"] = text
    _relabel(block, offer)


def apply(session_id: str, steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    try:
        offers = plan_cache.read_state(session_id)["offers"]
        wanted = {k: v for k, v in offers.items() if k in OFFER_SLOTS and _text(v) is not None}
        if not wanted:
            return steps
        result = []
        for step in steps:
            mine = [(oid, OFFER_SLOTS[oid][1]) for oid in wanted if OFFER_SLOTS[oid][0] == step.get("id")]
            if not mine:
                result.append(step)
                continue
            step = copy.deepcopy(step)
            for oid, slot in mine:
                _apply_one(step, slot, wanted[oid])
            result.append(step)
        return result
    except Exception:
        return steps
