#!/usr/bin/env python3
"""Thin caller for question-step answer matching (RMP-76 part 1; was P1615,
RMP-10, RMP-19, RMP-20, RMP-178).

RMP-76 ("all logic server-side, the plugin only executes"): the MATCHING
RULES -- exact-vs-fuzzy, casefold, the RMP-178 "X and Y" conjunction split
for a typed multi-pick, and the cross-step tie rule -- used to live here, as
`_match_one`/`_match_multi_items`/`split_multi_select`. They now live in
`app/services/plugin_answer_match.py`, reached through
`answer_match_client.call`. This file keeps only: building the request from
the step's own options (already known locally from `steps.json`/the
server's step-rules cache), interpreting the response, and the parts that
must stay local (see below).

WHAT STAYS LOCAL (prompts/COMMS.md, 2026-09-26, has the full scoping note):
- `extract_handle` -- the `@handle` regex/punctuation rules. Called from
  `step_gate_own_account.py` (a PreToolUse gate) and `step_recorder.py`'s
  own-account-change check, both of which must never depend on a network
  call; the format itself is Instagram's own public username rule, not this
  app's business logic.
- `free_text_reply`, `step_for_question_text` -- input hygiene and manifest
  lookup, not option-matching decisions.
- A `"handle"`-type step's OWN answer, in `match_label` (the clicked path):
  `AskUserQuestion`'s echo for a handle step is just the customer's typed
  text confirmed once, matched by `extract_handle` exactly as before --
  there is no "candidate list" to send the server for this branch at all.

FAIL-SAFE, ask-again-not-guess: if the server cannot be reached,
`match_label`/`match_typed_reply` return the `UNREACHABLE` sentinel (never
`None`, which means "the server said no match") -- see each function's own
docstring, and `step_recorder.py`'s callers, for why the two must never be
confused.
"""
from __future__ import annotations

import re
from typing import Any

import answer_match_client
import steps_manifest

# P1618: a reply holding exactly one `@handle` token counts as the handle.
_HANDLE_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9._])@(\S+)")
_HANDLE_SHAPE_RE = re.compile(r"^[A-Za-z0-9._]{1,30}$")
_TRAILING_SENTENCE_PUNCT = ".,!?;:)\"'"

# "The server could not be reached" -- distinct from `None` ("the server
# answered: no match"). `is`-compared only; never stored, never serialised.
UNREACHABLE = object()


def extract_handle(message: str, *, allow_bare: bool) -> str | None:
    """The spec's matching rule (P1618 SS2). Pure; never raises.

    Exactly one `@handle` token in `message` -> that handle, normalised
    (`@` stripped, trailing sentence punctuation stripped, lower-cased).
    Two or more tokens -> `None` ("one handle only"). No `@` token at all
    -> `None`, UNLESS `allow_bare` is true AND the whole stripped message
    is itself one handle-shaped word. A candidate containing ".." is always
    `None`."""
    if not isinstance(message, str):
        return None
    tokens = _HANDLE_TOKEN_RE.findall(message)
    if len(tokens) > 1:
        return None
    if len(tokens) == 1:
        candidate = tokens[0]
    elif allow_bare:
        candidate = message.strip()
    else:
        return None
    candidate = candidate.rstrip(_TRAILING_SENTENCE_PUNCT)
    if not candidate or ".." in candidate:
        return None
    if not _HANDLE_SHAPE_RE.fullmatch(candidate):
        return None
    return candidate.lower()


def free_text_reply(prompt_text: str, *, max_chars: int) -> str | None:
    """The customer's typed reply for a free-text question: stripped,
    ORIGINAL case kept, None when empty or longer than max_chars."""
    if not isinstance(prompt_text, str):
        return None
    stripped = prompt_text.strip()
    if not stripped or len(stripped) > max_chars:
        return None
    return stripped


def is_dont_know_reply(session_id: str, text: str) -> bool:
    """RMP-24 (S5-B6) + RMP-281 (P2233): is this typed description an "I can't answer this", in ANY
    language? The server decides by meaning (an embedder against labelled examples); no word list lives
    here. Fail-safe: server unreachable, slow or unsure -> False, so the words are kept as typed (the
    reply is never swallowed). A real description that merely mentions doubt is not a non-answer."""
    if not isinstance(text, str) or not text.strip():
        return False
    result = answer_match_client.call(session_id, {"mode": "cannot_answer", "message": text})
    return bool(result) and result.get("cannot_answer") is True


def step_for_question_text(steps: list[dict[str, Any]], text: str) -> dict[str, Any] | None:
    """The step whose fixed `question.text` equals `text` EXACTLY. None if
    no step's question matches -- "store nothing" (spec), regardless of
    whether that step has already passed."""
    for step in steps:
        if steps_manifest.question_text(step) == text:
            return step
    return None


def _step_options(step: dict[str, Any], state: dict[str, Any]) -> list[dict[str, str]]:
    """`[{"label", "value"}]` for one non-handle step: the live workspace
    list for `choose_workspace` (name -> workspace id), or the fixed
    question options for a step 3-onward question. This is exactly what the
    request sends -- the server never re-derives it from a manifest of its
    own, so a plugin using an older/newer cached step-rules manifest is
    always matched against the SAME options the plugin itself is showing."""
    if step["id"] == "choose_workspace":
        return [{"label": o["name"], "value": o["id"]} for o in state["workspace_options"]]
    return steps_manifest.question_options(step)


def match_label(session_id: str, step: dict[str, Any], label: str, state: dict[str, Any]) -> str | list[str] | None:
    """The clickable path: `label` against the step's own candidates.

    A handle step (P1618) is answered locally, always (see module
    docstring). Every other step asks the server. Returns `UNREACHABLE` if
    the server could not be reached -- callers must check for this BEFORE
    treating the result as "no match"."""
    if steps_manifest.answer_type(step) == "handle":
        return extract_handle(label, allow_bare=True)

    kind = "multi" if steps_manifest.answer_type(step) == "multi_options" else "single"
    body = {
        "mode": "label",
        "step": {"step_id": step["id"], "kind": kind, "options": _step_options(step, state)},
        "label": label,
    }
    result = answer_match_client.call(session_id, body)
    if result is None:
        return UNREACHABLE
    return result.get("value") if result.get("matched") else None


def match_typed_reply(
    session_id: str,
    steps: list[dict[str, Any]],
    state: dict[str, Any],
    message: str,
    *,
    bare_handle_steps: frozenset[str] = frozenset(),
    numbered_step_id: str | None = None,
) -> tuple[dict[str, Any], str | list[str]] | None:
    """The headless fallback: `message` against EVERY question step's own
    candidates, all in ONE server call so the cross-step tie rule (spec: "if
    two steps' options both match, store nothing") is decided in one place.
    `connection_check` has no question at all and is never sent.

    `numbered_step_id` (RMP-23): the ONE step the customer is being asked right now. Only
    that step lets a typed number ("1", "2, 3", "option 2") pick an option by position --
    the chat prints its choices numbered; sent to every step, a bare "1" would tie.

    A handle step (P1618) still takes part -- `extract_handle` runs LOCALLY
    (see module docstring) and only its result (or nothing) is sent, as one
    more candidate in the same tie rule every other step uses.

    Returns `(step, value)` for exactly one match, `None` for "the server
    said no match", or `UNREACHABLE` if the server could not be reached --
    callers must check for `UNREACHABLE` FIRST (see `step_recorder.
    handle_typed_answer`'s own docstring for why treating it as `None` is
    unsafe: `None` there falls through to "save this as the business
    description")."""
    payload_steps: list[dict[str, Any]] = []
    for step in steps:
        if step["id"] == "connection_check":
            continue
        answer_type = steps_manifest.answer_type(step)
        if answer_type == "handle":
            extracted = extract_handle(message, allow_bare=step["id"] in bare_handle_steps)
            payload_steps.append({
                "step_id": step["id"], "kind": "handle", "options": [], "extracted_value": extracted,
            })
        else:
            kind = "multi" if answer_type == "multi_options" else "single"
            payload_steps.append({
                "step_id": step["id"], "kind": kind, "options": _step_options(step, state),
                "extracted_value": None,
                **({"numbered": True} if step["id"] == numbered_step_id else {}),
            })
    if not payload_steps:
        return None

    result = answer_match_client.call(session_id, {"mode": "typed", "steps": payload_steps, "message": message})
    if result is None:
        return UNREACHABLE
    if not result.get("matched"):
        return None
    step_id = result.get("step_id")
    step = next((s for s in steps if s["id"] == step_id), None)
    if step is None:
        return None  # defensive: an unrecognised step_id counts as no match
    return step, result.get("value")


def guess_revenue_model(
    session_id: str, step: dict[str, Any], message: str, state: dict[str, Any]
) -> list[str] | None:
    """RMP-24 (S5-B1): the server's own guess (by meaning, P2233) at step 5's revenue_model,
    for a typed sentence `match_typed_reply` found no exact match for at all. ADVISORY only --
    the caller (`revenue_suggest.py`) must confirm it with the customer before it counts as
    their answer. Returns `None` for "no guess" AND for "server unreachable" alike (unlike
    `match_typed_reply`'s `UNREACHABLE` sentinel) -- a guess is never load-bearing enough to
    need that distinction; ask-again-not-guess still holds because nothing is ever saved from
    this function's result alone."""
    body = {
        "mode": "guess",
        "step": {"step_id": step["id"], "kind": "multi", "options": _step_options(step, state)},
        "message": message,
    }
    result = answer_match_client.call(session_id, body)
    if result is None or not isinstance(result.get("suggested"), list):
        return None
    suggested = result["suggested"]
    if not suggested or not all(isinstance(v, str) for v in suggested):
        return None
    return suggested
