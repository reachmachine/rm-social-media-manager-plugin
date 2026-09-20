> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 1 — First-plan mode (FRFRMU-1602): nine questions, then a plan

**When this file loads instead of `step-01-intake-fields.md` / `step-01-intake-fields-2.md`.**
Step 1 rule 1 already calls `get_creator_brief` before asking anything. When that call shows
**no saved plan on the brief** — a genuinely first-time customer — load THIS file for the field
list instead of the two full intake-fields files. A returning creator, or anyone who already has
a plan on file, gets the normal full intake unchanged. Everything else in `step-01-intake.md`
(the connections check, Rule 0, the five numbered rules, the website dossier offer) still runs
exactly as written — this file only replaces WHICH FIELDS get asked before the plan is built.

**Why nine and not more.** Steps 7–8 cannot build a Reel Bet (§A) without Proven Pattern (Step 0)
× First-Party Topic (`offer`, `proof`) × Audience Tension (`audience`, `problems`). `goal` picks
the metric, `capacity` drives batching, `content_language` decides what language the plan comes
out in, `plan_size` is the customer's own call by rule, and `constraints` is a compliance guard —
silence there cannot wait until after a plan exists. Nothing is deleted — the other sixteen
questions and the swipe file move to where they belong (below), never off the record.

## The CORE nine — the ONLY questions asked before the plan is built

Ask per `asking-rules.md`, using each field's own bar, card and example from
`step-01-intake-fields.md` / `step-01-intake-fields-2.md` (this file does not restate them —
only `question-help.json` and this ordering rule are new).

| # | `question_id` | One-line what it decides |
|---|---|---|
| 1 | `audience` | who every example, hook and word speaks to |
| 2 | `problems` | the audience's real words, in the audience's own language |
| 3 | `offer` | what the traffic this plan drives actually lands on |
| 4 | `proof` | the one real result a stranger should believe |
| 5 | `goal` | the ONE metric everything else is built to hit |
| 6 | `capacity` | the real, sustainable posting pace |
| 7 | `content_language` | the language every caption and script comes out in |
| 8 | `plan_size` | how many reels — the creator's call, informed |
| 9 | `constraints` | what the plan must never recommend |

**Nothing else is asked in this conversation.** `ownable_angle`, `bold_stance`, `funnel_assets`,
`production_capability`, `brand_voice` and `upcoming_moments` are asked **just-in-time**, at the
step that actually needs them (below). Everything else is offered later, at Step 13.

## One refinement, not two — for the first run only

**Step 1 rule 7's normal cap is two refinement tries per field.** In first-plan mode, each of the
nine core questions gets **ONE refinement at most**, using that question's own example from
`question-help.json` (`example_shape.bad` / `example_shape.good`) — never a second. Still thin
after that one try → mark it `answered_weak` (rule 6) and move on to the next question; this is
pacing, never a reason to skip a question or end the section early. This narrower cap applies
**only** to the nine core questions on a first-time customer's first run — Step 13's sharpen
pass restores the normal two-try cap (and the personal story's own no-cap exception) in full.

## Derived, not asked — `niche_seeds` and `stage`

These two never appear as questions in first-plan mode, and neither is deferred to Step 13 —
they are simply **derived from what the account already has on file before intake even starts**:

- **`niche_seeds`** — Step 2's own discovery finds accounts from the niche + hashtags without a
  named seed list (`step-01-intake-fields-2.md`). Whatever the creator happens to mention along
  the way is checked like any other seed; nothing here asks for it cold.
- **`stage`** — Step 1.6's self-account pull runs exactly as it does outside first-plan mode
  (`step-01-6-self-account.md`), and the stage is proposed from that real data, never asked as a
  blank question. First-plan mode changes nothing about when Step 1.6 runs.

## The six JIT questions — asked at the step that needs them, one line each

No bar, no card, no two-try cap — one plain question, accepted as given, at the moment the
answer is actually used:

| `question_id` | Asked at | File carrying the "ask it here" block |
|---|---|---|
| `ownable_angle` | Step 5 | `step-05-differentiate.md` |
| `upcoming_moments` | Step 7 (item 7.8) | `step-07-strategy.md` |
| `bold_stance` | Step 8, hook recipe | `step-08-just-in-time-asks.md` (pointed at from `step-08-hook-recipe.md` — no room left in that file) |
| `brand_voice` | Step 8, caption recipe | `step-08-caption-recipe.md` |
| `funnel_assets` | Step 8, CTA recipe | `step-08-cta-recipe.md` |
| `production_capability` | Step 8, visual recipe | `step-08-visual-recipe.md` — only the mandatory AI-generated follow-up (FRFRMU-1310, compliance) runs here; the rest of its full bar moves to Step 13 |

Each block reads the question's `shape`/`idk_path` from `playbook/question-help.json` the same
way any other question does (`asking-rules-help.md`) — a JIT question is asked more lightly, not
asked without help if the creator gets stuck.

## The ten Sharpen questions, the swipe file, and the conditional cards — all deferred to Step 13

Nothing below is skipped. It is asked in full, with its full bar, once the creator has a plan in
hand: `past_attempts`, `audience_questions`, `personal_story`, `backstory_sentence`, `flaw_1`,
`stance`, `parable_1`, `voice_descriptors`, the swipe file (p28), and the conditional cards 1.5 /
1.6a / 1.6b (their own entry rules are unchanged by first-plan mode). See
`playbook/step-13-sharpen.md`.

## The checkpoint rule — send `question_statuses` IN FULL, every time (FRFRMU-1309)

**This is load-bearing.** Until `playbook/question-registry.json` is re-homed (ticket F), every
bare checkpoint `"2"` … `"12"` requires a real status for all 25 Step-1-family ids the registry
lists — a missing one is rejected the same as `unasked` (`asking-rules.md` §14). First-plan mode
does not get a pass on this: it changes WHEN a question is asked, never whether its status is
reported.

**At every checkpoint (`update_creator_brief`, key `planning_progress`), send `question_statuses`
covering every registry id, using these rules:**

- The nine core ids: their real status (`answered_pass`, `answered_weak`, `declined`,
  `not_applicable` or `deferred`) once Step 1 has run.
- Each of the six JIT ids **not yet asked**: `deferred`, reason `"first-plan mode: asked at step
  <N>"` (`<N>` is that question's own consuming step from the table above) — once its step asks
  it, its status becomes real like any other question.
- `niche_seeds` and `stage`: their real derived status (§ above) — never `deferred` for "first-plan
  mode" reasons, since neither is ever asked as a question here.
- The remaining Sharpen ids **not yet asked**: `deferred`, reason `"first-plan mode: deferred to
  Step 13"` — once Step 13 asks one, its status becomes real.

**Never `unasked`. Never an omitted id.** Omitting a single deferred id here is the exact
FRFRMU-1309 incident, in reverse — the very failure this checkpoint rule exists to prevent.

## The words on the plan — "FIRST PLAN", never the old low-positioning stamp

A partial positioning object normally stamps a different, older banner at the top of the
deliverable (`step-01-intake-fields.md`). **In first-plan mode, the stamp reads instead:**

> **"FIRST PLAN — built on your 9 core answers. The stance, voice and story that sharpen it are Step ④ — pick it up any time."**

Same place (`TEMPLATE.md` Section 00), same honesty, never both stamps on one plan — the word
**GENERIC never appears** on a plan built in first-plan mode.

**The plan carries `inputs.business_context.depth: "first_plan"`.** `validate_content_plan` will
honestly warn `intake_completeness` below its 50 floor (9 confirmed of ~20 ≈ 45) — with `depth:
"first_plan"` set, the customer-facing line reads *"this is your first plan, built from your 9
core answers — sharpening it with Step 13 fills in the rest"* instead of a bare low-score
warning. Step 13 promotes `depth` to `"sharpened"` on the SAME plan version (FRFRMU-1063 plan
versions) — a sharpen is a new version, never a replacement of the first one.

**TEMPLATE Section 00's pinned identity/origin reel slot stays present** and reads *"added in
Step ④ once we have your story"* rather than being built now — this is a checked convention, not
a `validate_content_plan` rule.

**Part A still names every deferred field and what it costs (`asking-rules.md` §9)** — the same
rule, now with sixteen more entries than a full intake would ever leave open.

## Reusability — nothing niche-specific here

Every example in this file is rendered from `question-help.json`'s `example_shape` at ask time
(`asking-rules.md` §2 rule 2), the same re-render rule every other question in this method
already follows. Nothing above names a niche, a business, or a product on purpose.
