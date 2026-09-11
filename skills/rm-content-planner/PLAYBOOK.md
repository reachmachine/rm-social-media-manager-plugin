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

These ten rules (**§A–§J**, in full in `playbook/rigor-rules.md`) are **live in every step** —
not an appendix, not a final stage. They are the difference between a plan that is data-DRIVEN
and one that only *looks* data-informed. Each step below names the §s it must obey.

- **§A Reel Bet** — every reel = Proven Pattern × First-Party Topic × Audience Tension (never novel × novel).
- **§B Confidence** — read the **median, not the mean**; label High / Medium / "a bet"; below n ≈ 5 it can never be data-driven.
- **§C Cross-tabs** — pick winning **combinations** (`group_by`), not single levers read in isolation.
- **§D Goal-conditioned** — rank levers/topics by the metric that matches the goal (reach vs leads vs authority).
- **§E Niche** — the data's topics are the candidate set; weight by median, not competitor share; mine the creator's OWN comments/DMs too.
- **§F Audience** — model hook/structure/CTA/topic for the creator's ONE target segment, with the sample-size guard.
- **§G Honest labels** — show the real data niche AND the reframed idea; never dress one up as the other.
- **§H Experiment** — every reel gets a hypothesis + a **stage-appropriate** kill/scale rule.
- **§I Provenance** — tag every choice DATA-DRIVEN / DATA-INFERRED / JUDGMENT by the operational rule; the `validate_content_plan` code check (G118) now enforces the countable half.
- **§J Data first, judgment last** — thin slice → analyse more relevant reels (own, then community/niche) → only then judgment; a judgment reel still names what grounds it.

**When the data is thin or degraded**, do not fake confidence and
do **NOT** drop straight to judgment — §J in `playbook/rigor-rules.md`
gives the order and what an honest thin-data plan must say.

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
7. **Capture** — save to the Content Calendar on the creator's consent, always after a
   fresh `validate_content_plan` dry-run applying every `fix` (FRFRMU-1029). *(Step 12)*

## Progress checkpoints — after every step, not just at the end

**Record progress as you go, so closing the session mid-plan never loses it.** After you finish
each numbered step above (1 through 11 — Step 12's save already persists the whole plan), call
`update_creator_brief` with one field:

- key: `planning_progress`
- value: `{"last_completed_step": <int>, "step_name": "<short label>", "summary": "<1-2 sentences>", "plan_month": "<YYYY-MM, once known>", "status": "in_progress", "updated_at": "<ISO timestamp>"}`
- source: `"derived"`

**Three OPTIONAL fields resume a sitting per QUESTION, not just per step (FRFRMU-1051):**
`section`, `question_index`, `question_statuses` (a list of `{question_id, status, reason?}`,
`status` one of `playbook/asking-rules.md` §6's six words). Omit them and this checkpoint works
exactly as it always has — see `asking-rules.md` for the full contract.

**`status` is one of `"in_progress"`, `"delivered"` or `"abandoned"` — never left unset (FRFRMU-981).**
Every checkpoint 1–11 above writes `"in_progress"`. A plan that stops moving writes its own status
instead: Step 12 writes `"delivered"` when the creator declines the save (`playbook/step-12-capture.md`)
or clears the field entirely on a successful save (`playbook/step-12-after-the-save.md`); Step 1's
resume bullet below writes `"abandoned"` when the creator picks "something else" over an old
unfinished plan. This is what lets a later session tell a live, resumable plan apart from one that
already ended.

This is a full overwrite of the `planning_progress` key each time (matches how `update_creator_brief`
already treats existing keys — updated, not merged field-by-field), so it always reflects the
LATEST completed step, not a growing log. Keep the `summary` short — it exists to remind a human,
not to re-derive the plan from.

Skip this on a **headless** run (`runner.py`) — nobody is coming back to resume a run nobody is
watching; do not spend the extra tool call there. See Step 1's resume check below for the human-run
side of this.

**This field does not live forever.** A finished plan has no "unfinished session" left to resume, so
`planning_progress` must not still say `"in_progress"` once the plan is done — see Step 12 for how it
is cleared or marked `"delivered"`, and Step 1's resume bullet below for the defensive read that
protects against a record that, for any reason, was never cleared.

## Review gates — the two places the method STOPS for the human (FRFRMU-879)

**The agent is not a dictator.** Every output here is a judgement, and the human must get the
chance to catch a wrong one while catching it is cheap. But a pause on every micro-step makes
the user stop reading — so the method stops at exactly TWO gates, where a wrong answer is
expensive, and flows through the cheap mechanical steps. Each gate is marked `🛑 REVIEW GATE`
in its step file; the guard test (`backend/tests/unit/test_smm_review_gates.py`) pins both.

| Gate | Where | Why it earns a pause | Still needed? |
|---|---|---|---|
| **A — the strategy read** | end of Step 7 (`playbook/step-07-strategy.md`) | Part A is the judgement every reel then executes | re-check after FRFRMU-880 |
| **B — the delivered plan** | Step 12.0 (`playbook/step-12-capture.md`) | the final result the founder's review is about; save-consent is NOT a review | re-check after FRFRMU-880 |

**How a gate works — the same three rules at both:** (1) present the result WITH the
reasoning, then **end your turn** — never continue into the next step in the same message;
(2) **silence is not approval** — only an affirmative go-ahead passes the gate, and with no
reply the run simply stays stopped; (3) a correction revises the named part and its
dependents — it never starts the run over.

The audience call is gated twice on purpose: Step 1's derive-then-CONFIRM at intake, and
again inside Gate A (Step 7.0a's data-vs-stated-audience check). Spend and destructive tools
keep their own confirm-before-spend gates (ADR-016) — those are separate from, and in
addition to, these two. **Headless runs (`runner.py`) skip Gate A** — nobody is there to
answer — and never reach Gate B (Step 12 is unreachable headless, G208).

---


## Where each step lives — load ONE file, not the whole method

The method is split into small files in the `playbook/` folder next to this one. **Load only the
file for the step you are on.** Reading the whole method costs the creator a large slice of their
own Claude usage before a single number comes back, and that text is re-sent on every later turn.

| Step | File to load | What it covers |
|---|---|---|
| 1 | `playbook/step-01-intake.md` | The intake conversation |
| 1 (rest) | `playbook/step-01-intake-fields.md` | The fields the intake must end up with |
| 1 (rest, part 2) | `playbook/step-01-intake-fields-2.md` | Rest of the intake fields |
| 1.7 | `playbook/step-01-7-website-dossier.md` | Crawl the customer's website against a checklist, and store it (G234, FRFRMU-1149) |
| 1.4 | `playbook/step-01-4-persona-questions.md` | Attractive Character |
| 1.5 | `playbook/step-01-1-market.md` | Validate the market/niche (p01) |
| 1.6a | `playbook/step-01-2-avatar.md` | Define the dream-customer avatar (p02) |
| 1.6b | `playbook/step-01-3-congregations.md` | Map where the dream customer gathers (p03) |
| 1.6 | `playbook/step-01-6-self-account.md` | The creator's own account is the strongest signal |
| 2 | `playbook/step-02-benchmarks.md` | Find benchmark accounts |
| 3 | `playbook/step-03-mcp.md` | Use the RM MCP correctly |
| 3 (sufficiency) | `playbook/step-03-mcp-sufficiency.md` | Rule 2a |
| 3 (requested vs delivered) | `playbook/step-03-requested-vs-delivered.md` | Rule 6h |
| 3 (recipes) | `playbook/step-03-data-recipes.md` | Rule 5b |
| 3 (rest) | `playbook/step-03-mcp-spend-and-progress.md` | Rules 6-8 |
| 3.5 | `playbook/step-03-5-prospect-research.md` | Run prospect research (p04 |
| 3.6 | `playbook/step-03-6-magic-desk.md` | The magic desk interview (p05 |
| 2.8 | `playbook/step-02-8-dossier.md` | Competitor dossier (p07) — two passes bracketing Step 3's analysis |
| 3.7 | `playbook/step-03-7-big-domino.md` | The Big Domino (p08) |
| 3.8 | `playbook/step-03-8-why-people-buy.md` | Why-people-buy worksheet (p06) — 11 questions, gated on the offer |
| 3.9 | `playbook/step-03-9-origin-story.md` | Origin/epiphany story (p10) — 8 beats written once, cut for length |
| 3.10 | `playbook/step-03-10-false-beliefs-map.md` | False-beliefs map (p11) — >=10 rows, V/I/E, core three |
| 3.11 | `playbook/step-03-11-proof-bank.md` | Proof bank (p29) — ladder, permission, honest attempts |
| 4 | `playbook/step-04-stage.md` | Translate for the account's stage |
| 4.5 | `playbook/step-04-5-persona-assembly.md` | Attractive Character |
| 4.6 | `playbook/step-04-6-false-beliefs-form.md` | False-beliefs form join (p11) — myth-busting lift + structures |
| 4.7 | `playbook/step-04-7-movement.md` | Build the Movement (p12) — cause/identity/enemy, staged by proof |
| 5 | `playbook/step-05-differentiate.md` | Differentiate, never mimic |
| 6 | `playbook/step-06-retention.md` | Retention, not just hooks |
| 7 | `playbook/step-07-strategy.md` | Build the strategy (Part A) before the calendar |
| 7 (offer) | `playbook/step-07-1-offer-position.md` | Offer layer |
| 7 (offer stack) | `playbook/step-07-2-offer-stack.md` | Offer layer |
| 7 (ask campaign) | `playbook/step-07-3-ask-campaign.md` | Offer layer |
| 8 | `playbook/step-08-deliverable.md` | What the deliverable must contain — loads `TEMPLATE.md` |
| 8 (join) | `playbook/step-08-join-recipe.md` | Idea from the cards, pattern from the tool (p02-p29) |
| 8 (hook) | `playbook/step-08-hook-recipe.md` | How ONE slot's hook gets chosen |
| 8 (outline) | `playbook/step-08-outline-recipe.md` | How ONE slot's script row is built |
| 8 (CTA) | `playbook/step-08-cta-recipe.md` | How ONE slot's ask is chosen |
| 8 (caption) | `playbook/step-08-caption-recipe.md` | How ONE slot's caption is written |
| 8 (discovery) | `playbook/step-08-hashtag-recipe.md` | How ONE slot's keywords + 3-6 tag set are built |
| 8 (audio) | `playbook/step-08-audio-recipe.md` | How ONE slot's sound is chosen |
| 8 (visual) | `playbook/step-08-visual-recipe.md` | How ONE slot's shooting direction |
| 8 (reasoning) | `playbook/step-08-reasoning-recipe.md` | How ONE slot explains itself |
| 9 | `playbook/step-09-guardrails.md` | Guardrails (never do) |
| 10 | `playbook/step-10-checklist.md` | Run checklist |
| 11 | `playbook/step-11-rules-gate-critic.md` | Rules Gate + Critic loop — loads `RULES_GATE.md` and `rules/` |
| 12 | `playbook/step-12-capture.md` | Capture — save the plan to the creator's Content Calendar |
| 12.5 | `playbook/step-12-blockers-remain.md` | What to do when blockers are still open at save time |
| 12 (after the save) | `playbook/step-12-after-the-save.md` | The two write-backs once the plan is stored |
| — | `playbook/rigor-rules.md` | The Rigor Rules §A-§J in full |
| — | `playbook/rigor-rules.md` | The Rigor Rules §A-§I in full |
| — | `playbook/asking-rules.md` | The asking contract — how EVERY question the plugin asks is asked (FRFRMU-1051) |

**A "Step N" reference inside any step file means that step's file in the table above.**

**`TEMPLATE.md`, `RULES_GATE.md` and `rules/` are NOT loaded up front.** Each one loads at the step
that uses it — `TEMPLATE.md` at Step 8, `RULES_GATE.md` and `rules/` at Step 11. The step file says
so at the top.
