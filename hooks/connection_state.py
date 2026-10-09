#!/usr/bin/env python3
"""Connection-probe state for Reach Machine plugin v2, step 1 (RMP-3, RMP-4,
RMP-7, RMP-48). Spec: docs/plugin-v2/01-connection-check.md.

This module holds step 1's state: what each probe found, whether attempted
(`probed`), and whether recorded against the customer's account. Three
callers: `connection_state_cli.py` (writes results, reads state),
`session_record.py` (reads/writes `recorded`, computes `expected_results`),
`connections_gate.py` (reads only).

CLI logic moved to `connection_state_cli.py` to keep this file under the
300-line limit as RMP-7 added the `recorded`/`probed` fields.

STATE FILE: one per session, `${TMPDIR:-/tmp}/rm-plugin-v2-connections-
<session_id>.json`, shaped
`{"reachmachine": bool, "apify": bool, "playwright": bool, "recorded": bool,
"probed": {"reachmachine": bool, "apify": bool, "playwright": bool}}`, PLUS
(RMP-10, RMP-19) `step_state.py`'s own `workspace`/`workspace_options`/
`human_answers`/`steps_passed` keys in this same file -- see `write_patch`
below for how the two writers never stomp each other. A missing or corrupt
file, or a missing key, reads as the safe default -- `read_state` never
makes a caller guard against a missing key.

WHY THE PROBE MUST MATCH EXACTLY. `judge_probe` only records when the call
is EXACTLY the probe (fixed `runId`/`url`). Customer's own later calls to
the same tool names never flip a result. `None` = "write nothing".

RMP-48: Apify/Playwright inputs must be FLAT (raw `tool_input`, NOT
unwrapped). A wrapped call returns None (not a probe). Also returns None for
"Invalid arguments" errors (input mistake, not a connection result).
`probe_input_hint` delivers the correction same-turn.

FAIL-SAFE DIRECTION (different from the gate, on purpose): a malformed
payload, a missing session_id, or an unwritable temp dir must never crash a
tool call. `read_state` fails to "all False", and every write here catches
its own exceptions. The GATE (P1596) is what fails closed -- this file only
has to not crash.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
from typing import Any

import probe_input_hint
import state_file_io
from payload_util import tool_args
from plugin_api import server_of  # noqa: F401 -- re-exported, RMP-177 scopes this to OUR plugin name

PROBE_RUN_ID: str = "rmp-connection-probe-000"
PROBE_URL: str = "https://example.com/"
SERVERS: tuple[str, ...] = ("reachmachine", "apify", "playwright")


def state_path(session_id: str) -> pathlib.Path:
    tmp_dir = os.environ.get("TMPDIR") or "/tmp"
    return pathlib.Path(tmp_dir) / f"rm-plugin-v2-connections-{session_id}.json"


def _empty_state() -> dict[str, Any]:
    return {
        "reachmachine": False,
        "apify": False,
        "playwright": False,
        "recorded": False,
        "probed": {server: False for server in SERVERS},
    }


def read_state(session_id: str) -> dict[str, Any]:
    """All three servers + `recorded` + `probed`, defaulting to false for
    anything missing, corrupt, or not the right type."""
    result = _empty_state()
    try:
        raw = state_path(session_id).read_text(encoding="utf-8")
    except Exception:
        # Not just OSError (missing file) -- invalid UTF-8 bytes raise
        # UnicodeDecodeError here, and this must fail to "all False" exactly
        # like a missing or JSON-corrupt file, never crash the caller.
        return result
    try:
        data = json.loads(raw)
    except Exception:
        return result
    if not isinstance(data, dict):
        return result
    for server in SERVERS:
        value = data.get(server)
        if isinstance(value, bool):
            result[server] = value
    recorded = data.get("recorded")
    if isinstance(recorded, bool):
        result["recorded"] = recorded
    probed = data.get("probed")
    if isinstance(probed, dict):
        for server in SERVERS:
            value = probed.get(server)
            if isinstance(value, bool):
                result["probed"][server] = value
    return result


def read_raw(session_id: str) -> dict[str, Any]:
    """The state file's raw top-level dict, unfiltered -- unlike `read_state`,
    this does NOT reduce it to this module's own known keys. `step_state.py`
    (RMP-10, RMP-19) reads its own new keys (`workspace`, `human_answers`,
    `steps_passed`, ...) out of this SAME file this way. Fails to `{}`, never
    raises -- same direction as everything else here."""
    try:
        raw = state_path(session_id).read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def write_patch(session_id: str, patch: dict[str, Any]) -> None:
    """Merges `patch` onto whatever is ALREADY in the file, so a caller that
    only knows its own keys can never wipe out a sibling caller's -- this
    module's own `write_result`/`set_recorded` and `step_state.py`'s writers
    both go through this one function now that they share one file. Never
    raises."""
    # RMP-21: locked + atomic -- see `state_file_io` for the live bug (a
    # concurrent write wiped the probe keys and the gate denied step 1).
    state_file_io.update_json(state_path(session_id), lambda: read_raw(session_id), patch)


def write_result(session_id: str, server: str, ok: bool) -> None:
    """Records a probe outcome AND that the probe was attempted at all --
    the second part is what lets `expected_results` tell "broken" (probed,
    failed) apart from "needs_signin" (never probed), spec §3."""
    if server not in SERVERS:
        return
    state = read_state(session_id)
    state[server] = ok
    state["probed"][server] = True
    write_patch(session_id, {server: ok, "probed": state["probed"]})


def set_recorded(session_id: str) -> None:
    """`record_session_start` succeeded (RMP-7 §2/§3): the fourth check."""
    write_patch(session_id, {"recorded": True})


def all_passed(session_id: str) -> bool:
    """All three connections true AND the session is recorded (spec §3:
    "no session can run without leaving its log entry")."""
    state = read_state(session_id)
    return (
        all(state.get(server) is True for server in SERVERS)
        and state.get("recorded") is True
    )


def expected_results(session_id: str) -> dict[str, str]:
    """What the model is allowed to report to `record_session_start`,
    computed by the hooks, never trusted from the model (spec §2). For each
    server: "ok" if it passed; "broken" if a probe ran and failed;
    "needs_signin" if no probe for it ever ran this session."""
    state = read_state(session_id)
    result: dict[str, str] = {}
    for server in SERVERS:
        if state.get(server) is True:
            result[server] = "ok"
        elif state.get("probed", {}).get(server) is True:
            result[server] = "broken"
        else:
            result[server] = "needs_signin"
    return result


def reset_state(session_id: str) -> None:
    """SessionStart: every session starts closed."""
    try:
        state_path(session_id).unlink(missing_ok=True)
    except Exception:
        pass


def flatten_response_text(tool_response: Any) -> str:
    """`tool_response` can be a list of {"type":"text","text":...} blocks, a
    dict, or a string (spec, "Facts measured"). One helper flattens all
    three to plain text, so callers never have to branch on shape."""
    if isinstance(tool_response, str):
        return tool_response
    if isinstance(tool_response, dict):
        parts: list[str] = []
        text = tool_response.get("text")
        if isinstance(text, str):
            parts.append(text)
        content = tool_response.get("content")
        if content is not None:
            parts.append(flatten_response_text(content))
        return "\n".join(parts)
    if isinstance(tool_response, list):
        parts = []
        for item in tool_response:
            if isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
            elif isinstance(item, str):
                parts.append(item)
        return "\n".join(parts)
    return ""


def judge_probe(payload: dict) -> tuple[str, bool] | None:
    """None = not a probe call, change nothing. Otherwise (server, pass?).

    Rules from spec's "Facts measured" table:
      reachmachine — always counts (get_billing_status takes no arguments).
        PASS: PostToolUse and response contains `"plan"`.
      apify — counts only when tool_input.runId == PROBE_RUN_ID (RMP-48:
        flat input, not unwrapped). PASS: PostToolUseFailure and `error`
        contains "not found". PostToolUse SUCCESS is FAIL.
      playwright — counts only when tool_input.url == PROBE_URL (RMP-48:
        flat input). PASS: PostToolUse and response contains "Page Title:
        Example Domain".

    RMP-48: "Invalid arguments" error is never a connection result. Returns
    None (see probe_input_hint module).
    """
    if not isinstance(payload, dict):
        return None
    tool_name = payload.get("tool_name")
    server = server_of(tool_name)
    if server is None:
        return None
    assert isinstance(tool_name, str)  # server_of already required this

    event = payload.get("hook_event_name")
    # RMP-48: reachmachine uses tool_args (wrapped); apify/playwright use flat.
    if server == "reachmachine":
        tool_input = tool_args(payload)
    else:
        raw = payload.get("tool_input")
        tool_input = raw if isinstance(raw, dict) else {}

    # RMP-48: "Invalid arguments" errors never count as connection results.
    if event == "PostToolUseFailure" and probe_input_hint.is_input_error(payload):
        return None

    if server == "reachmachine":
        if not tool_name.endswith("__get_billing_status"):
            return None
        if event == "PostToolUse":
            text = flatten_response_text(payload.get("tool_response"))
            return ("reachmachine", '"plan"' in text)
        return ("reachmachine", False)

    if server == "apify":
        if not tool_name.endswith("__get-actor-run"):
            return None
        if tool_input.get("runId") != PROBE_RUN_ID:
            return None
        if event == "PostToolUseFailure":
            error = payload.get("error")
            error_text = error if isinstance(error, str) else ""
            return ("apify", "not found" in error_text.lower())
        return ("apify", False)

    if server == "playwright":
        if not tool_name.endswith("__browser_navigate"):
            return None
        if tool_input.get("url") != PROBE_URL:
            return None
        if event == "PostToolUse":
            text = flatten_response_text(payload.get("tool_response"))
            return ("playwright", "Page Title: Example Domain" in text)
        return ("playwright", False)

    return None


if __name__ == "__main__":
    # The CLI now lives in connection_state_cli.py. This module is a state
    # library, imported by that file, by session_record.py, and by the gate
    # -- it is never invoked directly by a hook anymore.
    print(
        "connection_state.py has no CLI of its own; run connection_state_cli.py",
        file=sys.stderr,
    )
    sys.exit(1)
