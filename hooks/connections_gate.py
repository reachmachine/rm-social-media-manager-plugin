#!/usr/bin/env python3
"""PreToolUse gate for plugin v2 step 1 (RMP-5, RMP-6, RMP-7).

Spec: docs/plugin-v2/01-connection-check.md, "How the hard stop is
enforced", and docs/plugin-v2/01b-session-log.md, "2 · The model cannot
misreport the results". Until all three connections have passed AND the
session is recorded (per `connection_state.all_passed`), this denies
everything on this plugin's three MCP servers except the probe calls
themselves, `browser_close`, and a correctly-verified `record_session_start`
call, and denies every `Skill` call for one of THIS plugin's other skills
except the `connection-check` skill itself. A skill call for anything else
(v1, graphify, another plugin) is never this gate's business.

Imports `read_state`, `server_of`, `PROBE_RUN_ID`, `PROBE_URL`,
`all_passed`, `expected_results` from the sibling `connection_state.py`, and
`read_queue` from `session_record.py` -- the same files
`record-connection-probe.sh` writes through -- so the gate can never read a
shape the recorder didn't write.

RECORD_SESSION_START (RMP-7): the model cannot misreport what the probes
found. A call to `…_reachmachine__record_session_start` is allowed while
the gate is otherwise closed ONLY IF `tool_input.client_session_id` matches
this session, `tool_input.results` matches `expected_results(session_id)`
exactly, and `tool_input.earlier_checks` matches the local queue's current
content exactly. This must go through Python, because it needs the state --
prompts/COMMS.md records the decision NOT to add this to the bash wrapper's
plain-text pre-allow list. If Python is missing, this call is denied like
everything else (fails closed) and the customer sees the generic reason.

FAILS CLOSED (the opposite of `connection_state.py`'s recorder, and of v1's
spend hook, deliberately): a state or plugin.json read failure, or stdin
that is not valid JSON, denies. The two things that must stay allowed even
through a crash -- the probe calls, and the `connection-check` skill -- are
handled by the BASH WRAPPER in plain text before this file ever runs (see
`connections-gate.sh`), because a missing `python3` must not be able to trap
either of them.

ONE DOCUMENTED JUDGEMENT CALL (flagged in prompts/COMMS.md for the
architect): the spec's decision table assumes the plugin's own name always
resolves. If `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json` cannot be
read even though python IS available, this file cannot tell "this plugin's
other skill" apart from "an unrelated plugin's skill" -- there is no name to
compare against. It denies that Skill call rather than guessing, on the
same "fails closed" reasoning as everything else here, accepting the small
risk of one unrelated plugin's skill call being blocked during an already-
broken configuration (its own plugin.json is presumably in the same broken
state) rather than silently opening this plugin's own gate.

RMP-79 part 2: `decide` (the public entry point) now wraps the real
decision logic below (`_decide`) with `session_stamp.apply` -- see that
module's own docstring for the full "why" and what it does and does not
change.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

_HOOKS_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_HOOKS_DIR))
import apify_actor_gate  # noqa: E402
import connection_deny_text as deny_text  # noqa: E402
import deny_lines  # noqa: E402
import hangouts_run_gate  # noqa: E402
from connection_state import (  # noqa: E402
    PROBE_RUN_ID,
    PROBE_URL,
    all_passed,
    expected_results,
    read_state,
    server_of,
)
from payload_util import tool_args  # noqa: E402
import session_stamp  # noqa: E402
from session_record import read_queue  # noqa: E402
import step_gate  # noqa: E402
import website_gate  # noqa: E402

# RMP-76: the denial texts live in `connection_deny_text.py` (customer-visible).
_GENERIC_DENY_REASON = deny_text.GENERIC_DENY_REASON
_RECORD_MISMATCH_REASON = deny_text.RECORD_MISMATCH_REASON
_ALL_CONNECTED_NOT_RECORDED_REASON = deny_text.ALL_CONNECTED_NOT_RECORDED_REASON


def _deny(reason_id: str, **fill: object) -> dict:
    return deny_lines.deny_id(reason_id, **fill)


def _plugin_name() -> str | None:
    root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if not root:
        return None
    try:
        raw = (pathlib.Path(root) / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        data = json.loads(raw)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    name = data.get("name")
    return name if isinstance(name, str) and name else None


def _is_probe_call(tool_name: str, tool_input: dict) -> bool:
    server = server_of(tool_name)
    if server == "reachmachine":
        return tool_name.endswith("__get_billing_status")
    if server == "apify":
        return tool_name.endswith("__get-actor-run") and tool_input.get("runId") == PROBE_RUN_ID
    if server == "playwright":
        return tool_name.endswith("__browser_navigate") and tool_input.get("url") == PROBE_URL
    return False


def _decide_record_session_start(tool_input: dict, session_id: str) -> dict | None:
    """RMP-7: allowed while otherwise closed only if the model sent back
    exactly what the hooks themselves found -- see module docstring."""
    if all_passed(session_id):
        return None
    if tool_input.get("client_session_id") != session_id:
        return _deny(_RECORD_MISMATCH_REASON)
    if tool_input.get("results") != expected_results(session_id):
        return _deny(_RECORD_MISMATCH_REASON)
    if tool_input.get("earlier_checks") != read_queue():
        return _deny(_RECORD_MISMATCH_REASON)
    return None


def _missing_denial(session_id: str) -> dict:
    """The refusal for "step 1 is not open yet" -- see `connection_deny_text.missing_reason` (0/1/2/3 missing)."""
    reason_id, fill = deny_text.missing_reason(read_state(session_id))
    return _deny(reason_id, **fill)


def _decide(payload: dict) -> dict | None:
    """None = allow. Otherwise the deny dict to print."""
    tool_name = payload.get("tool_name")
    if not isinstance(tool_name, str):
        return None

    # RMP-5: every Reach Machine tool's real input sits one level down, under
    # `tool_input["args"]` -- `Skill`, apify and playwright are unwrapped, and
    # `tool_args` falls back to the flat value for those (see payload_util.py).
    tool_input = tool_args(payload)

    session_id = payload.get("session_id")
    session_id = session_id if isinstance(session_id, str) and session_id else ""

    if tool_name == "Skill":
        skill = tool_input.get("skill")
        skill = skill if isinstance(skill, str) else ""

        plugin_name = _plugin_name()
        if plugin_name is None:
            # See module docstring's "ONE DOCUMENTED JUDGEMENT CALL".
            return _deny(_GENERIC_DENY_REASON)

        own_prefix = f"{plugin_name}:"
        if skill == f"{own_prefix}connection-check":
            return None
        if not skill.startswith(own_prefix):
            return None  # someone else's plugin/skill -- not our concern
        if all_passed(session_id):
            return None
        return _missing_denial(session_id)

    server = server_of(tool_name)
    if server is None:
        return None

    if server == "reachmachine" and tool_name.endswith("__record_session_start"):
        return _decide_record_session_start(tool_input, session_id)

    if _is_probe_call(tool_name, tool_input):
        return None
    if tool_name.endswith("__browser_close"):
        return None

    # RMP-66: off-site guard, playwright only, after the step 1 checks above
    # (the probe's own fixed navigate is already allowed by _is_probe_call).
    if server == "playwright" and tool_name.endswith("__browser_navigate"):
        deny = website_gate.check_navigate(tool_input, session_id)
        if deny is not None:
            return deny

    if all_passed(session_id):
        # RMP-202: cost/permission gate, apify only -- `call-actor` can run
        # ANY actor, so this checks the caller named one the server actually
        # approved for the current task (see apify_actor_gate.py's
        # docstring). Runs before step 1 could ever matter for it, since a
        # session with step 1 still open has never called `start_reviews_
        # fetch` (a reachmachine tool, itself denied before step 1 passes)
        # and so never has an allow-list to check against yet.
        if server == "apify" and tool_name.endswith("__call-actor"):
            deny = apify_actor_gate.check_call_actor(tool_input, session_id, payload.get("agent_id"))
            if deny is not None:
                return deny
        # P1853: a step 10 job may not read a dataset whose Apify run has not finished.
        if server == "apify" and tool_name.endswith("__get-dataset-items"):
            deny = hangouts_run_gate.check_dataset_items(tool_input, session_id, payload.get("agent_id"))
            if deny is not None:
                return deny
        # Step 1 is open -- steps 2+ (RMP-10, RMP-19) take over from here.
        return step_gate.decide(payload, session_id)
    return _missing_denial(session_id)


def decide(payload: dict) -> dict | None:
    """The public entry point. Runs the real step-1/step-N rules
    (`_decide`), then RMP-79 part 2: stamps an allowed Reach Machine call
    with this chat's `client_session_id` (`session_stamp.apply`) so the
    server can tell this chat's calls apart from another window's. Apify,
    Playwright, `Skill`, and any denied call pass through `_decide`'s
    result unchanged -- see `session_stamp.py`'s own docstring."""
    tool_name = payload.get("tool_name")
    decision = deny_lines.resolve(payload.get("session_id"), _decide(payload))   # RMP-291 P2321: the server's words
    if not isinstance(tool_name, str):
        return decision
    return session_stamp.apply(tool_name, tool_args(payload), payload.get("session_id"), decision)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        print(json.dumps(deny_lines.resolve("", _deny(_GENERIC_DENY_REASON))))
        return 0
    if not isinstance(payload, dict):
        print(json.dumps(deny_lines.resolve("", _deny(_GENERIC_DENY_REASON))))
        return 0

    try:
        result = decide(payload)
    except Exception:
        # Fails CLOSED: an unexpected crash anywhere inside decide() (a
        # corrupt state file with invalid UTF-8, an unreadable plugin.json,
        # anything not already anticipated) must deny, not let an unhandled
        # traceback exit non-zero with empty stdout -- the bash wrapper
        # treats empty stdout as "allow" (RMP-5, gate-fails-open fix).
        print(json.dumps(deny_lines.resolve("", _deny(_GENERIC_DENY_REASON))))
        return 0
    if result is not None:
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
