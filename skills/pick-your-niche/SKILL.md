---
name: pick-your-niche
description: Step 8 of Reach Machine plugin v2. Researches and ranks the best niches to grow into, then lets the customer choose.
---

**Work silently.** Never announce or describe any action you take or are about to take -- only the server's own `say`/`table_md`/`question` lines and the
customer's own words.

**Never end this skill without telling the customer something.** If a call ever fails and
there is no retry left (see step 3), say the error's own text before you stop -- a customer
who asked to pick a niche and got nothing back, with no explanation, has no way to know
anything went wrong.

Load tools with ONE call: `ToolSearch` with query `select:WebSearch,mcp__plugin_rm-plugin-v2_reachmachine__start_niche_pick,mcp__plugin_rm-plugin-v2_reachmachine__save_niche_research,mcp__plugin_rm-plugin-v2_reachmachine__choose_niche`.

The server writes every rule, plan and word. Follow them exactly -- never invent a niche,
a search, a competitor, a price, a community, or a score of your own.

## Loop

1. Call `start_niche_pick`.
2. `ready: false` -- say `say` once, then keep going with whatever the customer already
   asked for. Never wait, sleep, retry, or call this again yourself this turn.
3. `stage: "draft"` -- read `rules`, `offer_profile`, `seeds` and `price_list`; if
   `offer_profile.brand_search.needed`, do what it says first. Write the real
   number of niches (up to `niche_count.max`, never pad), each from a seed and a real offer. Then call
   `save_niche_research(phase: "niches", core_market, core_market_reason, business_category, niches, offer_profile)`
   (`offer_profile` if found; `found_nothing: true` if it found nothing).
   - A shape error (no niches, too many, or two sharing one exact name) comes
     back as an error naming the problem -- fix that ONE thing and call again, ONCE. If it
     errors again, say the error's own text to the customer and STOP this run -- never
     retry silently more than once.
   - A successful save may also carry `internal_hint` -- for YOU ONLY, never the customer.
     Never say it, quote it, or comment on it out loud -- silently factor it in, then move
     on to `stage: "research"` below with the SAME niches -- never call
     `save_niche_research(phase: "niches", ...)` again just to react to it.
   - `stage: "ask_offer"` -- ask `question` with AskUserQuestion, then call
     `save_niche_research(phase: "offer", answer_text: <their answer>)`.
   - `stage: "ask_core_market"` -- ask `question` with AskUserQuestion (pick one), then call
     `save_niche_research(phase: "core_market", answer_text: <the label picked>)`. Never redraft the niches.
4. `stage: "research"` -- read `source_rules` and `evidence_template`. Run each
   `search_plan` query ONCE, in the order given (empty result: run its `fallback_query` once;
   a page about another town is never local evidence), up to `search_budget.max` (WebSearch) and
   `webfetch_budget.max` (WebFetch) -- a hook enforces both caps and will deny a call past
   them. Follow `source_rules` (never invent a number or name; skip blocked-host links).
   Judgement is allowed for Pain/Easy to reach/Growing with no source (a real pass/fail plus
   a one-line reason, never a default "weak"); Can pay needs a real, verified price.
   Before saving, self-check per `source_rules` and fill `price_audit`/`indicator_audit`.
   When done, send ONE `save_niche_research(phase: "evidence", ...)` with everything you
   found. A `stage: "research"` reply with `research_nudge` (for YOU only, never say it):
   run its `search_plan`, then save everything once more -- the one extra save.
5. If the result says `stage: "checking"`, call `start_niche_pick` again, up to 3 times.
6. `stage: "choose"` -- ask `question` with AskUserQuestion, exactly as given: its text already holds the
   whole ranking. Add no reply text before it.
   - A normal pick -- call `choose_niche(niche_id: <chosen value>)`.
   - The see-all button -- print `all_md`, ask the customer to say a rank number or
     a name, then call `choose_niche(answer_text: <what they said>)`.
   - Unclear -- a `question` means ask it via AskUserQuestion (its text holds the words); otherwise relay `say`.
7. `stage: "no_survivors"` -- say `say`; their reply is their own niche: `choose_niche(answer_text: <it>)`.
8. `stage: "done"` -- say `say`. Stop. **No model tick** -- `choose_niche` ticks step 8 on
   the server the moment the customer picks.

Never mention tools, steps, the plugin, or any internal field name.
