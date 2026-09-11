> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

> **Load this at Step 7**, right after `step-07-1-offer-position.md`. This file grows one
> lettered part per offer-layer ticket (FRFRMU-1078) — **A** the value stack, **B** the
> profitable promise, **limits** scarcity/urgency, **C** bonuses, **D** the guarantee, **E**
> MAGIC names, **F** the one-page offer brief. Each part has its own entry rule; a missing
> upstream key means that part is skipped in one line, never invented.

**Consent, asked once per offer (FRFRMU-1148).** Before Part A, ask: *"Want me to help
strengthen this offer before we use it anywhere? It's about 4 questions, ten minutes, and you
decide every number. Or we can leave it as it is."* Record the answer with
`update_creator_brief` as `offer_improve_consent: {answer: yes|no|later, at: <iso>, offer_ref:
<what>}` — a resumed session never re-asks. `no` / `later` → Parts A–F skipped in one line,
nothing else changes.

## Part A — The value-stack offer (p15)

**Entry rule: only when `value_ladder` exists AND `price_signed: {by_user: true}` is on
record (Step 7.0c).** Otherwise skip this whole part in one line.

Turn the offer into: the result they want (dream outcome), every problem on the way, one
piece that solves each, each piece with an honest value, so the total obviously dwarfs the
price. **Never re-ask what is already on record** — pull from p04/p05/p06/p11/p02 first.
**Ask per `asking-rules.md`** — this part has 4 named questions (Q1-Q4 below), asked in full,
never capped short.

1. **Dream outcome (agent drafts from existing intake material, user confirms — Q1):**
   *result + timeframe*, never a guaranteed number. ❌ "AI automation setup" ✅ "Your quotes go
   out the same day without you touching them — within 30 days."
2. **Problem list (agent-fills, target 30+):** seed from what's already on record, then run
   the **4 lenses** over the customer's journey (before/during/after): won't be worth it /
   won't work for me / too hard / too slow. Every problem cites its source, or is tagged
   `agent`.
3. **Flip each problem to a "how to…"** and brainstorm delivery: DIY / DWY / DFY × medium ×
   speed.
4. **Cost to deliver (ask-user — Q2):** *"For each piece, roughly what does it cost you in
   hours or money to deliver?"* Only the business knows.
5. **Trim (agent proposes, user decides — Q3):** cut high-cost/low-value first, then
   low/low; keep low-cost/high-value and high/high. At least a few visible cuts — an untouched
   brainstorm is not an offer.
6. **Values with reasons (agent drafts, user approves — Q4):** every kept item's value is
   `time saved × their rate`, `cost replaced`, or `result`, never invented. ❌ a round number
   with no basis ✅ a figure that shows its working, e.g. "replaces about ten hours a month of
   admin at the rate they already pay." Three pieces map to the
   three doubts (vehicle / internal / external, from the belief map when it exists). Name the
   **fast win** — what the customer gets in the first days.
7. **10× check:** `stack_total / price ≥ 10`, or the plan says honestly "stack is Nx, add
   tools" — never inflate a value to hit the number.
8. **Read back, save** to brief key `offer_stack` (rung, dream outcome, problems, deliverables
   with values+reasons, fast win, stack total, multiple).

**Content translation (conditional on `offer_stack` and the rung rule from Step 7.0b):**
- **Fast-win reel** — "here's the full result in 90 seconds" (`demo`/`proof` beats). Pattern
  from the tool: `get_theme_lift` (dimension `angle`) for `proof`/`demo`/`hack`, with n.
- **Running-stack reel** — the pieces listed, each named with its value, price last —
  **BOF only, warm audience only, fulfillable rung only. Never on a cold account's first
  plan.** Uses the `list_item` beat.

**Guardrails:** values honest, never theater — an item that can't be justified is re-valued
or cut. Tools beat trainings on the stack. A DFY item needs a capacity check with the creator
before it appears in any reel. The plugin writes the stack doc and the two reel types — never
a sales page, checkout or stack slide.

## Part B — The profitable promise (p21)

**Two versions.** *Full:* right after the dream outcome above, only when `offer_stack`
exists. *Light:* **any account**, no offer needed — so the bio and the recurring/pinned hook
carry one promise. This is the only part of the offer layer that also serves reach-goal
accounts.

One sentence, four labelled parts, in the audience's OWN words — mined from what is already
on record (their quotes, DMs, phrases), never re-asked:

- **Hurdle** — their action verb (❌ "optimise your operations" ✅ "stop doing quotes at
  night").
- **Prize** — their result words, not the writer's.
- **Timing** — the SOFT form, "in as little as…" — never a hard "in 7 days you will".
- **Eliminator** — "even if… / without…" — and it must be TRUE. **Ask-user (Q1):** *"Does
  what you deliver really work for someone who [eliminator]? If not, what's the true
  version?"* A smaller true promise beats a bigger false one — narrow it, never inflate it.

Draft 5+ candidates with all four parts labelled and sourced (`source_quote_id` on hurdle and
prize — an uncited verb is a fail). Run the **never-blame pass**: any wording that makes the
shortfall the customer's fault ("if you'd just…") is rewritten — it is the old approach's
fault, never theirs. **Creator picks the promise (Q2).** Pattern from the tool:
`get_hooks_library` / `hook_promise_type` orders the candidates by what lifts in this niche,
with n — the words are the audience's, the form is the data's.

**Deploy — one promise, everywhere:** save to brief key `promise.chosen`. The bio line
derives from it when `promise.chosen` exists; the recurring/pinned hook may use it; the
offer brief's promise field (Part F) points at it. Two competing promises anywhere is a
KPI-review flag, never silently tolerated.

**Guardrail:** timing + prize never becomes a guaranteed result — income figures never, Gate
1 applies to the promise exactly as it applies to every other reel. No `promise` key →
today's bio/hook path is unchanged.

## Part limits — Scarcity & urgency (p16)

**Entry rule: only when `offer_stack` exists.** Real limits (quantity) and real deadlines
(time) only — a fake cap or countdown is a hard Gate 1 compliance fail; this part makes it
countable. **Ask per `asking-rules.md`** — this part has 2 named questions (Q1-Q2 below), asked
in full, never capped short.

1. **Real capacity (ask-user — Q1):** *"How many new clients can you actually take on this
   month without dropping quality — and why that number?"* ❌ "as many as possible" ✅ "3 —
   each build takes me a week." An evergreen product with no natural limit gets `bonus` or
   `cohort` scarcity — never an invented supply cap. Save as `scarcity.cap: {n, reason_capacity,
   by_user: true, first_run_guess}`.
2. **Cap below sellable (a rule the agent states, the creator decides — Q2):** didn't sell out
   last cycle → lower the cap next time, or examine the offer — **never fake a sell-out.**
3. **Urgency type + real date (agent drafts from `upcoming_moments`, user approves):** every
   urgency line binds to a `plan.anchors` entry (Step 12, G707) — no moment on record → no
   deadline in any reel; "join the next group when it opens" is the honest fallback.
4. **Fullness / sell-out plan (agent drafts):** a fullness update ("14 of 20 taken") is a
   Step 12 prerequisite that REQUIRES a dated `live_count` supplied by the creator before
   publishing — the plugin never estimates a count.
5. **Close sequence (agent drafts, advisory):** a final-day reel tied to the anchor, plus a
   note for stories/broadcast in the last hours — outside the reel calendar, said plainly.

**Countable rule:** any hook/caption/CTA carrying a limit or deadline phrase (spots, seats,
only N, closes, ends, deadline, last chance, sold out) must cite `scarcity_ref` (a recorded
cap) or `moment_tie` (a declared anchor) — same Gate 1 checkbox, now mechanical. A sell-out
claim needs a confirmed `live_count ≥ cap.n`.

## Part C — The bonus stack (p17)

**Entry rule: only when `offer_stack` exists.** Sits inside "Your offer" as part C, "the
extras" — not its own sitting. 🔴 **Never discount the core offer** — discounting teaches the
customer your price is negotiable; widen the value gap by ADDING named, priced bonuses
instead. Seven moves, each a senior-SMM habit the agent copies:

1. **Start from what exists, not ideas:** *"What do you already have — templates,
   checklists, recordings, prompt packs, a Loom you made for a client?"* Never let the
   creator build new product to decorate an offer. Nothing exists → distil a checklist FROM
   the core, note the build cost.
2. **Match each extra to a worry, not a feature:** each bonus needs `objection_ref` — the
   belief-map row id when the belief map (1045) exists, or **`{text: "<the doubt in the
   creator's words>", source: "creator", belief_id: null}`** when it doesn't yet, or the
   creator names a doubt not in the map. **Never drop the creator's answer.** An unmapped
   bonus (no objection_ref at all) is cut — that's stack-padding.
3. **Name it by what it does for them** (2 drafted per bonus, creator picks). ❌ "Bonus 2:
   Prompt Library" ✅ "The 20-Minute Handover Kit — your agent starts working the day you sign."
4. **Honest number with the reason** (same rule as Part A): *"Replaces ~10 hours of setup at
   your rate — that's the value, not a made-up $997."*
5. **Ask for proof, accept "none yet":** *"Have you seen this work — a client, a stat,
   yourself?"* None yet → the bonus stays, `proof: null`, its reel line makes no result claim.
6. **Check the shape:** tools/checklists/templates ≥ trainings; `bonus_total > core_value` —
   if not, add a tool, never touch the price.
7. **Rehearse the discount moment:** *"When someone says 'can you do it cheaper?' you say:
   'I can't move the price, but I can add X.'"* Written into the DM/CTA copy the plan drafts.

**Content translation:** ONE reel — the bonus reveal, one extra per beat, each answering a
"but what about…" objection (`list_item` + `objection` beats). BOF, warm audience, fulfillable
rung only. Never on a cold account's first plan.

## Part D — The guarantee (p18)

**Entry rule: only when `offer_stack` exists.** Risk is usually the #1 objection — reverse it
on purpose, chosen by refund MATH, never by nerves, and worded as a promise about the PROCESS
or the REFUND — 🔴 **never an income/outcome claim** (ad-account ban territory). Seven moves,
creator decides each:

1. **Type from economics (agent recommends, one-line reason):** expensive-to-deliver / high-ticket / done-for-you →
   `conditional` ("do the steps, or we keep helping free"); low-cost digital → `unconditional`
   trial; consumable/easily copied → `anti` (owned openly); performance deals → `implied`.
2. **Fill the formula on a DELIVERABLE:** *"If you don't get [X — something you DELIVER] within
   [Y], we [Z — refund / extend / work free]."* ❌ "If you don't double your leads in 30 days,
   money back" (outcome) ✅ "If your first workflow isn't live in 14 days, I keep building free
   until it is." X must reference a stack deliverable (Part A) that actually exists.
3. **Refund math (agent-fills, ask-user for the inputs):** *"Roughly how many of the people who
   ask end up buying today? And how many ask for their money back?"* No history → a labelled
   first-run assumption table, never a decision with no numbers.
4. **Name (agent drafts 3, creator picks):** the vividness test — would a prospect repeat it to
   a friend? ❌ "30-day money-back guarantee" ✅ "The Live-in-14 Promise".
5. **Stack decision (agent proposes, creator decides):** e.g. unconditional 30-day + conditional
   90-day on top.
6. **Regulated screen:** run the intake constraints field (health/finance/legal) over the
   wording — a regulated niche gets the process-only shape, or `none`.
7. **Sign:** *"This is your money on the line — do you accept this promise as written?"* →
   `signed: {by_user: true, date}`. **The agent never activates a guarantee unsigned.**

**Countable rule — this one may go `hard` first (ad-account safety, sooner than the other
foundation checks):** any hook/caption/CTA carrying "guarantee", "money back", "refund" or "or
we" must reference a `signed` guarantee whose formula's X is a deliverable, not an outcome
noun (leads, sales, revenue, followers, weight, income…). "Double your leads or money back"
fails even though "money back" alone is fine. Unsigned → no guarantee wording anywhere.

## Part E — Name it, MAGIC (p19)

**Entry rule: only when `offer_stack` exists**, for the offer/bonus/guarantee names. **A
lighter version runs for every plan's recurring series (Step 7.7)** — see below.

Naming is the wrapping paper: **M**agnetic reason, **A**vatar, **G**oal, **I**nterval,
**C**ontainer — 3-5 labelled parts per name.

1. **Gather parts already on record** — avatar (Part A/B), dream outcome, real duration (the
   stack's delivery), container from the vehicle (DWY → Sprint/Accelerator, DFY →
   Build/Service, DIY → Challenge/Blueprint). No new input questions.
2. **Write 5-8 candidates**, parts labelled ("… — A + I + G + C").
3. **Three silent screens before showing:** the **repel test** (would the WRONG buyer skip
   it?), **Goal-slot compliance** (outcome words allowed — "hands-off quotes"; a guaranteed-
   income/result number never — "Double Your Profit", "+₹1L"; duration + result number
   together never), **interval honesty** (the I part must equal the real duration). Failing
   candidates are shown crossed out WITH the reason, so the creator learns the rule.
4. **Creator picks the offer name; same pass for each bonus and the guarantee** — save to
   `offer_stack.names.{offer, bonuses, guarantee}`, each `{chosen: {text, components[],
   compliance_pass, interval_honest}}`.
5. **Refresh order, at the monthly review:** a response drop on a named offer → propose
   changes in fixed order only — creative → copy → name → interval → enhancer → offer LAST —
   each logged in `refresh_log`. A name that IS monetizing is never redesigned for novelty;
   rotate 2-3 winners instead.

**Series names — every plan, Step 7.7, lightweight (wired in `step-07-strategy.md`):** data
still picks WHICH pattern becomes a series; the agent shapes the NAME with Avatar + Goal (+
Container) — *"Owner-Operator Tuesdays — one task an agent takes off your plate"* beats
"Monday Tips". A legacy series with no `name_components` gets ONE friendly suggestion, never a
blocker — declining is recorded (`magic_declined_at`) so it's never asked again.

## Part F — The one-page offer brief (p20)

**Entry rule: only when `offer_stack` exists.** The LAST part of "Your offer" — after names
(Part E). One page every sales reel, caption and DM script reads FROM — never its own
component keys directly (the fork risk this part exists to close). **Ask per
`asking-rules.md`** — this part has 2 named questions (Q1-Q2 below), asked in full, never
capped short.

1. **Pull, don't ask:** rung (7.0b), price + category-of-one claim (7.0c), stack (Part A),
   limits (Part limits), bonuses (Part C), guarantee (Part D), names (Part E). Anything
   missing → listed in `gaps[]`, `status: partial` — **never a placeholder.**
2. **Money model (ask-user — Q1):** *"How do people pay — upfront, split, deposit,
   subscription? Any trial? What are the terms?"* Their legal commitment; recorded, **never
   drafted as T&Cs.**
3. **Rerun the comparison test** on the ASSEMBLED offer against the dossier: nearest
   comparable → `distinct` or `commodity` (commodity → 7.0c's sharpen path, never a price cut).
4. **Build-order check:** price signed ≤ stack updated ≤ enhancer dates — out of order is
   flagged, never blocked.
5. **Commitment (ask-user — Q2):** *"Will you ride this one offer until [date], and change it
   only if the data says so?"* → `commitment: {ride_until, review_date, by_user}`. A second
   offer later needs an explicit recorded decision against this line.
6. **Render the one page** (`rendered_md`, ≤1 page): what / for whom / result / price / what's
   included / extras / promise / how to pay / why nothing compares / what's missing. Read
   back, creator confirms → save `grand_slam_offer`.

**The single-source rule:** activation reels, stack reels, bonus reveals, guarantee lines,
CTA copy and the DM script all read from `grand_slam_offer` — never a component key directly.
Section E (7.0b) states gaps in plain words ("your offer page has no guarantee yet — sales
reels won't mention one until it's signed").

**Countable rule:** an offer stack with no assembled brief gets a nudge; a brief can never
claim `status: complete` while a component it lists (e.g. the guarantee) is still missing.
