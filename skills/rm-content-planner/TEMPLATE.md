# TEMPLATE — the standard content-plan output (every run, same shape)

> **Why this file exists.** Every run of this skill — for ANY creator, ANY niche, ANY goal — must
> produce the plan in THIS structure, in THIS order. Strategy first (the *why*), then the calendar
> (the *what*), then how it gets made and measured (the *how*), then the trust layer. A reusable
> template means a creator (or a reviewer) always knows where to look, and the critic can check the
> same things every time. **Do not skip a section.** If a section genuinely doesn't apply, keep the
> heading and write one line saying why.
>
> **Universal rule:** fill every section from the creator's OWN data + positioning. Never carry another
> business's strategy into it. Every recommendation is either backed by a data receipt (n + median +
> reliability) or clearly tagged as judgment — never a judgment dressed up as data.
>
> **The receipt numbers + funnel mix + provenance split are DATA, not just words.** In the STRUCTURED
> plan you save (PLAYBOOK Step 12), carry them as machine-readable fields — `reel.provenance`,
> `reel.receipt.{source_handle, n, median}`, `funnel.counts`, `receipts_summary.provenance_split` —
> **alongside** the plain-language prose here. `validate_content_plan` (G118) reads those fields to
> check the countable rules; a number that lives only inside a sentence can't be checked.
>
> **Write it in PLAIN LANGUAGE — a layman must understand it.** The creator may be non-technical. Short
> sentences; explain or avoid jargon; anchor every abstract point with a concrete example. Translate the
> internal terms: "ER" → "how many people like/comment per view"; "TOF/MOF/BOF" → "get seen / build
> trust / ask for the action"; "median" → "the typical (middle) result". The tags and §-labels are for
> YOUR reasoning — **the output speaks the creator's language**, not the tool's.
>
> **Presentation:** this markdown is the canonical content; the creator receives it as the
> **`dashboard.html`** dashboard (fill its embedded JSON with this plan). These Parts A–E map straight
> onto the dashboard's sections.

---

## PART A — STRATEGY (the *why*, before any calendar)

### A0. Overview & positioning
- One-paragraph overview: who this creator is, the ONE ownable angle, and the first-party proof behind it.
- The positioning sentence (the reframe every reel ladders back to). If positioning is missing, stamp the
  whole plan **"GENERIC — positioning not provided"** at the top and say what's needed to fix it.
- **State the positioning status: `hypothesis` or `confirmed`.** For a young/unproven account it is a
  **hypothesis** — the month tests 2–3 angles and the winner is promoted next cycle (see A5). Only a
  data-confirmed angle is stated as settled.
- **List any assumptions plainly (G225).** If Step 1 recorded assumptions (fields you guessed instead
  of confirming), list each one here in one line: what was assumed, and why — e.g. "We assumed your
  goal is reach because you didn't confirm it — let us know if that's wrong." This is
  `plan.section_00.assumptions` in the structured save. If there are none, say so in one line ("Every
  input below was confirmed by you") rather than omitting the point.

### A0b. Sales-readiness check  *(p33, FRFRMU-1071 — only when the account has an offer)*
- The 5-question check from `step-04-stage.md` Step 4.8: *"Can your foundation pitch yet? N of 5."*
- Each of the five questions names its pointer key, or **"unanswerable — [card] incomplete"** when the
  card behind it is empty. Never invents an answer to make the count look better.
- No offer on this account → omit this section entirely; there is nothing to pitch yet.

### A1. Goal & funnel objective  *(state it explicitly — this drives everything below)*
- The goal, named plainly: **reach** / **lead-gen** (e.g. DM automation + lead magnet) / **engagement** /
  **authority / sales**. Pick ONE primary (a secondary is allowed).
- The **ONE conversion action** for the period, worked backwards from the goal.
- The **funnel mix** for the period — TOF / MOF / BOF as a % — WITH the reasoning, goal-conditioned and
  stage-aware (never just mirrored from competitors). *(See `rules/funnel.md`.)*

### A2. Target audience  *(from the data, not a guess)*
- The ONE audience segment this plan serves, with its **size + confidence** from the data.
- If the creator's exact audience is a thin/low-reach slice, state the **on-ramp** honestly: which
  adjacent audience carries the reach, and how the plan bridges to the real target.

### A3. Patterns MATCHED — and WHY  *(the proven levers we're USING)*
- A short table of the levers this plan leans on. Each row: the lever (hook / structure / angle / topic /
  format / CTA) · **funnel role** (which role's slice the lever was read on) · **n** · **median** (never
  mean) · **reliability** (high/med/low) · **provenance tag**
  (DATA-DRIVEN / DATA-INFERRED / JUDGMENT) · one line WHY it fits this creator.
- Group or label rows by funnel role — one pattern set per role in the mix (G328); never one blended set.

### A4. Patterns to TEST — the bets  *(proven-elsewhere, unproven-here)*
- 2-4 patterns worth testing, each framed as an **experiment**: the hypothesis, the reel(s) that test it,
  and a **kill/scale rule** (what result scales it, what result retires it). This is how the plan learns.

### A5. Content pillars & distribution — CONCENTRATE vs DIVERSIFY is a decision, not a default
- 3-4 content **pillars** (recurring themes), each laddered to the positioning.
- The **% split** across pillars for the period, with data-weighted reasoning (favour pillars with proven
  demand for the target audience; don't just copy competitors' shares).
- **How concentrated the split should be depends on the account — there is NO one-size ratio.** Reason it out
  from these signals and STATE the reasoning; do not apply a fixed number:
  - **Has this account found a repeatable hit yet?** (its own past reels, or a very strong single lever for its
    exact audience.) *No hit yet* → **concentrate** most of the calendar on the single most-promising angle with
    2–3 variations, to *find the vein* before spreading. *A proven hit exists* → **diversify** — protect the
    winner and expand into adjacent pillars.
  - **Goal + stage:** a cold reach-goal account usually needs to find one working hook first (concentrate); an
    established authority account with several proven pillars should spread to stay fresh (diversify).
  - **Data confidence:** if only ONE lever clears the bet threshold for the target audience, concentrating there
    is honest; if several do, testing a few is justified. Thin data ≠ license to spray across many pillars.
  - **Capacity:** low output favours concentration (you can't test 4 pillars well at 3 reels/week).
- **Kill/scale rule tied to this:** a reel that beats the account's own bar → make **3 more like it** next cycle
  (double down), don't move on. Two flops on a pillar → retire it. Concentration is how you *find* the hit;
  diversification is what you do *after* you have one.

### A6. Format mix · recurring series · calendar alignment
- **Format %** (talking-head / tutorial / skit / b-roll…) — from *what wins in the data* × *what the creator
  can actually produce* + capacity (e.g. "60% talking-head · 30% tutorial · 10% skit"), with the reasoning.
- **1–2 recurring series** — a named, repeatable format with a cadence, built on the strongest proven-and-
  sustainable pattern.
- **Business-calendar alignment** — the launches / promos / seasonal moments the plan builds toward (and
  the trending slot stays reactive in the calendar, not planned here).

---

## PART B — FOUNDATION  *(fix BEFORE posting — a calendar on a broken profile leaks all the reach)*

### B1. Profile
- **Searchable name field** (put the main keyword in the NAME, not just the bio).
- **Bio** (who it's for + the promise + one CTA line).
- **Pinned first 3 reels** — including ONE identity/origin reel (from the creator's REAL story — never
  invented). Say which calendar reels fill the pins.

---

## PART C — THE CALENDAR (the *what* — the full period)

### C1. Calendar table — one row per reel
Every reel row MUST carry all of:
- **date / slot** · **pillar** · **series** *(if any)* · **moment-tie** *(building toward a launch/seasonal moment?)* · **topic** *(show the real data-niche AND the reframed idea)* · **angle** ·
  **audience segment** · **intent** *(educate/entertain/inform/inspire/etc.)* · **funnel role**
  *(reach/nurture/activation)* · **emotion** ·
- **how the TOPIC is chosen, and whether it is allowed this month —
  `playbook/step-05-differentiate.md` 5.1/5.2.** Two things it decides land in the row itself.
  **(1) The row carries its own topic receipt** — `kind: topic`, with `topic_id` (the topic's name
  exactly as `get_topic_heat` returned it), `viral_instances` (how many of its reels went viral —
  a real number above zero), `distinct_accounts` (how many different accounts posted them) and
  `hit_rate_band` (`hot` / `warm` / `cold` / `low_n`). An idea with no topic receipt is not a
  finished row; the one exception is a **declared test slot**, which says it is a test and is
  tagged JUDGMENT. **(2) A topic the last plans already covered is on COOLDOWN** and does not come
  back unless it is a named series, or a stated sequel — the row saying in plain words why it is
  back and what result brought it back. A repeat nobody explained is what the creator notices
  before we do. ·
- **4-layer hook** — **spoken** line · **on-screen text** line · **visual** cue · **sound** cue.
  All four are separate fields (`hook.spoken`, `hook.on_screen`, `hook.visual`, `hook.sound`) — the
  validator (G118) blocks the WHOLE reel if any one of the four is missing. **`sound` must never be
  left blank.** How it is chosen is its own recipe — **`playbook/step-08-audio-recipe.md`** — and
  the stakes depend on the mode: a bed under a voice on a talking-head reel, but on a music-only
  or lip-sync reel **the sound IS a hook layer** and must be deliberate. The row carries the audio
  STRATEGY (own voice / reused track / a named candidate that is **rising among the accounts we
  track**, with its numbers) plus the volume relationship; the creator confirms the exact track in
  their own Instagram panel at posting time. A stated judgement is allowed; a made-up claim about
  a specific song is not, and a sound's absence from our data proves nothing because the scraper
  often reports no sound at all. ·
- **how the hook is CHOSEN — `playbook/step-08-hook-recipe.md`.** That step file holds the
  recipe: which channels this reel's format actually has, which proven template to borrow, and
  the month's template test. Two things it decides land in the row itself. **(1) A layer this
  reel's format does not have carries an honest written value, never a blank** — e.g.
  `none — music-only format` for the spoken layer of a silent or music-only reel. It is a real
  value, so the all-four-layers check still passes without anyone inventing a spoken line.
  **(2) The hook carries its own template receipt** — `kind: hook_template`, with `template_id`
  (the canonical template), `count` (how many reels used it), `account_spread` (how many
  different accounts), `median` (their typical views) and `metric_used: views`. A hook with no
  count behind it is tagged JUDGMENT and gets no receipt. ·
- **retention object** (FRFRMU-1544/1546) — `{open_loop, rehook: {options: [{line, form,
  provenance, receipt, recommended}]}, loop_back}`. `open_loop` is the IDEA the hook plants,
  never its wording; each `rehook.options[]` entry is a real, SAYABLE line at ~40% (never a
  stage direction) — 3-5 of them, ranked, with `recommended: true` on at most one and only when
  it has real support behind it; `loop_back` points the ending at `open_loop`. See
  `playbook/step-06-retention.md` for the full shape, `get_retention_patterns`, and the
  mechanical checks. ·
- **beat outline — `playbook/step-08-outline-recipe.md`.** Beats, never a full script: each beat
  names what the moment DOES and roughly says, in about one line, so the words stay the
  creator's. A speech reel gets **talk-beats**; a silent or music-only reel gets **shot-beats**
  with on-screen text on every beat. **A re-hook beat at roughly the 40% mark is mandatory** —
  the mid-video re-grab that stops the viewer leaving — and the outline reserves a beat for the
  CTA without writing it. The outline carries its own receipt: `kind: structure`, with
  `structure_type`, `exemplars` (each one's `post_urls` plus its `structure_grounding` flag, so
  a reader can see whether the shape came from words that were heard or pictures that were
  read) and `n`. A beat quoted as words anybody said must come from a `speech_grounded`
  exemplar, never a `vision_only` one. ·
- **CTA** — stage-appropriate (reply-bait when reach/plumbing is thin; recommend keyword-DM only once
  there's real reach to convert — but it's allowed earlier, with an explicit "few replies at this
  size" caveat, once the automation is confirmed built AND tested; missing/untested plumbing is a
  hard no regardless of stage) ·
- **how the ask is CHOSEN — `playbook/step-08-cta-recipe.md`.** That step file holds the
  recipe: the stage ladder, the plumbing check, and the ranking. Three things it decides land
  in the row itself. **(1) Every activation row in the plan carries the SAME conversion
  action** — one month, one thing to convert to. **(2) An ask that needs plumbing the creator
  has not built AND tested is stepped down**, with the reason written in the row. **(3) The
  ask carries its own receipt when it is presented as evidence-backed** — `kind: cta_pattern`,
  with `cta_type`, `count` (how many reels in the slice made this ask), `accounts` (how many
  different accounts), `median` (their typical **comments**) and `metric_used: comments`. An
  ask's job is responses, so a CTA receipt quoting views is refused. ·
- **caption — `playbook/step-08-caption-recipe.md`.** Every reel row carries its own caption;
  it is not left to the creator. **The first line is a SECOND HOOK** — the reel's hook said in
  DIFFERENT words, written to still make sense where the feed cuts it at roughly 125
  characters. The body is stage-shaped (short and curious for reach, context for nurture, a
  mini pitch with the ask spelled out for activation) and in the audience's language. **The
  caption ends by echoing the reel's CTA exactly**, matching this row's own `cta` / `cta_type`
  — a viewer who reads but never hears the ask still gets it. Hashtags belong to D3, not here.
  ⚠️ `caption_axis` in the analysis data is the ON-SCREEN text style, NOT the Instagram
  caption; the caption text is `content` on a post payload. ·
- **keywords + tags — `playbook/step-08-hashtag-recipe.md`.** Every reel row carries its own
  **search keywords** (2-3 phrases the audience really types, placed naturally in the caption,
  the on-screen text and the spoken script) and a **functional set of 3-6 tags** — 1-2 niche,
  2-3 topic, plus the series tag when the reel belongs to a series. Every tag's role must be
  nameable; an off-topic trending tag is out. Stay within the niche's own tag-count norm and
  under the caption spam ceiling. **Never promise reach from tags** — nobody outside
  Instagram's own analytics can measure what a hashtag contributed, so the plan promises
  relevance and consistency only. ·
- **shooting direction — `playbook/step-08-visual-recipe.md`.** Not a table of numbers: the
  row carries **3-5 winning reels from this slot's own slice to WATCH** (links, each with a
  one-line note on what is on screen), the shot type from the delivery and format, and the
  first frame from the hook's visual layer. **The look — lighting, colour, wardrobe, location,
  styling — is the creator's own brand, tagged JUDGMENT, and never cites a competitor.**
  Copying a competitor's look is the most visible form of mimicry there is. The direction
  carries its own receipt: `kind: visual_exemplars`, with `post_urls`, `subject_descriptions`
  (the notes, in the same order) and `count`. It must be filmable inside the slot's effort
  budget. ·
- **expected structure / format** *(tutorial, listicle, story, skit, talking-head, etc.)* ·
- **effort** (light/medium/heavy) · **priority rank** ·
- **data receipt** — the exact lever(s) this reel is built on: source @handle + reel URL (if any) + **n** +
  **median** + **reliability** + provenance tag. A reel with no real tool result behind it is tagged
  **JUDGMENT** and gets no faked receipt. ·
- **Reasoning — three lines, on every slot, or the slot does not ship.**
  `playbook/step-08-reasoning-recipe.md`. This is the row that makes the slot explain itself, in
  plain language the creator can read:
  1. **Receipts** — one short line per claim this slot actually makes (the topic, the hook, the
     beats, the ask, the sound, the shooting direction, the time). A slot tagged
     `provenance: data_driven` must carry the matching receipts; a `judgment` slot must carry the
     tag. Nothing unlabelled.
  2. **Expected outcome — a base rate, never a forecast.** Only two shapes are allowed: *"posts
     of this class ran a median of X views / Y comments across N accounts — your own results will
     differ, and they are what tunes next month's plan"*, or *"Testing — no market evidence, this
     one is a deliberate experiment"*. **A predicted number for THIS post, a chance of going
     viral, or an outcome we cannot see (conversions, sales, what people replied) is banned.**
  3. **Goal served** — one line mapping the slot's `funnel_role` to the plan's goal: reach →
     **Reach**, nurture → **Engagement**, activation → **Leads**. An activation slot also names
     the ONE conversion action; an anchor-week slot cites its declared exception.

---

## PART D — EXECUTION & MEASUREMENT (the *how*)

### D1. Cadence, batching & priority
- A realistic cadence (default to the LOWER end of what the creator can sustain).
- A batching SOP (one film/build day → several reels), light-effort reels grouped so a bad week still ships.
- Priority ranks so the plan degrades gracefully, not collapses.

### D2. Distribution
- Posting time — a structured, REQUIRED field, not prose (rigor rule §K, FRFRMU-1539):
  `distribution.posting_time: {status: "checked_signal" | "checked_no_signal" | "not_checked",
  tool: "get_posting_time_performance", scope, timezone, quoted: [{name, count, reliability,
  median_views}], caveat}`. `checked_signal` is a SOFT tie-breaker only — never a hard rule.
  `timezone` is whatever the tool's own `timezone` field reports (the workspace owner's own zone,
  FRFRMU-922) — UTC only when none is set, and say so when it is. Weekday gaps are often flat,
  so don't oversell a small one.
- Audio — the month's audio stance, per `playbook/step-08-audio-recipe.md`. We CAN now read which
  sounds are **rising among the accounts we track** (never "trending on Instagram") and which
  sounds this workspace's own analysed reels keep reusing. Quote the coverage figure with every
  count: the scraper often reports no sound at all, so a sound's absence proves nothing. The
  exact track is confirmed in the creator's own Instagram panel at posting time — which is also
  what keeps the pick licensed for a professional account.

### D3. Captions / hashtags / on-platform SEO
- The caption + hashtag + searchable-text framework (keyword in name/first line; on-screen text carries
  silent viewers).
- **This section is the FRAMEWORK, not the captions themselves.** Each reel's actual caption is
  written per row in C1, using `playbook/step-08-caption-recipe.md`. Keep the two apart: a
  framework here with no caption on any row is the gap this recipe closes. The same split
  applies to tags: the per-reel keywords and tag set are written per row in C1 using
  `playbook/step-08-hashtag-recipe.md`, not here.
- **No reach promise, ever.** This section may describe what the tags and keywords are FOR
  (relevance, consistency, being findable in search). It must never say or imply that a tag
  set will get the creator reach or discovery — that is unmeasurable by anyone outside
  Instagram, and claiming it is the same failure as a guaranteed-result claim.

### D4. Community / engagement routine  *(how a cold account gets its first eyeballs)*
- A named **Dream 100** (the specific accounts this plan modelled) + a daily routine (minutes/day, how many
  accounts, genuine engagement, never spam-dropping your own link). *(See `rules/traffic.md`.)*

### D5. KPIs, weekly ritual & the learning loop
- Stage-appropriate KPIs (e.g. saves-per-1k, watch-time %, shares-per-1k, hour-1 velocity — not raw views
  for a cold account).
- A weekly measurement ritual + **kill/scale rules** that feed the NEXT period's plan (this closes the loop).

### D6. Honest benchmarks
- Realistic expected numbers for THIS account's stage vs the competitor "aspirational ceiling", clearly
  labelled. Never present competitor medians as what to expect.

### D7. What these words mean (FRFRMU-1551) — a glossary, built generic
- **One line per DISTINCT `format`/`structure` value actually used in `reels[]` this run** — never
  a fixed list. A creator without a video background cannot act on a label they cannot look up.
- **The plain-English text is `get_taxonomy_definitions`' own definition, quoted verbatim** — the
  agent never paraphrases or invents one. A value the taxonomy does not define yet is written in
  plain words and labelled "our description," never presented as sourced.
- **One real example link per term** — the first of that reel's `visual.watch_these` links whose
  label matches the term (`playbook/step-08-visual-recipe.md` V.2 already produces these). Seeing
  30 seconds of a real montage teaches more than a definition alone.
- **Never hardcode a term to one niche's vocabulary** — the glossary reads whatever this plan
  actually used, so it works the same for a gym plan and a SaaS demo plan.
- Saved as plan-level `glossary: [{term, field, plain, source, example_url?}]` — `plan_validator`'s
  `glossary_covers_terms` check warns when a used term has no entry.

---

## PART E — TRUST

### E1. Receipts summary  *(the QA + conversion surface — mechanical, never narrated)*
- **Coverage:** "built from N of your M analysed reels".
- **Tools that actually ran** this session (name them).
- **Provenance split as COUNTS:** X DATA-DRIVEN / Y DATA-INFERRED / Z JUDGMENT — the honest admission IS the point.
- **Competitor accounts** the plan drew from (@handles).
- **ONE action** to start with (FRFRMU-1548): "review the whole plan and approve it, then say
  'write the copy for this plan'" — never "start filming reel #1", since a beats-only plan has no
  words yet to film.
- **Intake confidence:** how deep this plan's inputs actually were — "X of Y key fields confirmed by
  you, Z derived by us and accepted, W missing." If the completeness score is below the floor (Step
  11 flags this), say so honestly: "this plan leans more on judgment than usual because the intake
  was thin."

### E2. Critic & Rules-Gate verdict
- The result of the mandatory loop (see PLAYBOOK Step 11 + the Rules Gate): the verdict, and a short list of
  what the critic/gate changed. Only the passed version ships.
- **This prose is the summary, not the record.** The machine-readable per-gate result (one entry per
  gate with pass / fail / not-applicable, what was checked, and what changed) goes to
  `submit_content_plan` as `rules_gate` — see PLAYBOOK Step 11. A verdict with no record behind it
  cannot be checked by anyone later. (G650)

### E3. Decision log — HOW this plan was reached (for QA)  *(in the final document AND written back)*
A plain-language, step-by-step trail of the big decisions and **why**, so a reviewer (or the creator) can
check the reasoning — this is the QA surface. Each line cites the tool result it came from, or is tagged
JUDGMENT. Include:
- **Business read** (Step 1): who the plan is for, the goal chosen **and why**, the positioning
  captured/derived, any profile mismatch found + fixed.
- **Self-vs-niche gap** (Step 1.6): what already works for THEM, the opportunity gaps vs the niche, what
  under-performs → so the strategy closes the gap.
- **What was analysed** (Step 3): which role→tag subsets (Step 3, G328) + why; which **hook templates went
  viral** and the reason each was chosen.
- **Strategy decisions** (Step 7): the funnel mix, patterns matched, patterns to test, and pillar split —
  each with its one-line reason.
- **Per-reel reason:** for each calendar reel, the one lever/gap it serves (mirrors its data receipt).
- **Critic/gate changes** (Step 11): what the review changed before shipping.

**Persist it for QA:** include this `decision_log` in the structured `plan` saved via `submit_content_plan`
(Step 12) — so it is written back to the account and verifiable later — and render it in the dashboard's
trust section. Plain language throughout (no raw tag names / §-labels in the creator-facing copy).

### E4. Review disclaimer  *(FRFRMU-1525 — standing notice, never a per-claim block)*
Print `plan_disclaimer.text` from `get_creator_brief`'s response verbatim, once, at the end of every
plan. This is a plain notice — "these are suggestions, please review them before you publish" — never a
warning about a specific claim, and it never stops you finishing or delivering the plan. Every account
starts on the same default wording and can edit + approve its own version; either way, the field is
always present, so there is nothing to fall back to yourself.
