# rm-content-planner

A reusable **Claude Skill** that turns Reach Machine (RM) competitor data into a
content plan for **one** creator — the right way. It exists because the first
hand-built plan scored 5/10 with a senior SMM: it decoded what travels for big
creators, then handed those tactics to a zero-follower account unchanged. This
skill forces the missing translation.

**If you're a customer: use it inside Claude Code (below). That's the only path
that works today.** This folder also has a headless `runner.py` script, but it is
engineering/automation tooling, not a second customer option — see the big
warning under "Headless / Agent SDK automation" before touching it.

## Files
| File | What it is |
|---|---|
| `SKILL.md` | The skill's operating contract. Its #1 rule: **understand the business before planning.** |
| `PLAYBOOK.md` | The full reusable method (8 steps + checklist) the skill follows. |
| `runner.py` | Headless Claude Agent SDK program — **engineering/automation only, not customer-ready** (see below). |
| `requirements.txt` | Python dependency (`claude-agent-sdk`), needed only for `runner.py`. |

## Using this plugin (the path for everyone — customers included)
**2026-08-15: this skill now ships packaged inside the `rm-social-media-manager`
plugin** (`.claude/skills/rm-social-media-manager/`, this folder moved to
`skills/rm-content-planner/` inside it). Claude Code still auto-discovers it —
no install step — because the plugin's own manifest lives under
`.claude/skills/`. The one change: invoke it by its namespaced slash form,
`/rm-social-media-manager:rm-content-planner`, or just ask for a "content plan
from Reach Machine" and Claude Code's own skill matching finds it. The plugin
also ships `agents/social-media-manager.md`, an agent that preloads and invokes
this skill directly — use `claude --agent social-media-manager` for that path.

**Anyone with a Claude subscription that includes Claude Code can install and
run this plugin.** That gives them the skill and agent, not your Reach Machine
data — they still connect their *own* accounts.

There is no "which path do I use" decision to make — asking Claude Code for a
content plan, or invoking the skill/agent directly, *is* this path. Nothing in
normal use ever points a user at `runner.py`.

### First run: two sign-ins, both through `/mcp`

`plugin.json` pre-fills **two** MCP servers, so there is no `claude mcp add`
step and nothing to type:

| Server | What it is for | Sign in with |
|---|---|---|
| `reachmachine` | your Reach Machine data — competitors, reels, analysis (`api.reachmachine.org/mcp`, a URL, not a secret) | `/mcp` → `reachmachine` → browser login |
| `apify` | the **live Instagram search** behind `find-competitors` / Step 2 (`mcp.apify.com`) | `/mcp` → `apify` → browser login |

They are **separate one-time sign-ins**. The first time a tool call needs one,
Claude Code flags that server as needing sign-in; run `/mcp`, pick it, and log
in through the browser window. Each person authenticates as themselves — no
token is baked into the plugin, and **there is no API key to paste and no
`.env` file to fill in** for either server.

**No Apify account yet? Creating one at apify.com is free** — new accounts come
with free usage credit. Skipping the Apify sign-in does not break the plugin,
but competitor discovery cannot search Instagram without it, and it will stop
and say so rather than guess. Apify then bills **your own** Apify account for
what you search — see "Two things worth knowing about money" below.

### Slash commands (v1.3.0)

All names below are shortened — the real form is
`/rm-social-media-manager:<name>`.

**The four end-to-end workflows** (each runs a whole stretch of the method):

| Command | What it does | Spends? |
|---|---|---|
| `workflow_plan` | The full method, start to finish (same as invoking the skill) | only on your explicit yes |
| `workflow_insights` | Ask any free-form question of your analysed data | never |
| `workflow_research` | Find benchmark accounts and add them (human-approved shortlist) | only on your explicit yes |
| `workflow_analyze` | Analyse reels by tag or by video — assist mode first (about half price, not free) | only on your explicit yes |

**Fourteen single-action commands**, so you can redo one step without redoing a plan:

| Command | What it does | Spends? |
|---|---|---|
| `know-business` | Understand + record the business: stage, positioning, funnel, goal | never |
| `market-research` | Size the market, pick the segment to target (TAM) | no RM credits |
| `find-competitors` | Find benchmarks — our catalog first, then a live Apify search | ⚠️ **your own Apify bill**, plus RM credits to add |
| `show-competitors` | List tracked competitors and how much data each has | never |
| `delete-competitors` | Remove competitors from this workspace | 🔴 **can erase data for good** |
| `switch-workspace` | Switch client workspace, and re-check whose account it is | never |
| `pull-data` | Fetch more reels for competitors already tracked | 💸 RM credits |
| `watch-video` | Analyse reels — by classification/tag, or by URL | 💸 RM credits |
| `check-classifications` | Check how reels were classified, and spot wrong calls | never |
| `hooks` | Hook patterns — what openings hold attention | never |
| `cta` | CTA patterns — what asks convert | never |
| `structures` | Content structures — how winning reels are built | never |
| `strategy` | The strategy the data implies — pillars and mix | never |
| `our-patterns` | Everything we have learned, in one combined view | never |

Every command checks its prerequisites first (e.g. `find-competitors` won't search
before it knows your business — it routes you through `know-business`) and defers
to the skill's PLAYBOOK as the single source of the method. They live in
`../../commands/` at the plugin root; the drift guard is `tests/test_commands.py`.

**Two things worth knowing about money.** RM credits are gated: nothing spends
without your explicit yes, and the up-front hold is much larger than the final
charge. **Apify is different** — it bills *your own* Apify account, so Reach
Machine cannot see or cap it. `find-competitors` therefore asks separately before
any Apify search. If Apify isn't connected, discovery **stops** and says so; it
will never quietly substitute a web search and pass the results off as our data.

## Headless / Agent SDK automation — NOT available to customers yet

> **This section is for engineers, not customers.** `runner.py` currently has
> no working way for a customer to authenticate:
> 1. It needs `ANTHROPIC_API_KEY` — the Agent SDK only bills through an
>    Anthropic API key, never a Claude subscription. That's an Anthropic
>    product boundary, not something this plugin can change.
> 2. It needs `RM_MCP_TOKEN` — and **Reach Machine has no self-service way for
>    a customer to generate one.** The only backend endpoints
>    (`connected_apps.py`) list or revoke tokens a *real OAuth client*
>    already created; there is no "create a token" button. Tokens are only
>    ever minted by a full OAuth browser flow through a real client (Claude
>    Code, Claude Desktop, claude.ai) — never as text a person can copy.
>
> So today, an ordinary customer **cannot** fill in `RM_MCP_TOKEN` at all.
> This path only works for someone with direct backend access who mints a
> token by hand. Don't point customers at it until a self-service token page
> exists.

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...     # your Anthropic API key
export RM_MCP_TOKEN=...                  # a bearer / OAuth access token for that MCP, tied to YOUR Reach Machine account
# RM_MCP_URL is optional — defaults to the public prod endpoint (api.reachmachine.org/mcp).
# Set it only to point at a different Reach Machine deployment (e.g. dev).

# recommended: hand it a short business brief so it understands the creator first
python runner.py --brief brief.md

# or start from a handle + goal and let it interview you for the rest
python runner.py --creator "@yourhandle" --goal leads
```

`brief.md` should answer the skill's four business questions: **stage**
(followers + sustainable posts/week), **positioning** (one ownable angle +
first-party proof + the one audience), **funnel assets** (lead magnet + DM
automation — yes/no), and **goal** (reach / leads / authority). Anything you leave
out, the agent will ask for before it plans.

## Auto-updates
`runner.py` now checks for a newer version at the start of each run and pulls
it in automatically for your **next** run. If you downloaded this skill
before this version, it has no update-check code and will not auto-update.
Re-download it once to get onto the self-updating version — after that,
updates arrive automatically.

## Notes
- Uses model `claude-opus-4-8`; edit `SYSTEM_PROMPT` / `model` in `runner.py` to change.
- The RM MCP is a remote (HTTP) server; set `RM_MCP_URL` / `RM_MCP_TOKEN` from your
  Reach Machine connector. Tool names are exposed to the agent as
  `mcp__reachmachine__<tool>`. The headless runner does **not** allow-list them
  with a wildcard (rule A11) — it enumerates the read/non-spend tools only
  (`_RM_NONSPEND_TOOLS` in `runner.py`).
- **The headless runner cannot spend or delete.** The spend tools
  (`run_pipeline*`, `pull_data`, `add_to_watchlist`, `refresh_competitor`) and
  destructive tools (`remove_competitor`, `stop_pipeline`) are intentionally NOT
  in the allow-list, so an unattended run cannot trigger them. Enabling headless
  spend — and its per-run budget ceiling — is founder decision **G63**; do not
  add a spend tool here without a real budget gate.
- Interactively (via the Skill tool, with a human watching), the skill CAN spend
  because you approve each confirm-prompt yourself. The skill always previews
  cost and waits for your explicit yes before any `confirm=true` call.
- Related product gaps this method works around: G51–G57 in
  `marketing/engineering-gaps.md`.
