---
description: "Analyse reels — a whole classification/tag group, or specific videos by URL. SPENDS RM credits; assist mode is about half price, not free"
argument-hint: "[a tag/category name, an @handle, or one or more reel URLs]"
---

Analyse reels so the insight tools have something real to read. This is the skill's analysis
step — load PLAYBOOK **Step 3**: `playbook/step-03-mcp.md` for rule 2,
`playbook/step-03-mcp-spend-and-progress.md` for rules 6, 6a, 6b, 6c and 6e, and
`playbook/step-03-progress.md` for rule 6d. Follow them exactly. Do not load the rest of the
method.

What to analyse: $ARGUMENTS

## Prerequisite gate

**Send `get_workspace_stats`, `search_watchlist` and `get_analysis_coverage` in ONE message —
they do not depend on each other.** One round-trip, not three, and none of the three spends
anything. If the watchlist is empty there is nothing to analyse — say so and route to
`/rm-social-media-manager:find-competitors`.

## Pick the target

1. **Coverage first** — read the `get_analysis_coverage` result from that message. Find which
   tag subsets are thin **for the user's goal**, per the PLAYBOOK's goal→tag table. Do not
   analyse what is already covered.
2. **Then choose the shape of the run:**
   - **By classification / tag group** → `run_pipeline_by_category` (pair with
     `query_posts_by_tag` to see what it will cover first). 🔴 Its `mode` field already defaults
     to `"assist"` (FRFRMU-1517) — leave `mode` unset for the assist path below; only pass
     `mode="full"` if the human explicitly asked for full price.
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

**Keep the assist loop small (rule 6e).** One reel at a time: fetch, analyse, `submit_analysis`,
then write ONE short line about that reel and drop its frames and its instruction bundle from your
working set before the next `get_assist_work`. Dispatch about **8 reels per batch, not 25** — each
reel drops 8 keyframe images into this chat and they never leave, so a long batch gets slower and
slower and can run out of room after the credits are already held.

**Pass `have_instructions_version` from your SECOND `get_assist_work` call onward (FRFRMU-1567)** —
the first call hands you the token; keep passing it while you still hold the instructions in
context, so later calls skip resending ~15K tokens. Before analysing ANY bundle, confirm it carries
an `end_of_bundle` block and one "Frame N of M" label per frame `end_of_bundle` says it sent —
missing either means your client cut the response before it arrived. Re-request the SAME reel
(`get_assist_work` with that `post_url`) rather than analysing a bundle you cannot confirm arrived
whole; the closing frames are exactly what a cut removes first, and that's where CTAs live.

## 🔴 Confirm-before-spend is a HUMAN gate

Every spend call shows its un-confirmed cost preview and **WAITS for an explicit yes** before
`confirm=true`. This applies to assist mode's dispatch too. Never set `confirm=true` yourself.
State every cost preview in credits, exactly as the tool returns it — never convert it to dollars
or state what it costs us (PLAYBOOK rule 6c, in `playbook/step-03-mcp-spend-and-progress.md`, G368).

## While it runs

Follow **PLAYBOOK rule 6d** (`playbook/step-03-progress.md`, FRFRMU-1289) exactly — 🔴 **wait
`next_poll_after_s` seconds before calling `get_pipeline_status` again.** That field is computed
server-side from the run's own real pace; read it off every reply and wait exactly that long —
never invent your own gap or fixed timer. Every poll re-sends this whole chat, so guessing a gap
burns the customer's own Claude usage for nothing, and a guess CAN drift (this replaced an
algorithm that did, in a live incident). The moment `stalled_for_s` comes back as a number instead
of `null`, `next_poll_after_s` tightens on its own — nothing extra to do. Give a friendly opening
ETA, let the customer know they can step away, and absorb a stall into a calm update instead of
turning it into a menu. `stop_pipeline` cancels, and is itself a destructive call needing an
explicit yes. If a run fails, relay the server's own message, which usually says whether credits
were taken.

## 🔴 Count what you asked for against what came back

Follow **PLAYBOOK rule 6h** (`playbook/step-03-requested-vs-delivered.md`, FRFRMU-1027). Short
version, and it is not optional:

- After **every** batch, read `unanalyzed_count` from `get_pipeline_status`. Above zero means the
  run is **not** finished — never say "done" or "all analysed" while it is. Say how many are
  missing, using the plain-English `reason` on each entry in `failed_reels` word for word.
- A **refused** batch (a run is already active, or the analysis service is not responding) accepted
  **nothing** and charged nothing. Its message says how many reels were turned away — add that to
  your tally and never record it as a batch that ran. Follow the recovery step in the message; if
  it says waiting will not fix it, do not retry in a loop.
- At the end, one tally line: *"You approved N reels; M are analysed; K did not finish (reasons).
  Retry the K? That holds credits for K reels only."* Follow `retry_hint` — it already knows when
  asking again cannot work (a private or removed post), and you must not offer a retry then.

When it finishes, point at `/rm-social-media-manager:our-patterns` or
`/rm-social-media-manager:check-classifications` to read what the new analysis shows. If you
scoped with `set_data_selection`, call `clear_data_selection`.

**Hard limit:** never call Apify here.
