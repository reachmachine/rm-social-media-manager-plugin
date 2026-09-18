---
description: "Run analysis on competitor reels — by performance tag or a specific video. Assist mode by default (about half price, not free); RM's full-price analysis only on an explicit yes"
argument-hint: "[tag name, @handle, or a reel URL to analyse]"
---

Analyse reels so the insight tools have data to read. This is a re-entry point
into the `rm-social-media-manager:rm-content-planner` skill's method — load its
PLAYBOOK's "Step 3 — Use the RM MCP correctly" rules — load ONLY `playbook/step-03-mcp.md`,
`playbook/step-03-mcp-spend-and-progress.md` (especially rules 2, 6, 6a, 6b, 6c and 6e), and
`playbook/step-03-progress.md` (rule 6d) and follow them exactly.

What the user wants analysed: $ARGUMENTS

## Prerequisite gate

**Send `get_workspace_stats`, `search_watchlist` and `get_analysis_coverage` in
ONE message — they do not depend on each other.** One round-trip, not three, and
nothing here spends anything. If the watchlist is empty, there is nothing to
analyse — say so and route to `/rm-social-media-manager:workflow-research` to add
competitors first.

## How to run it

1. **Coverage first:** read the `get_analysis_coverage` result from that message —
   find which tag subsets are thin for the user's goal, per the PLAYBOOK's goal→tag
   table (healthy tags only).
2. **Pick the target:** a tag subset (`run_pipeline_by_category` /
   `query_posts_by_tag`) or a specific video / hand-picked set (`run_pipeline`,
   or scope via `set_data_selection` with `post_urls`). Start with a small
   calibration batch, read the REAL cost from `get_credit_usage` (the hold is
   ~20× the real charge), then scale.
3. **Default to assist mode at EVERY confirm gate (PLAYBOOK rule 6a, in
   `playbook/step-03-mcp-spend-and-progress.md`) — never an
   even choice.** Recommend `run_pipeline_assist` first and say plainly: you
   read the frames yourself via `get_assist_work` → `submit_analysis`, so the
   FINAL charge is about half the credits of a normal run — a discount, not
   free (G339). The amount held up front is the same either way, and it uses
   their Claude usage and more time. Only fall back to RM's full-price
   `run_pipeline` if the human explicitly asks for it. 🔴 By tag/category
   (FRFRMU-1517): `run_pipeline_by_category`'s `mode` field already defaults to
   `"assist"` — leave it unset for this same assist path; only pass
   `mode="full"` when the human explicitly asked for full price.
4. **Pin the reel analysis itself to a Sonnet sub-agent (rule 6b)** — a default,
   not a lock. **And keep the assist loop small (rule 6e):** one reel at a time —
   fetch, analyse, `submit_analysis`, then write ONE short line about that reel and
   drop its frames and instruction bundle before the next `get_assist_work`. Dispatch
   about **8 reels per batch, not 25**; each reel drops 8 keyframe images into this
   chat and they never leave, so a long batch can run out of room after the credits
   are already held.
   - **Pass `have_instructions_version` from your SECOND `get_assist_work` call
     onward** (FRFRMU-1567) — the first call gives you the token, later calls
     skip resending ~15K tokens of instructions. Before analysing ANY bundle,
     confirm it carries an `end_of_bundle` block and one "Frame N of M" label
     per frame `end_of_bundle` reports as sent. Missing either means your
     client cut the response — re-request the SAME reel (`get_assist_work`
     with that `post_url`) before writing anything; do not analyse a reel you
     cannot confirm arrived whole.
5. **Confirm-before-spend is a HUMAN gate:** every spend tool call shows its
   un-confirmed cost preview and WAITS for an explicit yes before `confirm=true`.
   This applies to assist mode's dispatch too. State every preview in credits —
   never convert it to dollars or state what it costs us (PLAYBOOK rule 6c, G368).
6. If you scoped with `set_data_selection`, call `clear_data_selection` when
   done.
7. **While it runs, follow PLAYBOOK rule 6d exactly (`playbook/step-03-progress.md`,
   FRFRMU-1289):** 🔴 wait `next_poll_after_s` seconds before calling `get_pipeline_status`
   again — that field is computed server-side from the run's own real pace; read it off every
   reply and wait exactly that long, never invent your own gap or fixed timer. Every poll
   re-sends this whole chat, so guessing burns the human's own Claude usage for nothing, and a
   guess CAN drift (this replaced an algorithm that did, in a live incident). The moment
   `stalled_for_s` comes back as a number instead of `null`, `next_poll_after_s` tightens on its
   own — nothing extra to do. Give a friendly opening ETA, let the human know they can step
   away, and absorb a stall into one calm update instead of a menu of options.
8. 🔴 **When it ends, count requested against delivered — PLAYBOOK rule 6h
   (`playbook/step-03-requested-vs-delivered.md`, FRFRMU-1027).** Read `unanalyzed_count`
   from `get_pipeline_status`: above zero means the run did **not** finish, so never say
   "done" or "all analysed". Name the missing reels with the plain-English `reason` on each
   entry in `failed_reels`, word for word. A **refused** batch accepted nothing and charged
   nothing — its message says how many reels were turned away; add that to your tally and
   never record it as a batch that ran. At the end give one tally line: *"You approved N;
   M are analysed; K did not finish (reasons). Retry the K? That holds credits for K reels
   only."* Follow `retry_hint` — it already knows when asking again cannot work (a private
   or removed post), and you must not offer a retry then.

**Hard limit:** never call Apify from this command. Analysis works on reels we already
hold; Apify bills the user's own Apify account, which Reach Machine cannot see or cap.
Finding new accounts is `/rm-social-media-manager:find-competitors`.

When the run finishes, point the user at `/rm-social-media-manager:workflow-insights` to
read what the new analysis shows.
