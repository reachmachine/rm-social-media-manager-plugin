#!/usr/bin/env bash
# PreToolUse hook (FRFRMU-1519), matcher: mcp__.*__(run_pipeline|run_pipeline_assist|
# run_pipeline_by_category|pull_data|add_to_watchlist|remove_competitor)$
#
# WHY THIS EXISTS: PLAYBOOK rule 6 says confirm-before-spend is a HUMAN gate --
# show the cost preview, then WAIT for the customer's explicit yes before the
# confirm=true call. The server checks that `confirm` is present; it cannot
# check that a person actually said yes, because it never sees the
# conversation. On 2026-09-15 a smoke test found the model could call the
# preview and the confirm=true call in the SAME turn, so a real customer would
# be charged for something they never approved. This hook closes that gap for
# the plugin channel by denying a confirm=true call unless a human message
# arrived after the matching preview.
#
# HOW IT KNOWS A HUMAN SPOKE: every hook payload carries `prompt_id`, a UUID
# for the user prompt currently being processed. A new `prompt_id` means a new
# human message. A preview call (no confirm=true) records
# {tool_name: {prompt_id, args_hash}} in a small per-session state file. A
# confirm=true call is only allowed when the SAME tool has a stored entry
# whose prompt_id differs from the confirm call's own prompt_id (a real turn
# boundary happened) AND whose args_hash matches (the customer said yes to
# THIS spend, not a different one -- 5 reels previewed cannot become 25
# confirmed). One yes covers one spend: a successful confirm deletes the
# entry, so the next spend needs its own preview.
#
# `deny`, not `ask`, on purpose: the hooks docs say a hook's `ask` overrides an
# existing permission DENY rule but not an ALLOW rule -- so a customer who once
# clicked "always allow" on a spend tool would never be prompted again. A
# `deny` is honoured in every permission mode, including auto and bypass.
#
# STATE. `${scratchpad_dir}/rm-spend-gate.json` when the payload carries
# scratchpad_dir (2.1.257+), else `${TMPDIR:-/tmp}/rm-spend-gate-<session_id>.
# json` -- keyed by the FULL tool name, never the suffix, because this box can
# have reachmachine-dev and reachmachine-prod connected at once and a preview
# on one must never authorise a confirm on the other. A corrupt state file
# (readable, not JSON) is treated as empty, which is safe: the model just gets
# asked to re-preview.
#
# WHAT THIS DOES NOT CHECK, ON PURPOSE: whether the human's words were
# actually a "yes". A "no" followed by a confirm is still a new turn and
# passes this gate -- that judgment stays with the model and the eval suite /
# process-check record (FRFRMU-1531), not with this script. This script also
# never reads the transcript: the hooks docs warn it may lag the live
# conversation at PreToolUse time, so parsing it could deny a real yes that
# has not been flushed yet.
#
# FAILS OPEN: no python3/python on the machine; stdin is not JSON; `prompt_id`
# or `session_id` missing from the payload AND `agent_id` also absent (a
# genuinely old Claude Code build in a main session -- the server confirm gate
# and 24h spend ceiling still apply). The state directory cannot be created or
# written after trying both candidate locations -- never trap a customer whose
# temp dir happens to be read-only.
#
# NEVER FAILS OPEN FOR: a confirm=true call inside a sub-agent (`agent_id`
# present) with `prompt_id` missing -- a sub-agent can never receive a human
# yes mid-run, so denying costs nothing and letting it through would make
# every spend routed through a sub-agent ungated. Also never fails open for a
# missing preview entry, a same-prompt_id (same-turn) preview, or an
# args_hash mismatch -- those three are the deny cases this hook exists for.

PY=python3
"$PY" -c "" >/dev/null 2>&1 || PY=python
"$PY" -c "" >/dev/null 2>&1 || exit 0

CODE='
import hashlib
import json
import os
import re
import sys

GATED_SUFFIXES = (
    "run_pipeline",
    "run_pipeline_assist",
    "run_pipeline_by_category",
    "pull_data",
    "add_to_watchlist",
    "remove_competitor",
)
MATCHER = re.compile("mcp__.*__(" + "|".join(GATED_SUFFIXES) + ")$")


def deny(reason):
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )
    sys.stdout.write("\n")
    sys.exit(0)


def compute_args_hash(args):
    if not isinstance(args, dict):
        args = {}
    cleaned = {
        key: value
        for key, value in args.items()
        if key not in ("confirm", "dry_run", "preview_fingerprint")
    }
    blob = json.dumps(cleaned, sort_keys=True, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def resolve_paths(payload):
    paths = []
    scratchpad_dir = payload.get("scratchpad_dir")
    if scratchpad_dir:
        paths.append(os.path.join(str(scratchpad_dir), "rm-spend-gate.json"))
    tmp_dir = os.environ.get("TMPDIR") or "/tmp"
    session_id = payload.get("session_id") or "unknown"
    paths.append(os.path.join(tmp_dir, "rm-spend-gate-" + str(session_id) + ".json"))
    return paths


def pick_usable_path(paths):
    for path in paths:
        directory = os.path.dirname(path) or "."
        try:
            os.makedirs(directory, exist_ok=True)
            probe = path + ".probe"
            with open(probe, "w", encoding="utf-8") as fh:
                fh.write("")
            os.remove(probe)
            return path
        except OSError:
            continue
    return None


def load_state(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = fh.read()
    except OSError:
        return {}
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_state(path, state):
    try:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(state, fh)
    except OSError:
        pass


try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(0)

if not isinstance(payload, dict):
    sys.exit(0)

tool_name = payload.get("tool_name")
if not isinstance(tool_name, str) or not MATCHER.search(tool_name):
    sys.exit(0)

tool_input = payload.get("tool_input")
if not isinstance(tool_input, dict):
    tool_input = {}
args = tool_input.get("args", tool_input)
if not isinstance(args, dict):
    args = {}

confirm = args.get("confirm") is True

agent_id = payload.get("agent_id")
prompt_id = payload.get("prompt_id")
session_id = payload.get("session_id")

if agent_id is not None and prompt_id is None:
    if confirm:
        deny(
            "This call is running inside a sub-agent, which has no way to "
            "know whether a human said yes. A sub-agent can never confirm a "
            "spend on its own; run the confirm from the main session after "
            "the human has answered."
        )
    sys.exit(0)

if (prompt_id is None or session_id is None) and agent_id is None:
    # Old Claude Code build in a main session -- the server confirm gate and
    # 24h spend ceiling still apply even when this guard cannot run.
    sys.exit(0)

state_path = pick_usable_path(resolve_paths(payload))
if state_path is None:
    # State store unavailable this session -- never trap a customer.
    sys.exit(0)

state = load_state(state_path)
args_hash = compute_args_hash(args)

if not confirm:
    entry = state.get(tool_name)
    if entry is None or entry.get("args_hash") != args_hash:
        state[tool_name] = {"prompt_id": prompt_id, "args_hash": args_hash}
        save_state(state_path, state)
    sys.exit(0)

entry = state.get(tool_name)
if entry is None:
    deny(
        "This tool needs a cost preview shown to the customer before it "
        "runs with confirm=true. Call the same tool without confirm=true "
        "first, show the customer that preview, and wait for a fresh yes "
        "before confirming."
    )

if entry.get("prompt_id") == prompt_id:
    deny(
        "The cost preview for this tool was shown in this same turn, so no "
        "human has had a chance to answer yet. If the customer already said "
        "yes after seeing the preview, do not show the preview again -- "
        "wait for their fresh yes."
    )

if entry.get("args_hash") != args_hash:
    deny(
        "This confirm call does not match what was shown to the customer in "
        "the preview (different reels, count, or options). Show a fresh "
        "preview for exactly what is about to run, then wait for a fresh "
        "yes."
    )

state.pop(tool_name, None)
save_state(state_path, state)
sys.exit(0)
'

"$PY" -c "$CODE"
exit 0
