> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 13 — Sharpen (FRFRMU-1602): the other sixteen, now that they explain themselves

**When this step runs.** Any time after a first-plan-mode plan (`inputs.business_context.depth:
"first_plan"`, `step-01-first-plan-core.md`) has been delivered — most often when the creator
comes back for their next sitting. It is never forced into the first sitting: the whole point of
first-plan mode is that the creator leaves with something usable before this runs.

**The resume-hook offer.** On any return contact with a `depth: "first_plan"` plan on file, offer
this once, plainly, before anything else:

> *"Your first plan was built from 9 core answers, so some of it is honestly still generic — your
> stance, your voice, your story, what's worked before. Want to spend a few minutes sharpening it?
> It won't throw away what you have; it adds the parts that make the hooks and captions sound like
> YOU instead of anyone in your niche."*

Declining is a complete, respected answer — say what stays generic in one line, and move on to
whatever the creator actually asked for. There is no limit on how many times this can be offered
on later returns; a "not yet" is never treated as a permanent no.

## Coaching WITH evidence — the bar is shown against the plan they're holding

**This is the difference between Step 13 and the normal intake.** Every question below still
carries its full pass/fail bar from `step-01-intake-fields.md` / `step-01-intake-fields-2.md` /
`step-01-4-persona-questions.md` — nothing about the bar changed. What changed is WHEN it is
shown: not cold, against a blank form, but against the real plan the creator is holding, so the
bar reads as a reason, not a rule. Worked example:

> *"Your hooks came out sounding like they could be anyone in your niche — that's because
> 'authentic and professional' isn't a stance yet, it's two adjectives. Here's what a real stance
> looks like for a [niche] business: [2-3 examples]. Want to work out yours?"*

This is `asking-rules.md` §13's belief-draft protocol, applied at the moment its absence is
visible in the plan instead of at the moment the field was first skipped.

## The ten Sharpen questions

Ask per `asking-rules.md`, with the **normal two-refinement cap restored in full** (Step 1 rule
7) — `step-01-first-plan-core.md`'s one-try narrowing was for the first sitting only. The
personal story keeps its own no-cap, consent-based exception exactly as written
(`step-01-intake-fields-2.md`).

| `question_id` | Full bar + card lives in |
|---|---|
| `past_attempts` | `step-01-intake-fields-2.md` |
| `audience_questions` | `step-01-intake-fields-2.md` |
| `personal_story` | `step-01-intake-fields-2.md` (optional, G373, no cap) |
| `backstory_sentence` (F1) | `step-01-4-persona-questions.md` |
| `flaw_1` (F2) | `step-01-4-persona-questions.md` |
| `stance` (F3) | `step-01-4-persona-questions.md` — the pretend-counter-comment test |
| `parable_1` (F5) | `step-01-4-persona-questions.md` |
| `voice_descriptors` (F6) | `step-01-4-persona-questions.md` — a read-back test |

**Plus:** the swipe file's human half (p28, FRFRMU-1066, `step-01-intake-fields-2.md`) — one
occasional ask, `deferred` allowed — and the conditional cards **1.5** (`step-01-5-market.md`),
**1.6a** (`step-01-6a-avatar.md`) and **1.6b** (`step-01-6b-congregations.md`), whose own entry
rules decide whether each even applies. Nothing about any entry rule changes here.

## The promotion — `depth: first_plan → sharpened`

**A sharpen is a NEW plan version, never a replacement (FRFRMU-1063 plan versions exist for
exactly this).** Once enough of the ten questions above have real answers (judgment call — a
creator who answers three of ten still gets those three folded in; this step never blocks on a
completeness threshold), save a new version of the SAME plan:

1. Fold every newly-answered field into the plan the normal way each field already writes to it
   (positioning items into `update_business_profile`, everything else into
   `update_creator_brief` / the plan's own `inputs`).
2. Re-run the parts of Steps 5–8 that the newly-answered fields actually change — `ownable_angle`
   and `bold_stance` reshape positioning and hooks; `personal_story` and the F1–F6 set unlock the
   pinned identity/origin reel slot `step-01-first-plan-core.md` left as a placeholder.
3. Set `inputs.business_context.depth: "sharpened"` on the new version. The old `"FIRST PLAN"`
   stamp is replaced with the plan's normal positioning sentence — GENERIC still applies if
   positioning is genuinely still missing after the sharpen, exactly as it would for any plan.
4. Save via the normal Step 12 capture path, `stage: "calendar_drafted"` or later depending how
   much of the calendar the sharpen touched — this is not a special save path, just a normal
   Step 12 save on a plan that already has a `plan_id`.

**Never silently overwrite the first plan's own version.** The creator kept and possibly already
posted from the first-plan version; the sharpen adds a new one on top, so nothing they already
acted on disappears from the record.

## Registry note

`playbook/question-registry.json` covers the Step 1 family (`required_by_step` `"1"`, `"1.4"`,
`"1.6"`) only — it does not yet gate Step 13's own checkpoint. Until it does (ticket F), Step 13
follows the checkpoint discipline in `step-01-first-plan-core.md` by convention: as each Sharpen
question is answered here, its status flips from `deferred` ("first-plan mode: deferred to Step
13") to its real outcome on the very next checkpoint — never left stale once the answer exists.
