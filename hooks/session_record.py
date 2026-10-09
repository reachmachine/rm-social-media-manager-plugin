#!/usr/bin/env python3
"""RMP-7: recording each session's connection check, and the local queue for
when Reach Machine itself is down.

Spec: docs/plugin-v2/01b-session-log.md, §3-5.

This file owns everything about `record_session_start` that is NOT the core
three-probe state (that stays in `connection_state.py`, imported here):
  - "is this round of probing finished" (`check_complete`);
  - the local queue at `~/.claude/rm-plugin-v2/pending-checks.jsonl`
    (`read_queue`/`append_queue`/`clear_queue`), used when a check finishes
    while Reach Machine is not `ok` and the record call cannot reach the
    server at all;
  - reading `record_session_start`'s own response to decide whether it
    really succeeded (`response_confirms_recorded`), and clearing the queue
    only once the server confirms it received everything that was sent
    (`handle_record_session_start`);
  - the exact payload the reminder hands the model to copy
    (`build_reminder_payload`).

FAIL-SAFE: same direction as `connection_state.py` -- nothing here may crash
a hook. Every function that touches a file catches its own exceptions. The
CLI (`connection_state_cli.py`) additionally wraps every call into this
module in its own try/except, so a bug here degrades to "nothing recorded,
nothing queued" rather than a crashed tool call.
"""
from __future__ import annotations

import datetime
import json
import os
import pathlib
import re
from typing import Any

import connection_state as cs
import state_file_io
import transcript_cursor as tc
from payload_util import tool_args

QUEUE_MAX_LINES = 20
QUEUE_FILENAME = "pending-checks.jsonl"

# P1636: same "tolerant of a not-quite-clean JSON response" fallback
# `response_confirms_recorded` already uses for `"recorded": true` --
# `_parse_record_response` failing to parse must not silently lose the
# upload key.
_UPLOAD_KEY_RE = re.compile(r'"upload_key"\s*:\s*"([^"]+)"')


def check_complete(state: dict[str, Any]) -> bool:
    """"A check that fails because Reach Machine itself is down is not
    lost" (spec §4) needs to know when a round of probing is over. The
    skill always tries reachmachine FIRST (01-connection-check.md, "Run the
    three probes"), so by the time apify AND playwright have both been
    probed, reachmachine has either also been probed (all three ran this
    round), or its probe tool was never available this session (needs
    sign-in) and never will be probed this round. So "apify and playwright
    both probed" covers both halves of the spec's own definition: "all
    three probes have run, or reachmachine's probe is absent and the other
    two have run."."""
    probed = state.get("probed") or {}
    return probed.get("apify") is True and probed.get("playwright") is True


def _plugin_home() -> pathlib.Path:
    override = os.environ.get("RM_PLUGIN_V2_HOME")
    if override:
        return pathlib.Path(override)
    return pathlib.Path.home() / ".claude" / "rm-plugin-v2"


def _queue_path() -> pathlib.Path:
    return _plugin_home() / QUEUE_FILENAME


def read_queue() -> list[dict]:
    """Oldest-first. Skips any line that is not valid JSON or not an
    object, and treats a wholly unreadable file (missing, not UTF-8, no
    permission) as an empty queue -- never raises."""
    try:
        raw = _queue_path().read_text(encoding="utf-8")
    except Exception:
        return []
    entries: list[dict] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except Exception:
            continue
        if isinstance(data, dict):
            entries.append(data)
    return entries


def _write_queue(entries: list[dict]) -> None:
    try:
        path = _queue_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        body = "".join(json.dumps(e) + "\n" for e in entries)
        state_file_io.write_atomic(path, body)
    except Exception:
        pass


def append_queue(entry: dict) -> None:
    """Dedupe by `client_session_id` (last one wins for this session), then
    keep only the last QUEUE_MAX_LINES entries (spec §4: "at most 20
    entries; older ones are dropped")."""
    try:
        with state_file_io.locked(_queue_path()):  # RMP-76: read + rewrite as one step
            entries = read_queue()
            session_id = entry.get("client_session_id")
            if isinstance(session_id, str) and session_id:
                entries = [e for e in entries if e.get("client_session_id") != session_id]
            entries.append(entry)
            entries = entries[-QUEUE_MAX_LINES:]
            _write_queue(entries)
    except Exception:
        pass


def clear_queue() -> None:
    try:
        _queue_path().unlink(missing_ok=True)
    except Exception:
        pass


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _plugin_version() -> str:
    candidates: list[pathlib.Path] = []
    root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if root:
        candidates.append(pathlib.Path(root) / ".claude-plugin" / "plugin.json")
    candidates.append(
        pathlib.Path(__file__).resolve().parent.parent / ".claude-plugin" / "plugin.json"
    )
    for path in candidates:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        version = data.get("version") if isinstance(data, dict) else None
        if isinstance(version, str) and version:
            return version
    return "unknown"


def maybe_queue_check(session_id: str) -> None:
    """Called after every probe write. If this round is `check_complete`
    and Reach Machine did not pass, the check cannot be sent right now --
    queue it locally instead (spec §4)."""
    try:
        state = cs.read_state(session_id)
        if not check_complete(state):
            return
        if state.get("reachmachine") is True:
            return  # reachmachine ok -> record_session_start can be sent directly
        append_queue(
            {
                "client_session_id": session_id,
                "plugin_version": _plugin_version(),
                "results": cs.expected_results(session_id),
                "checked_at": _now_iso(),
            }
        )
    except Exception:
        pass


def build_reminder_payload(session_id: str) -> dict:
    """The exact JSON the reminder hands the model to copy verbatim into
    `record_session_start` (spec §6, prompt step 6)."""
    return {
        "client_session_id": session_id,
        "plugin_version": _plugin_version(),
        "results": cs.expected_results(session_id),
        "earlier_checks": read_queue(),
    }


def build_reminder_text(session_id: str) -> str | None:
    """The exact prose+JSON line handed to the model once step 1's check is
    `check_complete` and not yet `recorded` -- shared by the UserPromptSubmit
    reminder (`connection_state_cli._cli_reminder`) and, since P1612, the
    IMMEDIATE PostToolUse/PostToolUseFailure delivery
    (`connection_state_cli._connection_check_message`), so the two channels
    can never say something different. Returns None only if the payload
    itself cannot be serialised (never expected in practice -- every field
    is a plain str/dict/list).

    RMP-198 structural fix (2026-09-27): the earlier version only named the
    tool to call -- staying silent and closing the browser were left to
    SKILL.md prose, including one negative example of the exact leaked
    line, which likely primed a paraphrase of itself (RMP-159 part 5's
    known failure mode). This text now hands the model the literal next
    actions, the same "relay, don't decide" shape RMP-159 part 6 used for
    the final report, one step earlier."""
    try:
        payload_json = json.dumps(build_reminder_payload(session_id))
    except Exception:
        return None
    parts = ["Write nothing yet."]
    if cs.expected_results(session_id).get("playwright") == "ok":
        parts.append("Call browser_close.")
    parts.append("Call record_session_start with exactly this payload: " + payload_json + ".")
    parts.append(
        "Then say only record_session_start's own say result if it has "
        "one, or connection-check's own table if it does not -- nothing "
        "else, nothing about these calls."
    )
    return " ".join(parts)


def _parse_record_response(tool_response: Any) -> dict[str, Any] | None:
    text = cs.flatten_response_text(tool_response)
    try:
        data = json.loads(text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def response_confirms_recorded(tool_response: Any) -> bool:
    data = _parse_record_response(tool_response)
    if data is not None:
        return data.get("recorded") is True
    # The response wasn't clean JSON (extra text around it, say) -- fall
    # back to the same "substring in flattened text" convention the probes
    # themselves use (`'"plan"' in text`), tolerant of spaced vs unspaced
    # JSON (`json.dumps` vs Claude Code's own compact payloads).
    text = cs.flatten_response_text(tool_response)
    return bool(re.search(r'"recorded"\s*:\s*true', text))


def _extract_upload_key(tool_response: Any) -> str | None:
    """RMP-27/RMP-45: `record_session_start`'s response carries `upload_key`
    (docs/plugin-v2/01c-session-transcript.md §5) alongside `recorded` --
    same parsing helper (`_parse_record_response`), plus the same
    regex-on-flattened-text fallback `response_confirms_recorded` uses for
    `recorded`, so a response that is not perfectly clean JSON still hands
    the key over instead of losing it silently."""
    data = _parse_record_response(tool_response)
    if data is not None:
        key = data.get("upload_key")
        return key if isinstance(key, str) and key else None
    match = _UPLOAD_KEY_RE.search(cs.flatten_response_text(tool_response))
    return match.group(1) if match else None


def handle_record_session_start(session_id: str, payload: dict) -> None:
    """PostToolUse of `record_session_start` (RMP-7 §2/§3): mark this
    session `recorded`, then clear the local queue only if the server
    confirms it received everything this call sent -- `earlier_recorded`
    equal to what was sent, or `earlier_recorded + earlier_dropped` equal
    to it (spec §4, prompt step 5).

    RMP-27/RMP-45: after that existing logic, also save `upload_key` (if
    the response carried one) to this session's transcript cursor file --
    wrapped in its own try/except so a problem here can never stop the
    `recorded`/queue logic above from doing its job."""
    if payload.get("hook_event_name") != "PostToolUse":
        return
    tool_response = payload.get("tool_response")
    if not response_confirms_recorded(tool_response):
        return
    cs.set_recorded(session_id)

    try:
        upload_key = _extract_upload_key(tool_response)
        if upload_key:
            tc.save_upload_key(session_id, upload_key)
    except Exception:
        pass

    # RMP-5/RMP-7: record_session_start's real input is wrapped -- see
    # payload_util.tool_args.
    tool_input = tool_args(payload)
    sent = tool_input.get("earlier_checks")
    sent_count = len(sent) if isinstance(sent, list) else 0

    data = _parse_record_response(tool_response) or {}
    recorded_n = data.get("earlier_recorded")
    dropped_n = data.get("earlier_dropped")
    matched = isinstance(recorded_n, int) and recorded_n == sent_count
    matched = matched or (
        isinstance(recorded_n, int)
        and isinstance(dropped_n, int)
        and (recorded_n + dropped_n) == sent_count
    )
    if matched:
        clear_queue()
