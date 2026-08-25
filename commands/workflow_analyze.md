---
description: "Run analysis on competitor reels — by performance tag or a specific video. Assist mode by default (about half price, not free); RM's full-price analysis only on an explicit yes"
argument-hint: "[tag name, @handle, or a reel URL to analyse]"
---

Analyse reels so the insight tools have data to read. This is a re-entry point
into the `rm-social-media-manager:rm-content-planner` skill's method — load its
PLAYBOOK's "Step 3 — Use the RM MCP correctly" rules (especially rules 2, 6, 6a,
6b, 6c and 6d) and follow them exactly.

What the user wants analysed: $ARGUMENTS

## Prerequisite gate

Call `get_workspace_stats` (and `search_watchlist` if needed) first. If the
watchlist is empty, there is nothing to analyse — say so and route to
`/rm-social-media-manager:research` to add competitors first.

## How to run it

1. **Coverage first:** `get_analysis_coverage` — find which tag subsets are thin
   for the user's goal, per the PLAYBOOK's goal→tag table (healthy tags only).
2. **Pick the target:** a tag subset (`run_pipeline_by_category` /
   `query_posts_by_tag`) or a specific video / hand-picked set (`run_pipeline`,
   or scope via `set_data_selection` with `post_urls`). Start with a small
   calibration batch, read the REAL cost from `get_credit_usage` (the hold is
   ~20× the real charge), then scale.
3. **Default to assist mode at EVERY confirm gate (PLAYBOOK rule 6a) — never an
   even choice.** Recommend `run_pipeline_assist` first and say plainly: you
   read the frames yourself via `get_assist_work` → `submit_analysis`, so the
   FINAL charge is about half the credits of a normal run — a discount, not
   free (G339). The amount held up front is the same either way, and it uses
   their Claude usage and more time. Only fall back to RM's full-price
   `run_pipeline` if the human explicitly asks for it.
4. **Pin the reel analysis itself to a Sonnet sub-agent (rule 6b)** — a default,
   not a lock.
5. **Confirm-before-spend is a HUMAN gate:** every spend tool call shows its
   un-confirmed cost preview and WAITS for an explicit yes before `confirm=true`.
   This applies to assist mode's dispatch too. State every preview in credits —
   never convert it to dollars or state what it costs us (PLAYBOOK rule 6c, G368).
6. If you scoped with `set_data_selection`, call `clear_data_selection` when
   done.
7. **While it runs, follow PLAYBOOK rule 6d exactly:** poll `get_pipeline_status` every
   20-30 seconds, give a friendly opening ETA, let the human know they can step away, and
   absorb a stall into one calm update instead of a menu of options.

**Hard limit:** never call Apify from this command. Analysis works on reels we already
hold; Apify bills the user's own Apify account, which Reach Machine cannot see or cap.
Finding new accounts is `/rm-social-media-manager:find-competitors`.

When the run finishes, point the user at `/rm-social-media-manager:insights` to
read what the new analysis shows.
