> **Playbook reference file — load only this one, whenever a step file says "Ask per
> `asking-rules.md`."** The full step list, and which file holds each step, is in `PLAYBOOK.md`
> (small, always loaded). Like `rigor-rules.md`, this file is not a numbered step — it is the
> one shared rulebook every question-asking step points at instead of restating its own copy.

## The asking contract (FRFRMU-1051) — one way of asking, everywhere

**Founder decision, 2026-09-06, verbatim:** *"split each of the sections to users so we tell
the benefit of each section and let audience answer every question that we ask. if a question
is not answered then we can help them answer it by finding what's stopping them from answering
it. it takes a lot of time but that will give quality output right."* And: *"this task should be
done at last so that such rules are implemented to ask any questions that the plugin asks."*

**In plain words:** depth beats speed. Tell the creator why a section is worth their time, ask
every question in it, and when they get stuck, find out WHY and help — never quietly move on.
This is the single rulebook for every question the plugin asks: the Step 1 intake, every process
card (market, avatar, congregations, prospect research, magic desk, dossier, big domino,
why-people-buy, persona, origin story, belief map, movement), the whole offer layer, the ask
campaign, and any confirm/read-back/consent moment. A step file cites this rule with **"Ask per
`asking-rules.md`"** instead of restating it — one door, not forty copies that can drift.

## 1. Sectioned, benefit-first

A section is one card, or one part of the intake. Before the first question, say ONE plain
line: what the creator gets from finishing it, how many questions, and a rough time — never
call a deep section quick. Keep progress visible throughout, e.g.:

> *"Section 3 of 8 — Who you sell to — question 4 of 11."*

Time is stated honestly, not shrunk to sound easy. A section that genuinely takes fifteen
minutes says fifteen minutes.

## 2. The five rules of asking, every question

Seeded from `step-01-4-persona-questions.md` (FRFRMU-1043, p09) — the first card to write this
down, now generalised to every question the plugin asks:

1. Ask for the **scene**, never the abstraction.
2. A **bad/good example pair**, in the creator's own niche, before the question.
3. **One question, then read the answer back.**
4. A quality bar checked silently — one refinement prompt, never a third ask on the same
   question (see §6 below; this is pacing WITHIN a question, not a cap on how many questions
   the section asks).
5. **Safety before depth** — anything declined is never saved, not even as a fragment.

## 3. Every question is asked. None is silently skipped.

The per-field bar, why-line and niche-example pair a card already carries stay exactly as
written — they are what makes depth produce quality, not busywork. This contract never edits a
field's wording, bar, or score; it only wraps how the field is asked and how a stuck moment is
handled.

## 4. Unanswered → unblocked, never skipped

Before a question is ever marked `declined` or `deferred`, diagnose WHY it stalled and take the
matching path:

| The creator seems... | Path |
|---|---|
| confused by the question | Re-ask with a niche-specific bad/good example + one everyday analogy. |
| unsure / doesn't have the data | The agent finds what it can (web search, reviews, the account's own data, the dossier) and brings a **draft** back for confirmation. |
| overwhelmed by an abstract question | Break it into 2-3 concrete, scene-shaped questions (the 5-Why technique, `step-01-intake-fields-2.md`'s personal-story ladder is the worked example). |
| unwilling to answer (private) | `declined` — instantly, never re-asked, never saved even as a fragment. |
| genuinely outside scope | `not_applicable` — with a reason. A reason the agent accepts turns this into information, not a gap (see §7). |
| not ready right now | `deferred` — resumes next sitting with a one-line recap of where it left off. |

This is coaching, not interrogation: draft, find, break down, exemplify. It is never a fourth or
fifth re-ask of the identical question in the identical words.

## 5. The coaching hard line — never invent the creator's facts

The agent may draft, find, break down and exemplify. It may **never invent** a number, name,
result, or feeling that belongs to the creator. Every draft the agent produces on the creator's
behalf is read back and confirmed before it is saved — a draft that is never read back is a
fabrication wearing a confirmation's clothes.

## 6. The status vocabulary — the single source of truth

Every question the plugin ever asks ends in exactly one of:

```
answered_pass | answered_weak | declined | not_applicable | deferred | unasked
```

**A finished section carries zero `unasked` entries.** `unasked` is not a resting state — it
only ever describes a question mid-conversation, never one the plugin has stopped asking about.
Card files that already wrote this vocabulary locally (`step-01-1-market.md`,
`step-01-2-avatar.md`, `step-01-3-congregations.md`, `step-01-4-persona-questions.md`,
`step-03-5-prospect-research.md`) keep their own copy — this file is what a NEW or older card
points at instead of inventing a sixth spelling of the same six words.

**This does not lift Step 1 rule 7's two-refinement-try cap** (`step-01-intake.md`) — that cap
still governs a single re-ask of the SAME question in the SAME words. §4's unblock paths are
what happens INSIDE those two tries (a sharper example, a smaller question, a drafted answer),
never a third identical ask. The personal-story field keeps its own no-cap exception exactly as
written (`step-01-intake-fields-2.md`).

## 7. Question status vs. the intake completeness score (G225) — founder decision, 2026-09-07

The G225 completeness score's own vocabulary — `confirmed | weak | derived | missing` — is
**unchanged**: same 19 fields, same formula. The mapping from this file's vocabulary onto that
score is:

| Question status | Counts in the G225 score as |
|---|---|
| `answered_pass` | `confirmed` (or `derived`, exactly as today) |
| `answered_weak` | `weak` |
| `declined` | `missing` |
| `deferred` | `missing` |
| `not_applicable` **with** an accepted reason | `confirmed` — it is information, not a gap |
| `not_applicable` **without** a reason | `missing` |

**Declining is still respected instantly and never re-asked (§4) — the score reflects the gap,
it never pressures the creator.** The score line must always explain itself in plain words,
never stand as a bare number, e.g.:

> *"Score 42/100 — 3 answers declined, 2 deferred; the plan is thinner in sections 3 and 5."*

The GENERIC stamp logic (`step-01-intake-fields.md`) is unchanged — it keys off this same score,
just as it does today.

## 8. Resumable per question

`planning_progress` (`creator_brief_reserved_keys.py`) gains three OPTIONAL fields, validated
only when present, so an old 5-field record still parses exactly as it did before this ticket:

* `section` — the current section's label.
* `question_index` — where the sitting stopped inside that section.
* `question_statuses` — a flat list of `{question_id, status, reason?}` entries, `status` one of
  §6's six words.

A sitting can stop anywhere and reopen exactly there — Step 1's resume check
(`step-01-intake.md` rule 1) already offers to pick up an unfinished plan by step; this extends
the same idea down to the question inside a step.

## 9. The plan states its gaps

Any `declined`, `deferred`, or reason-less `not_applicable` answer that affected a decision is
named in Part A, in the same style as the existing GENERIC stamp — never hidden, never buried in
a footnote.

## 10. No cap on how many questions a section asks — ever

**This supersedes any "ask fewer questions" instinct anywhere in this method.** Depth over
brevity is the founder's explicit trade (§0), not a default to be second-guessed per card. A
step file may say how many questions IT HAS (a fact — "this section has 6 questions"); it may
**never** phrase that number as a ceiling on how many get asked — the exact phrasing this
ticket removed from `step-07-2-offer-stack.md` (a fixed count of creator questions, worded as
a limit rather than a fact). If a card genuinely has a fixed, small number of questions because
that is simply how many the topic has, say so as a count, not a ceiling — the difference is
whether hitting the number early ever means skipping a question that would otherwise have been
asked.

## 11. Lead with what the website already found (FRFRMU-1149)

**Before asking any intake question, check `website_dossier.checklist` for that field.** If it
is `found`, lead with the finding and ask for confirmation; never ask from a blank sheet for
something the site already states.

Examples: *"Your site lists a 5-day intro offer and a 3-session bundle — still current, and which
one do you push first?"* / *"Your results page shows a 60 lb loss and chronic-pain clients — can
I use those?"*

A `not_found_on_site` field is asked normally, like any other missing answer. A finding counts
as `derived` in the rule-6 completeness score (`step-01-intake.md`) until the customer confirms
it — then `confirmed`. **Found ≠ true until the owner says so** — rule 4 in `step-01-intake.md`
stands unchanged: a website is one more source to cross-check, never a source to trust blindly.
