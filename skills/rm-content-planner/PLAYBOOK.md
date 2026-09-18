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

These eleven rules (**§A–§K**, in full in `playbook/rigor-rules.md`) are **live in every step** —
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
- **§K Claim names its call** — "checked X" names the tool that ran, or the honest sentence is "not checked" (FRFRMU-1539).

**When the data is thin or degraded**, do not fake confidence and
do **NOT** drop straight to judgment — §J in `playbook/rigor-rules.md`
gives the order and what an honest thin-data plan must say.

---

## The method — the step order (the spine)

**The complete, ordered list — every step AND sub-step, in true run order, each one naming
what must already be done first — is the single table under "Where each step lives" below.**
Nothing runs that is not a row there, so you never have to guess at a missing sub-step or
browse the folder to find one. In broad strokes: 1 gathers/validates the business; 2 finds
benchmarks; 3–6 turn data into a plan; 7 builds the strategy before the calendar; 8 delivers
it; 9–11 guard it; **Step 12 — Capture** — saves it, on consent, after a fresh
`validate_content_plan` dry-run applying every `fix` (FRFRMU-1029).

## Progress checkpoints — after every step, not just at the end

**Record progress as you go, so closing the session mid-plan never loses it.** After you finish
each row of the ordered list below — a top-level step OR a sub-step, e.g. `1.6b` counts on its
own, not just `1` — call `update_creator_brief` with one field (skip only the very last row,
Step 12's own save, since that already persists the whole plan):

- key: `planning_progress`
- value: `{"last_completed_step": <step id, e.g. "1", "1.6b", "2.8", "12">, "step_name": "<short label>", "summary": "<1-2 sentences>", "plan_month": "<YYYY-MM, once known>", "status": "in_progress", "updated_at": "<ISO timestamp>"}`
- source: `"derived"`

**`last_completed_step` is a step id, not necessarily an integer** — a top-level `1`…`12` or a
lettered/decimal sub-step like `"1.6b"` (FRFRMU-1311). Full rule and why: the field-shape note
in `playbook/step-12-after-the-save.md`.

**Three OPTIONAL fields resume a sitting per QUESTION, not just per step (FRFRMU-1051):**
`section`, `question_index`, `question_statuses` (a list of `{question_id, status, reason?}`,
`status` one of `playbook/asking-rules.md` §6's six words). Omit them and this checkpoint works
exactly as it always has — see `asking-rules.md` for the full contract.

**Required questions, gated (FRFRMU-1309).** Above the skill's required-question floor, a
checkpoint must name a real status for every question `playbook/question-registry.json`
requires for that step — a missing one is rejected as `unasked`. Below the floor this is
unchanged. Full rule: `asking-rules.md` §14.

**`status` is one of `"in_progress"`, `"delivered"` or `"abandoned"` — never left unset
(FRFRMU-981).** Every checkpoint before Step 12 writes `"in_progress"`; Step 12 sets
`"delivered"` or clears the field on a successful save, and Step 1's resume bullet sets
`"abandoned"` when the creator skips an old unfinished plan. It does not live forever — full
mechanics (who sets what, and why): `step-12-capture.md`, `step-12-after-the-save.md`,
`step-01-intake.md`.

This is a full overwrite of the `planning_progress` key each time (matches how `update_creator_brief`
already treats existing keys — updated, not merged field-by-field), so it always reflects the
LATEST completed step, not a growing log. Keep the `summary` short — it exists to remind a human,
not to re-derive the plan from.

Skip this on a **headless** run (`runner.py`) — nobody is coming back to resume a run nobody is
watching; do not spend the extra tool call there. See Step 1's resume check below for the human-run
side of this.

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
file for the step you are on — never every file "just in case."** Reading the whole method costs
the creator a large slice of their own Claude usage before a single number comes back, re-sent on
every later turn. **This table IS the complete manifest — every step and sub-step, in true run
order, with what each needs done first (`Requires`) — replacing the old spine and file table,
which used to disagree (FRFRMU-1311).**

| Step | File to load | What it covers | Requires |
|---|---|---|---|
| 1 | `playbook/step-01-intake.md` | The intake conversation | — |
| 1 | `playbook/step-01-intake-fields.md` | The fields the intake must end up with | 1 |
| 1 | `playbook/step-01-intake-fields-2.md` | Rest of the intake fields | 1 |
| 1.1 | `playbook/step-01-1-website-dossier.md` | Crawl the customer's website against a checklist, and store it (G234, FRFRMU-1149) | 1 |
| 1.4 | `playbook/step-01-4-persona-questions.md` | Attractive Character — the question half (p09) | 1 |
| 1.5 | `playbook/step-01-5-market.md` | Validate the market/niche (p01) | 1 |
| 1.6a | `playbook/step-01-6a-avatar.md` | Define the dream-customer avatar (p02) | 1.5 |
| 1.6b | `playbook/step-01-6b-congregations.md` | Map where the dream customer gathers (p03) | 1.6a |
| 1.6 | `playbook/step-01-6-self-account.md` | The creator's own account is the strongest signal | 1.6b |
| 2 | `playbook/step-02-benchmarks.md` | Find benchmark accounts | 1.6b |
| 2.2 | `playbook/step-02-2-discovery.md` | Discovery — what Apify is for, and how (FRFRMU-1307/1312/1298) | 2 |
| 2.3 | `playbook/step-02-3-bands-and-ladder.md` | Which accounts qualify — derived size bands + escalation ladder (FRFRMU-1308/1300/1304/1285) | 2.2 |
| 2.6 | `playbook/step-02-6-screening.md` | Filter benchmarks on real metrics — the typical-reel-views gate (FRFRMU-1303) | 2.3 |
| 2.8 | `playbook/step-02-8-dossier.md` | Competitor dossier (p07) — two passes bracketing Step 3's analysis | 2 |
| 3 | `playbook/step-03-mcp.md` | Use the RM MCP correctly | 2 |
| 3 | `playbook/step-03-mcp-sufficiency.md` | Rule 2a | 3 |
| 3 | `playbook/step-03-requested-vs-delivered.md` | Rule 6h | 3 |
| 3 | `playbook/step-03-data-recipes.md` | Rule 5b | 3 |
| 3 | `playbook/step-03-mcp-spend-and-progress.md` | Rules 6-8 | 3 |
| 3 | `playbook/step-03-progress.md` | Rule 6d — while a run or pull is in flight (FRFRMU-1289/1284) | 3 |
| 3.5 | `playbook/step-03-5-prospect-research.md` | Run prospect research (p04) | 3 |
| 3.6 | `playbook/step-03-6-magic-desk.md` | The magic desk interview (p05) | 3.5 |
| 3.7 | `playbook/step-03-7-big-domino.md` | The Big Domino (p08) | 3.6 |
| 3.8 | `playbook/step-03-8-why-people-buy.md` | Why-people-buy worksheet (p06) — 11 questions, gated on the offer | 3.7 |
| 3.9 | `playbook/step-03-9-origin-story.md` | Origin/epiphany story (p10) — 8 beats written once, cut for length | 3.8 |
| 3.10 | `playbook/step-03-10-false-beliefs-map.md` | False-beliefs map (p11) — >=10 rows, V/I/E, core three | 3.9 |
| 3.11 | `playbook/step-03-11-proof-bank.md` | Proof bank (p29) — ladder, permission, honest attempts | 3.10 |
| 4 | `playbook/step-04-stage.md` | Translate for the account's stage | 3.11 |
| 4.5 | `playbook/step-04-5-persona-assembly.md` | Attractive Character — the assembly half (p09) | 4, 1.6 |
| 4.6 | `playbook/step-04-6-false-beliefs-form.md` | False-beliefs form join (p11) — myth-busting lift + structures | 3.10 |
| 4.7 | `playbook/step-04-7-movement.md` | Build the Movement (p12) — cause/identity/enemy, staged by proof | 3.7, 4.5 |
| 5 | `playbook/step-05-differentiate.md` | Differentiate, never mimic | 4 |
| 6 | `playbook/step-06-retention.md` | Retention, not just hooks | 5 |
| 7 | `playbook/step-07-strategy.md` | Build the strategy (Part A) before the calendar | 6 |
| 7 | `playbook/step-07-1-offer-position.md` | Offer layer — positioning | 7 |
| 7 | `playbook/step-07-2-offer-stack.md` | Offer layer — the stack | 7 |
| 7 | `playbook/step-07-3-ask-campaign.md` | Offer layer — the ask | 7, 3 |
| 8 | `playbook/step-08-deliverable.md` | What the deliverable must contain — loads `TEMPLATE.md` | 7 |
| 8 | `playbook/step-08-join-recipe.md` | Idea from the cards, pattern from the tool (p02-p29) | 8 |
| 8 | `playbook/step-08-hook-recipe.md` | How ONE slot's hook gets chosen | 8 |
| 8 | `playbook/step-08-outline-recipe.md` | How ONE slot's script row is built | 8 |
| 8 | `playbook/step-08-cta-recipe.md` | How ONE slot's ask is chosen | 8 |
| 8 | `playbook/step-08-caption-recipe.md` | How ONE slot's caption is written | 8 |
| 8 | `playbook/step-08-hashtag-recipe.md` | How ONE slot's keywords + 3-6 tag set are built | 8 |
| 8 | `playbook/step-08-audio-recipe.md` | How ONE slot's sound is chosen | 8 |
| 8 | `playbook/step-08-visual-recipe.md` | How ONE slot's shooting direction | 8 |
| 8 | `playbook/step-08-reasoning-recipe.md` | How ONE slot explains itself | 8 |
| 9 | `playbook/step-09-guardrails.md` | Guardrails (never do) | 8 |
| 10 | `playbook/step-10-checklist.md` | Run checklist | 9 |
| 11 | `playbook/step-11-rules-gate-critic.md` | Rules Gate + Critic loop — loads `RULES_GATE.md` and `rules/` | 10 |
| 12 | `playbook/step-12-capture.md` | Capture — save the plan to the creator's Content Calendar | 11 |
| 12 | `playbook/step-12-after-the-save.md` | The two write-backs once the plan is stored | 12 |
| 12.5 | `playbook/step-12-blockers-remain.md` | What to do when blockers are still open at save time | 12 |
| — | `playbook/rigor-rules.md` | The Rigor Rules §A-§K in full | — |
| — | `playbook/asking-rules.md` | The asking contract — how EVERY question the plugin asks is asked (FRFRMU-1051) | — |

**A "Step N" reference inside any step file means that step's file in the table above.**

**`TEMPLATE.md`, `RULES_GATE.md` and `rules/` are NOT loaded up front.** Each one loads at the step
that uses it — `TEMPLATE.md` at Step 8, `RULES_GATE.md` and `rules/` at Step 11. The step file says
so at the top.
