> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

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

**If this subject needs a NEW workspace and `create_workspace` comes back
`created=false` (FRFRMU-1145):** the account is at its plan's workspace limit — some
workspaces may be locked (over the limit), not deleted; nothing is ever deleted. Relay
the returned `message` **word for word** — both numbers are already in it. Then offer
THREE roads, in this order, never skipping the swap for the reset (FRFRMU-1146):
1. **Upgrade** — send them to `/settings/billing`.
2. **Swap** — call `list_workspaces` first; if another owned workspace suits this
   subject, offer to open it (`keep_workspace_open`) — nothing is reset or deleted.
3. **Repurpose** — only with nothing to swap to, or the customer picks it anyway:
   the repurpose-workspace command resets an existing workspace for this subject.
   Costs more than a swap (it clears saved answers), so always offer #2 first.

Never say "hiccup", "bug on our end", or "try again later" — this is not a bug, it is the
plan's real limit, and retrying changes nothing.

**Before asking anything else — say why, and what happens to it (G236, G240).** In one short line,
before the first profile question: *"I'm going to ask about your business and positioning — that's
what makes this plan accurate instead of generic, instead of only telling you after something
doesn't match. It's used only to build your plan and improve future ones for you. I'll save your
answers to your workspace as we go, so nothing is lost if we get interrupted, and no plan is
produced or published until you approve it."* This is the same reasoning rule 4 below already uses
when a mismatch is found, and the same privacy line Step 12 already gives at save-time — said ONCE
here, upfront, instead of only after
something goes wrong or only at the very end.

Then five rules govern the conversation itself (G100):

1. **Load what's already known FIRST — never re-ask it.** Call **`get_creator_brief`**
   (the durable memory of everything past sessions learned — goal, positioning, funnel
   assets, capacity, offer, baseline) **and** `get_business_profile`. Only ask what's
   **missing or stale**. A returning creator should feel remembered, not re-interrogated.
   - **Unfinished session? Ask, never assume (G369).** If the returned brief carries a
     `planning_progress` field, **check it before treating it as live (FRFRMU-981).** Only a
     record whose `status` is `"in_progress"` AND whose `updated_at` is within the last 14
     days is an unfinished session worth asking about — if `status` is not `"in_progress"`
     (a plan that already finished or was abandoned), or the record is older than 14 days,
     there is **nothing to resume**: say nothing about it and move on as if the field
     weren't there. This protects a returning creator from being nagged about a plan that
     already shipped, and needs no migration for a legacy record written before `status`
     existed — a record with no `status` field at all is treated the same as `status` not
     being `"in_progress"`.
     For a genuinely live record, this account has a plan in progress. Before doing anything
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
     with whatever they actually asked for — call `update_creator_brief` once with
     `planning_progress` `"status": "abandoned"` (same shape, `updated_at` refreshed) so the
     old record stops being offered as resumable next time either.
     **Load the working copy too (FRFRMU-980).** `planning_progress` says WHERE you stopped
     (the step); it does not say WHAT was already decided. Call `get_draft_plan` — when it
     returns `found: true`, its `stage` says how much survived (`strategy_approved` = Part A
     is already built, `calendar_drafted` = the calendar rows are built too), and its
     `plan`/`inputs` are the actual content, not just a name. Fold that into the SAME resume
     question, e.g. *"...we'd finished Step 8, and I still have the approved strategy and the
     draft calendar saved. Want to pick up from there, start over, or do something else?"* On
     "pick up from there," use the loaded `plan`/`inputs` directly — **do not re-call the data
     tools that already produced them.** When `get_draft_plan` returns `found: false` (expired,
     never written, or already superseded by a real save), say so honestly and resume from
     `last_completed_step` alone, same as before FRFRMU-980.
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
     **Second lens — the SAMENESS MAP (G696).** While you scan what the top 3-5 players SELL,
     also capture what they all CLAIM — the promise each one leads with. Then say the
     aggregate out loud: *"in your niche everyone says X, Y, Z."* Announce the pause before
     you start — *"give me 2 minutes to check what your niche is saturated with"* — and cite
     a source + date per claim, the same discipline as above. The sameness map exists for ONE
     customer-facing reason: the ownable-angle flow in `step-01-intake-fields.md` (section A)
     crosses it with the creator's own proof to propose angle candidates. It is JUDGMENT,
     never DATA-DRIVEN, like everything else in this scan — and the same G332 wall holds: the
     sameness map never finds, names, or surfaces Instagram accounts to track. Research for
     positioning, never for the watchlist.
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
   correct answer. **For the creator THEMSELVES, "ACTUAL data" only exists once their own
   account has been watchlisted, pulled and analysed** (Step 1.6 — charged like a
   competitor). Until then, this cross-check runs on competitor/niche data plus their
   stated answers — don't present a self-vs-niche conclusion you don't have the data for
   yet.
5. **PERSIST everything with provenance.** Save positioning to the profile
   (`update_business_profile` — the **only** tool that writes the `positioning` key) AND the rest
   of the intake to the Creator Brief (`update_creator_brief`) — each field carries
   `{value, source: form|conversation|derived, confidence}`. **Do not put a** `positioning` key in
   the `update_creator_brief` call; your draft wording, doubts and tier for positioning go under
   `positioning_notes` instead (FRFRMU-1150). **Persist EVERYTHING you learn — not just the
   standard fields.** If you asked extra questions to understand the business (offer details,
   website, client type, niche nuances), store them too, under any key the Creator Brief needs (it
   accepts arbitrary keys + keeps full history). That store IS the QA/QC record — the plan is
   only auditable if the inputs are written down. This is what makes the next session smarter and the plan QA-able. Save as
   you go, not just at the end.
5a. **An offer is captured the moment it is stated (FRFRMU-1148)** — whichever question you
   were asking, and whatever the goal is. Three sources: the creator says it ("I do 5 days for
   25 CAD"), the website shows it, or the intake question in the field list. Save it at once
   with `update_creator_brief` under the `offer` key — `{value: {what, price, rung, status},
   source: conversation|website, confidence}` — and **read it back** in your very next reply,
   before moving on: one plain sentence, e.g. *"Saved: 5 days of training for 25 CAD as your
   front-end offer. We'll come back to it in the offer section."* No read-back means the rule
   was not followed. `rung` is your guess from p13's five words (`bait | frontend | middle |
   backend | continuity`), said out loud; `status` is `current | proposed | dropped`. One
   `offer` field per creator — if the site shows several, the extras are parked candidates and
   the intake question (below) asks which ONE is the front-end offer.
6. **Score the intake, and never guess silently (G225).** Before building the plan, classify each of
   these key fields as **confirmed** (the human directly answered it AND the answer clears its
   quality bar — rule 7), **weak** (answered, but still below its quality bar after two refinement
   tries — rule 7), **derived** (you inferred or recommended it and the human accepted/didn't push
   back), or **missing** (never answered): audience, problems, ownable_angle, bold_stance, proof,
   stage, funnel_assets, goal, capacity, production_capability, niche/seeds, offer, constraints,
   brand_voice, upcoming_moments, past_attempts, audience_questions, plan_size, personal_story.
   Compute `score = 100 * confirmed_count / total_fields` (round to the nearest integer — a weak
   answer does NOT count as confirmed) and write it into
   `inputs.business_context.intake_completeness = {confirmed: [<field names>], weak: [<field
   names>], derived: [<field names>], missing: [<field names>], score: <int>}` when you call
   `validate_content_plan` / `submit_content_plan` (Step 11/12).
   **Never let a DERIVED or WEAK field pass silently as if it were confirmed.** Any time you filled
   a gap with your own guess — a recommended goal they didn't explicitly agree to, an assumed
   audience, a guessed capacity — do ONE of two things: (a) ask the human to confirm it before
   moving on, or (b) if you proceed without asking (e.g. a headless/unattended run), record it in
   `inputs.business_context.assumptions = [{field, guess, note}]` — one entry per assumption,
   `note` being a one-line plain-English reason you assumed it. **Every `weak` field ALWAYS gets an
   assumptions entry too** — `{field, guess: <the thin answer>, note: "still below the quality bar
   after two tries — the plan builds on a thin answer here; sharpening it upgrades the plan"}`.
   Write the SAME list into the plan itself as `plan.section_00.assumptions` (TEMPLATE.md A0) so
   it's visible to the customer, not just logged internally. **An assumption that exists only in
   your reasoning and never reaches the human or the plan is exactly the failure this rule exists
   to close.**
   **Ask per `asking-rules.md`** — a `declined`/`deferred` answer counts as `missing` above, a
   `not_applicable` answer with an accepted reason counts as `confirmed`, and the score is always
   said out loud in plain words, never as a bare number (full mapping: `asking-rules.md` §7).
7. **Every answer must clear its QUALITY BAR (G696) — refine at most twice, then mark it weak and
   move on.** Each intake field in `step-01-intake-fields.md` carries a written pass/fail bar with
   a bad and a good example. The general test behind every bar: **"Could this answer belong to 100
   other creators?"** If yes, it fails — reflect the bar back with its example and ask ONE sharper
   follow-up. **Maximum 2 refinement attempts per field.** Still below the bar after two tries →
   classify it `weak` (rule 6), say so kindly in one line, and move on. **Never interrogate the
   user** — a third ask on the same field is interrogation, whatever the words. The personal story
   (step-01-intake-fields.md, field 18) is the ONE exception: it runs as a consent-based interview
   with no fixed cap, because its depth is controlled by the user, not a counter.

**Read the customer's website first, if they have one (G234).** Load
`playbook/step-01-1-website-dossier.md` — one permission, a checklist crawl, one saved dossier.
That file is the whole rule: it covers asking permission, reading the pages that answer the
founder's 8-field checklist, and saving what was found so intake can lead with it instead of
asking cold.

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


**Step 1 continues in `playbook/step-01-intake-fields.md`, and its continuation
`playbook/step-01-intake-fields-2.md`** — the fields this conversation must end up with. Load
both next.
