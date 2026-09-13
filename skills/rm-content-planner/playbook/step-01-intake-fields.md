> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 1 (continued) — the fields the intake must END UP with

**Ask per `asking-rules.md`.**

The fields you must END UP with (derive/recommend/confirm your way to them — don't just
fire them as questions):

**Every field below carries a QUALITY BAR (G696)** — a written pass/fail rule with a bad and a
good example. Step 1 rule 7 (`step-01-intake.md`) says how to use them: fail → reflect the bar
back and refine, at most twice, then mark the field `weak` and move on. The general test: could
this answer belong to 100 other creators?

**Some bars come with a FRAMEWORK CARD** — one or two lines of a rulebook digest
(`${CLAUDE_SKILL_DIR}/rules/authority.md`, `rules/offer.md`), said in everyday words WITH the
question, never as a lesson. Delivery rules: 1–2 lines max · always a bad/good example · cite the
rulebook file internally but **never say "Secret #3" or a book chapter to the user — no
book-speak** · cards never bring guaranteed-result wording into the user's answers (the
compliance red line in `rules/copywriting.md` stands) · **and never OPEN a question with a
method term (FRFRMU-1014)** — lead every question in plain language a non-technical business
owner answers without needing a follow-up explanation; a method term like "ownable angle" may
follow as a label, never as the opening word. **The factual fields carry NO card on
purpose** — stage, capacity, production capability, seeds, constraints, upcoming moments, past
attempts, plan size. A framework there is noise, not help.

- **Who the plan is for — persist Rule 0's answer the moment it is decided (FRFRMU-1292).**
  Rule 0 (`step-01-intake.md`) already asks whether this plan is for the account owner's OWN
  brand or a client/managed account — but asking it is not the same as REMEMBERING it. Save the
  answer at once as a plain Creator Brief field (`update_creator_brief`, **not** a Foundation
  card — same pattern as `benchmark_breadth`, FRFRMU-1151) named `subject_type`:
  `{"value": "self"|"client", "source": "conversation", "confidence": "high"}`. This reuses the
  EXACT field name and vocabulary Step 12 already writes onto the plan itself
  (`inputs.business_context.subject_type` / `meta.subject_type`,
  `plan_validator_checks_phase3.py`'s `subject_check` cross-checks the two) — it is not a new
  concept, only the missing early save. Saving it here means a returning session's
  `get_creator_brief` call (Step 1 rule 1) already knows who the plan is for, instead of a fact
  that used to be lost the moment the conversation ended. **Bar (G696):** one of the two words,
  never left implicit. No card — factual.
- **Account stage — ask this AFTER Step 1.6 (the creator's own account), never before
  (FOUNDER DECISION, FRFRMU-1008).** Hold this field until the self-account add + pull
  (`playbook/step-01-6-self-account.md`) has happened, or the creator has declined it — do
  not ask for a follower count or posting history any earlier in the conversation.
  **If the pull happened:** find the self row (`search_watchlist`, the item with
  `role: "self"`), then read `follower_count` and `latest_post_date` from
  `get_profile_details`, and `account_metrics.post_frequency_weekly` from
  `get_profile_posts` (needs at least 2 stored posts — that tool's own note). Read those
  back and PROPOSE the stage in one sentence for a yes/no confirm — e.g. *"Your account
  shows about 4,300 followers, posting roughly 3 times a week — sound right for where
  you're at?"* Never ask for a number you already hold. Save with `source: "derived"`.
  **If the creator declined the pull, or Step 1.6 hasn't run yet:** ask both — a real
  follower number and how long they've posted — and save with `source: "self_reported"`.
  The next successful pull overwrites this value ONLY after telling the creator, never
  silently — e.g. *"you said about 4k followers — the account now shows 4,312, so I'm
  using that."*
  **Bar (G696):** a real follower number + posting history. "Small account" fails; "about 800
  followers, posting on and off for 2 years" passes. No card — factual.
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
  **Before asking items 2 (proof) or 3 (audience) — check Step 1.1 first (FRFRMU-1297).** If
  `website_dossier` is not yet in the Creator Brief and this session has `WebFetch`, run Step
  1.1 (`playbook/step-01-1-website-dossier.md`) — or get the decline recorded — before asking
  either question cold. This matters most when Rule 0 (`step-01-intake.md`) found the subject
  is a **client the person manages, not their own brand**: a manager who just took the account
  on rarely carries the client's proof/results in their head, so the client's own site is the
  right source, never a blank question to the manager. Once a dossier exists, lead with what it
  found (`asking-rules.md` §11) instead of asking cold either way.
  1. Their one **ownable angle** — theirs, not a copy of a competitor's. **Never ask this cold
     (G696) — bring research.** Run section A below AFTER items 2-5 are answered, so you can
     cross their proof with the niche's sameness map. **Look at their account** to ground it:
     what do they already do and prove?
     **Bar (G696):** a competitor couldn't copy it; tied to their proof, not an adjective. "I
     make quality content" fails; "I teach new moms to rebuild core strength in 10-min home
     sessions — the method I used after my own two C-sections" passes.
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

  **Bars for the six answers (G696)** — each is pass/fail, and each gets its card WITH the
  question (delivery rules above):
  1. *Ownable angle* — tied to something they DID or LIVED, not an adjective. "I make quality
     content" fails; "the 10-min core method I built after my own two C-sections" passes.
     (Card + full elicitation flow: section A below.)
  2. *Proof* — contains a number, a name, or a date. "Helped many people" fails; "12 clients,
     one went 0→40k" passes. **Card** (from `rules/authority.md`, the 4-minute-mile idea, no
     book-speak): "One concrete result that shows the 'impossible' is possible — yours or a
     client's, with a number or a name. One result outweighs ten adjectives."
  3. *Audience* — a situation + a struggle, not a demographic. "Moms" fails; "new moms returning
     to work after their first kid" passes. **Card** (from `rules/authority.md`, niching down):
     "The narrower, the stronger — 'moms' is invisible, 'new moms returning to work' owns a
     corner. Who's your corner?"
  4. *Problems* — written like a DM the audience would send, in their words. "They lack
     visibility" fails; "I post every day and get 200 views" passes. **Card** (from
     `rules/authority.md`, the Ask Campaign): "Not what they need — what they'd type in a DM at
     11pm. 'They need discipline' is your words; 'I can't stop snacking after the kids sleep' is
     theirs."
  5. *Bold stance* — someone in the niche would disagree with it. "Be consistent" fails;
     "counting calories is a trap" passes. **Card** (from `rules/authority.md`, the polarizing
     zone): "The best stance sits between mainstream and crazy — bold enough that some in your
     niche would argue, believable enough that your people nod."

  Once you have real answers, **save them** — call `update_business_profile`
  with a `positioning` object. All six answers, including the two new ones
  (bold stance, origin story), go into that **same** `positioning` object —
  there is no separate object for them. Send `positioning` only when you mean
  to **set** it: leaving it out (or sending it as empty/null) leaves the
  existing value **unchanged**. To deliberately erase a stored positioning, set
  `clear_positioning: true` — that is the only way to clear it.

  If `get_business_profile` returns `positioning_warning`, positioning WAS set and got overwritten
  — recover it from `get_creator_brief` and re-save; do not run the interview again and never call
  it a storage delay.

  **A. The ownable-angle flow (G696) — the agent brings research, then brainstorms:**
  - **A1 — Show the framework first (this IS the angle's card, FRFRMU-1014: ask it in plain
    language before naming any term):** *"What do you do differently from everyone else in
    your space? What would make someone pick you over another [niche] person? Here's what
    makes a strong answer — we call it your 'ownable angle,' but that's just a label, not the
    question: (1) rooted in something you DID or LIVED — a competitor can't copy it without
    lying; (2) it names YOUR way of doing it — a method, not an adjective; (3) it's for your
    ONE audience; (4) it says something the rest of your niche doesn't say. Bad: 'quality
    fitness content.' Good: 'I teach new moms to rebuild core strength in 10-min home sessions
    — the method I used after my own two C-sections.'"* (Internally this is
    `rules/authority.md`'s New Opportunity + `rules/offer.md`'s category-of-one — never
    book-speak to the user.)
  - **A2 — The sameness map.** Use the second lens of the G372 scan (`step-01-intake.md` rule 3)
    — what the top players all CLAIM — and read it back: *"in your niche everyone says X, Y, Z."*
    The white-space is what's missing from that list that THIS creator can prove. Sources +
    dates, always.
  - **A3 — Propose 2-3 candidates; don't ask cold.** Cross the sameness map with their proof and
    prior answers, then offer: *"Which feels most like you — or do these spark a different
    one?"* (The same derive-then-confirm pattern Step 1 already uses for ICP and goal.)
  - **A4 — Test every candidate out loud** — theirs or yours — against the 4-part framework. The
    LYING TEST: a competitor couldn't claim it without lying. *"'Authentic fitness content' — a
    competitor could claim that tomorrow. What did YOU do that they can't say?"*
  - **Boundaries:** every candidate is labelled JUDGMENT, never DATA-DRIVEN — Step 7's
    hypothesis→confirmed cycle stands unchanged, and the angle saved here is still a
    `positioning_status: hypothesis` bet for a young account. And the G332 wall holds here too:
    the sameness map never surfaces Instagram accounts to track — research for positioning,
    never for the watchlist.

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

**Step 1 continues in `playbook/step-01-intake-fields-2.md`** — the rest of the fields this
conversation must end up with (personal story, funnel, goal, capacity, and the rest). Load it
next.
