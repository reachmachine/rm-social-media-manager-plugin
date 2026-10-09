---
name: dream-customer
description: Step 9 of Reach Machine plugin v2. Builds the dartboard (niche -> 10 sub-niches -> 10 micro-niches) and 10 dream-customer personas, then lets the customer approve the main one.
---

**Work silently.** Never announce or describe any action you take or are about to take -- only the server's own `say`/`table_md`/`question` lines and the
customer's own words. Never mention tools, steps, stages, the plugin, or any internal field
name -- same rule as every other step.

**Never end this skill without telling the customer something.** If a save fails with no
retry left, say that you could not save that and they can try again soon. Never repeat
an error's own text, and never name a tool or a field.

Load tools with ONE call: `ToolSearch` with query
`select:WebSearch,WebFetch,mcp__plugin_rm-plugin-v2_reachmachine__start_dream_customer,mcp__plugin_rm-plugin-v2_reachmachine__save_dream_customer,mcp__plugin_rm-plugin-v2_reachmachine__get_dream_customer,mcp__plugin_rm-plugin-v2_reachmachine__choose_main_persona`.

The server writes every rule, template and word. Follow them exactly -- never invent a
sub-niche, a micro-niche, a persona name, a quote, a source, or a phrase of your own; when
you write "our view" text, keep it inside the shape the server's `RULES`/`SAVE_TEMPLATE`
give you.

## Loop

1. Call `start_dream_customer`.
2. `ready: false` -- say `say` once, then keep going with whatever the customer already
   asked for. Never wait, sleep, retry, or call this again yourself this turn. (Covers
   resuming mid-step too: calling `start_dream_customer` again always picks up wherever the
   saved doc actually is -- draft, mid-research, or already reviewed -- so never keep your
   own memory of where you were.)
3. `stage: "stale"` -- say `say` (the niche changed since last time, research is redoing
   itself). Then call `start_dream_customer` again and carry on.
3a. `stage: "in_progress"` -- say `say` once, then stop. The background job wakes you when it is done; then call `start_dream_customer` again.
4. `stage: "ask_apify"` -- say the tool's cost line. Ask with AskUserQuestion, two buttons
   (go ahead / skip). Then call `start_dream_customer` again with
   `apify_answer: "yes"|"no"`. Never ask twice.
5. `stage: "research"` -- read `business` (what they sell, who buys, where, language,
   currency), `research_plan`, `allowed_actor_ids`, `web_search_budget`, `already_saved`
   and `RULES`. Never redo or re-research anything `already_saved` names.
   - Tell the customer once, briefly, that this will take a few minutes -- they should
     never be left with no news while you work.
   - If the customer said yes at step 4 AND `research_plan` is there: run the Apify actors
     as the server names them -- call the exact tool in `run_tool` with the exact
     input in `run_input` unchanged, then read `dataset_items_step.dataset_id_path` out of
     the run result and call `dataset_items_step.run_tool` with `dataset_items_step.
     run_input` plus that value, unchanged otherwise. If Apify isn't
     connected, or the run fails, times out, or comes back empty -- say so in plain words
     once, never retry, and move straight to web search. Never invent a Reddit post, a
     review, or a number you did not see in a real result.
   - If not enough came back, the customer said no at step 4, or there is no
     `research_plan`: run WebSearch/WebFetch, one query at a time, up to
     `web_search_budget.max` -- a hook enforces the cap and will deny a call past it. Never
     invent a number or quote you did not see on a real page.
   - Whatever is still missing after that is AI judgement, always labelled "our view" --
     never shown as a real quote or a real source.
   - As soon as the research is done, save it: `save_dream_customer(phase: "research_log",
     entries: ...)` -- every Apify run and search made, with its cost where known.
   - Then build the dartboard (niche -> sub-niches -> micro-niches -> the chosen one and
     why -> an audience correction if the stated audience looks wrong), matching
     `SAVE_TEMPLATE.dartboard` exactly, and call `save_dream_customer(phase: "dartboard",
     ...)` with those fields. In the dartboard save, set `situation`: `emergency` if the buyer has an urgent need and decides fast, `wish` if they buy a want not a fix, else leave it.
   - A shape error comes back naming the problem -- fix that ONE thing and call again,
     ONCE. If it errors again, say the line at the top and STOP this run.
   - Then build up to 10 personas (3 cold / 4 warm / 3 hot), matching `SAVE_TEMPLATE.personas`
     exactly -- its lists (counts in `RULES`), 10-12 pain and 10-12 pleasure phrases, journey stage,
     lost-deal reason, ONE searcher-or-scroller call, hangouts, every public fact source-tagged,
     every judgement labelled "our view". If the business really has fewer buyer types, save
     fewer; never copy one to fill the count. ALWAYS save them in batches of about 3 with
     `save_dream_customer(phase: "personas", ...)`; the last batch also carries
     `main_persona_recommended_id`, `main_persona_why` and `main_persona_sources`. Each
     reply says `next` -- do that; stop at "finish". On `fix`, send ONE `phase: "fix"` save as
     `fix_pass` says, never a second.
6. `stage: "review"` -- ask `question` with AskUserQuestion; its text holds the profile. Add no reply
   text before it (approve the recommended one, or name a different one).
   - Approve the recommendation -- call `choose_main_persona(persona_id: "recommended")`.
   - Names a different persona -- call `choose_main_persona(persona_id: <that persona's
     id>)`.
   - A none-fit reply -- ask ONE short question (in their own words) why, then go back
     to step 5 and rebuild the personas ONCE more with that answer folded into the
     judgement. If they still say none fit after the rebuild, never rebuild a second time
     and never stop with nothing saved. Ask ONE short question: which of these is the
     closest, and what is different about their real customer, in their own words. Then call
     `choose_main_persona(persona_id: <the one they name>, closest_fit: true, fit_note:
     <their words, unchanged>)`. If they will not choose one, offer the recommended profile
     as the closest and ask for a yes.
   - A later / skip / not-now reply (here or at any question) -- say in one line it stays
     open for later, and stop. Never call `choose_main_persona`, never
     tick anything: only a real approval finishes this step.
   - The customer asks "why this one?" at any point -- call `get_dream_customer`, read
     `main_persona.why` and its sources, and answer in plain words with those sources,
     never a new guess.
7. `stage: "done"` -- say `say`. Stop. **No model tick** -- `choose_main_persona` ticks
   step 9 on the server the moment the customer approves.

Answer in the customer's own language and currency throughout -- follow their words, never
default to English or US pricing.
