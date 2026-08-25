---
description: "Read-only analytics deep-dive: tags, scores, hooks, CTAs, niches, structures — free, never spends credits"
argument-hint: "[hooks | ctas | structures | tags | niche | @handle | a question about the data]"
---

Answer the user's data question from Reach Machine — **reads only, never spend**.
This is a re-entry point into the `rm-social-media-manager:rm-content-planner`
skill's method (its PLAYBOOK, "Step 3 — Use the RM MCP correctly"), not a
replacement for it. Load that skill's PLAYBOOK section before answering so the
rigor rules apply.

What the user asked about: $ARGUMENTS
(If empty, ask ONE short question: which of hooks / CTAs / structures / tag
performance / a specific account they want to look at.)

## How to answer

1. **Confirm the workspace and scope deliberately** (PLAYBOOK Step 3, rule 1).
   For one account, pass `usernames=[handle]` to the insight tools or call
   `set_data_selection`. For a hand-picked group of videos, use
   `set_data_selection` with `post_urls`.
2. **Check coverage first** with `get_analysis_coverage` — insight tools only see
   analysed reels. If coverage is thin for what they asked, SAY SO and mark the
   answer low-confidence; recommend `/rm-social-media-manager:analyze` to widen
   it. Do not silently answer from a thin slice.
3. **Pull the matching reads:**
   - Hooks → `get_hooks_library` · CTAs → `get_cta_library`
   - Structures → `get_content_structures` · Breakdown/niche → `get_content_breakdown`
   - Tag performance (cross-account or per-account) → `get_tag_stats`, `get_avg_scores`,
     `query_posts_by_tag`
   - Strategy view → `get_content_strategy`
4. **Hold every claim to the skill's rigor rules:** medians not means, sample
   sizes stated, provenance tagged (DATA-DRIVEN only with real n behind it —
   otherwise DATA-INFERRED or JUDGMENT, labelled). Use RM's friendly tag labels;
   never speculate about how a tag is computed.
5. **If you scoped with `set_data_selection`, ALWAYS call `clear_data_selection`
   before finishing** — a leaked scope silently corrupts the next read.

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
