> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 3.8**, during the analysis wait. **Entry rule: only when the goal is
> leads/sales, or an offer is on file.** Otherwise skip this whole file in one line. This is p06
> "Find the WHY: the Reasons-People-Buy Worksheet"
> (`marketing/rules/process-cards/why-people-buy-worksheet.md`, FRFRMU-1041): before writing a
> single "here's why you need this" reel, force 5-10 real reasons someone would buy.

## Step 3.8 — Why people buy (p06)

**Ask per `asking-rules.md`.**

**No offer on file yet? Ask for it first** (price + deliverable, the existing intake bar) — this
step never runs on a blank offer.

### The ten reasons, and the eleven questions

People buy for one of ten reasons: make money · save money · save time · avoid effort · escape
pain · more comfort · cleanliness/hygiene → health · praise · feel more loved · social status.

| # | Question | Who answers |
|---|---|---|
| 1 | Five distinct ways this helps the customer make money. | agent-fills, confirm |
| 2 | How it saves money — this week, this month, this year. | agent-fills, confirm |
| 3 | How much time it saves, AND what else they'd do with that time (both halves). | agent-fills, confirm |
| 4 | One thing they no longer have to do once they have it. | agent-fills, confirm |
| 5 | The physical pain it removes, and what that means for their life/business. | agent-fills, confirm |
| 6 | The mental pain/worry it removes. | agent-fills, confirm |
| 7 | Three ways it makes them more comfortable. | agent-fills, confirm |
| 8 | How it makes them cleaner/more hygienic. | agent-fills, or honest N/A |
| 9 | How it makes them feel healthier or more alive. | agent-fills, confirm |
| 10 | Three ways it makes them envied by friends, more loved by family. | **ask-user** — real social context |
| 11 | How it raises their social status/popularity. | agent-fills, confirm |

**Always ask-user:** any answer stating a real result, a real client's story, or a number —
never invented.

### Process

1. **Draft 5-10 answers per question** from stored data (offer, positioning, first-party proof,
   PQR2, the website) — each labelled with its source or `JUDGMENT`.
2. **Bring the draft to the creator:** confirm the agent-fills answers, ask the ask-user ones.
3. **One refinement pass** on a thin question (same discipline as elsewhere in this method), then
   record honestly — Q8 may be marked N/A.
4. **The 100-others test on every answer:** "saves you time" fails; "no more 9pm scrolling
   competitor reels — the tool watches for you" passes. An answer only THIS product can claim.

### Save it

Creator Brief key `why_people_buy`, Foundation-card shape (FRFRMU-1042):

```
{
  "card": "why_people_buy", "title": "Why anyone buys this",
  "status": "confirmed",
  "summary": "<one line: how many of 10 reasons covered, the one non-obvious standout>",
  "items": [
    {"item_id": "q1_a1", "label": "Q1 — make money", "text": "<answer>", "who": "agent",
     "provenance": "JUDGMENT"},
    {"item_id": "q10_a1", "label": "Q10 — envied/loved", "text": "<answer>", "who": "you",
     "provenance": "FROM-EXPERT"}
  ],
  "updated_at": "<ISO date>"
}
```

One item per answer, `item_id` as `q<N>_a<M>`. A question left N/A gets one item with
`"text": "N/A — <reason>"`.

### What this step refuses to do

Invent a number, a client name, or a price — those are always asked · label any answer
`DATA-DRIVEN` (there is no analysed-reel sample behind a worksheet answer) · save a padded
generic answer that reads as N/A dressed up · run with no offer on file.

### Wired in

`step-08-caption-recipe.md` C.3 and `step-08-hook-recipe.md` H.4b (conditional — each does
nothing when `why_people_buy` is absent): an `activation`/`nurture` slot picks ONE answer as its
value point, ladders it Feature → Benefit → Meaning, and no two slots in a month cite the same
answer, spread across ≥3 reason types.

### Success criteria (falsifiable)

≥5 answers per applicable question, coverage ≥6 of the 10 reason types · Q3 answered in both
halves · every answer carries provenance, zero unlabelled · ≥2 activation/nurture slots in the
next plan cite a worksheet answer, no two the same one.
