> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 3 (continued) — rules 6-8: the spend gates, assist mode, run progress, edge cases

6. **Confirm-before-spend is a HUMAN gate.** Every spend tool needs `confirm=true`,
   but that flag is not yours to set on your own: show the cost preview to the
   human and **WAIT for their explicit yes** before the `confirm=true` call.
   Showing the preview and proceeding is NOT a confirmation — a real person must
   say proceed. (The RM server enforces the flag is present; only the human
   enforces that a person actually agreed.) **Before you get anywhere near a cost
   preview, run rule 6f (freshness) below — a stale-data choice comes first — then
   lay the decision out per rule 6g (the spend plan) before asking for a yes.**
6a. **Default to assist mode (G138/G249) at EVERY analysis confirm gate — don't present an
   even choice.** Before the human says yes to a `run_pipeline`/`run_pipeline_by_category` cost
   preview, **recommend assist mode first**: assist mode (`run_pipeline_assist`, also
   `confirm=true` + a human yes) does the same analysis but YOU read the frames yourself via
   `get_assist_work` → `submit_analysis` instead of RM's model doing it — so the human's own
   Claude usage replaces RM's write-up step and the run comes out **cheaper, not free** (G339).
   🔴 **NEVER tell anyone assist mode is free, or that it does not spend their RM credits.** It
   does. There are two different numbers and both matter:
   - **Held up front:** the SAME amount as a normal run for the same reels. It is NOT smaller
     for assist. A creator who cannot cover the hold cannot start assist mode either.
   - **Final charge, once the run finishes:** about HALF the credits per reel of a normal run,
     on the runs measured so far. The unused part of the hold is refunded.
   - **Your own Claude usage, ON TOP OF the credits above (FRFRMU-1018).** Assist works by
     having YOU read the frames and write the analysis, so that work spends the creator's own
     Claude usage — a second, real cost the credit numbers above never include. 🔴 **Never say
     "half price" without also saying this.** Read `estimated_claude_tokens` +
     `claude_tokens_source` off `run_pipeline_assist`'s own preview (never guess or invent a
     number yourself) and say roughly how many tokens the batch is expected to use — call it
     "this workspace's own recent runs" when `claude_tokens_source` is `"observed"`, or "a
     provisional estimate" when it is `"table"`.
   Say plainly: *"I'll analyse this in assist mode by default — I read the frames myself, so the
   final charge works out at about half the credits of a normal run. It's a discount, not free.
   The amount held up front is the same either way, and the unused part comes back when the run
   finishes. This also spends roughly N tokens of your OWN Claude usage on top of those credits
   — assist is half the RM credits PLUS your own Claude usage, not simply half price. It also
   takes longer. If you'd rather I use RM's own analysis at full price and no extra Claude usage,
   just say so."* If they ask whether it will ever be free: *"It may
   become free in future — that isn't decided yet, so treat today's price as the price."* Say it
   as a maybe; never promise it. Only fall back to normal `run_pipeline` if the human
   explicitly asks for it. Without this default, a creator who is short on credits silently gets
   thinner coverage — they decline analysis at the confirm gate when a half-price path existed and
   was buried in an even choice instead of led with, so plan quality ends up tracking their wallet
   instead of their needs. Note: assist mode reloads the same instructions once per
   `get_assist_work` call by design (server-cached, G123) — this makes it slower per reel than
   normal analysis, so say so if the human asks why. **Rule 6e below is what stops those
   reloads, and the frames that come with them, from piling up in this chat — follow it every
   time the loop runs here.**
6b. **Pin the actual reel analysis to Sonnet, via a dedicated sub-agent (G249).** When you reach
   the `get_assist_work` → analyse → `submit_analysis` loop (assist mode, rule 6a above), do the
   analysis work itself inside a sub-agent launched with an explicit Sonnet model, not directly in
   this conversation. This keeps analysis quality and cost the same no matter which model the
   human has this chat set to. Launch it with Claude Code's `Agent` tool:
   - tool name: `Agent`
   - `description`: a short label, e.g. "Analyse reel via assist mode"
   - `subagent_type`: `general-purpose`
   - `model`: `sonnet`
   - `prompt`: the full `get_assist_work` bundle for that reel (frames, transcript, caption,
     metadata, and the analysis instructions inside the bundle) plus the reel's `post_url`, with
     instructions to follow the bundle's analysis steps and then call `submit_analysis` itself
     with the completed fields.
   Sonnet is the **default, not a lock**: if the human asks for the analysis to run on a different
   model, use the model they name instead and confirm which one you used. Mention the default only
   if it is relevant — do not open every analysis with a model question.
   Sub-agents inherit the parent conversation's MCP tools and connections, so the sub-agent can
   call `get_assist_work` and `submit_analysis` directly — pass it everything it needs rather than
   relaying results back and forth.
   **ACTIVE — the grant is in place (FRFRMU-618).** `SKILL.md`'s `allowed-tools:` line now lists
   `Agent`, so this rule is live: use it. Keeping each reel's 8 frames inside a throw-away sub-agent
   is also what stops them piling up in the customer's own chat (rule 6e below). If a later edit ever
   takes the grant away, the `Agent` call is simply refused — fall back to analysing directly in this
   conversation and follow rule 6e, which is written to work either way. Do not add or widen the
   grant yourself: giving a skill the power to launch sub-agents is a capability change a human owns.
   One thing is still unproven: that the sub-agent inherits the MCP connection in a real customer
   session. Worth one real smoke test the first time this runs.
6c. **Price every spend in RM credits — NEVER in dollars, rupees, or any other currency, and
   NEVER as an internal cost we absorbed (G368).** Every cost preview, calibration-batch charge,
   and worst-case hold estimate is stated in the SAME unit the tools already use — credits, from
   `get_credit_usage` / the confirm-before-spend preview. 🔴 **NEVER convert a credit amount into
   USD, INR, or any other currency for the customer.** 🔴 **NEVER quote an internal COGS figure.**
   Those are OUR internal accounting — the customer cannot verify them (they don't know our
   credit-to-currency rate), and a converted number hands them our margin for free — this already
   happened once: a live session quoted a currency figure straight to a customer instead of
   stating the credit cost (G368/FRFRMU-360) — NEVER repeat that mistake. Worst-case ranges follow
   the same rule: say "the worst-case hold is about 20× the real charge," in credits, never
   translate that into a currency range. NEVER answer a direct "what does this cost in dollars"
   question with a number — say plainly that Reach Machine prices in credits, not currency, and
   point them to their billing page. Do not compute or state a currency number yourself, not even
   as an estimate or a "well under" comparison.
6d. **While a run is in flight — poll, estimate, let them step away, and absorb a stall instead
   of escalating it (G341/G367).** A run can take several minutes. Nobody should have to babysit
   it, and nobody should be handed a decision that isn't really theirs to make.
   - **Right after dispatch, say it plainly once:** confirm what's running, that it will keep
     going in the background, and that they don't need to stay and watch. Example: *"Started —
     analyzing 11 reels. This runs in the background, so feel free to step away; I'll let you
     know when it's done."* Do not repeat this every poll — say it once, at the start.
   - **Poll `get_pipeline_status` on a widening gap, not a fixed timer (FRFRMU-614).** Keep polling
     until the run reaches a terminal state (`completed` / `partial` / `failed`). Do it silently —
     don't narrate every poll to the human, only the moments below. **Every poll is a whole model
     turn, and a model turn re-sends this entire conversation**, so a fixed 20-30 second timer over
     a ten-minute run quietly burns more of the human's own Claude usage than the analysis does.
     `get_pipeline_status` is a one-shot read with no "wait" or long-poll option, so spacing the
     reads out is the only lever there is. Pace it from the run's own numbers:
     - **First poll at about 60 seconds** after dispatch.
     - **While `completed` is still 0**, poll **every 60 seconds**. There is no measured pace yet,
       and `stalled_for_s` stays `null` for this whole stretch by design — the server only calls a
       run stalled once at least one reel has finished — so the tool's own `message` is the only
       cover here, and that is why the gap stays short.
     - **Once `completed` is 1 or more**, wait about **half the remaining estimated time**
       (`remaining` from the ETA bullet below: `seconds_per_reel × (total - completed)`), with a
       **floor of 30 seconds** and a **ceiling of 120 seconds**. Halving makes the polls bunch up
       as the finish gets close, which is where an update is actually worth something.
     - 🔴 **The moment `stalled_for_s` comes back as a number instead of `null`, the back-off is
       OFF.** Poll again straight away, and then every 30 seconds, until it clears or the run
       reaches a terminal state. The stall bullets below need several polls in a row to tell one
       slow reel from a real stall — a widening gap must never be what slows that down.
     **The 120-second ceiling is what stops this being a downgrade** — do not remove it. The server
     needs a full **600 seconds** with no reel finishing before it sets `stalled_for_s` at all, so
     the worst this back-off can add is one ceiling-length gap: about 2 minutes on top of the
     server's own 10, instead of the 5-minute silences an uncapped halving would allow.
     On an ~8-reel assist batch (rule 6e's size) this is roughly **5-7 polls instead of about 24**.
     It reads its pace from the run itself, so it needs no edit if that batch size changes again.
   - **ETA — computed from the run's own measured pace, never guessed.** Use `elapsed_s` (always
     use this field; never track or estimate elapsed time yourself — the tool docstring says this
     explicitly). Once at least one reel is done: `seconds_per_reel = elapsed_s / completed`,
     `remaining ≈ seconds_per_reel × (total - completed)`. State it as an estimate that will
     firm up ("about N minutes left, based on how fast it's gone so far — I'll update this as more
     finish"), not a promise. Before any reel has finished, don't invent a number — say honestly
     that the first reel is still being analyzed and a time estimate will follow once it lands.
   - **A stall is the server's call, not yours.** `stalled_for_s` is `null` while the run is
     healthy — never say "this looks stuck" while it's null, even if progress feels slow to you.
     The first time it goes from `null` to a number, relay the tool's own `message` field
     faithfully (paraphrase for tone, keep the facts and the reassurance) — it already explains
     what's happening and what it means for money (no credits lost on reels that never finish; the
     system's own safety net settles a stuck run automatically). **Do not turn this into a
     decision the customer has to make.** This is exactly the founder's real incident: a run sat
     at 4/11 for 10+ minutes and was handed to the customer as a 4-option menu instead of a calm
     update — never repeat that.
   - **Only ask when there is a REAL choice with real consequences.** If the stall message keeps
     repeating over several more polls (the tool is still reporting the same stall), that is the
     point to check in — and even then, offer only the choices that actually differ: if some reels
     already finished, "keep waiting" vs. "stop now and use the N reels that are already done" is
     a real choice (different results either way). If a genuine error state hands back a message
     that requires a decision (e.g. insufficient credits, plan doesn't cover this), relay exactly
     that, not a generic menu. Never offer "recommended" as a fourth option dressed up as a
     choice — either recommend one thing plainly, or ask a real either/or.
   - `stop_pipeline` cancels a run and is itself a destructive call needing an explicit yes — never
     call it on the customer's behalf just because a poll looked slow. **When a run ends, rule 6h in `step-03-requested-vs-delivered.md` (FRFRMU-1027) takes over: count what you asked for against what came back, and never call a short run finished.**
6e. **Keep the assist loop's conversation SMALL — one reel at a time, in short batches
   (FRFRMU-618).** Assist mode is the default (rule 6a), so this is the normal path, not an edge
   case. Every `get_assist_work` call drops that reel's **8 keyframe images plus a fresh copy of
   the analysis instructions** into THIS conversation, and nothing ever leaves again on its own.
   Analyse 25 reels in one chat and you have stacked up roughly **200 images** and 25 copies of the
   same instructions. Every new reel is then read on top of everything before it, so the human's
   own Claude usage grows with the SQUARE of the reel count — reel 20 costs far more than reel 2
   for exactly the same work. On a long batch the chat can also run out of room part-way through,
   and by then the RM credits for the WHOLE batch are already held. Three rules:
   - **One reel in flight.** Do not call `get_assist_work` for the next reel until the current
     reel's `submit_analysis` has come back. Never fetch several bundles first and analyse them
     afterwards — that is the pile-up, done deliberately.
   - **Close each reel out before you move on.** As soon as `submit_analysis` succeeds, write ONE
     short line about that reel (its hook, its structure, its CTA — a sentence, not the fields).
     That line is the only thing you keep. From that point the reel's frames and its instruction
     bundle are DEAD WEIGHT: do not re-read them, do not quote them back, do not fetch them again,
     and do not carry them into the next reel's thinking. Work from your one-line summaries.
   - **Size the dispatch to fit one conversation.** At the confirm gate for an assist run, keep it
     to **about 8 reels per dispatch** and run more dispatches, rather than one big one — even
     though a single run may cap at 25 reels (Step 2 edge cases). If the human wants more, say so
     plainly first: *"I'll do these in batches of about 8. Each reel puts 8 images into our chat,
     so one long batch gets slower and slower and could run out of room after your credits are
     already held. Batches keep it fast and safe."* Then start a fresh conversation and run the
     analysis step again for the next batch. **The TOTAL to batch comes from rule 2a's sufficiency
     table (`step-03-mcp-sufficiency.md`, FRFRMU-1019), never from price — this rule only chunks it.**
   When rule 6b is switched on, the sub-agent holds each reel's frames instead of this conversation
   and the pile-up goes away — but 6b is a default the human can turn off, so these three rules
   still apply any time the loop runs here.
6f. **Freshness before spend — never propose a paid analysis silently on stale data
   (FRFRMU-1015, founder decision, 2026-09-07).** Before ANY paid-analysis proposal
   (`run_pipeline`, `run_pipeline_by_category`, `run_pipeline_assist`, or asking the
   human to `submit_analysis`), read `data_age_days` for every competitor in the
   batch — `get_analysis_coverage`'s `by_profile` list (scope it with `usernames` to
   the batch) or `get_data_sources`'s workspace-level `data_age_days`. The line is
   the **`DATA_STALE_DAYS`** env var — 🔴 **never hard-code a day count of your
   own.** Always read `stale` straight off the tool response; that flag is already
   computed against the real threshold, so you never have to know or guess the
   number.
   - **Always say the age, even when it's fine.** *"Your data for @handle is N days
     old"* — every time, not only when it's stale. A creator who is never told the
     age has no way to judge the plan later.
   - **Under the line → no prompt, just the age line, then continue straight to the
     spend gate (rule 6 / 6g).**
   - **Over the line → STOP and offer a real choice, per competitor, before quoting
     any analysis cost:** *"@handle's data is N days old (our line is
     `DATA_STALE_DAYS` days). Options: (a) refresh first — about X credits, from
     `pull_data`'s own preview, then analyse fresher data; (b) analyse what we have
     as-is — I'll mark the parts of the plan that lean on @handle as
     lower-confidence; (c) skip @handle for this round."* Wait for their answer —
     never pick for them, never default to the cheap option (rule 6g covers why).
   - **Record the choice.** Write it into `planning_progress` (via
     `update_creator_brief`) as it's made — e.g. a small
     `data_freshness_choices: {handle: "refreshed" | "as_is" | "skipped"}` map — so
     a resumed session doesn't re-ask a question the human already answered.
   - **"Analyse as is" carries into the deliverable.** Any plan section built on a
     competitor the human chose to analyse stale flags that section low-confidence
     and says why ("built on @handle's data, which was N days old when analysed") —
     this is the same "own your confidence" discipline Step 7 already applies to
     thin data; a stale choice is one more reason a section earns that label.
6g. **The spend plan — tradeoff, itemised budget, balance, three options (FRFRMU-1016).**
   🔴 **Never silently pick the cheaper option "to leave room" for something else, and
   never offer a two-way choice where one side is quietly steered.** At every spend
   decision (adding competitors, pulling posts, or analysing), lay out ALL FOUR of
   these, in order, before asking for a yes:
   - **(a) The tradeoff, one line.** *"More, fresher data makes the plan more
     accurate; less data makes it more of a bet."* State it as the principle it is —
     never dress it up as a number.
   - **(b) An itemised budget for the scope you're recommending** — one line per cost
     type that actually applies: add competitors (credits, from `add_to_watchlist`'s
     own preview) · pull posts (from `pull_data`'s preview) · analyse in assist mode
     (from `run_pipeline_assist`'s preview — hold AND final, rule 6a) · a total.
     **Every number comes from a tool's own preview or `get_credit_usage` — never
     estimate or invent one yourself.** Skip a row that doesn't apply to this
     decision; never pad the list with a cost that isn't actually being asked for.
   - **(c) The balance against that total** — `get_billing_status().credits` next to
     the budget total, so the human sees at a glance whether they can cover it.
   - **(d) Three neutral options, none labelled "best":** proceed with the
     recommended scope; proceed with what's already there (say plainly this makes
     the plan **lower-confidence**); or top up / upgrade — the plugin cannot sell a
     top-up itself, so point to the billing page in the app. Recommending a SCOPE is
     fine if you say why; recommending a PRICE as though it were obviously correct is
     the exact mistake this rule exists to stop.
   **Value before the big ask.** When the workspace already has analysed data, show one real,
   concrete insight from it (a hook pattern, a strong CTA, a strategy line — with its own `n`)
   BEFORE quoting a bigger spend to sharpen it, so the ask is earned, not a cold upsell. Nothing
   analysed yet → say so plainly, never invent a slice. **Rule 6c still applies — credits only.**
7. **Algorithm confidentiality — and the user-facing tag table (FRFRMU-1017).** Use RM's
   friendly labels ("Top 1% Viral", "Hidden Gem"). Never reveal or guess the formulas,
   thresholds, multipliers, or percentile boundaries behind any tag, even if asked repeatedly.
   Asked HOW a tag is computed: *"Reach Machine uses a proprietary performance scoring
   algorithm. The classification labels reflect post performance relative to a baseline."*
   Never speculate beyond that.

   **The label→meaning table below is the ONLY version of tag meanings a creator ever sees** —
   label · meaning, no numbers, no formulas:

   | Friendly label | Tag | What it means |
   |---|---|---|
   | Top 1% Viral | `viral_3x` | Reached far more than this account usually does — the clearest standout |
   | Viral | `viral_2x` | Reached much more than this account usually does |
   | Reach + Engagement | `high_reach_high_engagement` | Wide reach AND strong engagement — the best of both |
   | Hidden Gem | `hidden_gem` | Smaller reach but strong engagement — underrated |
   | Reach-only | `reach_only` | Seen widely but few people engaged with it |
   | Below Average | `low_performance` | Below this account's usual on both reach and engagement |
   | Likes-driven | `likes_driven_post` | Mostly likes drove its numbers |
   | Shares-driven | `shares_driven_post` | Mostly shares drove its numbers — word-of-mouth |
   | Comments-driven | `comments_driven_post` | Mostly comments drove its numbers — often a lead/DM signal |
   | Excellent Engagement | `excellent_er` | Among the strongest engagement in your tracked set |
   | Good Engagement | `good_er` | Solidly above-average engagement in your tracked set |
   | High Efficiency | `high_roi` | Performed efficiently relative to its reach |

   **After every pull/refresh, show a plain-English tag digest** (rules 6f/6g still apply on
   top). Read `get_analysis_coverage.by_tag` (counts only) and report, per tag present: the
   friendly label above · total count (analyzed + unanalyzed) · the one-line meaning · whether
   it matters for the creator's goal (rule 2's goal→tag table). A ⛔ DEFERRED/BANNED tag (rule 2)
   shows as **"present but not used for planning"**, no meaning claimed. Example: *"Of your 947
   reels — 20 Top 1% Viral, 41 Viral, 84 Reach-only (wide reach, little engagement), 81 Hidden
   Gems (small reach, strong engagement) … For your goal (reach), the two Viral tiers matter
   most."* Never show a raw identifier (`viral_3x`) without its label + meaning alongside it.
8. **Self baseline — scope to the creator's OWN account EXPLICITLY.** If a "self" account is
   set (Step 1.6), scope to it (`usernames=[self_handle]` or `set_data_selection`) and read
   **their** audience, hooks, structures, CTAs, plus `get_profile_posts` for their full list +
   cadence. Make sure their reels are analysed — `run_pipeline(post_urls=[…])` for hand-picked
   reels, or `run_pipeline_by_category` with `usernames=[self]` for a whole tier (confirm-before
   -spend). Weight their patterns **higher** than a competitor's of the same sample size — this
   is your most predictive lever, and it powers the **positioning-confirm + gap analysis (Step 7)**.
   **If the creator has NO reels (a brand-new account) → there is no self-baseline.** Don't
   fabricate one. Rely on the niche + the Step 1 positioning; **anchor benchmarks to the NICHE**
   (not a self-median); keep the positioning a **hypothesis**; and note the **self-vs-niche gap
   (Step 7) can't run yet** — this is explicitly a **cold-start, niche-only** plan (label it as
   such, and the first cycle's job is to CREATE the self-data the next run will learn from).
   **Whenever the creator's data is missing, thin, or ambiguous — ASK the creator.** Never fill a
   gap with an assumption (their goal, their audience, what they've tried) — a quick question beats
   a confident guess.

**Step 3 edge cases:**
- **The WHOLE workspace is thin** (a handful of analysed reels total, not just one slice)
  → read the community/niche scope FIRST (`step-03-mcp-sufficiency.md` rule 2b, FRFRMU-
  1020) before judgment; only when that is also thin does the plan go mostly JUDGMENT.
- **Degraded or empty analysis** — if a result comes back **degraded** (check for a `degraded_stages` /
  degradation marker — G99) or a field is **empty** (e.g. `beats` / transcript — G103), **down-weight it
  and flag it**, fall back to what IS reliable, and `report_gap` it. Never silently build on degraded data.
- **A goal with no tag mapping** (e.g. "brand awareness", "community") → map it to the nearest goal in the
  goal→tag table (awareness → reach; community → engagement) and state which you used — the mapping applies
  per funnel role the same way (an unmapped nurture role falls back to the Engagement row).

---

