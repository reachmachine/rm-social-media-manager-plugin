#!/usr/bin/env python3
"""PostToolUse / UserPromptSubmit recorder for question steps 2+ (RMP-10,
RMP-19).

Spec: docs/plugin-v2/02-workspace-selection.md, docs/plugin-v2/03-whose-
account.md "The reusable question step". Called from
`connection_state_cli.py`'s `record`/`reminder` entry points, the SAME
scripts step 1's own recorder (`session_record.py`) is reached through.

CAPTURING THE CUSTOMER'S ANSWER:
  - `AskUserQuestion`'s result carries the choice in `tool_response.answers`
    (question text -> chosen option LABEL string), confirmed against the
    installed Claude Code 2.1.280 build (Agent SDK TypeScript reference,
    `AskUserQuestionOutput.answers: Record<string, string>`, and the tool's
    own schema description found in the binary: "The answers provided by the
    user (question text -> answer string; multi-select answers are
    comma-separated)"). This is `tool_response`, NOT `tool_input` -- the
    PreToolUse `tool_input` schema for this tool has no `answers` field at
    all (Claude never sets it going in). See prompts/COMMS.md for the
    correction against the prompt's original text.
  - The headless fallback (`handle_typed_answer`) reads `payload["prompt"]`,
    the UserPromptSubmit event's own field for the customer's typed text
    (Claude Code hooks reference) -- never model text, because this hook
    only ever fires on a human-submitted prompt.

P1615: the QUESTION TEXT (the `answers` dict's own key) is what an answer is
matched against, via `answer_matcher.step_for_question_text` -- never "the
next step not yet in steps_passed". The old rule permanently skipped past
`choose_workspace` once it had passed once, so a later "switch workspace"
pick, or a changed answer for `account_owner_type`, was silently dropped
before the gate ever saw it (see `answer_matcher.py`'s own docstring for the
full bug report). The typed (headless) fallback matches every question
step's own live options the same way, in `answer_matcher.match_typed_reply`.
Neither path runs before `connection_check` itself has passed -- there is
nothing to match yet.

RECORDING REAL TOOL RESULTS: `list_workspaces` -> `workspace_options`; `set_active_workspace`
(confirmed) -> `workspace`, resets the previous workspace's progress (RMP-9, `step_state.reset_
for_new_workspace`); `get_creator_brief`/`update_creator_brief` -> `already_known`/`answered` for
a single-answer step (`answer_type == "options"`), or delegated to `step_recorder_revenue.py` for
step 5's own two-question shape (P1627, RMP-38). `record_session_event`, `get_resume_checklist`
and `record_checklist_step` (RMP-9, RMP-18) are handled by the sibling `checklist_recorder.py`,
imported (via `step_recorder_dispatch.py`, RMP-96 -- see that module's own docstring for why it
was split out) into `_POST_TOOL_USE_HANDLERS`, so there is still one place PostToolUse events are
wired, not two.

FAIL-SAFE: nothing here may crash a hook. Every entry point is wrapped by
its caller in `connection_state_cli.py`; every parse failure here degrades
to "nothing recorded", never an exception.
"""
from __future__ import annotations

import answer_captures
import answer_matcher
import connection_state as cs
import own_account_mismatch
import own_account_not_found
import own_account_suggestion
import payload_util
import revenue_suggest
import step_order
import step_recorder_revenue as revenue_recorder
import step_recorder_website as website_recorder
import step_rules_cache
import step_state
import steps_manifest
from step_recorder_dispatch import _POST_TOOL_USE_HANDLERS, _tool_suffix  # noqa: F401 -- re-exported, test_hooks_json_wiring.py reads step_recorder._POST_TOOL_USE_HANDLERS


# ------------------------------------------------------- AskUserQuestion --

def handle_ask_user_question(session_id: str, payload: dict) -> None:
    step_state.sync_connection_check(session_id)
    if not step_state.is_step_passed(session_id, "connection_check"):
        return  # step 1 not open yet -- nothing to match against

    tool_response = payload.get("tool_response")
    if not isinstance(tool_response, dict):
        return
    answers = tool_response.get("answers")
    if not isinstance(answers, dict) or len(answers) != 1:
        return  # ambiguous or empty -- never guess which question this answers
    ((question_text, label),) = answers.items()
    if not isinstance(question_text, str) or not isinstance(label, str):
        return

    # RMP-23, founder decision 6: a mismatch answer must NEVER be read as a
    # step answer -- checked BEFORE the normal step matching below.
    if own_account_mismatch.try_capture_ask_user_answer(session_id, question_text, label):
        return
    # RMP-52/RMP-66: skip/reoffer and website re-offer answers come BEFORE
    # step answers too -- see answer_captures.py for the exact order.
    if answer_captures.capture_ask_user_answer(session_id, question_text, label):
        return

    state = step_state.read_state(session_id)
    steps = steps_manifest.load_steps(session_id)
    step = answer_matcher.step_for_question_text(steps, question_text)
    if step is None:
        return  # matches no known step's question -- store nothing (spec)
    value = answer_matcher.match_label(session_id, step, label, state)
    if value is answer_matcher.UNREACHABLE:
        return  # RMP-76: server unreachable -- ask again, never guess
    if value is not None:
        step_state.set_human_answer(session_id, step["id"], value)
        if step["id"] == "own_instagram_account":
            own_account_mismatch.clear_on_new_handle(session_id)
            own_account_not_found.clear_on_new_handle(session_id)
            own_account_suggestion.clear_on_new_handle(session_id)
        elif step["id"] == "website":
            website_recorder.handle_website_question_answer(session_id, value)


# ------------------------------------------------ typed (headless) fallback --

def _handle_steps_waiting(steps: list[dict], state: dict) -> frozenset[str]:
    """Handle-type step ids waiting for their answer RIGHT NOW: not passed,
    no stored answer yet, no known own account (RMP-23, 04-own-instagram-
    account.md, "a bare word counts only while the plugin is waiting for a
    handle"), AND every EARLIER step (by `number`) has already passed --
    i.e. this step is actually the customer's current one, not merely "not
    finished yet".

    prompts/COMMS.md, 2026-09-24: without that last condition, step 4 counts
    as "waiting" from the very start of the session -- before step 3 is even
    answered -- and a plain step-3 reply like "own" (a real option VALUE for
    `account_owner_type`) is ALSO a valid handle-shaped bare word, so it ties
    across the two steps and gets stored nowhere. Same "cumulative, by step
    number" reasoning `step_gate._allowed_suffixes` already applies to tool
    gating, applied here to typed-answer matching too."""
    waiting: set[str] = set()
    for s in steps:
        if steps_manifest.answer_type(s) != "handle":
            continue
        if s["id"] in state["steps_passed"] or s["id"] in state["human_answers"]:
            continue
        if state["own_account_handle"]:
            continue
        if all(other["id"] in state["steps_passed"] for other in steps if other["number"] < s["number"]):
            waiting.add(s["id"])
    return frozenset(waiting)


def _own_account_change_signal(state: dict, message: str) -> bool:
    """RMP-168: the customer names a DIFFERENT own account than the one
    already on file, in a free message -- the RMP-113 "change the account"
    signal (`skills/own-instagram-account/SKILL.md`, "Changing the
    account"). Requires the own account to actually be set already (never
    fires off a passed-but-unset test fixture, or a stale `steps_passed`
    entry with no handle behind it), an explicit `@handle` (never a bare
    word here -- a passed step is never in `_handle_steps_waiting`), and
    that handle must differ from `own_account_handle` -- so the SAME handle
    typed again, or an unrelated `@someone` mentioned in passing, changes
    nothing."""
    current = state["own_account_handle"]
    if not current:
        return False
    candidate = answer_matcher.extract_handle(message, allow_bare=False)
    return candidate is not None and candidate != current


def _handle_steps_open_for_typed_match(
    steps: list[dict], state: dict, message: str, *, allow_change_signal: bool,
) -> frozenset[str]:
    """Handle-type step ids a typed reply may still match against.

    RMP-168 (live 2026-09-26): step 4 was excluded from matching outright
    once it was in `steps_passed` -- for ANY `how`, including `skipped`.
    That silently dropped two real customer messages: (1) "Not now" (skip)
    then later, in plain chat, "actually, add my Instagram account now:
    @nasa" -- there was no handle on file yet, only a spent skip; and (2)
    the RMP-113 "change the account" case above. Both are reopened here;
    an `answered` step with no change signal stays closed, same as before,
    so a spent, already-added answer is never silently overwritten by an
    unrelated `@mention`.

    `allow_change_signal` is False while ANOTHER step's own free-text
    window is open right now (step 5's description, step 6's website reply)
    -- that window's own reply must win a message like "@natgeotravel posts
    daily" (a business description that happens to name a handle), never
    step 4's change signal. Confirmed by `test_step5_redaction.py`'s own
    `handle_kept` vector, which went RED without this guard -- the message
    was swallowed as a (spurious) own-account change and never reached
    `revenue_recorder.capture_description_reply` at all."""
    open_ids: set[str] = set()
    for step in steps:
        if steps_manifest.answer_type(step) != "handle":
            continue
        how = state["steps_passed"].get(step["id"])
        if how != "answered":
            open_ids.add(step["id"])  # never passed, or spent by a skip -- always open
        elif allow_change_signal and _own_account_change_signal(state, message):
            open_ids.add(step["id"])
    return frozenset(open_ids)


def handle_typed_answer(session_id: str, payload: dict) -> None:
    step_state.sync_connection_check(session_id)
    if not step_state.is_step_passed(session_id, "connection_check"):
        return  # step 1 not open yet -- nothing to match against

    prompt_text = payload.get("prompt")
    if not isinstance(prompt_text, str) or payload_util.is_system_generated_prompt(prompt_text):
        return  # not the customer's own words (e.g. a background-task notification)
    message = prompt_text.strip().casefold()
    if not message:
        return

    # RMP-23, founder decision 6: a mismatch answer must NEVER be read as a
    # step answer -- checked BEFORE the normal step matching below. Only
    # consumes the message when it actually resolves to yes/no while a
    # mismatch is pending; any other typed reply falls through as normal.
    if own_account_mismatch.try_capture_typed_answer(session_id, message):
        return
    # RMP-52/RMP-66: skip/reoffer and website re-offer typed fallback -- see
    # answer_captures.py for the exact order.
    if answer_captures.capture_typed_answer(session_id, message, payload.get("transcript_path")):
        return

    state = step_state.read_state(session_id)
    steps = steps_manifest.load_steps(session_id)
    waiting = _handle_steps_waiting(steps, state)
    website_waiting = website_recorder.typed_answer_waiting(steps, state)
    revenue_waiting = revenue_recorder.description_waiting(
        steps, state, revenue_recorder.read_progress(session_id),
    )
    open_handle_steps = _handle_steps_open_for_typed_match(
        steps, state, message, allow_change_signal=not (website_waiting or revenue_waiting),
    )
    # The website step (P1668) is dropped entirely unless it is genuinely
    # the customer's current step -- its own option values ("yes", "later")
    # are plain English words a stray typed reply could otherwise match
    # long before step 6 is ever reached (see step_recorder_website.py's
    # own docstring).
    steps_for_matching = [
        s for s in steps
        if (steps_manifest.answer_type(s) != "handle" or s["id"] in open_handle_steps)
        and (s["id"] != "website" or website_waiting)
    ]
    current = step_order.first_unfinished(steps, state)
    hit = answer_matcher.match_typed_reply(
        session_id, steps_for_matching, state, message, bare_handle_steps=waiting,
        numbered_step_id=current["id"] if current is not None else None,
    )
    if hit is answer_matcher.UNREACHABLE:
        # RMP-76: server unreachable -- ask again, never guess. In
        # particular, never fall through to the P1627 line below: a
        # customer's real step-5 description reply must never be swallowed
        # as "not an answer" just because a network call failed, and a
        # customer's real answer must never be silently dropped either.
        return
    if hit is None:
        revenue_recorder.capture_description_reply(session_id, prompt_text)  # P1627
        revenue_suggest.maybe_guess_from_sentence(session_id, steps, state, message)  # RMP-24
        return
    step, value = hit
    step_state.set_human_answer(session_id, step["id"], value)
    if step["id"] == "own_instagram_account":
        own_account_mismatch.clear_on_new_handle(session_id)
        own_account_not_found.clear_on_new_handle(session_id)
        own_account_suggestion.clear_on_new_handle(session_id)
    elif step["id"] == "website":
        website_recorder.handle_website_question_answer(session_id, value)


# ------------------------------------------------------- real tool results --
# `get_creator_brief`/`update_creator_brief` and every other real tool result
# this plugin records against now live in `step_recorder_dispatch.py`
# (RMP-96) -- see that module's own docstring.


def handle(session_id: str, payload: dict) -> None:
    """PostToolUse dispatch, called from `connection_state_cli.py`'s
    `record` entry point for every tool this plugin now records against."""
    tool_name = payload.get("tool_name")
    if not isinstance(tool_name, str):
        return
    if payload.get("hook_event_name") != "PostToolUse":
        return  # only a successful result ever advances a question step

    if tool_name == "AskUserQuestion":
        handle_ask_user_question(session_id, payload)
        return

    if cs.server_of(tool_name) != "reachmachine":
        return
    suffix = _tool_suffix(tool_name)
    # RMP-173 P2: cache the server's step rules independently of whichever
    # handler below records this same call's other effects -- runs for both
    # cached tools, whether the call was confirmed, locked, or refused
    # (the server hands back rules_version/rules in every case, see
    # `agent_step_rules.rules_for_client`'s callers).
    if suffix in step_rules_cache.CACHED_TOOLS:
        step_rules_cache.maybe_cache_rules(session_id, payload)
    handler = _POST_TOOL_USE_HANDLERS.get(suffix)
    if handler is not None:
        handler(session_id, payload)
