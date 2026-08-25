# Playbook — Reach Machine → a creator's content plan

> **What this is.** A repeatable method for turning Reach Machine (RM) competitor
> intelligence into a content plan that actually grows **one specific creator's**
> account. It exists because the first attempt (the AI-influencer calendar test,
> 2026-07-17) produced a beautiful plan that a senior SMM scored **5/10**: it
> decoded what travels for big creators, then handed those tactics to a
> zero-follower account unchanged. This playbook is the translation layer that
> stops that happening again.
>
> **Plain English.** RM tells you *what already goes viral for established
> creators.* It does **not** tell you *what THIS account, at ITS size, in THEIR
> voice, should post.* This playbook is everything you add on top of RM so the
> plan is real, not a pile of copied reels.

---

## The one principle

**RM data is an ingredient, not the recipe.** Every RM number describes creators
who already have reach. Before it becomes a plan you must translate it for (1) the
account's **stage**, (2) the creator's **own identity/proof**, and (3) the SMM
fundamentals RM was never built to give (profile, retention, cadence, measurement,
community). Skip the translation and you ship confident-looking mimicry.

---

## The Rigor Rules — the standard EVERY step is held to (NOT a stage you do once)

These nine rules (**§A–§I**, spelled out in full at the end of this file) are **live in every
step** — not an optional appendix, not a final stage. They are the whole difference between a plan
that is data-DRIVEN and one that only *looks* data-informed, so carry them through the entire
method. Each step below tells you which §s it must obey.

- **§A Reel Bet** — every reel = Proven Pattern × First-Party Topic × Audience Tension (never novel × novel).
- **§B Confidence** — read the **median, not the mean**; label High / Medium / "a bet"; below n ≈ 5 it can never be data-driven.
- **§C Cross-tabs** — pick winning **combinations** (`group_by`), not single levers read in isolation.
- **§D Goal-conditioned** — rank levers/topics by the metric that matches the goal (reach vs leads vs authority).
- **§E Niche** — the data's topics are the candidate set; weight by median, not competitor share; mine the creator's OWN comments/DMs too.
- **§F Audience** — model hook/structure/CTA/topic for the creator's ONE target segment, with the sample-size guard.
- **§G Honest labels** — show the real data niche AND the reframed idea; never dress one up as the other.
- **§H Experiment** — every reel gets a hypothesis + a **stage-appropriate** kill/scale rule.
- **§I Provenance** — tag every choice DATA-DRIVEN / DATA-INFERRED / JUDGMENT by the operational rule; the `validate_content_plan` code check (G118) now enforces the countable half.

**When the data is thin or degraded** — a small audience segment, empty transcripts/`beats`, a
degraded analysis batch, or a workspace with too few analysed reels — do **NOT** fake confidence.
Drop to a clearly-labelled **judgment-heavy plan**, say plainly to the creator *why* it's thin, and
offer to get more data (analyse the viral tier, add competitors, or have them bring real comments/
DMs). An honest "this is a bet because the data is thin" always beats a confident-looking guess.

---

## The method — the step order (the spine)

Run these in order. **1–2 gather and validate the raw material; 3–6 turn it into a
plan; 7 packages it; 8–10 guard it; 11 saves it.**

1. **Understand → update → VALIDATE the business** — who the plan is FOR (self or a
   client), positioning, goal, stage, capacity; cross-check the profile against real
   data and FIX it; persist everything to the Creator Brief. *(Step 1)*
2. **Find benchmark accounts** — discover relevant, *modellable* accounts (via Apify
   when the tool exists; a manual fallback until then) and track the good ones. Runs
   for **every** plan, not just empty workspaces. *(Step 2)*
3. **Use the RM MCP levers** *(Step 3)* · **Translate for stage** *(Step 4)* ·
   **Differentiate, never mimic** *(Step 5)* · **Retention** *(Step 6)*.
4. **BUILD the strategy (Part A)** — commit the goal + funnel mix, patterns matched,
   patterns to test, and pillars **before** the calendar. *(Step 7)*
5. **Deliver** the calendar in the TEMPLATE shape, presented as the dashboard. *(Step 8)*
6. **Guardrails · checklist · Rules Gate + Critic loop.** *(Steps 9–11)*
7. **Capture** — save to the Content Calendar on the creator's consent. *(Step 12)*

## Progress checkpoints — after every step, not just at the end

**Record progress as you go, so closing the session mid-plan never loses it.** After you finish
each numbered step above (1 through 11 — Step 12's save already persists the whole plan), call
`update_creator_brief` with one field:

- key: `planning_progress`
- value: `{"last_completed_step": <int>, "step_name": "<short label, e.g. 'Step 4 — Translate for stage'>", "summary": "<1-2 plain-English sentences: what was decided in this step>", "updated_at": "<ISO 8601 timestamp>"}`
- source: `"derived"`

This is a full overwrite of the `planning_progress` key each time (matches how `update_creator_brief`
already treats existing keys — updated, not merged field-by-field), so it always reflects the
LATEST completed step, not a growing log. Keep the `summary` short — it exists to remind a human,
not to re-derive the plan from.

Skip this on a **headless** run (`runner.py`) — nobody is coming back to resume a run nobody is
watching; do not spend the extra tool call there. See Step 1's resume check below for the human-run
side of this.

---

## Step 1 — The intake: an EXPERT CONVERSATION, not a form (do this FIRST)

Run this like a senior SMM sitting across from the client — **not** a questionnaire.

**Before anything else — confirm the connections work (G235).** Do this BEFORE asking the
creator a single business question, in one short message, not three separate interruptions:

1. **Reach Machine MCP — a real check, not an assumption.** Call `list_workspaces` (it is free
   and read-only). If it errors, times out, or the connection clearly isn't there, **STOP** and say
   plainly: *"I can't reach Reach Machine right now — please connect it in your Claude settings,
   then let's try again."* Do not improvise a plan from memory instead of real data.
2. **Automatic account discovery — say the honest state up front, not deep in Step 2.** RM now
   has a `discover_accounts` tool, but it only returns accounts RM has **already collected data
   for** — it does not search Instagram (Step 2 covers this in full). Tell the creator once,
   here: *"I'll check what Reach Machine already holds for your niche first. If it holds nothing,
   I'll suggest accounts by hand from what you tell me and flag them as unverified, and you
   approve each one before I add it."*
3. **Website-reading — only if this session has it.** If `WebFetch` (and, on request, Playwright)
   is available this run (Step 1's website step below, G234), no need to say anything yet — it'll
   come up naturally when asked. If neither is available, say so now: *"I won't be able to read
   your website automatically this run — I'll rely on what you tell me instead,"* so a later skip
   never reads as the AI forgetting a step.

A customer should never hit a confusing tool failure mid-conversation that one line up front would
have caught.

**Rule 0 — WHO is the plan FOR? (a gate before everything else).** Is this the account
owner's **OWN** brand, or a **client / brand they manage**? Agencies, freelancers and
social-media managers create for **clients** — so capture positioning, audience, stage
and goal for the **SUBJECT of the plan, never the owner**, and scope the workspace +
Creator Brief to that subject (one workspace per subject). Getting this wrong plans the
wrong brand. If the owner IS the subject, confirm it and proceed.

**Before asking anything else — say why, and what happens to it (G236, G240).** In one short
line, before the first profile question: *"I'm going to ask about your business and positioning —
that's what makes this plan accurate instead of generic, instead of only telling you after
something doesn't match. It's used only to build your plan and improve future ones for you;
nothing leaves your workspace, and nothing is saved anywhere without your OK at the very end."*
This is the same reasoning rule 4 below already uses when a mismatch is found, and the same
privacy line Step 12 already gives at save-time — said ONCE here, upfront, instead of only after
something goes wrong or only at the very end.

Then five rules govern the conversation itself (G100):

1. **Load what's already known FIRST — never re-ask it.** Call **`get_creator_brief`**
   (the durable memory of everything past sessions learned — goal, positioning, funnel
   assets, capacity, offer, baseline) **and** `get_business_profile`. Only ask what's
   **missing or stale**. A returning creator should feel remembered, not re-interrogated.
   - **Unfinished session? Ask, never assume (G369).** If the returned brief carries a
     `planning_progress` field, this account has a plan in progress. Before doing anything
     else, tell the creator plainly what it shows — the step name and the one-line summary —
     e.g. *"Looks like we got partway through your plan last time: we'd finished Step 4
     (translating patterns for your stage). Want to pick up from there, start over, or do
     something else?"* **Always ask. Never resume or restart on your own — always ask
     first** — this is the founder's own instruction ("let user decide the direction"), not
     a convenience default. Whatever they choose, proceed accordingly: "pick up from there"
     means skip straight to the step after `last_completed_step` (re-confirm anything you are
     not sure is still current, same as the staleness rule below); "start over" means ignore
     the saved progress and run Step 1 fresh, and overwrite `planning_progress` on the next
     checkpoint; "something else" means drop out of the planning method entirely and help
     with whatever they actually asked for.
   - **"Stale" is not a feeling — `get_creator_brief` tells you.** Each returned field
     carries a `stale` flag (G229): true when it's older than 30 days. For `goal` and
     `offer` specifically, if `stale` is true, **always re-confirm in one line** before
     building on it — e.g. "Last time your goal was reach — is that still right, or has
     it shifted?" Other stale fields are a judgment call (re-ask if it plausibly changed,
     skip if it's the kind of thing that doesn't — e.g. their origin story). Never
     silently build a new plan on a `goal` or `offer` value the skill knows is 30+ days
     old without asking.
2. **Ask CONVERSATIONALLY — 1–2 questions at a time**, building on each answer. Never
   dump the whole list at once. React like an expert ("got it — so your edge is X…").
   **Be token-sensitive and plain (G237) — write every message as if the person reading it has
   ADHD.** Short sentences. One idea per message. Anchor every question or explanation in ONE
   concrete example instead of a paragraph of theory — e.g. "what's your ONE audience — like 'new
   moms returning to work,' not just 'moms'?" beats explaining what an audience segment is first.
   Don't restate context you already have (if they said their goal is leads, don't re-explain what
   leads means before the next question). Prefer stating a real recommendation over asking an open
   question whenever you can — "I'd guess reach first, since you're at zero followers right now —
   sound right?" beats "what's your goal?" This is the same discipline
   `${CLAUDE_SKILL_DIR}/rules/copywriting.md` already applies to the WRITTEN plan; apply it to the
   LIVE conversation too, not just the deliverable.
3. **DERIVE and RECOMMEND; don't offload the thinking.** From the value proposition you
   can BUILD most of it yourself:
   - **ICP** — construct it from the positioning (S8 PQR2 + the market-segmentation
     method), then CONFIRM it. Don't just ask "who's your ONE audience?" — propose it.
     **Then size it (G233) — real market research, not a vibe.** `WebSearch` the audience/niche
     (e.g. "how many small business coaches in India," "[niche] market size") for a real, cited
     public estimate or range — even a rough one beats none. Give the creator: the number/range
     + its source, what it MEANS in plain terms ("roughly 40,000 potential customers — enough to
     build a business on, even reaching a small slice of them"), and a plain-English
     recommendation — is this audience big enough to build toward, or should they widen/narrow it,
     and WHY. **If nothing credible turns up, say so honestly instead of inventing a number** —
     "I couldn't find a solid public estimate for this niche; treat the audience size as unknown,
     not zero." Save the estimate + source + your recommendation to the Creator Brief
     (`update_creator_brief`, key `market_sizing`) so it's on record, not just spoken.
   - **Goal** — RECOMMEND it from stage + data (cold-start ~0 followers ⇒ **REACH first**;
     you can't harvest leads with no audience), explain why, then confirm.
   - **Funnel assets** — ADVISE from goal + stage whether they even NEED a lead magnet /
     DM automation yet (at ~0 followers it's premature — reply-bait until reach exists),
     asking enough to understand their setup, then decide. Don't gate on a bare yes/no.
   - **Niche commercial landscape (G372)** — a quick, bounded look at how the niche's
     leading players actually operate commercially, outside Instagram content itself.
     **Depth: a quick scan of the top 3-5 players, never a full competitive teardown.**
     Draw the players from the niche's well-known leaders — the creator's own named seed
     accounts if they gave any, plus your general knowledge of the space. For each player,
     `WebSearch` their **offer** (what they actually sell), their **price point** if it's
     public, their core **promise / positioning claim**, and the **funnel step** they lead
     with (a free lead magnet, a DM automation, a waitlist, a paid course, a booked call) —
     read from their **website or public pricing page**, not their Instagram bio. **Cite a
     source and a date for every finding**, same discipline as the G233 sizing step above.
     If a player's offer or price isn't public, say so plainly instead of guessing —
     "couldn't find [name]'s pricing publicly" is a real answer.
     **Why a quick scan and not a deep teardown:** a real teardown needs private data —
     email sequences, DM flows, ad spend — that a web search cannot see, so going deeper
     would mean guessing to fill the gaps, which is exactly what the next rule exists to
     stop. A 3-5-player scan gives enough signal for the white-space in Step 1's
     positioning gate, item (c), without turning a few-minute research step into a
     multi-hour project; a creator who wants a real teardown can ask for one as a separate,
     explicitly scoped request. Save the findings to the Creator Brief
     (`update_creator_brief`, key `niche_commercial_landscape`: a list of `{player, offer,
     price, promise, funnel_step, source, date}`). **Label the whole output JUDGMENT,
     never DATA-DRIVEN** — DATA-DRIVEN stays reserved for claims backed by a real sample
     size from analysed reels, and this is web research, not analysed data.
     🔴 **This NEVER finds, names, or surfaces Instagram accounts to track, and NEVER
     feeds Step 2 (G332, restored once already by G364 — do not repeat that
     regression).** It answers "how does this niche make money," never "who should we
     watch." A player turning up in this scan is not an approved benchmark — that decision
     belongs to Step 2's Apify discovery plus the human-approval gate, alone. Keep the two
     fully separate, out loud, the same way `/market-research` already keeps market-sizing
     separate from `/find-competitors`.
   Ask the human only for what you genuinely **cannot** infer (their story, their real
   numbers, their bold stance).
4. **CROSS-CHECK stated vs ACTUAL data — this is our edge.** The profile/onboarding
   answers are OFTEN wrong. Reconcile every claimed field against the real workspace data:
   if the profile says "business coach" but the tracked competitors + topics are ~90%
   AI/tech, **flag the mismatch and ask which is right** — never plan on a field you have
   reason to doubt. If the web-form persona/stage is wrong, you can't set those via MCP
   (web-only), so tell the human to fix them, and capture the correction in the brief.
   **On any mismatch, TELL THE USER WHY it matters, plainly:** "your profile data is what
   makes the plan accurate — a wrong field gives you a wrong plan." Then update what MCP
   can (positioning), and ask them to fix the web-only fields. Transparency earns the
   correct answer.
5. **PERSIST everything with provenance.** Save positioning to the profile
   (`update_business_profile`) AND the FULL intake to the Creator Brief
   (`update_creator_brief`) — each field carries `{value, source: form|conversation|derived,
   confidence}`. **Persist EVERYTHING you learn — not just the standard fields.** If you
   asked extra questions to understand the business (offer details, website, client type,
   niche nuances), store them too, under any key the Creator Brief needs (it accepts
   arbitrary keys + keeps full history). That store IS the QA/QC record — the plan is
   only auditable if the inputs are written down. This is what makes the next session smarter and the plan QA-able. Save as
   you go, not just at the end.
6. **Score the intake, and never guess silently (G225).** Before building the plan, classify each of
   these key fields as **confirmed** (the human directly answered it), **derived** (you inferred or
   recommended it and the human accepted/didn't push back), or **missing** (never answered): stage,
   positioning, funnel_assets, goal, capacity, production_capability, niche/seeds, offer, constraints,
   brand_voice, audience_questions, plan_size, personal_story. Compute `score = 100 * confirmed_count / total_fields`
   (round to the nearest integer) and write it into `inputs.business_context.intake_completeness =
   {confirmed: [<field names>], derived: [<field names>], missing: [<field names>], score: <int>}`
   when you call `validate_content_plan` / `submit_content_plan` (Step 11/12).
   **Never let a DERIVED field pass silently as if it were confirmed.** Any time you filled a gap with
   your own guess rather than a human-confirmed answer — a recommended goal they didn't explicitly
   agree to, an assumed audience, a guessed capacity — do ONE of two things: (a) ask the human to
   confirm it before moving on, or (b) if you proceed without asking (e.g. a headless/unattended run),
   record it in `inputs.business_context.assumptions = [{field, guess, note}]` — one entry per
   assumption, `note` being a one-line plain-English reason you assumed it — AND write the SAME list
   into the plan itself as `plan.section_00.assumptions` (TEMPLATE.md A0) so it's visible to the
   customer, not just logged internally. **An assumption that exists only in your reasoning and never
   reaches the human or the plan is exactly the failure this rule exists to close.**

**Read the customer's website first, if they have one (G234).** If the creator mentions a
website, ask before you touch it: *"Can I take a quick look at your website before we go further —
it'll save you repeating things you've already written down?"* On a yes:
- Try `WebFetch` first — fast, no browser needed.
- If the site blocks a plain fetch (a wall, JS-only rendering, a 403/timeout) AND the Playwright
  tools (`mcp__playwright__browser_navigate` etc.) are available this session, ask again,
  specifically: *"Your site blocked the normal way — can I try a browser-based method instead?"*
  Only use it after that SECOND explicit yes; never silently escalate to a heavier tool. When you
  do: `browser_navigate` to the URL, `browser_wait_for` a moment if the page looks JS-rendered,
  `browser_snapshot` to read it, then `browser_close` when you're done with it.
- Treat what you read as ANOTHER input to the questions below, not a replacement for asking —
  confirm what you found with the creator (a stale or generic-template site is common) rather than
  assuming it's still accurate.
- If neither tool is available, or the creator says no, skip it and rely on the conversation alone
  — you already said so plainly in the connections check at the top of this step (G235).

**Software or SaaS product? Offer the codebase dossier (G408).** When the SUBJECT's business
is a software product (a SaaS, an app, a tool), the two normal sources routinely undersell it:
creators forget or under-explain their own features on the spot, and public sites lag the
product — features ship months before the site mentions them. But the creator's codebase knows
everything. If the creator (or their developer) uses an AI coding agent (Claude Code or
similar) inside the product's codebase, offer this ONCE during intake:

- Say plainly: *"Your website and what you tell me might miss features worth making content
  about. If you or your developer use an AI coding agent in your product's code, I can give
  you a short prompt to run there — it reads your product and writes me a plain-English
  dossier: every feature, who it's for, what each one lets a user do. No code or secrets
  leave your machine; you review the dossier before pasting it back to me."*
- On a yes, hand over the prompt **verbatim** from
  `${CLAUDE_SKILL_DIR}/PRODUCT_DOSSIER_PROMPT.md` (the fenced block in that file) as a
  copy-paste block, and say it's **re-runnable**: whenever the product grows, they run the
  SAME prompt again and paste back the fresh dossier, so the strategy stays current.
- **Never REQUIRE it.** This is an offer — a creator with no dev agent, or who says no, just
  continues the normal conversation. Missing dossier is not a blocker and never delays the plan.
- **When the dossier comes back:** treat it as creator-supplied first-party input — label it
  never DATA-DRIVEN (§I reserves that for analysed-reel medians); it feeds positioning,
  audience and topic selection, not performance claims. Cross-check it against the website
  and the conversation (rule 4 above) and flag mismatches instead of silently preferring
  either source. Anything the dossier marks **NOT YET PUBLIC** never becomes calendar
  content without the creator's explicit ok — a leaked roadmap is our fault, not theirs.
- **Persist it (rule 5):** `update_creator_brief` key `product_dossier` =
  `{value, source: "creator's dev agent via PRODUCT_DOSSIER_PROMPT", date, confidence}`.
- **Refresh on later sessions:** on any strategy update for a software subject, read the
  brief's `product_dossier` first — if its `stale` flag is set (30 days, G229) or the
  creator mentions new features, remind them in one line to re-run the same prompt before
  you plan on the old dossier.

The fields you must END UP with (derive/recommend/confirm your way to them — don't just
fire them as questions):

- **Account stage:** follower count (0 / <1k / 1k–10k / 10k+), how long they've
  posted, and how many quality reels/week they can realistically sustain.
- **Positioning — a GATE, and the main output of Step 1. Here you build the DRAFT; Step 7
  confirms it with the data.** Call `get_business_profile` first. If `positioning` is
  **empty**, do **not** plan yet. **The right positioning sits at the intersection of three
  things:** (a) what the creator can **OWN** — their first-party proof / method / story (a
  competitor can't copy it); (b) what their **ONE audience desperately WANTS** — their PQR2;
  (c) the **white-space the niche leaves open** — what everyone else already says, so you say
  what they don't. In Step 1 you nail **(a) and (b) by ASKING + LOOKING at their account**;
  **(c) the white-space — and *validating* the audience — needs the data, so it is
  confirmed/sharpened in Step 7.** Run this 6-question capture (the marketing system's avatar
  framework — **F.R.E.D.** + **PQR2**), then sharpen it into a **Big Domino** (the ONE belief
  that, once accepted, makes everything else fall) framed as a **New Opportunity** (a new
  *way*, not "the same thing, better"):
  1. Their one **ownable angle** — theirs, not a copy of a competitor's. **Look at their
     account** to ground it: what do they already do and prove?
  2. Their **first-party proof** — their own business, results, or story; the
     thing a competitor can't fake.
  3. The **ONE** audience they serve — not three squeezed into one bio. **Ask explicitly: is
     this the IDEAL audience for your business, or just who you currently attract?** (Step 7
     cross-checks this against the *actual* audience their own reels reach.)
  4. Their **top 2–3 problems**, in the audience's own words, not marketing-speak.
  5. Their **bold stance / POV** — the ONE thing they believe about their niche
     that others in it won't say out loud. A brand with no stance is
     forgettable — that's the test. *Example:* a fitness coach who says
     "counting calories is a trap" when everyone else preaches macros.
  6. Their **origin / transformation story** — the real before → after: who
     they were, the shift that changed them, who they are now. This is their
     highest-trust content. Ask for it plainly — do **not** write one for them.

  Once you have real answers, **save them** — call `update_business_profile`
  with a `positioning` object. All six answers, including the two new ones
  (bold stance, origin story), go into that **same** `positioning` object —
  there is no separate object for them. Send `positioning` only when you mean
  to **set** it: leaving it out (or sending it as empty/null) leaves the
  existing value **unchanged**. To deliberately erase a stored positioning, set
  `clear_positioning: true` — that is the only way to clear it.

  If the human genuinely can't answer after you've asked — including either of
  the two new questions — you may proceed, but the plan must be stamped
  **"GENERIC — positioning not provided"** at the very top of the deliverable
  (Section 00), not buried in a footnote.

  **If what's already stored contradicts what you just captured** (e.g. the
  onboarding answers describe one audience, the fresh capture describes
  another), stop and ask the human which one is current, then save the
  correction. The freshly-confirmed positioning always wins over stale stored
  answers — this applies to every field in the object, including the bold
  stance and origin story, not just the original four.

  **Positioning is a HYPOTHESIS until the account's own data confirms it.** For a
  young/unproven account (roughly under ~10k followers, under ~90 days, or with no
  self-data yet), the captured positioning is a **bet**, not a fact — the market
  decides which angle actually resonates. So: (a) save it with a
  `positioning_status` of **`hypothesis`** in the Creator Brief
  (`update_creator_brief`); (b) build the month to **TEST 2–3 distinct angles**
  (not over-commit to one unproven line) — each angle is a mini-experiment with a
  kill/scale rule (§H); (c) add a **positioning-review** step to the KPI ritual
  (Step 8): after the cycle, whichever angle wins on the goal metric is promoted to
  **`confirmed`** in the brief, and the next plan concentrates there. An
  established account with a proven angle keeps `confirmed` and ladders to it as
  today. Never present an unproven positioning as settled truth.
- **Their personal story — a separate, optional question, never gated on this decision (G373).**
  Ask it on its own, once, plainly, in the founder's own words: *"Who are you? Why did you start
  this, and why does this matter to you?"* This is different from the origin/transformation story
  above (positioning item 6, the audience-facing proof-of-change) — that one sells the *belief*;
  this one is the plain, personal answer of who they are and what they personally care about. It
  is never subject to the positioning hypothesis/confirmed cycle (Step 7) — it's a fact about the
  person, not a market bet to validate. Make it easy to skip: *"Totally optional — skip it if you'd
  rather not share."* If they answer, save it to the Creator Brief (`update_creator_brief`, key
  `personal_story`, `{value, source: conversation, confidence}`) — never into the `positioning`
  object above (that one gates the "GENERIC" stamp; this one must never block a plan). If they
  decline, save `{value: "declined", source: conversation}` so the skill never re-asks it as if it
  had simply been forgotten. **A declined personal story is a normal outcome, exactly like any
  other missing field — it never blocks the plan.**
- **Funnel plumbing:** do they already have a lead magnet **and** a DM automation
  (e.g. ManyChat) wired and tested? This gates whether any "comment KEYWORD" CTA is
  even allowed (see Step 4).
- **Goal + horizon:** reach, leads, or authority — and over what window.
- **Capacity — ask, don't guess.** "Realistically, how many QUALITY reels/week
  can you make while also running your business?" Default the plan to the
  **LOWER end** of what they say — anything above that is a stretch goal, not
  the baseline. This number drives the effort tagging and batching in Step 8.
- **Production capability — ask, and treat it as an ON-RAMP, not a filter.**
  "What can you produce well right now — comfortable on camera? can you edit /
  screen-record? can you perform a skit, or only talk to camera?" Save it to the
  Creator Brief (`production_capability`). **This does NOT let you drop a format the
  market rewards.** The data defines the *target*; ability defines the *starting
  ramp*. So: lead the early calendar with formats they can execute **well now** (for
  quick wins), AND when a high-reach format needs a skill they lack, **never silently
  cut it** — surface it with a **production path**: learn it, use an AI tool / avatar,
  outsource the edit, or a doable **adjacent** format that hits the *same*
  psychological driver (e.g. can't perform skits → a reaction or POV talking-head that
  lands the same relatable-humor beat). Flag it as the capability to grow into. A plan
  that ignores what the market wants because the creator "can't do it yet" is following
  the creator, not the market — that is the mistake to avoid. (See Step 8 + the Rules
  Gate production check.)
- **Niche + seed accounts + hashtags — this feeds discovery (Step 2).** Their **niche/topic** in a
  phrase, their **core hashtags**, and **2–3 accounts they admire or see as competitors**. **Seeds are
  OPTIONAL and VALIDATED, not trusted:** many creators won't know any — that's fine, the Step 2 angles
  find accounts from the niche + hashtags anyway. Whatever they DO name, **check it yourself** (real?
  relevant? right size to model? reels-active?) and drop bad seeds — a user's guess is often off.
- **Their offer — ask if the goal is leads / sales.** What they actually sell + rough price, so the
  activation / CTA reels (Step 7) drive to a real thing, not a vague "link in bio."
- **Upcoming moments — launches / promos / seasonal.** Any launches, promos, or seasonal peaks in the
  next weeks the content should build toward (Step 7.8). If they don't know, the agent MAY **web-search**
  the niche's seasonal / timely moments to seed it.
- **Constraints & off-limits (MUST ASK).** Anything the plan must NOT recommend: won't show face? topics
  or **claims they can't make** (health / finance / legal / regulated)? competitors they won't name?
  brand no-go words or tone? Capture them — a plan that ignores them is unusable.
- **What they've already tried** — briefly, what's worked or flopped for them. Feeds Step 7: double down
  on their wins, don't re-recommend their failures.
- **Brand voice / tone — DERIVE, then confirm.** Read it off their account (professional / casual /
  funny) + any words to avoid, and confirm. Drives every hook + caption (Steps 5, 8).
- **Their audience's real questions / DMs / FAQs — PROMPT them to bring a batch.** The strongest *demand*
  signal for topics (§E). If they can't yet, tell them to collect their last ~20 DMs / most-asked
  comments before the next run.
- **Plan size — ASK, don't assume.** How many reels does the creator want in this plan?
  **Ask the human, and give YOUR recommendation** as the senior SMM, derived from their
  stage + sustainable cadence + horizon (e.g. a 0-follower account doing 3/week → a
  ~2-week, 6-reel starter is usually right; a warm account chasing a launch may want
  12–20). Never silently pick the number — the count is the human's call, informed by
  your recommendation.

---

## Step 1.6 — The creator's own account is the strongest signal (once there's something to compare it to)

A creator's own past reels — what already worked for **them** — beat a
competitor's pattern at the same sample size. Use that, but only once there's a
workspace to compare against.

- **Capture the subject's own @handle — ASK, don't assume.** **Check the Creator Brief FIRST**
  (`get_creator_brief`, field `instagram_handle`) — that's the value scoped to THIS workspace. Only if
  the Creator Brief has none, fall back to `business_profile.instagram_handle` **and confirm it out
  loud with the subject before trusting it** — that field is shared across every workspace on this
  account, so for a 2nd+ client it's very likely stale (someone else's handle). If neither has one,
  ASK the subject for their Instagram @handle. Then **look at the account** (niche, tone, follower
  count, what they already post) to ground the plan. **Save it to the Creator Brief**
  (`update_creator_brief`, key `instagram_handle`) — this is the authoritative, per-workspace copy.
  Also mirror it to `update_business_profile` for continuity with the web page, but never trust that
  copy back for a different workspace. It's needed for the self-baseline, discovery seeding (Step 2),
  and the bio / pinned reels in the deliverable. Don't ship a plan with a placeholder handle.
- **Guardrail — competitors first, always.** Only recommend adding the
  creator's own account to the watchlist **after** competitors are already
  analysed in the workspace. Never make it the first or only account in a thin
  or empty workspace. **Why, in plain words for the user:** a brand-new
  workspace guesses its niche from whichever accounts are already in it — if
  the creator's own account goes in first, it can set the workspace's niche
  wrong before there's any real competitor data to correct it.
- Once competitors are in place, confirm with the human which watchlisted
  account is theirs (or offer to add it), and treat that account as **"self"**
  in every pull that follows.
- **Weight self-patterns above competitor patterns of the same sample size.**
  If the creator already has 5 reels proving a pattern works for them, that
  beats 5 competitor reels proving it works for someone else.
- **Add the subject's own account to the watchlist and TRACK it.** Once competitors are
  analysed, add the subject's own account (`add_to_watchlist`, confirm-before-spend), then
  **pull + analyse their reels** (`pull_data` → `run_pipeline` / `run_pipeline_by_category`) so
  RM tags **their** reels by the same levers — then you can see **what works and what doesn't for
  THEM specifically**, not just what works in the niche. Scope to them with `usernames=[self]` /
  `set_data_selection` (Step 3, rule 1).
- **Self-vs-niche GAP ANALYSIS — a top input to the strategy (Step 7).** Compare the
  subject's own analysed reels against the niche medians, lever by lever (hooks, formats,
  topics, ER, funnel roles):
  1. **What already works for THEM** (beats their own median) → **double down**.
  2. **What the niche does that they don't** (a lever the niche wins on that they've never
     tried) → the **opportunity gap** to test.
  3. **What they do that UNDER-performs the niche** → **fix or drop**.
  This gap — "what works in the niche" vs "what THIS account should do next" — is one of the
  strongest strategy inputs. Carry it into Step 7 explicitly.
- **Anchor the honest-benchmarks item (Step 8) to the creator's own rolling
  median**, wherever enough of their own data exists — that's a more honest
  ceiling than a competitor's mega-view.
- **Close the loop.** The weekly measurement ritual (Step 8) should produce a
  tiny tracker — per reel: saves-per-1k, watch-time %, shares-per-1k — for the
  creator to fill in after each reel goes out. The **next** planning run reads
  that tracker back, so the plan actually learns instead of starting from zero
  every time.

---

## Step 2 — Find benchmark accounts (Apify discovery — runs for EVERY plan)

**Trigger:** after Step 1, ALWAYS check the benchmark set — `get_workspace_stats` +
`get_analysis_coverage`. An empty workspace needs a full set; a populated one should
still be **refreshed** (niches drift, accounts go stale). Never plan off a thin or
stale benchmark set.

**The SUBJECT drives discovery.** Seed everything off the subject's niche from Step 1
(their handle, topics, hashtags, and the 2–3 accounts they named) — for an agency
that finds the **client's** competitors, not the agency's.

**The honest state of discovery — TWO sources, in this order.**

1. **`discover_accounts` FIRST — free, read-only.** It returns only accounts Reach Machine
   has **already collected real data for**. It does NOT search Instagram, so it comes back
   empty for any niche we have not covered yet. Empty is normal, not an error.
2. **Then Apify, for a LIVE Instagram search** — the plugin ships an `apify` MCP connection
   and the creator signs into **their own Apify account** (browser sign-in, no token to
   paste). This is what actually powers angles A–F below against real Instagram.

   🔴 **Say the sign-in path OUT LOUD, in these words, the first time discovery runs in a
   session — do not keep it to yourself (G366).** Tell the creator: *"Instagram search runs
   through Apify, which is a separate one-time sign-in from Reach Machine. Run `/mcp`, pick
   the `apify` server, and sign in in the browser. If you don't have an Apify account,
   making one at apify.com is free. There's no API key to paste and no `.env` file."* Then
   wait for them. Never let a creator meet the STOP rule below without first having been
   told how to get past it.

🔴 **Apify spends the creator's OWN money, and Reach Machine cannot see or stop it.** RM
credits, the spend ceiling and every confirm-before-spend guard in Step 3 rule 6 govern
**RM** tools only. An Apify scrape is billed by Apify to the creator directly. So treat
every Apify call as a spend gate you enforce yourself: say which angles you plan to run and
roughly how many scrapes that is, and **WAIT for an explicit yes**. Never run a batch of
Apify calls off one vague approval.

🔴 **If Apify is not connected, STOP — do not substitute anything (G332, founder decision
2026-08-19).** A generic web search is NOT a valid substitute. If `discover_accounts` is
empty and Apify is unavailable, unreachable, or the creator declines the spend, say plainly
that you cannot do Instagram discovery right now and why — then stop. Do **not** quietly run
a web search and present its results as benchmark accounts. Do **not** invent handles. The
propose-from-seeds fallback below is **opt-in only**: offer it in one line, and use it solely
if the creator explicitly asks, labelled to their face as **unverified suggestions, not Reach
Machine data**. Any run that degrades from a live source must say so out loud, every time —
never silently.

**The Step 2 flow:**
2.1. **Seed** from the subject — niche, handle, named accounts, core hashtags.
2.2. **Expand — the STANDARD discovery angles (run every one that applies, then dedupe across
   them).** Same set every run, so discovery is consistent for any account or niche. Each angle
   names the Apify tool that does it — call these **bare**, never with a hardcoded `mcp__…`
   prefix, because the prefix differs on a customer install:
   - **A · Hashtag → top posts → authors** — the accounts winning on the subject's core niche
     hashtags. → `instagram-hashtag-scraper`
   - **B · Viral reel → its author** — the highest-view reels on those hashtags/keywords, then add
     who made them (proven performers, not just active accounts). → `instagram-hashtag-scraper`
     to find them, `instagram-scraper` for the reel's owner.
   - **C · Collabs & tags on a viral reel** — its coauthors + tagged accounts (`coauthorProducers`
     + `taggedUsers`); check each for relevance and add the fits. → `instagram-scraper`
   - **D · Similar / related accounts** — Instagram's own "related profiles" off each strong seed.
     🔴 **NOT covered by the bundled Apify tools.** Say so if you skip it; do not fake it by
     guessing which accounts are "related".
   - **E · Keyword search** — the niche terms → more accounts + hashtags.
     → `instagram-search-scraper`
   - **F · Trending-audio page** *(optional)* — accounts riding a niche's trending audio now.
     🔴 **NOT covered by the bundled Apify tools.** Same rule as D — skip it and say so.
   **Report which angles actually ran.** "Ran A, B, C, E; D and F are not available" is a real
   answer. Silently running two angles and calling the set complete is not.
   *(Opt-in fallback, only if the creator explicitly asks after being told Apify is unavailable:*
   propose ~8–15 candidate handles by applying A–F logics to the seeds + your knowledge, one line
   each on why it's a good role model, **labelled unverified**. Invalid handles cost $0 —
   Step 2.5 validates them.)
2.3. **Cheap PRE-filter — BEFORE spending a cent.** From the scraped/known metadata,
   drop brands, media companies, agencies, mega-accounts a small creator can't model,
   off-niche and inactive accounts. Rank by **FIT** (right size band, reels-active,
   niche match, engagement signal). **Benchmark for FIT, not fame** — a 10M celeb is
   mimicry bait (same anti-mimicry, stage-aware thinking as Step 4/Step 5).
2.4. **The human approves the shortlist** — never add an account the human didn't
   approve. A **human gate**, same weight as every other approval here.
2.5. **Add** with `add_to_watchlist` — it validates each handle on Instagram and only
   charges for real ones. **Confirm-before-spend is a human gate:** show the cost
   preview and WAIT for an explicit yes before `confirm=true` (same rule as Step 3.6).
2.6. **Filter on REAL metrics AFTER adding — the honest catch.** The true numbers
   (`follower_count`, `median_er`, `avg_views`) only exist once tracked. So
   `search_watchlist` + `get_profile_details`, and **drop the bad benchmarks** —
   `remove_competitor` is free, so cleanup costs nothing. Confirm with
   `get_workspace_stats`.
2.7. **Show the FINISHED set back to the customer — a second human gate, not just the
   shortlist one (G238).** After 2.6's filtering, list the surviving benchmarks for the creator —
   handle, why it was kept (the fit reason from 2.3, plus its real metrics from 2.6) — and ask
   plainly: *"Here's your final benchmark list — does this look right to you?"* Then:
   - **If they say yes** — move on to 2.8.
   - **If they object to one** (e.g. "that account isn't really like me") — ASK why, then decide
     for real: if their reasoning holds, drop it (`remove_competitor`, free) and say so; if you
     still think it belongs, SAY YOUR REASONING BACK to them plainly (the real metric or fit signal
     that kept it) rather than silently complying OR silently ignoring them. Never just remove an
     account to avoid a disagreement, and never keep one without explaining why once challenged.
   - **If the set looks thin or off after this conversation**, treat it like Step 2's other edge
     cases — widen the niche, re-run discovery, and say so — don't proceed on a set the human
     doubts.
2.8. **Pull + analyse — same confirm gate.** `pull_data` → `run_pipeline` (or
   `run_pipeline_by_category` for the viral tier), the confirm-before-spend gate on
   every call. Check `get_analysis_coverage` after.

**Step 2 edge cases:**
- **Tiny niche** — if A–F discovery + the fallback yield too few FIT accounts (say < 5), **widen to
  the nearest adjacent niche** and **tell the user you did**; never force a plan on 2–3 competitors.
- **Operational limits** — only ONE pipeline run per workspace at a time (if one's active,
  `stop_pipeline` it or wait), a run caps at **25 reels** (re-call `run_pipeline_by_category` until
  `remaining_after_this_run` is 0), and spend tools **refuse when credits are short** (relay it). If you
  can't analyse everything you'd like, **proceed on what's already analysed and SAY SO** — don't stall.
- **Dead accounts** — an account that validates on add but returns no usable reels (private, deleted,
  inactive) → drop it like a bad benchmark (`remove_competitor`, free).
- **Stale set** — treat a benchmark set as stale if it hasn't been refreshed in ~30–60 days or the
  niche has visibly moved; re-run the discovery angles then.

**Then continue to Step 3** with a fresh, fit benchmark set.

---

## Step 3 — Use the RM MCP correctly (tool-usage rules)

1. **Workspace + subset — scope the data DELIBERATELY, the SAME way every run (this is the
   standard; do it identically for every account + niche).** Confirm the active workspace.
   Filter competitors to the **right modelling set** — solo creators for a personal brand;
   move corporate brands + media to a "news radar" (topic ideas), never model reel structure
   on them. **How to scope — use these tools every time:**
   - **One account** (the creator themselves, or a single competitor): pass **`usernames=[handle]`**
     to any insight tool (`get_content_strategy` / `get_hooks_library` / `get_content_structures` /
     `get_cta_library` / `get_content_breakdown`), OR call **`set_data_selection(scope='mine',
     filters={usernames:[handle]})`** so every following read defaults to it.
   - **A hand-picked GROUP of videos:** `set_data_selection(filters={post_urls:[…]})` (or
     `get_content_breakdown` with `filters.post_urls`).
   - **A profile's full post list + cadence:** `get_profile_posts(profile_id)` (the watchlist UUID,
     not the @handle).
   - **Reset when done:** call **`clear_data_selection`** before the next step, so a scoped set never
     silently leaks into an unrelated read.
   **Standardising the SCOPE does NOT lower quality — that is the point.** Inside *any* scope the same
   rules always apply: cross-tabs (§C), **median** not mean, audience-weighting (§F), provenance tags
   (§I), and the **sample-size guard** — a thin scope → widen + mark low-confidence (§B), never forced
   into a confident claim. Same rigour, any account, any niche, any business, whoever runs it.
2. **Coverage before insight — and analyse the subset each FUNNEL ROLE needs (G328).** Call
   `get_analysis_coverage` (it breaks down by performance tag). RM's insight tools only
   see **analysed** reels, so spend the analysis budget on the reels that teach **this
   goal** — not always "viral." Map the goal → the tag subset below, check its coverage,
   and if it's thin, analyse **that subset first** via `run_pipeline_by_category` /
   `query_posts_by_tag` (small **calibration batch** → read the **real** cost from
   `get_credit_usage`, the worst-case *hold* is ~20× the real charge, then scale). This
   feeds the strategy you build in Step 7.

   **Goal → tag subset to analyse — HEALTHY TAGS ONLY** (these are the tags the audit
   confirmed classify reliably; the buggy ones are DEFERRED below until their fix ships):

   | Goal | Analyse (healthy tags) | Anti-pattern |
   |---|---|---|
   | Reach / awareness | `viral_3x`, `viral_2x`, `high_reach_high_engagement`, `high_views`, `reach_only`\* | `low_performance` |
   | Engagement / community | `high_reach_high_engagement`, `excellent_er`, `good_er`, `comments_driven_post`, `hidden_gem`, `polarizing` | `reach_only` |
   | Leads / DMs / conversions | `comments_driven_post`, `excellent_er`, `hidden_gem` | `reach_only` |
   | Authority / saves | `hidden_gem`, `excellent_er`, `utility_content` | `reach_only` |
   | Sales / direct response | `excellent_er`, `high_reach_high_engagement` | `low_performance` |
   | Shareability / word-of-mouth | `shares_driven_post`, `high_reach_high_engagement`, `viral_2x` | — |
   | Retention / watch-time | `top_25_rewatch_driven`\*\* | — |
   | Repost / quick wins | `hidden_gem`, `good_er` | — |

   \* `reach_only` under the **reach** ROLE only — study it for what triggers the *initial view*
   (hook / topic / first frame), but weight `high_reach_high_engagement` higher, because
   engagement is what *sustains* reach. For every other role's slice `reach_only` is an anti-pattern.

   \*\* `top_25_rewatch_driven` is now LIVE (G107 shipped 2026-07-25) — the rewatch/share driver is
   decided **per post** now, not by one dataset-wide correlation (G112), so a real per-post receipt is
   possible again. **Caveat you must state plainly:** the tag only exists on reels analysed AFTER the
   2026-07-25 deploy — older reels won't carry it until a re-tag backfill runs, so don't assume every
   reel has it; check for it, don't guess it in. **`rewatch_driven` itself stays off the map** — cite
   `top_25_rewatch_driven` only (see the deferred list below for why).

   **Apply the table PER FUNNEL ROLE, not once per plan (G328).** The plan's goal is the
   PARENT; every reel also carries a funnel-role SUB-GOAL — `reach` / `nurture` /
   `activation` (Step 8, item 2) — and a reel's data must come from the slice that matches
   ITS role, not the plan's headline goal. Map each role to a row of the table above:

   | Funnel role (sub-goal) | Which row of the table to use |
   |---|---|
   | `reach` (TOF) | ALWAYS the "Reach / awareness" row — whatever the plan goal is |
   | `nurture` (MOF) | "Engagement / community" row by default; "Authority / saves" row when the plan goal is authority |
   | `activation` (BOF) | The plan goal's own row (leads → "Leads / DMs / conversions"; sales → "Sales / direct response"; authority → "Authority / saves"). A reach-goal plan keeps minimal/zero BOF (Step 8, item 2) — any activation reel it does contain sources from the "Leads / DMs / conversions" row, never the Reach row (activation is conversion by nature) |

   **What to analyse = the UNION of those rows, budgeted by the mix %.** Take every role the
   plan's mix will contain, union their rows' tags (a tag shared by two roles — e.g.
   `high_reach_high_engagement` — counts ONCE), and split the analysis budget roughly by the
   mix. Worked example: a 40/35/25 Leads plan spends ~40% of the analysis budget on the Reach
   row (`viral_3x`, `viral_2x`, `high_reach_high_engagement`, `high_views`, `reach_only`) and
   ~60% on the Engagement + Leads rows (`comments_driven_post`, `excellent_er`, `hidden_gem`,
   `good_er`, `polarizing` — the shared tags dedupe). Because the rows overlap, a plan
   analyses ~1.5–2 subsets' worth of tags, not 3 — the mix-% budgeting keeps cost
   proportional, and the calibration-batch + confirm-before-spend gates (rules 6/6a) still
   cap every spend.

   **Which mix, this early?** Step 3 runs before the real TOF/MOF/BOF mix is set (Step 7.1 /
   Step 8 item 2). Budget from the goal-conditioned DEFAULT mix directions already stated in
   Step 8 item 2 (reach goal → TOF-heavy; leads → shifted toward MOF+BOF; authority →
   MOF-heavy) — do not invent a different prior. When Step 7.1 finalises the real mix, if it
   adds a role or materially grows one whose slice coverage is thin, come back through this
   rule for that role: coverage check → calibration batch → confirm gate → top-up. Never
   silently keep building on the provisional slice.

   **Anti-patterns are per-ROLE too.** The `reach_only` footnote above already works this
   way: study `reach_only` under the `reach` ROLE only (what triggers the initial view); for
   `nurture`/`activation` slices it stays an anti-pattern. Same for the rest of the
   anti-pattern column — read it against the role's row, not the plan goal's row.

   **Check coverage PER ROLE.** `get_analysis_coverage` breaks down by tag — read it per
   role's tag set. One role's slice can be healthy while another's is thin; a thin role
   slice widens + gets marked low-confidence (§B/§F) for THAT role's reels only.

   **Anti-patterns — study a FEW, don't analyse the set.** For any goal you may analyse **3–5**
   `low_performance` reels as a contrast (what NOT to do) — never the whole tag: `low_performance`
   is ~62% of posts, so analysing it wholesale burns credits for little signal.

   **What each tag means (reason with the MEANING; only ever SHOW the friendly label — never a
   formula, §7):** `viral_3x`/`viral_2x`=each account's top ~1% / ~5% by views (account-relative) ·
   `high_reach_high_engagement`=lots of views AND engagement (the best of both — a clean, reliable tag) ·
   `high_views`=top-quartile views · `reach_only`=reaches but doesn't make them interact ·
   `hidden_gem`=low views but high engagement (underrated) · `low_performance`=below average on both ·
   `comments_driven_post`=comments drove it (the DM/lead gateway) · `shares_driven_post`=shares drove it
   (word-of-mouth) · `excellent_er`/`good_er`=engagement rate in **your set's** top-10% / top-25%
   (RELATIVE to the competitors you track — NOT an absolute industry %) · `utility_content`=save-worthy /
   useful · `polarizing`=divisive, drives comments/debate.

   **⛔ DEFERRED/BANNED tags — do NOT use in the map or on a receipt:**
   `high_reach` & `high_engagement` (G109 — silently dropped from the best posts) ·
   `rewatch_driven` (kept off-limits on purpose — see the retention row above: its narrower sibling
   `top_25_rewatch_driven` is the live, citable tag now, `rewatch_driven` itself is not) ·
   `high_roi` & `highly_efficient` (G108/G111 — collinear with `excellent_er`, use ER instead) ·
   `needs_improvement` & `likes_driven_post` (G111 — fire on ~65% / ~82% of posts, uninformative) ·
   `unhealthy_account`/`*_account` (G110 — account-level, unreliable from missing data; do not filter
   benchmark accounts on it in Step 2). **When a gap closes, move its tag(s) from here into the map above.**
3. **Right benchmark lens — pick the `analysis_mode` that answers your actual question.**
   `query_posts`, `query_posts_by_tag`, `get_tag_stats`, `get_avg_scores` (plus
   `get_analysis_coverage`) all take an `analysis_mode` with **FOUR** real values (verified against
   the live tool schema). **None of the four normalize for follower count** — a small account's best
   post can still look weak next to a huge account's, in any `cross_account` variant:
   - **`per_account`** (default) — each post ranked only against that SAME account's own posts.
     Never compares across accounts by size.
   - **`cross_account`** — every tracked post ranked against every other TRACKED post — comparable
     across your watchlist, but skewed toward whichever tracked account posts the most / biggest.
   - **`community_per_account`** — same as `per_account`, but the ranking pool also includes your
     niche's community picks as extra context, not just this account alone.
   - **`community_cross_account`** — same as `cross_account`, but the pool is your tracked accounts
     PLUS your niche community — bigger and more representative than `cross_account` alone, though
     still not follower-normalized.
   Prefer `cross_account` (or a `community_*` variant once niche picks exist) over raw `per_account`
   mega-views for a size-fairer read, then apply the Step 4 stage ladder on top for the rest of the
   fairness work. **The lever tools take no `analysis_mode` at all** (`get_content_breakdown`,
   `get_content_strategy`, `get_hooks_library`, `get_content_structures`, `get_cta_library`) — that's
   expected, not a bug: they aggregate classification fields, not performance tags (G116).
4. **Pull the levers — and MODEL THEM FOR THE TARGET AUDIENCE.** `get_content_strategy`,
   `get_content_breakdown`, `get_hooks_library`, `get_content_structures`, `get_cta_library`.
   Read by **median** per dimension value (not the outlier-inflated mean). **Filter the
   breakdown by the target-audience macro** — `get_content_breakdown` with
   `filters.audience=[segment]` — so the winning **hook / structure / CTA / topic** are the
   ones that work for THIS audience, not the niche average. Apply the **§F sample-size guard**:
   if the segment is thin (< ~5–8 reels), widen to the adjacent/on-ramp audience or the whole
   board and mark it low-confidence. Note the split: a high-volume **base** lever vs. a
   huge-reach **swing** lever.
5. **Hooks — pull ALL templates, find what went VIRAL, and REASON.** From
   `get_hooks_library` pull every hook **template + category with its view performance**;
   identify which templates/categories have **gone viral** (highest **median** views for the
   goal + target audience), and for each winner write a one-line **reason it works** that you
   carry into Step 7 (patterns matched) AND every calendar reel's 4-layer hook + receipt —
   **never a hook without a "why this, here."** Then `query_posts_by_tag` (the tags of the ROLE
   the reel will serve — the rule-2 role→row mapping above) →
   `get_post_transcript` on the top reels for the exact wording and the **retention** data
   (`beats` / `segments` / `template_structure` — the watch-time proxy, since RM can't scrape
   competitor watch-time).

   **The hooks library is TAG-BLIND (G116):** `get_hooks_library` cannot filter by performance
   tag, so in a leads-focused workspace its winners are silently dominated by lead-pattern
   reels. Before citing a hook winner on a reel's receipt, cross-check it against that reel's
   ROLE slice via `query_posts_by_tag` + `get_post_transcript` — a hook that only wins in the
   wrong role's slice is not a receipt for this reel.

   **Call `get_hooks_library` scoped, not blind.** Pass `usernames` (the tracked profiles this plan
   actually cares about) or a narrower `scope` — don't rely on one wide, unfiltered call. **If
   `top_templates` comes back empty on a workspace you know has analysed data** (check
   `get_workspace_stats` or `get_analysis_coverage` first if you're unsure), **that is G52, a known
   backend bug — not "this workspace has no hook data."** Do not silently proceed as if there's
   nothing to learn. Instead: (a) call `report_gap` once, briefly describing the empty result and the
   filter you used, so engineering has a live example; (b) re-query with a DIFFERENT filter (a single
   `usernames` entry, or `scope="niche"` instead of `"mine"`) before concluding the hooks layer is
   genuinely thin. Only after a re-query still comes back empty should you treat it as real absence of
   data and say so plainly in the deliverable's receipts section (not silently downgrade to
   judgment-only without a note).
6. **Confirm-before-spend is a HUMAN gate.** Every spend tool needs `confirm=true`,
   but that flag is not yours to set on your own: show the cost preview to the
   human and **WAIT for their explicit yes** before the `confirm=true` call.
   Showing the preview and proceeding is NOT a confirmation — a real person must
   say proceed. (The RM server enforces the flag is present; only the human
   enforces that a person actually agreed.)
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
   Say plainly: *"I'll analyse this in assist mode by default — I read the frames myself, so the
   final charge works out at about half the credits of a normal run. It's a discount, not free.
   The amount held up front is the same either way, and the unused part comes back when the run
   finishes. It also uses more of your Claude usage and takes longer. If you'd rather I use RM's
   own analysis at full price, just say so."* If they ask whether it will ever be free: *"It may
   become free in future — that isn't decided yet, so treat today's price as the price."* Say it
   as a maybe; never promise it. Only fall back to normal `run_pipeline` if the human
   explicitly asks for it. Without this default, a creator who is short on credits silently gets
   thinner coverage — they decline analysis at the confirm gate when a half-price path existed and
   was buried in an even choice instead of led with, so plan quality ends up tracking their wallet
   instead of their needs. Note: assist mode reloads the same instructions once per
   `get_assist_work` call by design (server-cached, G123) — this makes it slower per reel than
   normal analysis, so say so if the human asks why.
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
   **🔴 NOT ACTIVE YET — this rule needs one human edit first.** Launching a sub-agent requires
   `Agent` to be listed in this skill's `allowed-tools:` line in `SKILL.md`, and that grant has not
   been made. Until `SKILL.md`'s `allowed-tools:` line includes `Agent`, do the analysis directly in
   this conversation as before and ignore this rule. Do not try to add the grant yourself — giving a
   skill the power to launch sub-agents is a capability change a human owns.
   Also still unproven: that the sub-agent inherits the MCP connection in a real customer session.
   Worth one real smoke test the first time this runs.
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
   - **Poll `get_pipeline_status` about every 20-30 seconds** (the tool's own guidance) until it
     reaches a terminal state (`completed` / `partial` / `failed`). Do this silently — don't
     narrate every poll to the human, only the moments below.
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
     call it on the customer's behalf just because a poll looked slow.
7. **Algorithm confidentiality.** Use RM's friendly labels ("Top 1% Viral", "Hidden
   Gem"). Never reveal or guess the formulas behind the tags.
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
- **The WHOLE workspace is thin** (only a handful of analysed reels total, not just one slice) → the
  plan is **mostly JUDGMENT** — label it that way, lean on the positioning + niche, and make the first
  cycle's job to build more data. Never dress a 10-reel workspace up as data-driven.
- **Degraded or empty analysis** — if a result comes back **degraded** (check for a `degraded_stages` /
  degradation marker — G99) or a field is **empty** (e.g. `beats` / transcript — G103), **down-weight it
  and flag it**, fall back to what IS reliable, and `report_gap` it. Never silently build on degraded data.
- **A goal with no tag mapping** (e.g. "brand awareness", "community") → map it to the nearest goal in the
  goal→tag table (awareness → reach; community → engagement) and state which you used — the mapping applies
  per funnel role the same way (an unmapped nurture role falls back to the Engagement row).

---

## Step 4 — Translate for the account's STAGE (the anti-trap layer)

The single biggest failure mode: copying a scaled tactic onto the **wrong-stage** account. Everything the
data shows comes from creators who already have reach — so read the account's **stage** (from Step 1) and
pick the right translation. **This is a LADDER, not a cold-start-only rule** — the correct move flips as the
account grows (the same CTA that hurts a 500-follower account is right for a 50k one).

**The data helps with SIZE-FAIRNESS — via the `cross_account` mode.** RM's tags / viral % are computed
**per follower-tier** when you read the tag/coverage tools in **`cross_account` mode** (Step 3 rule 3,
verified in the engine) — so a size-fair comparison exists there: model reels from **the account's own
size band**, not a 10M celebrity's raw views. *(The deeper normalized / community lenses exist in the
engine but aren't exposed via the MCP yet — G116; and the lever tools take no mode selector, so lean on
`cross_account` on the tag tools + judgement.)* That covers the *benchmark* layer as far as the tools
allow; the ladder below covers the *tactical* layer (CTA, cadence, funnel, concentrate-vs-diversify).

| Stage (Step 1) | CTA | Focus | Cadence / KPIs |
|---|---|---|---|
| **Cold-start (0–~1k)** | **Default to reply-bait** — a keyword-DM CTA on a tiny audience usually gets very few replies and costs reach. **Only use keyword-DM if the lead magnet + DM automation are confirmed built AND tested** — recommend against it anyway unless the creator has a real reason, and say plainly it will get fewer replies at this size. | Find ONE working hook; reach-first; **concentrate** | 3/week; judge by hour-1 speed / watch-time / saves-per-1k, **not raw views** |
| **Growing (~1k–10k)** | Keyword-DM **only once a reel clears ~5–10k AND the freebie + auto-DM exist**; else reply-bait | Double down on early hits + start light nurture; begin diversifying pillars | build cadence; add follower-growth + save/share rate |
| **Established (~10k–100k)** | Keyword-DM works; run **activation / offer reels** | Diversify pillars; weight authority + nurture; can push offers | judge by **leads / sales**, not just reach |
| **Large (100k+)** | Full funnel — big-creator tactics apply directly (the data *is* them now) | More formats / cadence; protect the winners | leads / sales / retention |
| **Stalled / plateaued (any size, flat)** | Same CTA as its size row | **The problem isn't reach volume — it's a stale pattern:** test NEW hooks/angles/formats, check if the positioning drifted | watch the **trend**, not the absolute |

**Harden it — the gaps this exposes (handle each):**
- **Stage ≠ follower count alone.** Read the size band *together with* **engagement/reach health** — a 5k
  account with dead engagement is really acting like a cold-start. Mis-stage the account and the whole row
  is wrong.
- **Detecting "stalled."** Read the **trend** of the creator's OWN recent reels (Step 1.6 / Step 3): flat or
  declining views / follower growth over recent posts = stalled → use the stalled row, whatever the size.
- **Goal ↔ stage mismatch.** A cold-start account with a **leads/sales** goal is premature — flag it and
  steer to **reach first** (you can't harvest leads with no audience). Catch it here, before building.
- **Very small / new accounts → the size-tiered tags are UNRELIABLE** (thin data; the per-account viral
  tags over-fire on 2–4-post accounts — G109–G112). For a cold-start, lean on the **`cross_account`
  (follower-tier)** view + judgment; don't over-trust "their own top 1%."

---

## Step 5 — Differentiate, never mimic

- Every idea must **ladder to the one positioning sentence** from Step 1.
- Reframe any competitor format around the creator's **first-party proof** ("I ran
  this on my *actual* business — here's the receipt"). That's what a big account
  can't copy back.
- **Reject near-clones.** An RM top reel is a **pattern reference**, not a script.
  If the idea is recognisably "X creator's reel re-skinned", kill it.

**The METHOD — the "Reel Bet" (§A), so differentiation is a procedure, not a guess.** Every reel =
**Proven Pattern × First-Party Topic × Audience Tension:** a pattern (hook + structure + emotion) that's
**proven in the data**, on a **topic drawn from the creator's own proof / demand**, resolving **one real
tension** of the ONE audience. **Never a novel pattern on a novel topic** — that's maximum risk; put the
novelty in the **framing / proof**, never in the pattern or the demand.

**The near-clone TEST (concrete, not a vibe).** A reel is a clone if it keeps the source's **hook AND
structure AND topic** — three matches = a re-skin, kill it. Change **at least one** substantially —
**ideally the topic + first-party proof**, so it's unmistakably theirs. *(Same proven hook + structure on a
**different, first-party topic** is fine — that's modelling; same all three is mimicry.)*

---

## Step 6 — Retention, not just hooks

The hook buys the *test* impressions; **watch-time + replays** decide whether the
algorithm pushes past the follower base. For every reel specify:

- an **open loop** in the hook,
- a **mid-reel re-hook** (~40% mark),
- a **loop-back ending** so the reel replays.

**Be honest about the evidence — retention is the weakest-sourced lever, and it
matters most.** RM cannot see competitor watch-time, so retention is inferred, not
measured. **Build the recipe DATA-FIRST — derive it, don't default it:** (1) pick which reels to model
retention from by **saves + shares per 1k** — the reels that provably HELD people, not just high-view
ones; (2) **derive the actual open-loop / mid re-hook / loop-back from THOSE reels' beat-structure** where
it's present, instead of applying a generic template; (3) only where no structure data exists, fall back
to the generic recipe as craft. Tag every retention line by which of these it came from:
- **If a real beat structure came back** (`beats` / `segments` / `template_structure`
  from `get_post_transcript`), build the retention line from it and cite it — that is
  the strongest available signal. *(Note: `beats` is often empty even on analysed
  reels — a known bug; when it is, fall back to `template_structure`/`segments`.)*
- **If nothing usable came back, the retention line is SMM JUDGMENT (craft), and it is
  tagged JUDGMENT — never DATA-DRIVEN.** Do not dress a structural guess as data.
- **A defensible proxy for "did this reel actually HOLD people":** shares- and
  saves-per-1k. A reel people save and share held their attention; rank the reels you
  model retention on by that, not just by views. Tag it DATA-INFERRED.
- **The real retention data lives in the creator's OWN analytics.** Once their account
  is tracked (Step 1.6), ask them to report their posted reels' **average watch-time /
  %-watched** from Instagram — that is measured retention for *their* audience, and it
  beats any competitor proxy. Feed it back via the Creator Brief for the next cycle.

---

## Step 7 — Build the STRATEGY (Part A) — commit it BEFORE the calendar

**This is the step that actually builds the strategy.** Until now you gathered raw
material (Step 3 levers) and the rules for shaping it (Steps 4–6). Now — **before writing
a single calendar reel** — turn that into a **stated strategy**: the decisions the whole
calendar then executes. Write it as **TEMPLATE Part A**, in this order, each decision with
its reasoning + provenance (§I):

7.0. **First, confirm the FOUNDATION with the data you now have — before the strategy.**
   a) **Confirm & sharpen the POSITIONING (drafted in Step 1).** Reverse-engineer the subject's
      **actual** audience from their own reels (`get_content_strategy` on self) and **check it
      against the IDEAL audience** they named in Step 1 — if they differ, surface the gap and let
      the creator choose (a creator who says "founders" but whose reels pull "students" *has* a
      positioning problem — caught by data, not opinion). Confirm **what they demonstrably OWN**
      (from their own top reels), and **sharpen the differentiation against the niche WHITE-SPACE**
      (what everyone else says → say what they don't; this closes the third circle you couldn't
      finish in Step 1). Lock it — save via `update_business_profile`, status `confirmed` (or a
      sharpened `hypothesis` for a young account). Everything below ladders to THIS.
   b) **Read the self-vs-niche GAP (Step 1.6).** What already works for THIS account (double
      down), the niche's proven levers they haven't tried yet (the opportunity to test), and what
      they do that under-performs (fix/drop). The strategy below is built to **close that gap**,
      not copy the niche.
7.1. **Goal & funnel objective.** State the goal (reach / leads / authority) plainly, the
   **ONE conversion action** for the period, and the **funnel mix (TOF/MOF/BOF %)** —
   goal-conditioned and stage-aware (§D), with the reasoning. Never mirror competitors'
   mix.
7.2. **Target audience.** The ONE segment this serves (from Step 1), how much proven
   material actually targets it, and — if that slice is thin — the honest **on-ramp** (which
   adjacent audience carries the reach and how the plan bridges to the real target) (§F).
7.3. **Patterns MATCHED — modelled FOR THE TARGET AUDIENCE.** The proven **hook, structure,
   CTA and topic** you'll USE, each read on the **target-audience slice** (§F — filter by the
   audience macro; widen + mark low-confidence if the segment is thin), cross-tabbed (§C),
   with **n + median + reliability + provenance tag** and one line on why it fits this subject.
   The plan should say "for YOUR audience, this hook/structure/CTA wins," not "the niche does X."

   **Split the matched patterns PER FUNNEL ROLE (G328).** One pattern set per role in the mix —
   reach patterns (from the Reach-row slice) for `reach` reels, nurture patterns for `nurture`
   reels, activation patterns (from the goal's own row) for `activation` reels — each with its
   OWN n + median + reliability + provenance tag, read on that role's tag slice × the target
   audience. Never present one blended pattern set: a `hidden_gem` lead pattern is not evidence
   for a reach reel, however high its n.
7.4. **Patterns to TEST** — 2–4 bets framed as experiments: hypothesis + kill/scale rule
   (§A/§H). This is how the plan learns.
7.5. **Content pillars & distribution** — 3–4 pillars laddered to the positioning, and the
   **% split**, with the **concentrate-vs-diversify decision REASONED to this account**
   (has it found a hit yet? goal, stage, data confidence, capacity — no one-size ratio).
7.6. **Format MIX — data × what they can produce.** Set the format distribution (talking-head /
   tutorial / skit / b-roll…) from the **winning formats in the data** (for the goal + audience,
   `get_content_breakdown` on `content_delivery`/`content_formats`) **∩ what the creator can actually
   film** (production capability, Step 1) + capacity. State it as a % (e.g. "60% talking-head · 30%
   tutorial · 10% skit") with the reasoning — don't leave format to ad-hoc per-reel choices.
7.7. **Recurring SERIES — 1–2, from the strongest repeatable pattern.** From 7.3, pick the proven pattern
   (hook × structure × topic) that is both high-performing **and** sustainable, and turn it into a named,
   repeatable series with a cadence ("every Mon: I automate one thing"). Series build a return habit and
   cut ideation load. Data picks *which* pattern to seriesify; the name + cadence are craft.
7.8. **Business-calendar alignment — sequence toward their real moments.** Map the plan to the creator's
   **upcoming launches / promos / seasonal moments** (from Step 1; ask if not captured), e.g. two weeks of
   nurture before a launch. The agent MAY **web-search** for relevant seasonal / timely moments in the
   niche to seed this. Never *calendar* breaking news — that's the opportunistic slot (Step 8).

**Three rules that govern the whole strategy:**
- **Tie-breaker when inputs conflict:** **constraints/compliance > positioning > goal > raw data.** A viral
  pattern NEVER overrides who they are, what they can't do, or the goal.
- **Own your confidence:** if Step 3 came back thin, say so at the strategy level — "this is bets, not
  measured data" — don't only tag it per reel.
- **Reels don't grow alone:** note the supporting content they need — Stories that drive to the reel +
  collabs (the Dream 100, Step 8).

**Gate before the calendar:** if you cannot state 7.1–7.8 cleanly, you are not ready to
build reels — go back to Step 3. The calendar (Step 8) must **execute this stated
strategy**, and the Rules Gate's **strategy-adherence** check (Step 11) verifies the
calendar actually delivers the goal / funnel mix / pillars / audience you set here. A
strategy built explicitly here is what makes that check meaningful.

---

## Step 8 — What the deliverable MUST contain

> **Output shape is fixed: follow `TEMPLATE.md` (Parts A–E) exactly — same structure every run, for
> every creator.** The items below map into it: strategy first (Part A: overview/positioning, goal +
> funnel objective, target audience, patterns MATCHED, patterns to TEST, pillars + distribution), then
> Foundation (Part B), then the calendar (Part C), then execution + measurement (Part D), then the trust
> layer (Part E). Do not reorder or drop a section.

1. **Section 00 — Foundation** (ships *before* any calendar reel): the one
   positioning sentence — or the "GENERIC — positioning not provided" stamp
   (Step 1) — bio + searchable name field, and the **pinned first 3 reels** that
   define the account. **One of the three pinned reels must be an identity /
   origin-story reel** — the reel that makes a first-time visitor trust this
   creator. Structure it plain: *who I was → the shift that changed me → who I
   am now → why that matters to YOU (the viewer).* Source it from the creator's
   own captured **personal story** (Step 1, `personal_story` in the Creator
   Brief) and/or their transformation story (Step 1 positioning item 6) —
   prefer the personal story when both exist, since it answers "why does this
   matter to them," the stronger trust signal — never invented, and never a
   competitor's story reframed as theirs. If neither was captured, this pinned
   slot falls back to the strongest proof/result reel instead, and the
   deliverable flags that fallback so the creator knows to fill it in later.
   **HARD GUARD — never let invented/placeholder content ship silently.** If ANY
   reel's content had to be filled with a placeholder, an invented example, or an
   unverified claim (the origin story, a result, a testimonial, a number), that
   reel MUST carry an explicit `needs_real_content: true` field AND be listed at
   the TOP of the deliverable under "⚠️ Fill these in before publishing." Do NOT
   present or save an invented reel as if it were final. This exists because a
   real stored plan (6a6241ee) persisted an invented origin script with only a
   buried note — a note is not a guard. (**Shipped 2026-07-27, live in code
   today** — `validate_content_plan`'s `no_unflagged_placeholder` check
   enforces this; see Step 11.0.)
   **A captured `personal_story` doesn't stop at the pinned reel (G373).** If one exists, name at
   least one more reel elsewhere in the calendar — ideally an objection-busting or Big Domino reel
   (`rules/authority.md` Secrets #6/#9) — that explicitly draws on it (e.g. "I used to believe that
   too, until..."). Tag it in the calendar so the story is actually used, not left sitting unused in
   the brief.
2. **Section 00.5 — The month as a funnel** (ships *before* the calendar): lay
   out the journey this month builds — **reach → follow → 2–3 designated
   ACTIVATION reels** that route a warm viewer to the lead magnet via the DM
   automation the creator already has (still gated by the Step 1 funnel-plumbing
   check). State the **ONE conversion action** for the month and work backward
   from it. **Set the month's funnel MIX — the TOF/MOF/BOF ratio — explicitly,
   data-driven and GOAL-CONDITIONED, and state it with the reasoning.** Read
   `funnel_distribution` from `get_content_strategy` as the niche reference (what
   the tracked accounts actually do), but do **NOT** just mirror it — the RIGHT mix
   depends on the goal + stage, not on what competitors post:
   - **Reach goal / cold start (~0 followers):** TOF-heavy (get *seen* first), a
     little MOF (build trust), **minimal/zero BOF** — no audience to convert yet, so
     BOF reels are wasted. (Copying a competitor's 86/10/2 here is the mimicry trap.)
   - **Leads goal:** shift toward MOF + BOF (nurture + convert).
   - **Authority goal:** MOF-heavy (deep educational).
   Then tag every reel with a **funnel role** — `reach` / `nurture` / `activation`
   (= TOF / MOF / BOF) — so the calendar actually HITS the ratio you set. Pick the
   activation reels on the **goal-conditioned** metric (§D) — for a leads goal that's
   saves + comment rate, not raw views. Activation reels still follow the
   stage-appropriate CTA rules from Step 4.
3. **The calendar** — per reel: format · intent · topic/niche · angle · **pillar** ·
   **series** (which recurring series, if any) · **moment-tie** (building toward a Step-7.8
   launch/seasonal moment?) · **funnel role** · audience · emotion · hook **template** · full **4-layer
   hook** (spoken / on-screen / visual / sound) · **retention line** ·
   **stage-appropriate CTA** · **effort tag** (heavy = screen-record/build,
   light = talking-head/POV) · **priority rank** · and a **MECHANICAL
   RECEIPT (G74)** in place of a plain "source reel" note:
   - The receipt must be built ONLY from the actual tool results this run
     collected — never written as prose. It names the **source competitor
     (@handle)**, the **specific source reel URL**, the **`n`**, the
     **`median_views`** (never the mean), the **`reliability`** band
     (high/medium/low), and the **provenance tag** from §I (DATA-DRIVEN /
     DATA-INFERRED / JUDGMENT).
   - ✅ **GOOD (mechanical):** *"Curiosity hook × Tutorial. Source:
     @competitorX (instagram.com/p/ABC) + 11 like it in your data. Median
     112k views, reliability HIGH (n=14 in your Tech/AI audience). Tag:
     DATA-DRIVEN."*
   - ❌ **BAD (narrated):** *"Uses a curiosity hook because curiosity hooks
     grab attention and tend to perform well."* — no number, no named
     source, no tool result. That is a **JUDGMENT** call, and it must be
     tagged JUDGMENT, not dressed up to look like data.
   - A recommendation that cannot cite a real tool result gets tagged
     **JUDGMENT** and gets **no data-receipt at all** — it never fakes one.
     (This is §I made explicit, and mirrors `rules/copywriting.md`
     **S14: "never manufacture a results testimonial."**)
   - **The receipt must come from the reel's OWN funnel-role slice (G328).** Source reels for a
     receipt are found via `query_posts_by_tag` with the tags the reel's role maps to (Step 3
     rule 2's role→row mapping) + `get_post_transcript` — a `reach` reel cites the Reach-row slice, an
     `activation` reel cites the goal-row slice. A receipt built from another role's slice is a
     wrong-slice receipt: re-source it from the right slice, or tag the reel JUDGMENT. Never
     ship a reach reel wearing a lead-tag receipt.
   - **Sequence the calendar** so each series lands on its cadence and any launch / seasonal build-up runs
     BEFORE the moment, not after (Step 7.8).
   - **Write every hook / caption in the AUDIENCE'S language**, not assumed English. Ask/detect it (their
     account, Step 1) and write in it. **Shipped (G117) — read it, don't guess:** RM processes
     multilingual reels by translating to English, but it now returns the reel's real spoken
     language too — `original_language` on `get_post_transcript` (top-level field), and under
     `classification.original_language` on `get_posts_detailed`. The transcript text itself may be
     an English TRANSLATION of that language, not a verbatim quote — say so if you quote it. Set
     `meta.language` in the saved plan (Step 12) to the language you actually wrote the hooks/CTAs
     in — the `language_set` check needs it.
   - **Draw from MULTIPLE sources** — the receipts must cite **≥3 distinct competitor accounts**; never
     model the whole plan off one account (fragile + mimicry-adjacent).
4. **Cadence** realistic for the creator's stated capacity (Step 1) — default to
   the **lower end** of what they said they can sustain; anything above is a
   stretch, not the plan. A **batching + repurposing** SOP (one film day → 3–4
   reels → re-cut for Shorts/TikTok), with **light-effort reels batched
   together** so a bad week still ships something. The **priority rank** on
   every reel means the plan degrades gracefully if the week goes sideways,
   instead of collapsing.
   **Total effort ≤ capacity — check the SUM, not just per-reel tags.** Add up each week's effort
   (heavy / medium / light) and make sure it fits what the creator can actually film + edit that week; if
   it's over, cut or reschedule reels — an un-shippable calendar is worse than a smaller one.
   **Plan-size honesty — never pad to hit a number.** If the data only supports fewer STRONG reels than the
   creator asked for (say 6 of 12), **tell them**, and offer in order: (a) **analyse more data** to find
   more strong reels; (b) if they're **out of credits**, offer to **upgrade the plan** and explain the
   benefit (more analysis → more data-backed reels); (c) else **stretch to the number but clearly LABEL the
   extra reels** as lower-confidence "stretch" — never dress a stretch reel up as data-driven.
5. **News = an opportunistic slot**, never calendared (you can't schedule when
   OpenAI ships); keep an evergreen filler ready.
6. **Captions / hashtags / on-platform SEO** framework.
7. **Section 04.5 — Distribution: posting time + trending audio.**
   `get_content_breakdown`'s `day_of_week` / `hour_of_day` dimensions give real
   medians — use them, but only as a **soft tie-breaker, tagged data-inferred**,
   never a hard rule, because of two honest caveats you must state to the user:
   (1) the times are in **UTC**, not localized to the audience's own timezone,
   and (2) weekday differences in the data are often flat, so don't oversell a
   small gap. **Trending audio isn't in the RM data** — instruct the creator to
   pull it straight from Instagram's own trending-audio panel and layer it onto
   the format, tagged **JUDGMENT**. This is also what every reel's `hook.sound`
   field should say when you have no specific sound to name — a stated
   judgement, never an invented song (TEMPLATE.md C1, G118 blocks an empty one).
8. **Weekly measurement ritual** with stage-appropriate KPIs, the **mid-month
   tracker** (Step 1.6: saves-per-1k, watch-time %, shares-per-1k per reel) for
   the creator to fill in, and a rule for how that data updates next week's plan.
9. **Daily community/engagement routine — a real "Dream 100."** Don't just say
   "comment on creators for 20–30 minutes" — name the actual shortlist and give
   it a method:
   - **(a) The shortlist.** The Dream 100 is the specific accounts this plan
     already modelled (Step 3) — you already know exactly who they are, don't
     make the creator guess.
   - **(b) Serve before you ask.** A genuine, specific comment (not "🔥 love
     this!"), sharing their best reels to your own story, being a real fan of
     their work. Never drop your own link or pitch in their comments — that
     reads as spam and gets you ignored or blocked.
   - **(c) A cadence a cold, 0-follower account can sustain:** 15–20 minutes a
     day, spread across 5–8 of the Dream 100 accounts, rotating through the
     full list across the week. This — not paid reach — is how a cold account
     gets its first real eyeballs: the creators you engage with, and their
     audiences, start noticing a familiar, genuinely useful name.

   Plus a weekly line: **check trending audio + format** on the accounts you're
   modelling.
10. **Honest benchmarks:** normalised numbers up top, **anchored to the
    creator's own rolling median where Step 1.6 gives you one**; mega-view
    figures clearly labelled "aspirational ceiling", with a caveat.
11. **Section 05 — Receipts: how this plan was built from YOUR data (G74).**
    This is the **QA + conversion summary surface** — it exists so a reviewer
    can tell whether the plan actually used the creator's own RM research (QA),
    and so the creator can feel the plan is built on THEIR competitors and
    THEIR numbers (conversion). Every line in it is **MECHANICAL, never
    narrated** — the same rule as item 3's per-reel receipt. It must contain:
    - **Coverage line:** *"Built from N of your M analysed reels"* — pulled
      from `get_analysis_coverage` (or the total inside `get_content_strategy`).
    - **Which MCP tools actually ran** this session — name them (e.g.
      `get_analysis_coverage`, `get_content_strategy`, `get_content_breakdown`,
      `query_posts_by_tag`, `get_posts_detailed`).
    - **The honest split, as COUNTS, not adjectives:** *"X of the Y calendar
      reels are DATA-DRIVEN (each cites a real lever + n + median), Z are
      DATA-INFERRED, W are JUDGMENT."* The admission **is** the point — never
      inflate it. A plan claiming everything is data-driven reads as marketing
      and gets discounted by anyone who checks.
    - **Name the competitor accounts** the plan actually drew from, by
      @handle: *"these ideas come from @X, @Y, @Z's viral reels."* They are
      the creator's own tracked competitors, so naming them is fine to show
      the creator.
    - **Drive ONE action** (`rules/copywriting.md` S1): e.g. *"start
      with reel #1 — the highest-confidence DATA-DRIVEN pick."*
    - **If ZERO reels are DATA-DRIVEN (or the count is low), give the fix — don't
      just confess.** A workspace whose reach lives in an audience ADJACENT to the
      creator's exact ICP (the on-ramp case) produces 0 data-driven reels — that is
      honest, but it is also a fixable data gap. So the receipts section MUST add a
      concrete **"How to make next month DATA-DRIVEN"** line: *add ≥3 competitors who
      serve your EXACT audience (ICP-matched, not just the same broad niche), analyse
      their winners, and next cycle these reels graduate from inferred to data-driven.*
      This closes the learning loop instead of leaving the creator stuck at "it's all
      a bet." (Found in the real stored plan 6a6241ee: 0 data-driven, honestly owned,
      but no forward fix offered.)

    **The hard rules behind this section, spelled out:**
    - Mechanical, never narrated — same test as item 3's ✅/❌ example.
    - **Never fabricate a number the tools didn't return** (S14, same as
      item 3) — if a tool didn't return it, the plan doesn't say it.
    - **Honesty IS the sales mechanism.** The line *"3 of these are my
      judgment because your data was thin"* is what makes the other 7 land as
      genuinely measured — a plan that hides its judgment calls is less
      convincing, not more.
    - **Only cite a row as hard proof if it's reliable** — a low-n row (§B) is
      a **bet**, never a DATA-DRIVEN receipt.
12. **HAND IT OVER — say WHERE the dashboard is (G370).** The plan is delivered as
    `dashboard.html` (see `SKILL.md`, the Deliver step). We used to write that file and
    never tell the creator where it landed, which for a non-technical creator is the same
    as never getting it. So, the moment the file is written:
    - **Print the absolute path** — the full path from the drive or root, e.g.
      `A:\work\content-plans\@handle\2026-08\dashboard.html`. Never just the file name,
      never a relative path. Put it **on its own line**, nothing else on that line, so it
      can be copied or clicked.
    - **One short sentence on what is inside it**, e.g. *"your full month — strategy,
      calendar, hooks and receipts."*
    - **Then try to open it in their default browser** (`start` / `open` / `xdg-open`, or
      `mcp__playwright__browser_navigate` with a `file://` URL). **If it will not open, say
      "open this file in your browser" and carry on.** Never fail the delivery over the
      opening step and never loop on retries — the printed path is the part that must
      always happen. **Headless runs (`runner.py`) skip the auto-open** and still print the
      path; a browser popping up on a server helps nobody.

---

## Step 9 — Guardrails (never do)

The single "never do" reference — the red lines, grouped. (Each also lives in its own step / the
Rules Gate; this is where a fast pass looks.)

**Honesty & data integrity**
- Never present competitor mega-views / medians as **expected** results.
- Never dress a **stretch or JUDGMENT** reel as data-driven; never manufacture a number the tools didn't return.
- Never **pad the plan** to hit a requested count — label stretch reels, or offer more data / an upgrade (Step 8).
- Never over-trust a **thin data slice** or a **tiny/new account's** tags (§B/§F); never trust the
  **buggy/deferred tags** (`high_reach`/`high_engagement`, `rewatch_driven` (its narrower sibling
  `top_25_rewatch_driven` is live now — see Step 3),
  `high_roi`≈`highly_efficient`, `needs_improvement`, `likes_driven`, `unhealthy_account` — G109–G112) or the
  size-modes the MCP doesn't expose (G116).

**Confidentiality**
- Never reveal or guess RM's classification formulas — friendly labels only.

**Anti-mimicry**
- Never ship a **near-clone** (hook AND structure AND topic all match); never model the whole plan off **one**
  competitor (**≥3 distinct sources**).
- Never carry **another business's strategy** into the plan (the rules are generic on purpose).

**Fit & feasibility**
- Never recommend a **CTA whose plumbing doesn't exist** (keyword-DM without a confirmed, tested lead
  magnet + auto-DM — this blocks regardless of stage; a cold-start account with real plumbing is a
  warned judgement call, not a block, see Step 4).
- Never plan an **un-shippable calendar** (a week's effort > capacity).
- Never write the deliverable in the **wrong language** (don't assume English).

**Subject & positioning**
- Never plan for the account **OWNER instead of the SUBJECT** (agencies plan for their client).
- Never present an **unproven positioning** as settled truth (it's a hypothesis until results confirm it).
- Never let a **viral pattern override** positioning / constraints / goal (tie-breaker: constraints >
  positioning > goal > raw data).

**Process**
- Never add the creator's own account **before competitors are analysed** (a thin workspace guesses its niche
  from whichever accounts are in it).
- Never **calendar** time-sensitive news (reactive slot only); never present **posting-time** as a hard rule
  (UTC, not the audience's timezone; weekday gaps are flat).
- Never **fill a gap with an assumption — ASK**; and **`report_gap`** anything unforeseen.

---

## Step 10 — Run checklist

- [ ] Stage + positioning + first-party proof + assets + capacity captured (Step 1)
- [ ] **Creator Brief loaded first (`get_creator_brief`); only missing/stale fields asked; intake saved back with provenance (`update_creator_brief`)** (Step 1, G100)
- [ ] **Intake run as a conversation (1–2 Qs at a time); ICP DERIVED, goal RECOMMENDED, funnel advised — not offloaded to the user** (Step 1, G100)
- [ ] **Stated profile CROSS-CHECKED against actual data; any mismatch surfaced + resolved** (Step 1, G100)
- [ ] **Month's TOF/MOF/BOF funnel ratio set explicitly, data-driven + goal-conditioned (not mirrored from competitors)** (Step 8, G100)
- [ ] **Positioning gate passed** — either captured and saved via
      `update_business_profile`, or the plan is stamped "GENERIC — positioning
      not provided" at the top (Step 1)
- [ ] Workspace + creator subset + coverage OK; viral tier analysed if needed (Step 3)
- [ ] Normalised benchmark mode used, not raw per-account (Step 3.3)
- [ ] **Own-account baseline offered** only after competitors are analysed, and
      "self" account confirmed if the creator has one (Step 1.6)
- [ ] Every idea laddered to the positioning sentence + first-party proof (Step 5)
- [ ] Stage-appropriate CTAs (reply-bait vs keyword-DM) (Step 4)
- [ ] Retention line on every reel (Step 6)
- [ ] **Every reel tagged with a funnel role** (reach/nurture/activation) and
      the month's ONE conversion action stated (Step 8)
- [ ] **Analysis tag subsets chosen PER FUNNEL ROLE (union of rows, budgeted by mix %) — coverage checked per role** (Step 3, G328)
- [ ] **Patterns MATCHED split per funnel role; every reel's receipt cites its OWN role's tag slice** (Steps 7.3 + 8, G328)
- [ ] **Every reel tagged with an effort level and a priority rank** (Step 8)
- [ ] Section 00 + realistic cadence + KPIs + community routine present (Step 8)
- [ ] Benchmarks honest; no clones; no calendared news (Step 9)
- [ ] **Plan size asked + your recommendation given** (Step 1)
- [ ] **Every item tagged data-driven / data-inferred / judgment, using the §I
      operational rule (median + n≥§B threshold, audience-matched)** (§I)
- [ ] **Output follows `TEMPLATE.md` (Parts A–E), same shape every run** (Step 8)
- [ ] **≥3 distinct source accounts behind the receipts; no single-source plan** (Step 5 / Gate 8)
- [ ] **Plan-size honest — if data supports fewer strong reels than asked, the creator was told + any stretch reel is labelled JUDGMENT, never padded as data** (Step 7 / Gate 8)
- [ ] **Decision log written (TEMPLATE E3) and included in the saved plan** (Step 12)
- [ ] **`RULES_GATE.md` walked (all 8 gates) — voice/compliance, structure, retention, benchmark-not-copy, CTA/funnel, STRATEGY ADHERENCE (calendar delivers the declared goal/mix/pillars/audience), data integrity, deliverable feasibility & variety (effort ≤ capacity · ≥3 sources · no clones · variety)** (Step 11)
- [ ] **Rules Gate + critic loop run; only the passed version shipped** (Step 11)
- [ ] **Offered to save the plan to the Content Calendar; stored ONLY on explicit consent** (Step 12)

**If any box above cannot be honestly ticked, do NOT ship — go back and fix it, or state the limitation plainly in the plan (Part E) and to the creator. A checklist walked but not satisfied is worse than none.**

---

## Step 11 — Rules Gate + Critic loop (MANDATORY — never ship the first draft)

The first draft is **not** the deliverable. Before you hand over the plan:

0. **Call `validate_content_plan` first (free, read-only) — G118, 17 checks.** Pass the STRUCTURED
   `plan` + `inputs` you built. It runs every deterministic, countable check the backend ships (the
   tool's own `summary.checks_run` always tells you the live count — trust that over this list if
   they ever disagree — **and if it DOES disagree, your cached copy of this PLAYBOOK is stale (G113):
   say so plainly to the user and `report_gap` it — don't silently keep using the number below**):
   - **Phase 1 (7):** `effort_within_capacity` · `reel_completeness` (every required field, including
     all 4 hook layers) · `provenance_integrity` (a DATA-DRIVEN reel needs `receipt.n≥5` + a median) ·
     `provenance_split_honest` · `min_source_diversity` (≥3 source accounts) · `funnel_mix_delivered` ·
     `plan_size_honesty`.
   - **Phase 2 (4):** `no_banned_tags` · `activation_needs_plumbing` (a `keyword_dm`/`lead_magnet`
     `cta_type` blocks if the lead magnet + DM automation aren't confirmed built AND tested, whatever
     the stage; once they are, a cold-start account only gets a warn about the reach cost) ·
     `language_set` (needs `meta.language`) · `no_unflagged_placeholder` (shipped 2026-07-27 — every
     invented/placeholder reel from Step 8's HARD GUARD must carry `needs_real_content: true`, or this
     blocks).
   - **Phase 3 (4):** `variety` (hook/structure/angle shouldn't repeat past ~60% of the plan) ·
     `self_cannibalization` (two reels shouldn't chase the same `topic_idea`) · `producible_format` ·
     `subject_check` (needs `meta.subject_handle` / `meta.subject_type`).
   - **Intake (2, G225):** `intake_completeness` (warns if `inputs.business_context.
     intake_completeness.score` is below the floor — a thin intake) · `assumptions_disclosed` (warns
     if the intake recorded assumptions but the plan doesn't list them in `section_00.assumptions`).
   **Fix every `blocker` it returns and re-validate until `ok: true`.** Warnings
   are surfaced to you + the creator but don't block. This tool checks the *countable* things so the
   gate + critic below can focus on the *judgment* things (is the hook strong? is a reel a near-clone
   in spirit?). If the tool isn't available on this connection, walk those same checks by hand.
   **G207 — `verify_receipts: true`.** The 17 checks above are arithmetic on whatever the plan
   self-reports; they cannot tell a real receipt from an invented one (confirmed: a plan with 3
   fabricated receipts passed all 17 with `ok: true`). Pass `verify_receipts: true` whenever you are
   reviewing/finishing a plan you did NOT personally pull every receipt for THIS run (e.g. resuming a
   plan from an earlier session, or checking someone else's draft) — it cross-checks each DATA-DRIVEN
   receipt's `source_handle`/`n`/`median` against this workspace's own tracked-competitor data. A
   receipt that fails this is fabricated or wrong; fix it or downgrade the reel to JUDGMENT.

1. **Run the draft through `RULES_GATE.md` yourself first.** It is a universal, book-derived
   checklist (built from the generic principles in `rules/` — copywriting, funnel, authority, offer,
   traffic — with **no business's private strategy in it**). Walk all eight gates:
   (1) voice & compliance — no guaranteed-result/income claims, no fake urgency, hype is optional not
   forced; (2) structure — hook-story-offer, one job per reel, an origin reel, objections handled;
   (3) retention on every reel; (4) benchmark-never-copy (kill re-skins); (5) stage-appropriate CTA +
   value-ladder; (6) **STRATEGY ADHERENCE — does the Part C calendar actually deliver the Part A
   strategy? count the funnel mix, the pillar %, the audience fit, the goal fit**; (7) data integrity
   (median not mean, honest provenance); (8) **deliverable feasibility & variety — each week's effort
   fits capacity, plan-size is honest, activation CTAs have plumbing, CTAs/hooks vary, ≥3 source
   accounts, audience's language**. Fix every fail, then re-walk it.
2. **Pass it to a senior-SMM critic with fresh eyes — a genuinely separate context, every time
   (G224).** Spawn a **Task subagent**, given ONLY the draft plan + `RULES_GATE.md` — never the run
   history or reasoning that produced the draft. **There is no "clean-slate pass" option** — the same
   session re-reading its own output is not independent review, however careful it tries to be. Have
   the critic **re-run the same `RULES_GATE.md`** plus hunt for: mimicry, unrealistic benchmarks, a
   CTA whose plumbing is wrong, near-clones, a **judgment dressed up as data**, weak retention, a reel
   that won't survive the feed, or a calendar that drifts from its declared strategy.
   **Record the critic payload as `{verdict, rounds, changes, no_findings_note}`**: `changes` is the
   list of concrete edits the critic's feedback produced (may be empty). **If `changes` is empty,
   `no_findings_note` is REQUIRED** — one line naming what was actually checked (e.g. "checked all 8
   RULES_GATE items + mimicry + retention on every reel — no material issues"). A verdict with neither
   a change list nor a no-findings note is not a real review — it's a rubber stamp, and
   `submit_content_plan` will flag it as such (see below).
3. **Apply every valid recommendation** and re-draft.
4. **Repeat** until the gate is fully clean and the critic has no material objections left —
   **but cap the loop at 3 rounds.** If a real objection still stands after 3 rounds (the critic
   and the fix keep disagreeing, or a fix isn't possible with the data on hand), **stop looping.**
   Ship the best version, name the unresolved issue plainly in Part E2 ("what we couldn't fully
   resolve, and why"), and — if it's a product limitation — log it in `marketing/engineering-gaps.md`.
   A plan shipped with an honest, named limitation beats an endless loop or a hidden flaw.
   *(Cosmetic nitpicks that don't change the plan's quality are not a reason to keep looping — close them out.)*
5. **Ship only the passed (or capped-and-disclosed) version**, and state briefly *what the gate +
   critic changed*, plus any unresolved issue (Part E2).

**If a Task subagent genuinely cannot be spawned** (e.g. a headless run with no subagent support),
do not substitute a clean-slate self-read and call it independent review (G224) — that is the exact
loophole step 2 closes. Instead, name that limitation plainly in Part E2 ("no independent critic pass —
subagent unavailable this run") and submit the plan without a `critic` payload at all — `submit_content_plan`
will then honestly record `critic_trace: "missing"` rather than a false "reviewed" signal. (Sending an
empty or note-less `critic` object instead would record `"unverifiable"`, not `"missing"` — either
value is an honest "not reviewed" signal, but only omitting `critic` entirely produces "missing".)

This is the exact loop that turned the first attempt (5/10 — big-creator tactics copied
onto a cold account) into a real plan. Skipping it is how you ship confident mimicry.

---

## Step 12 — Capture: save the plan to the creator's Content Calendar

Once the **critic-passed** plan is delivered, offer to SAVE it to Reach Machine so it
lives in the creator's month-organised **Content Calendar** (Plan → Content Calendar),
and — with their permission — helps improve this planner. This is a **free, no-spend
write** (G62).

**🔴 HEADLESS RUNS (G208, `runner.py`) NEVER REACH THIS STEP** — `consent: true` on
`submit_content_plan` means "a human just said yes," and a headless run has no human
to ask. `submit_content_plan` is deliberately NOT in `runner.py`'s allow-list, so an
unattended run cannot call it at all — that is not a bug, it is the point: an
"explicit yes" a headless agent invents for itself would poison the exact dataset
(`content_plans`) a later QA/eval loop reads to judge plan quality against reality.
A headless run's deliverable is the in-chat/rendered plan only. If unattended saving
is ever wanted, it needs a real consent-provenance mechanism (recording WHO/WHAT
said yes, not just a boolean) — that is a product decision for the founder, not an
engineering default, and is not built here.

1. **ASK for consent — explicitly, and WAIT for a yes.** e.g. *"Want me to save this
   to your Content Calendar in Reach Machine? It'll be filed under [Month Year] and
   you can reopen it any time. Saving also lets Reach Machine review plan quality to
   improve the planner — your call."* Storing without asking is not allowed (the same
   discipline as confirm-before-spend, though nothing is spent here). A **"no" ends the
   step cleanly** — the plan is still delivered in-chat.

2. **On an explicit yes, call `submit_content_plan`** with:
   - **`plan`** — the **STRUCTURED** plan you just built (a JSON object, NOT the prose /
     rendered version):
     ```
     { meta: { language: "<the plan's language, e.g. 'en' or 'hi-en'>",         ← MACHINE-READABLE
               subject_handle: "<@handle this plan is FOR>",
               subject_type: "self" | "client" },
       section_00, decision_log,
       funnel: { mix: "<plain sentence>", reasoning: "…",
                 counts: { reach: <int>, nurture: <int>, activation: <int> } },   ← MACHINE-READABLE
       prerequisites: [ { what: "dm_automation" | "lead_magnet", by_week: <int>, why: "..." } ],  ← MACHINE-READABLE
       reels: [ { id, title, format, intent, niche, angle, structure, topic_idea,   ← MACHINE-READABLE
                  funnel_role, audience_segment,
                  emotion, hook: {spoken, on_screen, visual, sound}, retention, cta,
                  cta_type,                                                      ← MACHINE-READABLE
                  week: <int>, depends_on: "dm_automation" | "lead_magnet",        ← MACHINE-READABLE
                  effort, priority,
                  provenance: "data_driven" | "data_inferred" | "judgment",         ← MACHINE-READABLE
                  receipt: { source_handle, source_url, n: <int|null>,              ← STRUCTURED, not a
                             median: <number|null>, reliability, tag, note } },       sentence
                … ],
       cadence: { per_week: <int>, weeks: <int> },                              ← MACHINE-READABLE
       kpis, captions_seo, distribution,
       receipts_summary: { …, provenance_split: { data_driven, data_inferred, judgment } } }  ← COUNTS
     ```
     **Cross-account receipts (G336).** If a reel's pattern is real across MULTIPLE tracked
     accounts (e.g. a hook style with a strong median across 20 reels from several creators — not
     one), write `receipt: { source_handles: ["@a", "@b", "@c"], n, median, ... }` instead of a
     single `source_handle`. Each handle in the list counts toward the ≥3-source-diversity
     requirement, and `verify_receipts` pools the real stored views across every listed handle
     before comparing your claimed `n`/`median`. Use `source_handle` OR `source_handles`, never
     both on the same receipt.
     **Why the machine-readable fields matter (G118).** `validate_content_plan` (Step 11) and the
     save-time check read these fields to enforce the countable guarantees — effort ≤ capacity, ≥3
     distinct `receipt.source_handle`, a DATA-DRIVEN reel must carry `receipt.n ≥ 5` + a `median`, the
     `funnel.counts` the calendar actually delivers, the honest `provenance_split`. **Put the numbers in
     the STRUCTURED fields, not only in the prose** — a receipt written as a sentence can't be checked,
     so a `receipt` object with `n`/`median` null (and the human line in `receipt.note`) is how you say
     "no data receipt" honestly. Keep the human-readable prose too (the dashboard uses it); the
     structured fields sit ALONGSIDE it. **Include the `decision_log` (TEMPLATE E3)** so the reasoning
     is written back and QA-verifiable later.
     **The Phase 2/3 checks (G118) read these fields — never leave them out:**
     - `meta.language` — the language the hooks/captions are actually written in (Step 3 item 3).
       Checked by `language_set`; missing it means nothing that depends on language can be verified.
     - `meta.subject_handle` + `meta.subject_type` (`self` = the creator's own account, `client` = an
       agency planning for someone else) — who the plan is FOR. Checked by `subject_check`, which
       also compares `subject_type` against `inputs.business_context.subject_type`, and `subject_handle`
       against `inputs.business_context.subject_handle` (G223), when both sides are set (add both fields
       to `inputs` — see below) to catch a plan that drifted onto the wrong account or the wrong client's
       handle.
     - `reel.structure` — the narrative structure this reel uses (the same value you read from
       `get_content_structures` / the breakdown's `structure_type` dimension, e.g. `"listicle"`,
       `"before_after"`, `"pov"`). Checked by `variety`, which warns if too many reels repeat one value.
     - `reel.topic_idea` — the specific idea this reel covers, in a few words (not the niche — the
       actual angle, e.g. `"why most X fail in month 1"`). Checked by `self_cannibalization`, which
       flags two reels chasing the same idea so they don't compete with each other.
     - `reel.cta_type` — set this ONLY when the CTA promises an activation action the automation must
       back up: `"keyword_dm"` or `"lead_magnet"`. Leave it unset for reply-bait / no-CTA reels.
       Checked by `activation_needs_plumbing` — an explicit `cta_type` is the plan stating its own
       intent: missing/untested plumbing always **blocks** (the creator can't keep the promise), no
       matter the account's stage; with the plumbing confirmed built AND tested, a cold-start account
       only gets a **warn** about the reach cost (Step 4). A free-text CTA that merely reads like a DM
       promise (no `cta_type` set) never blocks — at most a warn.
     - `plan.prerequisites`, `reel.week`, `reel.depends_on` (G129) — if a reel needs something built
       first (e.g. a keyword-DM automation for an activation CTA), **schedule the prerequisite and give
       the reel a later week — do NOT downgrade the CTA to something weaker.** Example: if week-4 reels
       need the dm_automation, add `prerequisites: [{what: "dm_automation", by_week: 1, why: "..."}]`
       and mark those reels `week: 4, depends_on: "dm_automation"`. The validator downgrades to a warn
       (gated, do not post before the prerequisite is tested) instead of blocking. Without a prerequisite,
       or if the prerequisite is scheduled the same week or later than the reel, the validator blocks —
       a plan that cannot be delivered in order is not a plan.
     - `inputs.business_context.production_capability` — the formats the creator can actually shoot
       (e.g. `["talking_head", "screen_record"]`), from Step 1. Checked by `producible_format` against
       every `reel.format`; without it the check can't verify a reel isn't asking for a format the
       creator can't produce.
   - **`plan_month`** — the calendar month this plan is FOR, as **`YYYY-MM`** (e.g.
     `2026-08`). This is what files it under the right month — get it right.
   - **`title`** — a short human title, e.g. *"August 2026 — <the positioning angle>"*.
   - **`inputs`** — what it was built from, so a later review is diagnosable:
     `{ business_context: {stage, positioning, funnel_assets, goal, subject_type: "self" | "client",
     subject_handle: "<the confirmed per-workspace @handle from Step 1.6>",
     production_capability: [<string>],
     capacity: { reels_per_week: <int> }, requested_plan_size: <int>,
     target_audience_segment}, data_signature: {analysed_reels_count, competitors_count,
     audience_segments, levers_used: [{lever, winner, median, n, reliability}]} }`.
     **`capacity.reels_per_week` and `requested_plan_size` must be integers** — the validator
     compares the plan's effort + size against them (G118).
   - **`critic`** — the Step 11 result: `{verdict, changes: [...]}` (what the critic changed).
   - **`consent: true`** — ONLY because the human just said yes. Never hard-code it true
     without the ask. **Headless/unattended runs never call this tool at all** (see the
     Step 12 headless note below) — an "explicit yes" that never came from a person is
     not consent.
   - **`skill_version`** — read `${CLAUDE_SKILL_DIR}/VERSION` fresh and use its contents
     verbatim (G113 — do NOT hardcode a version string in your own memory; that file is
     the only source of truth, bumped every time this method changes).

3. **Confirm** to the creator: *"Saved to your Content Calendar under [Month Year] — open
   it any time under Plan → Content Calendar."*

   **If the save fails, try again before giving up (G250).** Before your first `submit_content_plan`
   call, make up a short unique `idempotency_key` for this plan — any random string is fine, e.g.
   `plan-2026-08-a7f3c1`. Send that same key on the first attempt and on every retry of that same
   plan. The server uses it to tell a retry apart from a new plan, so retrying cannot create a
   second copy: a repeat comes back with `already_saved: true` and the id of the plan it stored the
   first time. Treat that as success and stop retrying.

   How to retry:
   - **The call errored or timed out** — you don't know whether it landed. Send it again with the
     same `idempotency_key`. Try up to **three times in total**, and wait before each retry so a
     brief outage has time to clear: **wait about 2 seconds before the second attempt and about 5
     seconds before the third.** Stop as soon as one comes back `stored: true` (with or without
     `already_saved`).
   - **It returned `stored: false` with a reason** — read the reason. Missing consent or a rejected
     field is your input being wrong, and sending the identical call again will fail identically.
     Fix what the message names, then send it once more. Do not loop on a rejection.
   - **Write tools are not enabled on this connection** — that is not a transient failure and no
     number of retries will change it. Say so once and move on.

   **If it still hasn't saved after three tries, do not just move on — hand the work back.**
   Never fail the delivered plan over the save, but never let the customer discover the loss on
   their own either. Do all four of these, in this order:

   1. **Say plainly what happened and what it means for them**, in your own words, covering: the
      plan itself is fine, but it is NOT in their Reach Machine library, so it will not appear
      under Plan → Content Calendar. Do not say "saved" or imply it is recoverable from our side.
   2. **Write the complete plan to a file they can open**, using the same full format you used to
      deliver it in chat. Name it so it is obvious, e.g. `content-plan-<Month>-<Year>.md`, and
      tell them the filename **and its absolute path, on its own line** — the full path from the
      drive or root, not just the name (G370: a file they cannot find is a file they did not get).
      This is the step that means their work survives the conversation.
   3. **Give them the `idempotency_key` you used**, and tell them to keep it. Explain why in one
      sentence: if they ask you to save again later, reusing that key means a save that quietly
      succeeded the first time cannot turn into a second copy.
   4. **Offer the next step**: they can ask you to try saving again at any point in this
      conversation, and you will reuse the same key.

   If write tools are not enabled on this connection, skip step 3's promise about retrying — say
   the save is unavailable on this connection, and still do steps 1 and 2.

   **The same key-and-retry rule applies to `report_gap` and `record_content_plan_run`** — each gets
   its own key per logical save, and they report a repeat as `already_logged` / `already_recorded`.
   **`submit_analysis` is different and needs no key**: its save is already keyed to the reel, so a
   repeat is safe on its own and it tells you with `already_analyzed: true`.

**Privacy:** the plan is the creator's own content strategy — stored only on their
explicit yes, scoped to their workspace, used only to review/improve the planner. No
data beyond the plan + the inputs above.

---

*Companion: `SKILL.md` (invokes this method) and `runner.py` (runs it headless via
the Claude Agent SDK against the Reach Machine MCP). Product gaps this method works
around are logged in `marketing/engineering-gaps.md`.*

---

## The Rigor Rules (§A–§I) — the full standard every step is held to

*(This is the detail behind the "Rigor Rules" summary near the top. Not an appendix — these are
applied INSIDE the steps, referenced by each step that uses them.)*

A plan is only honest if it separates **data** from **judgment** out loud. Apply
all of these on every run, and **put the confidence + sample size in the output.**

### A. The universal formula — "the Reel Bet"
Every reel = **Proven Pattern × First-Party Topic × Audience Tension.**
- **Proven Pattern** — a hook-template + structure + emotion combo with a high
  *goal metric* in the data (found via cross-tab, §C), with adequate sample.
- **First-Party Topic** — a topic from the **demand-validated candidate set** (the
  niches that already exist in the data), reframed through the creator's own proof.
- **Audience Tension** — one specific pain / desire / identity of the ONE audience
  the reel resolves. Anchor it to the target **audience segment** from the data (§F)
  so the reel speaks to a real, sized segment rather than a vague "everyone".

**Never combine a novel pattern with a novel topic — that is maximum risk.**
Novelty belongs in the *framing / proof*, not in the pattern or the topic-demand.
A plan is a **portfolio of bets**, not a set of guarantees: expect most reels to be
average and a few to carry the reach — that is how the creators in the data operate.

### B. Confidence — label every recommendation
`confidence = f(sample size n, median lift over baseline, recency)`:
- **High** — large n, **median** (not mean) beats baseline, recent.
- **Medium** — decent n or strong median, one caveat.
- **Low / "a bet"** — n below threshold (≈ 5) or mean inflated by one outlier.

Always read **median**, not mean — the mean is survivorship-inflated by a few mega
reels. Show the confidence + n next to each lever in the deliverable. This n≈5
threshold is also the bar for the **DATA-DRIVEN** tag in §I — below it, a
recommendation can never carry that tag, however good the median looks.

### C. Cross-tabs, not single levers
Use `get_content_breakdown` **`group_by`** (e.g. `["angle","structure_type"]`,
`["hook_emotion","structure_type"]`) to find the **combinations** that co-occur in
winners for the goal metric — do not read each lever in isolation. Assign the
highest-goal-metric combo with adequate sample; if thin, fall back to the single
strongest lever and mark it **Low confidence**.

### D. Goal-conditioned selection (keep the goal in mind)
Rank levers / topics by the metric that matches the goal:
- **Reach** → median **views + shares**; favour amusement / skit / relatable-meme;
  CTA = reply-bait or none.
- **Leads** → **comments + saves** + a real CTA; keyword-DM (gated by stage + plumbing).
- **Authority** → **saves + watch-time**; insight / proof / contrarian.

### E. Niche — follow the data for SELECTION, judge the FRAMING (don't mirror shares)
- The data's topic list is the **candidate set** — proven audience demand. Do **not**
  invent topics outside it.
- **Weight by median performance**, NOT by the competitors' raw share (their share
  reflects *their* business, not the creator's).
- Reframe each chosen topic through the creator's positioning + first-party proof.
- Mirroring exact percentages copies competitors' strategy — that is not the goal.
- **A second proven-demand source: the creator's own audience.** Competitor data
  proves a *pattern* works for someone. The creator's own comments, DMs, replies,
  and FAQs prove *demand* — the exact questions their own audience asks, in
  their own words. Ask the creator to bring you a batch of real comments/DMs/
  FAQs and mine them for the recurring questions and topics. Combine both
  sources: a topic that shows up in **both** the competitor candidate set
  **and** the creator's own audience questions is the strongest bet.
- **Tag audience-sourced topics DATA-DRIVEN** (§I) — it's real first-party
  audience data — but **only if the creator actually supplies** the comments/
  DMs/FAQs. If they don't have any to hand over yet, this becomes a
  **JUDGMENT** prompt instead: tell the creator to go collect them (their last
  20 DMs, their most-asked comment questions) before the next planning run.
- This **strengthens**, not contradicts, the anti-mimicry rule above — the
  creator's own audience's real words can never be a competitor clone.

### F. Audience — MODEL THE LEVERS FOR THE TARGET SEGMENT, not just the niche
`get_content_strategy` groups the tracked reels into clean **audience segments** ("Who Are
They Speaking To?", reverse-engineered per reel) with real counts + shares. The whole
strategy — **hook, structure, CTA, topic** — should be modelled **for the creator's ONE
target segment**, not the niche average:

1. **Pick the ONE segment this creator serves** (from Step 1) and read how deep the proven
   material is for it.
2. **Filter the levers BY that segment.** `get_content_breakdown` with
   **`filters.audience=[the canonical macro label]`** (the same label `get_content_strategy`
   shows — matching ignores case/spacing) **DOES return real data**. Pull the audience-specific
   winning **`hook_template`, `structure_type`, `cta_type`, and topic** — so the plan says
   "for THIS audience, X wins," not "for the niche overall."
3. **Sample-size guard (the real limit is n, not the filter):**
   - Segment has **≥ ~5–8 reels** → read it audience-specific and tag by §B (DATA-DRIVEN /
     DATA-INFERRED **on that slice**).
   - **Thinner** → the audience-specific read is **Low-confidence**; **widen** to the adjacent /
     on-ramp audience (or the whole board) for the pattern read and **say so**. Never force a
     3-reel audience slice into a confident claim.
4. **Weight by median WITHIN the segment**, not the segment's raw share (don't mirror what
   competitors post — favour what performs for this audience).

**Correction to the old note:** the audience-macro filter is **not broken** — it returns real
reels; what was thin in testing was *small segments* (e.g. n=10). So audience-specific
modelling of hook/structure/CTA is the **DEFAULT when the segment is deep enough**, with the
widen-and-label fallback above when it isn't.

### G. Honest topic labels
On every reel show the **real data niche** it maps to, separately from the
**reframed idea** — e.g. *idea:* "I replaced a $2k hire with AI" → *data niche:*
"AI tools". Never let a reframed label masquerade as a data value.

### H. Every reel is an experiment
Attach a **hypothesis** + a **kill / scale rule**: after N reels on a pattern, if the reel beats
the account's own rolling median → **scale** it; two consecutive flops on a pattern → **retire** it.
This turns the calendar from a guess into a measured loop.

**The scale/kill METRIC must be stage-appropriate — don't judge every account the same way.**
- **Cold / small account (~0–few-thousand followers):** hour-1 velocity and raw views are near-zero
  **noise** — a good reel can sit for days before it travels. Judge on **saves-per-1k, watch-time %,
  shares-per-1k, and replay rate** against the account's OWN baseline, not on early view count.
- **Established account with real reach:** hour-1 velocity + watch-time vs the rolling median are
  meaningful — use them.
Always compare to **this account's own bar**, never a big creator's numbers (that's the 5/10 trap).

### I. Tag the PROVENANCE of every recommendation (data vs inferred vs judgment)
The plan is only trustworthy if the human can see what's earned from data and what's
your craft — and if two different runs would tag the same recommendation the same
way. Use this **operational rule**, not a vibe check:

> A recommendation is **DATA-DRIVEN** only when the exact lever choice is backed
> by a **median** with a **stated sample size at or above the bet threshold
> (§B, n≈5)**, read from the **audience-matched slice** (§F — the creator's
> target segment, not the whole board). Anything thinner is **DATA-INFERRED**
> or a **bet** — never DATA-DRIVEN.

Tag every lever, topic, and reel choice with where it comes from, paired with the
confidence (§B):
- **DATA-DRIVEN** — meets the rule above. *"Curiosity × Tutorial, median 112k,
  n=8, from the target-audience slice."*
- **DATA-INFERRED** — a judgment **extrapolated** from the data (thinner sample,
  wrong slice, or a reasonable cousin of a proven pattern). *"Skit wins biggest but
  you're solo, so relatable-POV is the doable cousin of that pattern."*
- **SMM JUDGMENT** — craft with no data behind it: stage translation, framing around
  first-party proof, retention structure, cadence, trending-audio picks.
Make it legible in the deliverable — a per-row tag or a clear section legend — and
**never let a judgment masquerade as a data claim** (this is §G, enforced on every cell).
A plan that can't tell the human which is which is not senior work.

**This is now checked in code (G118).** `validate_content_plan` (called in Step 11) enforces the
countable half of this rule: a reel tagged **DATA-DRIVEN** must carry a structured `receipt` with a
**sample size n ≥ 5** and a **median**, and the plan's provenance-split counts must be honest. So the
provenance tag is no longer just a promise you make in prose — emit the numbers in the structured
fields (Step 12) or the check flags it. The rule above still governs the *judgment* half (which
tier a borderline call belongs to) — the code checks the arithmetic, you own the judgment.
