---
description: "Analyse reels — a whole classification/tag group, or specific videos by URL. SPENDS RM credits; assist mode is about half price, not free"
argument-hint: "[a tag/category name, an @handle, or one or more reel URLs]"
---

Analyse reels so the insight tools have something real to read. This is the skill's analysis
step — load PLAYBOOK **Step 3** and follow rules 2, 6, 6a, 6b, 6c and 6d exactly.

What to analyse: $ARGUMENTS

## Prerequisite gate

`get_workspace_stats` (and `search_watchlist` if needed). If the watchlist is empty there is
nothing to analyse — say so and route to `/rm-social-media-manager:find-competitors`.

## Pick the target

1. **Coverage first** — `get_analysis_coverage`. Find which tag subsets are thin **for the
   user's goal**, per the PLAYBOOK's goal→tag table. Do not analyse what is already covered.
2. **Then choose the shape of the run:**
   - **By classification / tag group** → `run_pipeline_by_category` (pair with
     `query_posts_by_tag` to see what it will cover first).
   - **Specific videos by URL, or a hand-picked set** → `run_pipeline`, or scope with
     `set_data_selection` using `post_urls`.
   Say which one you are using and why — they cost differently.
3. **Start with a small calibration batch**, read the REAL charge with `get_credit_usage`, then
   scale. The up-front hold is far larger than the final charge; say that plainly so a large
   hold does not read as a large bill.

## 🔴 Default to assist mode — and price it honestly (rule 6a, G339)

Recommend `run_pipeline_assist` first, never as an even choice. But **never call it free.**
There are two different numbers:

- **Held up front:** the SAME as a normal run. Not smaller for assist. Someone who cannot cover
  the hold cannot start assist either.
- **Final charge:** about **HALF** the credits per reel of a normal run, because the user's own
  Claude usage writes the analysis. Unused hold is refunded.

Say "about half the credits of a normal run — a discount, not free." If asked whether it will
ever be free: "It may become free in future — that isn't decided yet, so treat today's price as
the price." A maybe, never a promise. Fall back to full-price `run_pipeline` only if the user
explicitly asks.

**Pin the reel analysis itself to a Sonnet sub-agent (rule 6b)** — a default, not a lock.

## 🔴 Confirm-before-spend is a HUMAN gate

Every spend call shows its un-confirmed cost preview and **WAITS for an explicit yes** before
`confirm=true`. This applies to assist mode's dispatch too. Never set `confirm=true` yourself.
State every cost preview in credits, exactly as the tool returns it — never convert it to dollars
or state what it costs us (PLAYBOOK rule 6c, G368).

## While it runs

Follow **PLAYBOOK rule 6d** exactly — poll `get_pipeline_status` every 20-30 seconds, give a
friendly opening ETA, let the customer know they can step away, and absorb a stall into a calm
update instead of turning it into a menu. `stop_pipeline` cancels, and is itself a destructive
call needing an explicit yes. If a run fails, relay the server's own message, which usually says
whether credits were taken.

When it finishes, point at `/rm-social-media-manager:our-patterns` or
`/rm-social-media-manager:check-classifications` to read what the new analysis shows. If you
scoped with `set_data_selection`, call `clear_data_selection`.

**Hard limit:** never call Apify here.
