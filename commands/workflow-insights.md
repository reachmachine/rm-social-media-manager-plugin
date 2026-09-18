---
description: "Read-only analytics deep-dive: tags, scores, hooks, CTAs, niches, structures — free, never spends credits"
argument-hint: "[hooks | ctas | structures | tags | niche | @handle | a question about the data]"
---

Answer the user's data question from Reach Machine — **reads only, never spend**.
This is a re-entry point into the `rm-social-media-manager:rm-content-planner`
skill's method (its PLAYBOOK, "Step 3 — Use the RM MCP correctly"), not a
replacement for it. Load ONLY that one step file, `playbook/step-03-mcp.md`,
before answering — never the whole method — so the
rigor rules apply.

What the user asked about: $ARGUMENTS
(If empty, ask ONE short question: which of hooks / CTAs / structures / tag
performance / a specific account they want to look at.)

## How to answer

1. **Confirm the workspace and scope deliberately, FIRST and on its own**
   (PLAYBOOK Step 3, rule 1, in `playbook/step-03-mcp.md`).
   For one account, pass `usernames=[handle]` to the insight tools or call
   `set_data_selection`. For a hand-picked group of videos, use
   `set_data_selection` with `post_urls`. If you call `set_data_selection`, let it
   come back before you send point 2 — a read that travels alongside the scope
   change can still answer for the OLD scope.
2. **Then send the coverage check and the matching reads in ONE message — they do
   not depend on each other.** One round-trip, not one per read. Always include
   `get_analysis_coverage`; add whichever of these fit the question:
   - Hooks → `get_hooks_library` · CTAs → `get_cta_library`
   - Structures → `get_content_structures` · Breakdown/niche → `get_content_breakdown`
   - Tag performance (cross-account or per-account) → `get_tag_stats`, `get_avg_scores`,
     `query_posts_by_tag`
   - Strategy view → `get_content_strategy`
3. **Read coverage before you write the answer** — insight tools only see
   analysed reels. If coverage is thin for what they asked, SAY SO and mark the
   answer low-confidence; recommend `/rm-social-media-manager:workflow-analyze` to widen
   it. Do not silently answer from a thin slice.
4. **Hold every claim to the skill's rigor rules:** medians not means, sample
   sizes stated, provenance tagged (DATA-DRIVEN only with real n behind it —
   otherwise DATA-INFERRED or JUDGMENT, labelled). Use RM's friendly tag labels;
   never speculate about how a tag is computed.
5. **If you scoped with `set_data_selection`, ALWAYS call `clear_data_selection`
   before finishing** — a leaked scope silently corrupts the next read.

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

## Hard limits

- Never call a spend or destructive tool from this command (`run_pipeline*`,
  `pull_data`, `add_to_watchlist`, `refresh_competitor`, `remove_competitor`,
  `stop_pipeline`). If the user's question needs new analysis or new accounts,
  point them to `/rm-social-media-manager:watch-video` or
  `/rm-social-media-manager:find-competitors` instead.
- **Never call Apify here either.** Apify bills the user's own Apify account, which
  Reach Machine cannot see or cap, so it is never part of a read-only answer.
  Finding accounts is `/rm-social-media-manager:find-competitors`.
- **Never substitute a web search for missing data (G332).** If the analysed data
  cannot answer the question, say that plainly. Do not fill the gap from the open
  web and present it as Reach Machine data.
