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

**This includes a stance, opinion, or belief (FRFRMU-1301) — a bold stance IS a feeling that
belongs to the creator.** But drafting one from the creator's OWN **published sources** — their
website, their reviews, what they already told you — and reading it back for a plain yes/no is
NOT invention. It is this section's own "draft… and confirm" pattern, applied to a harder
field. What crosses the line is inventing a belief with **no source** and presenting it as
theirs, or saving a draft the creator never confirmed. See §13 for the full bold-stance
protocol.

## 6. The status vocabulary — the single source of truth

Every question the plugin ever asks ends in exactly one of:

```
answered_pass | answered_weak | declined | not_applicable | deferred | unasked
```

**A finished section carries zero `unasked` entries.** `unasked` is not a resting state — it
only ever describes a question mid-conversation, never one the plugin has stopped asking about.
Card files that already wrote this vocabulary locally (`step-01-5-market.md`,
`step-01-6a-avatar.md`, `step-01-6b-congregations.md`, `step-01-4-persona-questions.md`,
`step-03-5-prospect-research.md`) keep their own copy — this file is what a NEW or older card
points at instead of inventing a sixth spelling of the same six words.

**"I don't know" is `deferred` (or `answered_weak` if a thin guess was given), never
`declined` (FRFRMU-1301).** `declined` is for a question the creator was unwilling to answer;
"I don't know" or "I haven't spoken to them yet" is someone who WANTS to answer but lacks the
facts right now — exactly §4's "unsure / doesn't have the data" row, so it gets that row's
coaching path, not a silent skip. §13 is the deepest version of this, for a bold stance/belief.

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

## 12. Never claim a save that has not happened yet (FRFRMU-1290, FRFRMU-1296)

**Founder decision, 2026-09-12: save as you go, and only say so once the save has actually
happened.** Step 1 saves each answer to the workspace as the conversation goes (Step 1 rules 5
and 5a) — that is what stops a long interview being lost if a session dies. The words the agent
uses about it must stay honest on both sides of that fact: never promise nothing is saved when it
is, and never claim something is saved when it is not.

**The agent may only tell the creator something is saved, recorded, locked in or captured AFTER
the write call has returned successfully.** If no write has been made yet, it says what is true
instead — "got it, I'll save that with the rest in a moment" — or it makes the write first and
then reports it. The gated words: *saved*, *locked in*, *recorded*, *captured*, *noted down*, *on
file*. None of them is said in the future tense as if it already happened.

This cuts both ways. A promise that "nothing is saved anywhere" is false the moment a later rule
saves as it goes (FRFRMU-1290); a claim that an answer is "locked in" when no write call has run
is false in the other direction, and across a long interview that silently loses every answer
(FRFRMU-1296). Neither failure is fixed by removing the saving behaviour — only by making the
words match whichever one, save or don't-yet-save, actually happened.

## 13. The bold-stance / belief question — the deepest "unsure" case (FRFRMU-1301)

**Founder decision, 2026-09-12, verbatim:** *"when customer tells dont know, use their webuste
and suggest them and also give them examples and a process on how they can answer that
question. use simple english as well."*

The bold-stance field (`step-01-intake-fields.md` item 5) and any question shaped like it — ask
for a BELIEF, not a fact — hits §4's "unsure / doesn't have the data" row hardest, because a
creator who has never put their POV into words has nothing to recall. §5 already says drafting
from published sources and confirming is allowed, not invention; this section is the worked
protocol for that, so the agent never just parks the field on the first "I don't know."

**Offer the draft BEFORE parking the field — the agent never decides alone:**

> *"I don't have enough to answer that myself either — but I can take a first crack at a draft
> from your website and reviews, show you 2-3 examples from other [niche] businesses so you can
> see the shape of a good answer, and give you a simple way to work out your own if none of
> them fit. Want that, or would you rather park this one for now?"*

Say what parking costs **in the offer itself**, not only after the creator picks it — e.g.
*"parking this means the plan skips the identity pillar for now; we add it once you have an
answer."* Never decide to park without asking first.

**On a yes, the four moves, in this order:**
1. **Draft from published sources.** The source is Step 1.1's `website_dossier`
   (`playbook/step-01-1-website-dossier.md`) plus reviews found by `WebSearch`. A missing
   dossier is a reason to go run Step 1.1 first, never a reason to give up on the draft.
2. **Show 2-3 examples from their niche** — real bold stances other businesses in the same
   space have taken, so the creator sees the shape of a good answer before judging their own.
3. **Give a plain-English process** — a short, simple way for them to work out their OWN answer
   later, e.g. *"ask yourself: what do you believe about training [audience] that most [niche]
   places won't say out loud?"* A label like "the polarizing zone" is never the opening word
   (same rule as every framework card, `step-01-intake-fields.md`'s delivery rules).
4. **Read the draft back for a yes/no** — never save it as if the creator said it (§5).

If the creator declines the OFFER itself (not the draft — the offer to try), park the field as
`deferred`, restate what it costs, and move on. That is the honest end state, reached only after
offering, never before.

## 14. The required-question registry — closing the gap this contract left open (FRFRMU-1309)

**What went wrong.** This whole file existed and an agent still finished an intake having never
asked ~14 required fields, while `planning_progress` kept saying "Step 2 complete." Nothing
listed WHICH questions a step needs, and nothing ever read `question_statuses` back to find a
gap — §8's three fields validated their own shape and nothing else. A markdown rule nobody is
forced to check gets skipped; this section is the backend half that cannot be.

**The registry.** `playbook/question-registry.json` lists every
`question_id` this contract enforces, and the step it belongs to. It mirrors, byte-for-byte,
`app/mcp/creator_brief_question_registry.py` in the backend — one list, two copies, checked
equal by that module's own test. Today it covers the Step 1 family only (`1`, `1.4`, `1.6`) —
`step-01-intake.md` rule 6's 19 canonical fields (minus `stage`, held to `1.6` per FRFRMU-1008)
plus `step-01-4-persona-questions.md`'s five fixed sub-questions. The rest of the method (market,
avatar, congregations, the offer layer, and every other card this file governs) is not yet
enforced this way — see `prompts/COMMS.md` (FRFRMU-1309) for the reasoning and the follow-up.

**What the backend does with it.** Once the write's own `skill_version` reaches a floor
(`CREATOR_BRIEF_QUESTION_STATUS_FLOOR`, `app/config.py`), a `planning_progress` checkpoint for a
step that has registered required questions must carry `question_statuses` naming a real status
(anything but `unasked`) for every one of them — a missing entry is rejected the same as an
explicit `unasked`. Checkpointing a bare top-level step (`"2"`, not `"1.6"`) also requires
everything registered under every earlier top-level step — this is what makes a `"2"` checkpoint
catch a gap Step 1 left open, instead of only checking Step 2's own (empty) list. `delivered` and
`abandoned` writes are always exempt — they end a plan and must never be blocked. Below the
floor, or on any older build, nothing changes: this is a pure addition, never a new way to fail a
write that used to save clean.

**Two decisions already made — restated here so this file is the one place that has them
(founder, 2026-09-06/07):**

* **"Waiting on the owner" is `deferred` plus a reason — never a seventh status word.** A
  question the creator can't answer without asking someone else (a partner, a business owner
  they manage the account for) is `deferred`, same as "not ready right now" (§4). Do not invent a
  new status for this — it would touch the vocabulary in §6, every card file that already wrote
  it locally, and the 1042 chip plan.
* **A skipped CONDITIONAL card writes `not_applicable` for each of its questions, with a reason
  naming the entry rule — never silence.** `step-01-5-market.md`, `step-01-6a-avatar.md` and
  `step-01-6b-congregations.md` each open with an "Entry rule: only when…" line that can skip the
  whole file. When that happens, the questions it would have asked are not left `unasked` (which
  would look, later, exactly like a forgotten question) — they are recorded `not_applicable`,
  reason `"entry rule: <the file's own condition>"`, e.g. `"entry rule: positioning already
  confirmed, creator did not ask to re-check the niche."` Absence must never mean both "didn't
  apply" and "we forgot" — this is how the record tells the two apart.

**What the customer sees — one honest line per section, in plain words, e.g.:**

> *"Section 2 of 6 — Your business: 9 of 11 answered, 1 skipped, 1 saved for later, 0 not yet asked."*

Never a bare "Step 2 complete" with no breakdown — that phrasing is exactly what let the original
gap hide in plain sight.
