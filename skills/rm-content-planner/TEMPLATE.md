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
- **4-layer hook** — **spoken** line · **on-screen text** line · **visual** cue · **sound** cue.
  All four are separate fields (`hook.spoken`, `hook.on_screen`, `hook.visual`, `hook.sound`) — the
  validator (G118) blocks the WHOLE reel if any one of the four is missing. **`sound` must never be
  left blank, even though RM has no trending-audio data (see D2).** When you don't have a specific
  sound to name, write an honest judgement call instead of inventing one — e.g. *"no trending-audio
  data — using a spoken-word open"* or *"layer the platform's own trending audio here (judgment
  call, pick at posting time)"*. A stated judgement is allowed; a made-up claim about a specific
  song/sound is not (same honesty rule as everywhere else in this template). ·
- **retention line** — the open loop (in the hook) → mid re-hook (~40%) → loop-back ending that earns replays ·
- **CTA** — stage-appropriate (reply-bait when reach/plumbing is thin; recommend keyword-DM only once
  there's real reach to convert — but it's allowed earlier, with an explicit "few replies at this
  size" caveat, once the automation is confirmed built AND tested; missing/untested plumbing is a
  hard no regardless of stage) ·
- **expected structure / format** *(tutorial, listicle, story, skit, talking-head, etc.)* ·
- **effort** (light/medium/heavy) · **priority rank** ·
- **data receipt** — the exact lever(s) this reel is built on: source @handle + reel URL (if any) + **n** +
  **median** + **reliability** + provenance tag. A reel with no real tool result behind it is tagged
  **JUDGMENT** and gets no faked receipt.

---

## PART D — EXECUTION & MEASUREMENT (the *how*)

### D1. Cadence, batching & priority
- A realistic cadence (default to the LOWER end of what the creator can sustain).
- A batching SOP (one film/build day → several reels), light-effort reels grouped so a bad week still ships.
- Priority ranks so the plan degrades gracefully, not collapses.

### D2. Distribution
- Posting time — a SOFT tie-breaker only, with the honest caveat (data is UTC, not the audience's timezone;
  weekday gaps are often flat). Trending audio — from the platform's own panel (judgment; usually not in data).

### D3. Captions / hashtags / on-platform SEO
- The caption + hashtag + searchable-text framework (keyword in name/first line; on-screen text carries
  silent viewers).

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

---

## PART E — TRUST

### E1. Receipts summary  *(the QA + conversion surface — mechanical, never narrated)*
- **Coverage:** "built from N of your M analysed reels".
- **Tools that actually ran** this session (name them).
- **Provenance split as COUNTS:** X DATA-DRIVEN / Y DATA-INFERRED / Z JUDGMENT — the honest admission IS the point.
- **Competitor accounts** the plan drew from (@handles).
- **ONE action** to start with.
- **Intake confidence:** how deep this plan's inputs actually were — "X of Y key fields confirmed by
  you, Z derived by us and accepted, W missing." If the completeness score is below the floor (Step
  11 flags this), say so honestly: "this plan leans more on judgment than usual because the intake
  was thin."

### E2. Critic & Rules-Gate verdict
- The result of the mandatory loop (see PLAYBOOK Step 11 + the Rules Gate): the verdict, and a short list of
  what the critic/gate changed. Only the passed version ships.

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
