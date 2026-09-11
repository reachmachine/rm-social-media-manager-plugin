> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

> **Load this at Step 7**, right after 7.0 confirms the positioning and before 7.1 states the
> funnel mix. This is the advise-only offer layer (epic FRFRMU-1078): the plugin recommends, the
> creator decides and builds. It never writes a funnel, a page, an automation, or takes payment.
>
> **Advisory entry — every goal, reach included (FRFRMU-1148).** Runs whenever Step 1 is
> complete. Covers the p13 inventory and ladder (7.0b steps 1, 4, 5), the missing-rung / bait
> advisory, p14's commoditization and lying tests (7.0c steps 1–3), and Section E items 1, 3, 5,
> 6, 7. Its job for a reach creator: leave with a front-end offer defined and parked, not with
> the topic never raised. For a creator with nothing, the agent proposes ONE bait and ONE
> front-end candidate — the rung, what it is, who it is for, the outcome — with
> `source: proposed`; the creator names the price (p14's rule, unchanged — the agent never sets
> a price). The chosen one is saved as `offer` with `status: proposed` and read back.
>
> **Selling entry — only when goal ∈ {leads, sales}.** Covers everything that puts a paid ask in
> the calendar: Section E items 2 and 4 pointing at a paid rung, the rung-aware conversion action
> CT.1 to `frontend` or above, the fast-win and running-stack reels, and the activation ask
> carrying a guarantee or bonus. For a reach creator, Section E item 2 reads *"This month pushes
> nothing paid — your `[bait]` is the only ask; the front-end is parked until `[trigger]`"*, and
> the activation share follows Recipe A exactly as today.

## Step 7.0b — Map the value ladder (p13)

**Ask per `asking-rules.md`.**

A senior SMM does not redesign the client's business. They map what exists, fix the ENTRY step
(the only step content can sell to a stranger), and refuse to run "buy" content for a step that
doesn't exist. Work these moves in order — **3-4 questions total**, everything else drafted.

**1. Inventory (agent-fills, Phase 1, from the offer field + funnel plumbing).** Place what
exists onto five rungs — `bait` (free), `frontend` (small paid), `middle`, `backend` (premium),
`continuity` (recurring) — each `{name, price, value_delivered, exists, fulfillable_today,
source: user|dossier|proposed}`. Show the picture before saying anything: most creators have
ONE filled rung. Several lead magnets/tripwires exist → they are candidates, not all active;
one becomes THIS month's step (§3 below), the rest are parked.

**2. Top-right (ask-user, Phase 3):** *"If a client said money's no object — do the most for
me — what would that be?"* ❌ "a bigger package" ✅ "I run their whole back-office automation
for 12 months." This sets the direction people climb toward; it is **never** this month's ask.

**3. Continuity (ask-user, Phase 3):** *"What could you honestly bill monthly that people keep
needing?"* No history → write "none yet". A fake subscription is worse than no subscription.
**Placement rule:** continuity is asked only after bonding — never in a cold account's first
plan.

**4. Missing rungs + bait (agent-fills, Phase 4, from `get_cta_library` + the dossier's niche
norms + p06 buying reasons):** propose 1-2 bait candidates, run the **dream-client filter** —
*"would only the dream client want this, or would everyone?"* — against the avatar. A one-offer
creator gets **at least one missing rung named**, with a source. Hand back ONE build
recommendation (usually the missing bait), scheduled as a Step 12 prerequisite.

**5. Ascension triggers (agent-fills):** per rung, the signal of readiness ("asked a pricing
question in DMs" → frontend). At the KPI review the creator pastes what they saw — the plugin
cannot read DMs — and next plan's conversion action may move one rung up if the trigger fired.

**What the senior SMM refuses to do (and this step must too):** run activation reels for a rung
that doesn't exist · pitch the backend to strangers · put a subscription ask in front of a cold
audience · invent a price or a rung · build the funnel itself · promise revenue.

### The IG-fit rule — the ladder never overrides the funnel mix

Recipe A (7.1) sets **how many** sales-oriented slots the month has. The ladder only sets
**which rung** those slots point at, and which free step everything else drives to. A plan
whose BOF share exceeds the Recipe-A-derived mix "because the ladder needs selling" fails.

### Rung-aware conversion action (wires into 7.1)

The ONE conversion action (CT.1) must name a rung that `exists && fulfillable_today`, at the
**lowest fulfillable rung for the account's temperature**: cold → bait only; warm → frontend;
backend only to a warm audience that already bought. A recurring-offer ask may appear only in
`activation` slots after nurture slots exist in the same plan, and never in a cold account's
first plan. `Gate 5` (`gate_5_stage_cta_funnel`) checks this — see `RULES_GATE.md`.

## Step 7.0c — Premium price, category of one (p14)

Runs after the ladder (Step 7.0b), only when `value_ladder` exists. **"Stop being the cheaper
option — be the only option."** No price is ever set, averaged or "suggested" by the agent —
the creator names every price. Work these moves in order:

**1. Commoditization test (agent-fills, from the dossier):** for the frontend/middle rungs,
name the nearest comparable competitor offer + price (public page, cited, dated), or "none
found publicly". Verdict `distinct` or `commodity` — a prospect could reasonably say "same
thing, cheaper there".

**2. The LYING TEST on the offer, only if `commodity`:** *"Could that competitor honestly
describe their offer the way you describe yours?"* If yes, reword the offer's claim — **never
lower the price.** The fix path is always sharpen the category-of-one claim, never a discount.

**3. Anti-averaging guard (a rule, not a question):** dossier prices exist ONLY for the
comparison test above. The agent never proposes a price computed from them (average, median,
"slightly below"). If asked for a number, the agent frames it as a value-gap argument
(what they get vs. what they give), never a competitive number.

**4. The price conversation (ask-user, one question):** *"Does this price feel a bit
uncomfortable to say out loud? A price that doesn't sting usually means the value isn't
being shown yet."* The creator names the price and answers — recorded as `price_signed:
{by_user: true, date, stings}`. The agent never sets a price.

**5. Status framing (agent drafts, user confirms):** one line on how buying reads as
status-raising ("owners who run on agents, not admins") — Gate-1 clean, never an income claim.

**6. Named-method reels (content translation):** the creator's method/framework, shown by
name — the Instagram form of category-of-one. Pattern from the tool: `get_theme_lift`
(dimension `angle`) for `framework`/`proof` angles, with n — if they lift in this niche they
get pillar share; if not, the method is still named, inside the structures the data prefers.

**No price-competition claims — countable, every plan, not gated on this step.** Any hook,
caption or CTA reading "cheaper", "cheapest", "affordable", "discount", "lowest price", "for
less money", "pay less" fails — reword around the value gap, or add a bonus, never a discount.
This rule applies to every plan, whether or not `value_ladder` exists — see `RULES_GATE.md`
Gate 1.

## Section E — "Your offer advice" (required output whenever `value_ladder` exists)

Write this in Part A of the plan, every cycle, in plain language, sourced sentence by sentence
(a number the data didn't produce fails Gate 7):

1. **Your ladder as it stands** — five rungs, filled/missing, every lead magnet/tripwire named,
   premium, continuity or "none yet".
2. **This month pushes ONE thing: `[rung + offer name]` — because `[temperature + data +
   plumbing reason]`.** e.g. *"Your account is cold (4 followers, no DM replies yet) → the free
   20-minute audit. DM-keyword ask allowed — ManyChat tested 3 Sep. Niche data: 62% of
   activation reels use a DM keyword (n=41)."*
3. **What's parked and what unparks it** — per other offer, the ascension trigger that promotes
   it.
4. **How the calendar treats each rung this month** — reach → bait; nurture → proves the small
   step; activation → the one ask; premium → proof-only.
5. **The next 2-3 months, conditionally** — never a promise, always "IF this signal appears".
6. **Which offer steps applied to this month's offer** — a checklist: price claims / stack
   values / limits real / bonus-not-discount / guarantee signed / name — each ✓ or n.a.
7. **What the plugin can't do** — one honest line: no DM/email sequence, no visibility into
   purchases; ascension signals come from the creator.

Section E never states a number the tool data did not produce, and never says a tripwire "will
convert" (Gate 1/7). It never recommends the premium as this month's action for a cold account.
