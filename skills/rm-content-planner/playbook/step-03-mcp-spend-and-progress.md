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
   🔴 **By tag/category (FRFRMU-1517):** `run_pipeline_by_category` has its OWN `mode` field —
   `mode="assist"` is already the default, so calling it with no `mode` argument at all IS the
   assist path described here, no separate call needed. **Never pass `mode="full"` unless the
   human explicitly asked for full price** — that flips it to the same cost as a plain
   `run_pipeline` run, silently doubling the charge. If `mode="assist"` comes back
   `status="assist_disabled"`, that means this server has assist switched off entirely — relay
   that plainly and only then fall back to `mode="full"`, the same as the "server refused, ask
   for full price" case below.
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
   🔴 **Feed the token estimate back, or it never becomes real (FRFRMU-1288).** Rule 6a's
   `claude_tokens_source` can only ever say `"observed"` if something reports actual usage back.
   When the sub-agent's own `Agent` tool result shows its input/output token counts for that ONE
   reel, pass them as `claude_tokens_in` / `claude_tokens_out` on that SAME reel's
   `submit_analysis` call (both optional — omit entirely if you don't know the numbers; never
   guess or estimate one yourself). This is per reel, not a one-off end-of-batch report — do it on
   every `submit_analysis` where you actually have the numbers, so the workspace's own observed
   average keeps building instead of staying stuck on the table estimate forever.
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
6d. **While a run OR a data pull is in flight.** Poll, estimate, let them step away, absorb a
   stall instead of escalating it, and never treat a data pull's thinner honesty as an excuse to
   skip the same discipline — full rule + the pull-specific additions now live in
   `playbook/step-03-progress.md` (FRFRMU-1289/1284) so this file stays under the line cap. Load
   it whenever you dispatch `run_pipeline`/`run_pipeline_assist`/`run_pipeline_by_category` or
   `pull_data` and need to wait for it.
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
   - **Pass `have_instructions_version`, and confirm the bundle arrived whole (FRFRMU-1567).**
     Your FIRST `get_assist_work` call of a run hands back `instructions_version` — pass it as
     `have_instructions_version` on every later call (while you still hold the instructions in
     context) so those calls skip resending the ~15K-token instructions block. Before analysing
     ANY bundle, check it carries an `end_of_bundle` block and one "Frame N of M" label per frame
     `end_of_bundle`'s `frames_sent` says it sent. Missing either means your client cut the
     response before it arrived — the closing frames (where CTAs live) are exactly what a cut
     removes first. Do not analyse a reel you cannot confirm arrived whole: call `get_assist_work`
     again with that SAME `post_url` to re-fetch it (this re-serves the reel without claiming a
     different one), or `get_assist_instructions` if only the trailing instructions were cut.
   When rule 6b is switched on, the sub-agent holds each reel's frames instead of this conversation
   and the pile-up goes away — but 6b is a default the human can turn off, so these four rules
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
6g. **The spend plan — tradeoff, itemised budget, balance, the reels, three options
   (FRFRMU-1016/1518).** 🔴 **Never silently pick the cheaper option "to leave room"
   for something else, and never offer a two-way choice where one side is quietly
   steered.** At every spend decision (adding competitors, pulling posts, or
   analysing), lay out ALL FIVE of these, in order, before asking for a yes:
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
   - **(d) The reels, and why each one (FRFRMU-1518).** Every `run_pipeline` /
     `run_pipeline_by_category` / `run_pipeline_assist` preview now carries its own
     `candidates` — the EXACT reels that call would dispatch — plus `tag_landscape`,
     the free cross-account classification count for the same window. Use them, don't
     re-derive them:
     - **First, one line from `tag_landscape`**, friendly labels only, with the window
       it printed — *"Across your 6 accounts, last 90 days (312 posts): Top-1%-Viral
       14 · Hidden Gems 22 · Comments-driven 9."*
     - **Then list every reel in `candidates`** (up to the cap) as `@handle · friendly
       labels · views · one line: why this reel serves YOUR goal` — the "why" comes
       from rule 2's goal→tag table, applied per the reel's **funnel role** (G328),
       not just the plan's overall goal once.
     - **Above the cap** (`candidates_truncated: true`), list by account from
       `candidates_by_account` (handle → count) instead, and offer the full list.
     - **Never a raw internal tag name or a formula** — labels only (rule 7 /
       FRFRMU-1017).
     - **If the human wants to swap one out** ("replace #6"), re-call the SAME preview
       with that reel's URL added to `exclude_urls` — the pool backfills from the rest
       to the same count — and show the NEW list before asking again.
   - **(e) Three neutral options, none labelled "best":** proceed with the
     recommended scope; proceed with what's already there (say plainly this makes
     the plan **lower-confidence**); or top up / upgrade — the plugin cannot sell a
     top-up itself, so point to the billing page in the app. Recommending a SCOPE is
     fine if you say why; recommending a PRICE as though it were obviously correct is
     the exact mistake this rule exists to stop.
   **Value before the big ask.** When the workspace already has analysed data, show one real,
   concrete insight from it (a hook pattern, a strong CTA, a strategy line — with its own `n`)
   BEFORE quoting a bigger spend to sharpen it, so the ask is earned, not a cold upsell. Nothing
   analysed yet → say so plainly, never invent a slice. **Rule 6c still applies — credits only.**
   **Record (d)'s disclosure** as one more `select` BuildStep in Step 12's batched
   `record_build_steps` call (`step-12-after-the-save.md`) — `inputs: {tag_landscape,
   candidates_shown, cap, reason_rule: "rule-2 row <role>"}`, `action: "shown to
   customer before spend"`. Don't send it separately; it rides the same batch as every
   other step from this run.
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

