"""
runner.py — headless Reach Machine -> creator content-plan agent.

Runs the `rm-content-planner` skill via the Claude Agent SDK against the Reach
Machine MCP server. The skill makes the agent understand the creator's business
FIRST, then build a stage-appropriate, non-mimicry content plan.

Prereqs (see README.md):
  pip install -r requirements.txt
  export ANTHROPIC_API_KEY=...   # your Anthropic API key
  export RM_MCP_TOKEN=...        # bearer / OAuth access token for the Reach Machine MCP
  export RM_MCP_URL=...          # optional — defaults to the public prod endpoint (_DEFAULT_RM_MCP_URL);
                                  # set this only to point at a different Reach Machine deployment (e.g. dev)

Usage:
  python runner.py --brief brief.md               # a markdown business brief (recommended)
  python runner.py --creator "@handle" --goal leads

  --brief is the RECOMMENDED path for an UNATTENDED run: a headless agent cannot
  stop and ask you questions (see the permission model below), so front-load the
  creator's business answers in the brief. Without them the plan is produced but
  stamped "GENERIC — positioning not provided".
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

from claude_agent_sdk import query, ClaudeAgentOptions

# repo root = the parent of the `.claude` directory this file lives under.
_HERE = pathlib.Path(__file__).resolve()
REPO_ROOT = next(p.parent for p in _HERE.parents if p.name == ".claude")

# Plugin root = the ancestor directory that owns `.claude-plugin/plugin.json`
# (this skill now lives at <plugin_root>/skills/rm-content-planner/, per the
# 2026-08-15 rm-social-media-manager plugin packaging). Found by walking up
# looking for the marker file, not a fixed parent-count, so this keeps working
# if the plugin is ever nested differently.
PLUGIN_ROOT = next(
    p for p in _HERE.parents if (p / ".claude-plugin" / "plugin.json").is_file()
)

# Public prod endpoint — same URL for every customer, not a secret. Only the
# per-user RM_MCP_TOKEN is ever required from the caller; RM_MCP_URL is a
# fill-in-the-blank default so most runs don't have to set it at all.
_DEFAULT_RM_MCP_URL = "https://api.reachmachine.org/mcp"

SYSTEM_PROMPT = (
    "You are a senior social media manager and short-form growth strategist. "
    "You build Instagram Reels content plans for ONE creator using the Reach "
    "Machine MCP. You ALWAYS understand the creator's business first (stage, "
    "positioning, first-party proof, the one audience, funnel assets, goal) "
    "before you pull any competitor data or plan anything. Follow the "
    "rm-content-planner skill and its PLAYBOOK exactly. Never present competitor "
    "mega-views as expected results, never recommend a CTA whose plumbing does "
    "not exist, never ship a near-clone of a source reel."
)

# --- Tool policy (claude-agent-sdk rulebook: A1/A2/A3/A7/A11/A115) -------------
# THE SAFETY MODEL, stated correctly (the earlier version got this wrong):
#   * `allowed_tools` AUTO-APPROVES — it does NOT restrict (rulebook A7:
#     "unlisted tools fall through to permission_mode and can_use_tool"). So
#     merely leaving the spend tools OUT of the allow-list does NOT block them.
#   * The wall is TWO explicit mechanisms:
#       1. permission_mode="dontAsk" — deny-by-default: anything not pre-approved
#          by `allowed_tools` is DENIED, and there is no prompt to hang on in an
#          unattended run (A115). This is what makes the allow-list act like a
#          restriction.
#       2. disallowed_tools = the spend/destructive tools — an explicit DENY,
#          which holds "in every permission mode, including bypassPermissions"
#          (A3). Belt-and-suspenders in case the mode is ever weakened.
#   * A11: never an MCP wildcard in an allow-list — list tools by name.
#
# Net effect headless: the planner can READ everything and update the business
# profile + creator brief (writes, but they do NOT spend credits), and CANNOT
# spend or destroy. Enabling unattended spend — and its per-run budget ceiling —
# is a founder decision tracked as G63 (marketing/engineering-gaps.md); do it by
# adding the tool here AND a real budget check (a can_use_tool callback), never a
# bare allow.
#
# G208(a): validate_content_plan is free, read-only, no workspace data touched
# by its base checks — it was missing from this list entirely, so under
# dontAsk it was DENIED, and Step 11.0's own fallback ("walk those same checks
# by hand") legalised a headless run silently losing its only code gate. One
# line, no security implication (it can't mutate anything).
#
# G208(c): submit_content_plan is DELIBERATELY NOT in this list (it used to
# be). Its `consent: true` field's entire contract is "a human just said
# yes" — a headless run has no human to ask, so any unattended call setting
# it true is fabricating consent, and Step 2.4's shortlist-approval gate is
# equally unreachable headless (its only downstream effect, add_to_watchlist,
# is already in the deny-list below, so removing it here is the one decision
# that closes both gates at once). See PLAYBOOK.md Step 12 for the full
# reasoning. This is a genuine "how much may headless do unsupervised"
# product call, made here as an engineering default: headless PRODUCES a
# plan, it does not PERSIST one.
_RM_NONSPEND_TOOLS = [
    "mcp__reachmachine__get_business_profile",
    "mcp__reachmachine__update_business_profile",   # write, does NOT spend — positioning capture
    "mcp__reachmachine__get_creator_brief",
    "mcp__reachmachine__update_creator_brief",       # write, does NOT spend — durable intake
    "mcp__reachmachine__validate_content_plan",      # read, free — the Step 11.0 code gate (G208a)
    "mcp__reachmachine__report_gap",                 # write, does NOT spend — logs a product gap
    "mcp__reachmachine__list_workspaces",
    "mcp__reachmachine__set_active_workspace",
    "mcp__reachmachine__get_workspace_stats",
    "mcp__reachmachine__get_analysis_coverage",
    "mcp__reachmachine__get_content_strategy",
    "mcp__reachmachine__get_content_breakdown",
    "mcp__reachmachine__get_content_structures",
    "mcp__reachmachine__get_hooks_library",
    "mcp__reachmachine__get_cta_library",
    "mcp__reachmachine__get_post_transcript",
    "mcp__reachmachine__get_posts_detailed",
    "mcp__reachmachine__get_profile_details",
    "mcp__reachmachine__get_profile_posts",
    "mcp__reachmachine__query_posts",
    "mcp__reachmachine__query_posts_by_tag",
    "mcp__reachmachine__get_tag_stats",
    "mcp__reachmachine__get_avg_scores",
    "mcp__reachmachine__get_credit_usage",
    "mcp__reachmachine__get_data_sources",
    "mcp__reachmachine__get_billing_status",
    "mcp__reachmachine__set_data_selection",         # write, does NOT spend — scopes a later read (G226)
    "mcp__reachmachine__clear_data_selection",        # write, does NOT spend — resets that scope (G226)
]

# Explicitly DENIED (A3 — a deny holds in every mode). Every tool that spends
# credits or destroys/changes shared state. dontAsk already denies anything not
# in the allow-list; this is the second wall if the mode is ever loosened.
_RM_SPEND_OR_DESTRUCTIVE_TOOLS = [
    "mcp__reachmachine__run_pipeline",
    "mcp__reachmachine__run_pipeline_assist",
    "mcp__reachmachine__run_pipeline_by_category",
    "mcp__reachmachine__pull_data",
    "mcp__reachmachine__add_to_watchlist",
    "mcp__reachmachine__refresh_competitor",
    "mcp__reachmachine__remove_competitor",
    "mcp__reachmachine__stop_pipeline",
    "mcp__reachmachine__submit_analysis",
    "mcp__reachmachine__add_competitor_tags",
]

_ALLOWED_TOOLS = ["Read", "Write", "Skill", *_RM_NONSPEND_TOOLS]


def _preflight_mcp(url: str, token: str) -> str | None:
    """Rulebook A14: a missing/failing MCP server does NOT raise — the run just
    continues WITHOUT its tools and improvises a plan around thin air. So probe
    the endpoint up front and stop on a clear failure. Returns an error string,
    or None if the endpoint looks reachable + authenticated.

    Conservative on purpose: only a clear auth failure (401/403) or a wrong
    endpoint (404) or an unreachable host stops the run. Any other status is
    treated as 'reachable — let the SDK negotiate the protocol', so a streamable
    -HTTP quirk never produces a false 'broken' verdict.
    """
    body = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "rm-content-planner-runner", "version": "1.0"},
        },
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15):  # 2xx: headers received, don't read body
            return None
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            return f"Reach Machine MCP rejected the token (HTTP {e.code}) — RM_MCP_TOKEN is invalid or expired."
        if e.code == 404:
            return f"Reach Machine MCP endpoint not found (HTTP 404) — check RM_MCP_URL."
        return None  # 400/405/5xx etc: reachable, let the SDK negotiate
    except Exception as e:  # noqa: BLE001 — any network failure = dependency missing
        return f"Cannot reach the Reach Machine MCP endpoint ({url}): {e}"


def _parse_semver(version: str | None) -> tuple[int, int, int] | None:
    """Parse 'v1.2.0' or '1.2.0' into (1, 2, 0). Returns None if `version` is
    missing or not a clean 3-part integer semver (prd.md Amendment 44 §44.8:
    a malformed local VERSION must be treated as 'definitely outdated', not
    crash or silently skip)."""
    if not version:
        return None
    v = version.strip()
    if v.startswith("v"):
        v = v[1:]
    parts = v.split(".")
    if len(parts) != 3:
        return None
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return None


def _parse_sse_json_rpc(raw: str) -> dict:
    """Extract the JSON-RPC payload from an SSE-framed streamable-HTTP
    response (P1165 — verified live against the real server; every
    tools/call reply is SSE, Content-Type text/event-stream, never plain
    JSON). The server may prepend ": ping - <timestamp>" keep-alive comment
    lines (SSE comments start with ':') before the real "data: {...}" line.
    A single tools/call reply is always exactly one data line. Raises
    ValueError if none is found — the caller's own fail-open wraps this."""
    for line in raw.splitlines():
        if line.startswith("data: "):
            return json.loads(line[len("data: "):])
    raise ValueError(f"No SSE 'data:' line in MCP response: {raw[:200]!r}")


def _call_mcp_tool(url: str, token: str, name: str, arguments: dict) -> dict:
    """One JSON-RPC 'tools/call' POST against the same Reach Machine MCP
    endpoint `_preflight_mcp` already probes above — same raw-HTTP mechanism,
    no second connection, no new client library, and independent of the
    query() SDK session's own tool-permission model (this runs before/outside
    ClaudeAgentOptions entirely). Raises on any failure; the caller
    (`check_and_update_skill`) fails open around it.

    Two wire-format details verified live against the real server (P1165):
    1. Every tool function takes one Python parameter named `args`
       (e.g. `async def get_skill_version(args: GetSkillVersionInput)`), so
       the real JSON schema requires the call arguments NESTED under an
       "args" key, not sent flat.
    2. The response is always SSE-framed (Content-Type: text/event-stream),
       so it needs `_parse_sse_json_rpc`, not a bare `json.loads`.
    """
    body = json.dumps({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {"name": name, "arguments": {"args": arguments}},
    }).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            # Both values are required — the server returns 406 if either
            # is missing from Accept (verified live: JSON-only -> 406).
            "Accept": "application/json, text/event-stream",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read().decode("utf-8")
    payload = _parse_sse_json_rpc(raw)
    if "error" in payload:
        raise RuntimeError(payload["error"].get("message", f"MCP tool '{name}' failed"))
    result = payload.get("result", {})
    if result.get("isError"):
        raise RuntimeError(f"MCP tool '{name}' returned an error result")
    if "structuredContent" in result:
        return result["structuredContent"]
    for block in result.get("content", []):
        if block.get("type") == "text":
            return json.loads(block["text"])
    raise RuntimeError(f"MCP tool '{name}' returned no usable content")


def _write_bundle_files(skill_dir: pathlib.Path, files: dict[str, str]) -> None:
    """Write every file in `files` under `skill_dir`, VERSION LAST — so a run
    interrupted mid-write leaves an old-but-consistent VERSION and the NEXT
    run detects 'still needs an update' and retries (prd.md §44.8 point 3).
    Raises on the first failure; the caller decides whether to fail-open.
    `..` in any filename is skipped defensively and logged (§44.8 point 7 —
    the server-side whitelist in P1159 is the real security boundary, this
    is just 'don't do something dumb with a bad filename')."""
    version_content = files.get("VERSION")
    for filename, content in files.items():
        if filename == "VERSION":
            continue
        if ".." in filename:
            print(f"debug: skipped suspicious skill-bundle filename: {filename}", file=sys.stderr)
            continue
        dest = skill_dir / filename
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    if version_content is not None:
        (skill_dir / "VERSION").write_text(version_content, encoding="utf-8")


def check_and_update_skill(skill_dir: pathlib.Path, call_tool) -> None:
    """Version-check-and-pull, called once near `_preflight_mcp()` (prd.md
    Amendment 44 §44.8). `call_tool(name, arguments) -> dict` is the MCP
    tool-call mechanism (production: `_call_mcp_tool` bound to the live MCP
    session; tests: a fake). Fail-open, unconditionally — a version check
    must never block or delay a customer's run, so every failure path here
    ends in a debug log and a normal return, never a raised exception.

    `skill_dir` is this skill's OWN directory (where VERSION lives), NOT the
    plugin root — resolved by the caller as `_HERE.parent`, which still
    points at the right place whether this file lives directly under
    `.claude/skills/` or nested inside a plugin's `skills/` dir, since VERSION
    always sits next to runner.py regardless of nesting depth."""
    try:
        try:
            local_raw = (skill_dir / "VERSION").read_text(encoding="utf-8").strip()
        except OSError:
            local_raw = None
        local = _parse_semver(local_raw)

        info = call_tool("get_skill_version", {"skill_id": "rm-content-planner"})
        remote_str = info.get("current_version")
        if remote_str is None:
            return  # nothing ever published — not "newer than mine"

        remote = _parse_semver(remote_str)
        if remote is None:
            return  # malformed remote version — don't act on garbage

        if local is not None and remote <= local:
            return  # local parsed fine and isn't older — nothing to do

        # Either local VERSION is malformed (always attempt repair) or the
        # remote version is strictly newer.
        bundle = call_tool("get_skill_bundle", {"skill_id": "rm-content-planner"})
        files = dict(bundle.get("files", {}))
        if "VERSION" not in files:
            files["VERSION"] = f"v{bundle.get('version', remote_str)}\n"
        _write_bundle_files(skill_dir, files)

        print(
            f"Updated rm-content-planner to v{bundle.get('version', remote_str)} — "
            "this run continues on the old version.\n"
            "The update takes effect on your NEXT run.\n"
            f"What changed: {bundle.get('changelog', '')}"
        )
    except Exception as e:  # noqa: BLE001 — fail-open: a version check/update
        # must never crash or block a paying customer's run. This also
        # covers an older backend where the tool doesn't exist yet.
        print(f"debug: skill version check/update skipped: {e}", file=sys.stderr)


def build_prompt(args: argparse.Namespace) -> str:
    if args.brief:
        brief = pathlib.Path(args.brief).read_text(encoding="utf-8")
        return (
            "Use the rm-content-planner skill to build a content plan. Here is the "
            "creator's business brief — understand it first, use what it gives you, "
            "and proceed:\n\n" + brief
        )
    # No brief: this is likely UNATTENDED, and a headless agent cannot ask you
    # questions (dontAsk denies the prompt). So tell it to proceed with what it
    # can infer and stamp the plan GENERIC rather than stall on missing intake.
    return (
        "Use the rm-content-planner skill to build a content plan for "
        f"{args.creator or 'the creator'} (primary goal: {args.goal}). Understand "
        "the business first from any data you can pull. This is a HEADLESS run: you "
        "CANNOT ask the operator questions. If positioning / stage / first-party "
        "proof are genuinely unavailable, do NOT wait — build the plan from the data "
        "you have and stamp it 'GENERIC — positioning not provided' at the top, per "
        "the PLAYBOOK. Prefer re-running with --brief for a real, non-generic plan."
    )


async def run(args: argparse.Namespace) -> int:
    os.environ.setdefault("RM_MCP_URL", _DEFAULT_RM_MCP_URL)
    for var in ("ANTHROPIC_API_KEY", "RM_MCP_TOKEN"):
        if not os.environ.get(var):
            print(f"error: {var} is not set. See README.md.", file=sys.stderr)
            return 2

    # A14: fail fast if the MCP dependency is unreachable/unauthenticated, rather
    # than silently producing a data-free plan.
    mcp_err = _preflight_mcp(os.environ["RM_MCP_URL"], os.environ["RM_MCP_TOKEN"])
    if mcp_err:
        print(f"error: {mcp_err}", file=sys.stderr)
        return 3

    # prd.md Amendment 44 §44.8: check for a centrally-published skill update
    # and pull it in for the NEXT run. Fail-open by design — see
    # check_and_update_skill's own try/except; nothing here can block this run.
    check_and_update_skill(
        _HERE.parent,
        lambda name, arguments: _call_mcp_tool(
            os.environ["RM_MCP_URL"], os.environ["RM_MCP_TOKEN"], name, arguments
        ),
    )

    options = ClaudeAgentOptions(
        # G249: the pipeline's own reasoning runs on Sonnet by DEFAULT, not the
        # caller's model. Matches backend/app/config.py CLAUDE_SONNET_MODEL.
        # FRFRMU-124: a default, not a lock — RM_SKILL_MODEL overrides it, so an
        # operator can change the model without editing code.
        model=os.getenv("RM_SKILL_MODEL", "claude-sonnet-4-6"),
        cwd=str(REPO_ROOT),
        setting_sources=["project"],          # keep discovering any other project-level skills
        # 2026-08-15 plugin packaging: this skill now lives inside the
        # rm-social-media-manager plugin's skills/ dir, not directly under
        # .claude/skills/, so `setting_sources=["project"]` alone no longer finds
        # it (agent-sdk/skills: "If you set settingSources explicitly, include
        # 'user' or 'project' to keep skill discovery, or use the `plugins`
        # option to load skills from a specific path"). `plugins=[...]` is what
        # actually loads it — confirmed via `claude --agent social-media-manager`:
        # the init message's `skills` list registers it as the NAMESPACED name
        # "rm-social-media-manager:rm-content-planner", not the bare skill name.
        plugins=[{"type": "local", "path": str(PLUGIN_ROOT)}],
        skills=["rm-social-media-manager:rm-content-planner"],
        system_prompt=SYSTEM_PROMPT,
        # Layered defense (confirmed against the Python SDK PermissionMode +
        # disallowed_tools docs):
        #   * permission_mode="dontAsk" — deny-by-default: anything NOT in
        #     allowed_tools is denied outright, with no prompt to hang on (A115).
        #     This also blocks any FUTURE spend tool not yet in the denylist.
        #   * disallowed_tools — an explicit DENY that holds in EVERY mode, even
        #     bypassPermissions (A3), so the known spend/destructive tools stay
        #     blocked even if the mode is ever loosened.
        #   * allowed_tools only AUTO-APPROVES (A7) — it is the pre-approved set
        #     dontAsk checks against, NOT a restriction on its own.
        # All tools the agent actually needs (Read, Write, Skill, the non-spend RM
        # tools) are pre-approved, so dontAsk does not block legitimate work.
        permission_mode="dontAsk",
        allowed_tools=_ALLOWED_TOOLS,            # pre-approved set (A7); NOT a wildcard (A11)
        disallowed_tools=_RM_SPEND_OR_DESTRUCTIVE_TOOLS,  # explicit deny, every mode (A3)
        mcp_servers={
            "reachmachine": {
                "type": "http",
                "url": os.environ["RM_MCP_URL"],
                "headers": {"Authorization": f"Bearer {os.environ['RM_MCP_TOKEN']}"},
            }
        },
    )

    async for message in query(prompt=build_prompt(args), options=options):
        # agent-sdk/plugins: "When plugins load successfully, they appear in the
        # system initialization message." Surface that explicitly rather than
        # trusting "no error thrown" — a missing/misspelled plugin path is
        # skipped silently by the SDK, not raised as an error.
        if getattr(message, "subtype", None) == "init":
            print(f"[init] plugins={message.data.get('plugins')}")
            print(f"[init] skills={message.data.get('skills')}")
        print(message)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="RM content-planner agent (Claude Agent SDK).")
    ap.add_argument("--brief", help="Path to a markdown business brief for the creator (recommended).")
    ap.add_argument("--creator", help="Creator handle, e.g. @name.")
    ap.add_argument("--goal", default="reach", choices=["reach", "leads", "authority"])
    args = ap.parse_args()
    return asyncio.run(run(args))


if __name__ == "__main__":
    raise SystemExit(main())
