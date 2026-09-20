> **Playbook reference file — load only this one, whenever a question needs the help path.** The
> full step list, and which file holds each step, is in `PLAYBOOK.md` (small, always loaded).
> Like `rigor-rules.md`, this file is not a numbered step — it is the companion to
> `playbook/asking-rules.md`, split out because that file sits at exactly 300/300 lines with no
> room left (FRFRMU-1609). This file never restates §2/§4/§6/§9/§13 of `asking-rules.md` — it
> cites them and adds the one thing they didn't have: per-question help content
> (`playbook/question-help.json`).

## FRFRMU-1603 — one mechanism, chosen by the question's shape

**"I don't know" and "that's too thin" are the SAME failure, and they take the SAME path.** Both
mean the creator is stuck on this ONE question right now — not that the question is wrong, and
not that they should be pushed past it unhelped. `asking-rules.md` §4 already says this ("unsure
/ doesn't have the data" → the agent finds what it can and brings a draft back) and §13 already
works it out in full for a belief question. This file generalises both to every question the
plugin asks, by reading `question-help.json`'s `shape` field and running the matching path below.
**The refinement prompt IS the help** — there is no separate "help mode"; the very next thing said
to the creator when they are stuck is what unblocks them.

## The three paths, by shape

Every entry in `question-help.json` carries one `shape`: `belief`, `fact`, or `memory`. Each shape
has exactly one path — read it from the JSON's `idk_path` for that question, which may specialise
the path with real content (`proof`'s dig-it-out ladder is the worked example, founder 2026-09-19).

| Shape | The path when stuck or thin |
|---|---|
| **belief** | `asking-rules.md` §13's four moves, already written: draft from THEIR published sources · 2-3 examples from THEIR niche · a plain-English process · read the draft back for a yes/no. Never invented, never saved unconfirmed. |
| **fact** | the agent PROPOSES with its reason from what it already holds (the peek, the dossier, the stage) — *"I'd guess reach first, since you're at 1,300 followers — sound right?"* "Don't know" makes the proposal the answer, saved `derived`, read back. `constraints` walks its four categories one at a time instead of one big blank ask. |
| **memory** | the agent LOOKS first — their posts via the peek, the website dossier, reviews via WebSearch — and drafts. Nothing found: ONE smaller, scene-shaped question (not the feeling — an actual moment). Still nothing: `deferred` with a concrete collection instruction and one line on what the plan loses meanwhile. |

**Statuses are unchanged (`asking-rules.md` §6).** Taking any of these three paths never changes
the outcome vocabulary — the question still ends `answered_pass | answered_weak | declined |
not_applicable | deferred`. "I don't know" is `deferred`, never `declined` (FRFRMU-1301) — this
file adds no seventh status word.

## The escape hatch — a printed invitation, from one place (founder, 2026-09-19)

Every question the plugin asks carries this line, appended once, so asking for help is never
something the creator has to guess is allowed:

> *(Stuck? Say **"help me with this one"** and I'll walk you through it.)*

**This line lives in exactly one place — here — so 25+ hand-typed copies never drift.** A step
file does not retype it; it says "ask per `asking-rules.md`" (which already points at this
companion) and the line is said with every question.

**Recognising the trigger.** Saying the line above, or anything close to it — *"I don't know"*,
*"not sure"*, *"help"*, *"can you explain"* — enters the help path for THAT question (the shape
table above). **It is never read as an answer and saved.** Storing "I don't know" as the
creator's actual positioning is exactly the failure this rule exists to prevent — the same reason
§6 makes "I don't know" `deferred`, never `declined`.

**Using it is never penalised.** The question's status stays whatever the shape's path produces
(usually `deferred`, sometimes `answered_weak` once a proposal lands) — never `declined`, and the
creator is never told they failed or made the agent's job harder.

## The re-render rule — every example is about THEIR niche, never about them

`asking-rules.md` §2 rule 2 already says a bad/good example pair belongs "in the creator's own
niche" — `question-help.json`'s `example_shape` is written niche-neutral so this is possible at
all. **Once Step 0 knows the niche (`step-01-intake.md`), every `example_shape` pair is rewritten
in that niche before it is ever asked.** A dentist does not see a fitness example; a bakery does
not see a SaaS example — each question's bad/good pair is re-rendered fresh, every time, in
whatever niche this specific creator is in.

**The line that must never move: examples are about OTHER businesses in the niche, never about
the customer.** Re-rendering an example into the creator's niche is not the same as rendering an
example about the creator — that crosses into `asking-rules.md` §5's line against inventing the
creator's own facts. The belief path's drafts (§13) are the one place the agent proposes something
*about* the creator, and those are always read back for a yes/no before they are saved; a
niche-rendered `example_shape` pair is never saved as anything, confirmed or not — it is only ever
shown.

## What this file refuses to do

Treat "I don't know" as a reason to skip a question · save a "help" trigger as if it were the
answer · penalise a deferred question with a lower score than the honest gap it represents (that
mapping is `asking-rules.md` §7, unchanged) · invent a fact, number, or belief with no source
behind it (§5 stands, unchanged) · retype a per-question example, bar, or path — that content
lives in `question-help.json` alone.
