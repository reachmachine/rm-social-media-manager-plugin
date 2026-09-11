---
description: "Everything we have learned, in one place — hooks, CTAs, structures, strategy and classifications together. Free, never spends credits"
argument-hint: "[@handle or a tag to focus on, or leave empty for the whole workspace]"
---

One combined view of every pattern Reach Machine holds for this workspace. **Reads only —
never spend.** This is the "show me everything we know" command; the single-topic commands
(`hooks`, `cta`, `structures`, `strategy`) go deeper on one slice.

Focus: $ARGUMENTS

## Build it in this order

1. **Scope FIRST, on its own.** Scope once so every section describes the same data. Either
   pass `usernames=[handle]` to every read in point 2, or, for a hand-picked set of reels,
   call `set_data_selection` **by itself and wait for it to come back**. Never send that call
   in the same message as the reads: a read that goes out before the scope lands would
   describe different reels from the rest of the answer, and a mixed-up answer is far worse
   than a slow one.
2. **Then send ALL of these reads in ONE message — they do not depend on each other.** One
   round-trip covers the lot instead of eight: `get_workspace_stats`, `get_analysis_coverage`,
   `get_hooks_library`, `get_cta_library`, `get_content_structures`, `get_content_strategy`,
   `get_content_breakdown` and `get_tag_stats`. What each one gives you:
   - `get_workspace_stats` + `get_analysis_coverage` — the honest base: which workspace, how
     many competitors, how many reels analysed. Every section below inherits that confidence
     level. **If coverage is thin, say so once at the top** and mark the whole answer
     low-confidence rather than repeating the caveat per section.
   - `get_hooks_library` — the openings
   - `get_cta_library` — the asks
   - `get_content_structures` — the shapes
   - `get_content_strategy` — the pillars and mix
   - `get_content_breakdown` + `get_tag_stats` — how it splits by category, and which
     performance tags actually have volume behind them
3. **Then say what it ADDS UP to.** This is the point of the command, not the five lists. Name:
   - the 2–3 patterns with the strongest evidence (real n, stated),
   - where the sections **disagree** (e.g. the winning hook style sits in a category the
     strategy barely covers) — disagreement is a finding, not an error to smooth over,
   - the biggest **hole**: what we cannot answer yet and which tag subset would fill it.
4. If you scoped with `set_data_selection`, **always** `clear_data_selection` before finishing.

## Rigor

Follow the skill's PLAYBOOK Step 3 and Step 7 rules exactly — load ONLY those two files,
`playbook/step-03-mcp.md` and `playbook/step-07-strategy.md`, never the whole method: **medians not means**, sample size
stated on every claim, each claim labelled DATA-DRIVEN (real n behind it) / DATA-INFERRED /
JUDGMENT. A combined view makes it easy to sound authoritative off five thin slices — that is
the specific failure to avoid here. Use RM's own tag labels; never speculate about how a tag
is computed.

**Benchmark lens — say which creators the answer came from.** These reads default to the
accounts on your watchlist only. The pattern tools (`get_content_strategy`, `get_hooks_library`,
`get_cta_library`, `get_content_structures`) take `scope`: `mine` is your watchlist, `niche` is
the wider community pool, `both` combines them. The tag and post tools (`get_tag_stats`,
`get_avg_scores`, `query_posts_by_tag`) take `analysis_mode`, whose
`community_per_account` and `community_cross_account` values widen the pool the same way.
**When a finding is about to drive a recommendation, read it again through the wider lens and
compare** — a casual "just show me the list" answer stays on one lens. Label every answer with
the set behind it and how many reels that is ("your 15 tracked accounts, 212 analysed reels"),
and quote the count the wider read actually returns instead of assuming it is bigger. If the
wider view is not available here — the community tools are not offered, or the pool comes back
empty — say so plainly; never quietly fall back to the watchlist after being asked for the
wider picture. Full detail: `playbook/step-03-mcp.md`.

**If something in the answer looks wrong, do not explain it away.** Say the likely
reason in plain words, say what can still be trusted, and report anything we do not
already know about. The known signatures and the exact wording: `data-quality.md`.

**Hard limit:** never call a spend or destructive tool here, and never call Apify. If the real
answer is "we have not analysed enough yet", say that and point at
`/rm-social-media-manager:watch-video`.
