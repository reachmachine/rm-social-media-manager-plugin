> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 1 (continued, part 2) — the fields the intake must END UP with

**Ask per `asking-rules.md`.**

**Continued from `playbook/step-01-intake-fields.md`** — that file's Account stage and
Positioning fields, plus the shared quality-bar / framework-card rules, apply here too. This
file holds the rest of the field list, split out only to stay under the 300-line limit
(FRFRMU-1008/1014).

- **Their personal story — an EXPERT INTERVIEW, not a form question (G696; optional as ever,
  G373).** Open it plainly, in the founder's own words: *"Who are you? Why did you start this,
  and why does this matter to you?"* This is different from the origin / transformation story
  above (positioning item 6, the audience-facing proof-of-change) — that one sells the belief;
  this is the person. It is never subject to the positioning hypothesis/confirmed cycle. Make it
  easy to skip: *"Totally optional — skip it if you'd rather not share."*
  **This field is EXEMPT from the 2-try refinement cap (Step 1 rule 7) — depth here is
  consent-based, not counted.** No hard limit on follow-ups, but each deeper push asks
  permission with the reason: *"Mind if I ask a couple more questions? The more I understand you
  and the business, the more compelling we can make your story."* "Let's move on" — or two
  deflections in a row — is the stop signal: stop at once, keep what you have, no comment.
  **Consent for personal ground (no protocol existed before this; architect-proposed, pending
  founder ratification):** before the deeper questions, one plain line — *"some of this can get
  personal — share only what you're comfortable seeing used in content."* If an answer reveals
  something clearly painful (loss, illness, mental health, a family matter), acknowledge it
  briefly, do NOT probe further into that topic, and ask whether they want it in their story or
  left out. Anything they ask to leave out is never saved — not even as a fragment.
  **The interview ends when the success criteria are met (or the person stops it), not when the
  questions run out:**
  - a **specific scene** a viewer could picture — "I always loved helping people" fails; "the
    night my client ghosted a $4k invoice" passes;
  - **external AND internal struggle** — "I had no clients" + "I felt like a fraud"; the
    internal layer carries the passion;
  - a **low point or flaw** — the gap between then and now is what moves people; a polished
    highlight reel fails;
  - the "why" **bottoms out at love or status** — run the 5-Why drill until it lands there;
    "freedom" is not the bottom, "I missed my kid's play for a client who didn't pay" is;
  - it **compresses to one sentence: character + desire + conflict.** Can't form that sentence
    from their answers → something is still missing.
  **The 6-question ladder — a REFERENCE template, not a script.** Reorder, skip, or invent
  questions as their actual life demands; after each answer, check which criteria are satisfied
  and chase the biggest missing one:
  1. *Backstory* — "Before this business, what were you doing?" If unrelated: "From [bank
     teller] to [cooking] — what happened in between?" (the disconnect IS the story).
  2. *The Wall* — "Was there a moment you realised that wasn't working? Not the feeling — an
     actual day you remember. A call, a bill, something someone said?"
  3. *5-Why drill* — on abstract answers ("freedom", "growth"): "[Freedom] from what,
     specifically?" → "What was staying costing you — money aside?" Stop the moment it touches
     love or status.
  4. *Internal struggle* — asked AFTER trust is built, never first: "What were you afraid of
     back then?" If they deflect to external: "Was there anyone you dreaded telling?"
  5. *Point of No Return* — "Was there a moment it flipped from 'I should' to 'I can't NOT do
     this'?" If genuinely gradual, record "gradual" — never force a moment that didn't happen.
  6. *False beliefs* — "What were you SURE about back then that turned out backwards?" Each
     answer is a future belief-breaking reel.
  (Internally this is `rules/authority.md`'s Epiphany Bridge material — never book-speak to the
  user.)
  **Honesty rules (non-negotiable):** one question per message · react to each answer before the
  next · **never invent details the person didn't say** · assemble the story from THEIR
  fragments and read it back — *"Did I get that right? What did I miss?"* — the correction is
  usually the best material · save only after they confirm. Assembling their fragments and
  confirming is NOT writing one for them — reflect back, never fabricate.
  **Saving:** to the Creator Brief (`update_creator_brief`, key `personal_story`, `{value,
  source: conversation, confidence}`) — never into the `positioning` object (that one gates the
  "GENERIC" stamp; this one must never block a plan). Criteria unmet after honest effort → save
  it with `status: partial` — a partial story with a real scene beats a complete story of
  summaries. If they decline entirely, save `{value: "declined", source: conversation}` so the
  skill never re-asks it as if forgotten. **A declined personal story is a normal outcome — it
  never blocks the plan, and declining still counts as this field handled (G373).**
- **Funnel plumbing:** do they already have a lead magnet **and** a DM automation
  (e.g. ManyChat) wired and tested? This gates whether any "comment KEYWORD" CTA is
  even allowed (see Step 4).
  **No bar and no card** — this is a factual yes/no gate; it is still scored (rule 6).
- **Goal + horizon:** reach, leads, or authority — and over what window.
  **Bar (G696):** a metric + a horizon. "Grow" fails; "1k followers in 90 days to launch my
  course" passes. **Card:** "One goal, measurable, with a deadline — chasing reach AND leads at
  once usually gets neither."
- **Capacity — fixed choices, framed by reality, not motivation (FOUNDER DECISION,
  FRFRMU-1008).** Ask: *"On a normal busy week — not your best week — how many QUALITY reels
  can you actually make while running your business?"* Offer these choices, each with its own
  honest note:
  - **2 a week** — sustainable for almost anyone; slower growth, but you'll actually keep it up.
  - **4 a week** — needs a real routine (a regular filming day); drop-off risk if life gets busy.
  - **Daily** — only realistic with batching or help; most solo creators can't sustain this past
    a few weeks.
  - **Other** — let them name their own number; reality-check it the same way as the choices.
  Default the plan to the **LOWER end** of what they pick — anything above that is a stretch
  goal, not the baseline. This number drives the effort tagging and batching in Step 8.
  **Bar (G696):** a number tied to their real calendar, not motivation. "Daily if I push myself"
  fails; "2 a week — I film Sundays" passes. No card — factual.
- **Production capability — a LIST, not one dial (FRFRMU-1310); ask, and treat it as an
  ON-RAMP, not a filter.** "What can you actually produce?" — check every box that fits, not
  just one: **real people on camera** / **real member or client footage** / **coach talking to
  camera** / **screen recording** / **graphics only** / **AI-generated**. A creator can name more
  than one; save all that apply.
  **AI-generated gets ONE mandatory follow-up, always — never accepted bare (FRFRMU-1310).**
  *"When you say AI-generated, what exactly — an AI voiceover over stock or generated visuals, an
  AI avatar standing in for a real person, AI-generated 'client' footage, or something else? Just
  so the plan never shows something that isn't real as if it were."* An answer with no detail is
  not a pass — ask the follow-up before saving.
  **Cross-check it against the proof already on file, out loud (FRFRMU-1310).** This same
  intake may already carry real first-party proof or an origin/transformation story (positioning
  items 2 and 6, `step-01-intake-fields.md`) — named clients, a real before/after. If the
  AI-generated answer would depict PEOPLE or RESULTS (an AI avatar standing in for a real client,
  generated "before/after" footage) while real proof like that is already on record, say so
  plainly: *"you told me about [the real story/proof] — AI-generated footage of a person or a
  result would contradict that, since it isn't really them. I'd keep the AI generation to
  graphics, voiceover, or b-roll, and use your real footage for anything showing a person or an
  outcome. Sound right?"* Never let an AI-generated answer silently stand in for a real story
  already told.
  **The safe default for health, fitness, medical, and other regulated wellness niches
  (FRFRMU-1310).** When the niche/topic (below) is one of these and the creator hasn't
  explicitly said otherwise, default to: **no AI-generated depictions of people or of results**
  (before/afters, transformations, testimonials). Say it as a recommendation, not a silent rule —
  *"for health content I'd keep any AI generation to graphics or voiceover, never a person or a
  result — want that as the default, or do you have a specific case in mind?"* **Carry the
  decision into Constraints (below)** so Step 8 sees it as an off-limit, not something only this
  field remembers.
  Save to the Creator Brief (`production_capability`): `{"value": {"capabilities": [<one or more
  of the six words above>], "ai_generated_detail": "<the follow-up answer, or null if AI-generated
  wasn't picked>", "ai_people_or_results_ok": true|false}, "source": "conversation", "confidence":
  "high"}`.
  **None of this lets you drop a format the market rewards.** The data defines the *target*;
  ability defines the *starting ramp*. So: lead the early calendar with formats they can execute
  **well now** (for quick wins), AND when a high-reach format needs a skill they lack, **never
  silently cut it** — surface it with a **production path**: learn it, use an AI tool / avatar
  (subject to the cross-check and default above), outsource the edit, or a doable **adjacent**
  format that hits the *same* psychological driver (e.g. can't perform skits → a reaction or POV
  talking-head that lands the same relatable-humor beat). Flag it as the capability to grow into.
  A plan that ignores what the market wants because the creator "can't do it yet" is following the
  creator, not the market — that is the mistake to avoid. (See Step 8 + the Rules Gate production
  check.)
  **Bar (G696):** names what they do WELL right now and what they can't, and — if AI-generated is
  named — the follow-up detail. "I can do anything" fails; "comfortable talking to camera, can't
  edit" passes; "AI-generated" alone fails (no detail); "AI-generated — voiceover over stock
  footage" passes. No card — factual.
- **Niche + seed accounts + hashtags — this feeds discovery (Step 2).** Their **niche/topic** in a
  phrase, their **core hashtags**, and **2–3 accounts they admire or see as competitors**. **Seeds are
  OPTIONAL and VALIDATED, not trusted:** many creators won't know any — that's fine, the Step 2 angles
  find accounts from the niche + hashtags anyway. Whatever they DO name, **check it yourself** (real?
  relevant? right size to model? reels-active?) and drop bad seeds — a user's guess is often off.
  **Bar (G696):** a niche specific enough to search Instagram with. "Food" fails; "vegan meal
  prep for busy professionals" passes. Seeds stay optional — but any named handle must be real,
  relevant, and reels-active (the validation rule above IS the bar). No card — factual.
- **Their offer — ask EVERY creator (FRFRMU-1148).** What they actually sell + rough price, so the
  activation / CTA reels (Step 7) drive to a real thing, not a vague "link in bio." If the
  website already shows an offer, lead with it — "your site says 5 days for $25 — still
  current?" For a reach goal, say why you're asking: "we're going for reach first, but that
  traffic needs somewhere to land — do you have anything you sell or give away, even a trial or
  a free consult? If not, that's fine, I'll help you arrive at one." A reach creator with
  genuinely nothing answers "nothing yet" — `offer` stays empty for now, and Step 7's advisory
  layer fills it later.
  **Bar (G696):** a price + a deliverable. "Coaching" fails; "a 6-week group program priced at
  ₹40,000" passes. **Card** (from `rules/offer.md`, the value equation, no book-speak): "People weigh four
  things: how good the outcome is, how much they believe it'll work for them, how long it takes,
  how much effort. So name the outcome + the timeframe + what's included. 'Coaching' says none
  of those."
- **Upcoming moments — launches / promos / seasonal.** Any launches, promos, or seasonal peaks in the
  next weeks the content should build toward (Step 7.8). If they don't know, the agent MAY **web-search**
  the niche's seasonal / timely moments to seed it.
  **Bar (G696):** a dated event, or an explicit "nothing in the next 8 weeks." "Maybe something
  later" fails. No card — factual.
- **Constraints & off-limits (MUST ASK).** Anything the plan must NOT recommend: won't show face? topics
  or **claims they can't make** (health / finance / legal / regulated)? competitors they won't name?
  brand no-go words or tone? Capture them — a plan that ignores them is unusable. **If production
  capability (above) landed on a no-AI-people-or-results default or decision, it lands here too**
  (FRFRMU-1310) — e.g. "no AI-generated depictions of people or results" — so Step 8 sees it as an
  off-limit alongside every other constraint, not only inside `production_capability`.
  **Bar (G696):** silence FAILS. Pass = a concrete list, OR an explicit "none of these apply"
  given AFTER you prompted the categories (face on camera? regulated claims? competitors not to
  name? no-go words?). An unprompted "no constraints" is not a pass. No card — factual.
- **What they've already tried** — briefly, what's worked or flopped for them. Feeds Step 7: double down
  on their wins, don't re-recommend their failures.
  **Bar (G696):** at least ONE concrete win or flop with rough numbers. "Tried everything,
  nothing works" fails; "talking-head tips died at ~200 views, one skit got 20k" passes. No card
  — factual.
- **Brand voice / tone — DERIVE, then confirm.** Read it off their account (professional / casual /
  funny) + any words to avoid, and confirm. Drives every hook + caption (Steps 5, 8).
  **Bar (G696):** 2–3 concrete descriptors PLUS one avoid-word or one example reel they like.
  "Authentic and professional" alone fails. **Card** (from `rules/authority.md`, the Attractive
  Character): "Flaws included — the gap between where you were and where you are is what moves
  people. Polished-perfect is forgettable."
- **Their audience's real questions / DMs / FAQs — PROMPT them to bring a batch.** The strongest *demand*
  signal for topics (§E). If they can't yet, tell them to collect their last ~20 DMs / most-asked
  comments before the next run.
  **Bar (G696):** verbatim questions — even 3–5 — not paraphrase from memory. "They ask about
  pricing" fails; three pasted DMs pass. If they can't yet, the existing rule stands: collect
  ~20 before the next run. **Card:** "Word-for-word beats memory — your audience's exact words
  are tomorrow's hooks."
- **Plan size — ASK, don't assume.** How many reels does the creator want in this plan?
  **Ask the human, and give YOUR recommendation** as the senior SMM, derived from their
  stage + sustainable cadence + horizon (e.g. a 0-follower account doing 3/week → a
  ~2-week, 6-reel starter is usually right; a warm account chasing a launch may want
  12–20). Never silently pick the number — the count is the human's call, informed by
  your recommendation.
  **Tell them what a bigger number really costs — honestly (FRFRMU-630).** They are being asked
  for a number with no idea what it buys or what it charges, so say it in plain words:
  - A bigger plan does **not** spend more Reach Machine credits on its own. Analysing reels is
    what spends credits, and that is a separate ask with its own confirm gate (Step 3 rule 6).
  - It does **not** make you read more competitor reels either — deep reads are capped at
    **12 a plan** whatever size they pick (Step 3 rule 5a).
  - What it does cost is **their time and this chat**: more reels to write, more to check at the
    rules gate, and up to three critic rounds over a longer plan.
  - **Never quote a currency figure and never invent a credit number** (Step 3 rule 6c).
  Example: *"Twelve is fine — that means a longer session, not a bigger bill. And a plan you'll
  actually finish beats a bigger one you won't."*
  **Bar (G696):** a number the human chose AFTER hearing your recommendation. A number you
  picked for them fails the bar by definition. No card — factual.
- **Content language — REQUIRED, one ISO code (FRFRMU-1575).** Ask plainly: *"What language do
  your customers read and watch in?"* This is NOT about comparing your language to a
  competitor's (that check already runs separately, per-account, once a benchmark is added) —
  it decides the language the captions and scripts THIS plan writes come out in. Save the
  ISO 639-1 code (e.g. `en`, `pt`, `hi`) with `update_business_profile`'s `content_language`
  field. If the creator already set it on a past plan, read it back and confirm rather than
  asking cold — never ask twice for the same fact.
  **Bar (G696):** a real language, named or clearly implied ("English", "we post in Hindi").
  "Whatever's easiest" fails — ask once more for the actual language; still vague after that,
  default to the language the creator is asking you in and record it as `derived`. No card —
  factual.

- **The swipe file's human half (p28, FRFRMU-1066) — one occasional ask, `deferred` allowed
  per FRFRMU-1051.** *"Anything you've saved that made you buy or stop scrolling — an ad, an
  email, a post from any industry? Paste it and say why."* Bar: a WHY in the creator's own
  words; a screenshot with none is recorded `why_it_worked: null` and flagged, never admitted
  as a `classic`. Save to `swipe`: `{entries: [{id, folder: ads|headlines|ctas|stories|
  bullets|emails|full_pieces, source: {url|screenshot_note, industry, date_seen}, what_it_is,
  why_it_worked, made_me_buy, by_user: true, cross_industry, classic, used_in[]}],
  last_prompted_at}`. **RM-library items (hooks, structures, CTAs already in the tool) are
  NEVER copied into this key — they stay where they are, referenced by id only.** The agent
  never sets `classic: true` on its own; that needs the creator's confirmation
  (`step-12-after-the-save.md` §4's winners feed).

---
