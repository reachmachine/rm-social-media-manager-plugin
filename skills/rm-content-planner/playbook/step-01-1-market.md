> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 1**, right after the positioning draft, before `step-01-6-self-account.md`.
> **Entry rule: only when positioning is empty, OR the creator says something like "check my
> niche".** Otherwise skip this whole file in one line — an already-validated, unchanged niche
> never sees this again, and the transcript for that account is unchanged. This is p01 "Pick and
> Validate the Market/Niche" (`marketing/rules/process-cards/p01-pick-and-validate-market.md`,
> FRFRMU-1013): the niche pick is not a form field, it is checked.

## Step 1.5 — Validate the market (p01)

**Ask per `asking-rules.md`.**

A hungry, well-matched audience matters more than the offer, which matters more than
persuasion. This step checks that before anything downstream (discovery, the avatar, the
plan) is built on top of it. Work these moves **one question at a time** — every question ends
in a status: `answered_pass | answered_weak | declined | not_applicable | deferred`, never
`unasked`.

**1. Drill-down (ask-user).** From the creator's own story, propose a ladder: core market
(Health / Wealth / Relationships) → sub-market → niche. The creator picks, or corrects it.

**2. Score the four indicators (agent-fills, WEB RESEARCH WITH CITATIONS ONLY).** Massive Pain
· Purchasing Power · Easy to Target · Growing. Use `WebSearch`/`WebFetch` for each — never
Reach Machine's own view or niche-distribution data. **🔴 Hard data boundary (founder,
2026-08-30): RM's own view data measures attention, not pain or purchasing power, the tracked
set is virality-biased, and there is no time-series for "growing" — using it here is a
provenance violation.** Each score needs one cited fact with a working source link; a score
with no citation **FAILS** and must not be saved. **A "bad" Growing score STOPS this
evaluation** — say so plainly and do not continue to discovery on a shrinking market.

**3. Passion check (agent-fills, real searches, named finds).** At least 2 **named, linked**
communities, real vocabulary examples pulled from them, at least 1 event, at least 2 named
experts. Being first to serve a market is a red flag, not a win — **never invent a community,
event or expert name.** Found less than the floor → record an honest FAIL, not a passing
score padded with invented names.

**4. Willing AND able (agent drafts + ask-user).** Willing (they say they'd pay) and able
(they already do) are checked separately. Ask the creator for **one real price point their
audience already pays someone** — record it as a fact the creator confirms, never a number the
agent invents or "suggests." (No currency figure appears in this file — the number lives only
in the creator's own answer.)

**5. "Made exactly for me" specificity test (agent drafts, user confirms).** Draft one line
describing the niche narrow enough that the avatar would recognise themselves in it. The G648
check: *could this describe 100 other businesses?* → if yes, narrow it and redraft.

**6. Commit line with a date (ask-user — always the human's call).** A dated sentence: "we
serve `[niche]` — `[date]`." "We'll try X and Y" is not a commitment and fails this step.

**Already-committed creator:** run steps 2-3 to VALIDATE and surface red flags; do not
re-open the niche decision. The one exception is a shrinking market — the Growing stop still
applies even to a creator who has already committed.

### What this step refuses to do

Score any of the four indicators from Reach Machine's own tag/view data · accept an indicator
with no citation · invent a community, event or expert name to hit the passion-check floor ·
suggest, average or set the price point itself · continue past a "bad" Growing score · silently
skip a question (every question ends in a status).

### Save it

Write the result to the Creator Brief as the Foundation card key `market_validation`, in the
shape `/settings/profile` renders (FRFRMU-1042):

```
{
  "card": "market_validation",
  "title": "Market & niche validation",
  "status": "confirmed",            # or "hypothesis" if any indicator is FAIL/weak
  "summary": "<one line: the committed niche + date>",
  "items": [
    {"item_id": "ladder", "label": "Core -> sub-market -> niche",
     "text": "<the ladder the creator picked>", "who": "you", "provenance": "JUDGMENT"},
    {"item_id": "indicator_pain", "label": "Massive Pain", "tag": "indicator",
     "text": "<score + the cited fact>", "who": "agent", "provenance": "FROM-EXPERT",
     "source_url": "<link>"},
    {"item_id": "indicator_purchasing_power", "label": "Purchasing Power", "tag": "indicator",
     "text": "<score + the cited fact>", "who": "agent", "provenance": "FROM-EXPERT",
     "source_url": "<link>"},
    {"item_id": "indicator_easy_to_target", "label": "Easy to Target", "tag": "indicator",
     "text": "<score + the cited fact>", "who": "agent", "provenance": "FROM-EXPERT",
     "source_url": "<link>"},
    {"item_id": "indicator_growing", "label": "Growing", "tag": "indicator",
     "text": "<score + the cited fact, or 'STOP: shrinking market'>", "who": "agent",
     "provenance": "FROM-EXPERT", "source_url": "<link>"},
    {"item_id": "passion_check", "label": "Passion check",
     "text": "<>=2 communities, vocabulary, >=1 event, >=2 experts, or an honest FAIL>",
     "who": "agent", "provenance": "FROM-EXPERT"},
    {"item_id": "price_point", "label": "Willing and able",
     "text": "<the one real price point the creator confirmed>", "who": "you",
     "provenance": "FROM-EXPERT"},
    {"item_id": "specificity", "label": "Made exactly for me",
     "text": "<the confirmed line>", "who": "you", "provenance": "JUDGMENT"},
    {"item_id": "commit", "label": "Commit line",
     "text": "<the dated commit sentence>", "who": "you", "provenance": "JUDGMENT"}
  ],
  "updated_at": "<ISO date>"
}
```

**An `indicator_*` item saved with `provenance: "DATA-DRIVEN"` instead of `"FROM-EXPERT"` is a
defect — it means an RM-data shortcut reached the four scores. Reject it before saving and
re-score from a cited web source.**

Cache this per niche — run once, reuse on later plans for the same creator, and only re-run
when the niche itself changes (the web-research pass is the expensive step, not the plan).

## Wire into

* **Step 2 (discovery, `step-02-benchmarks.md`):** discovery is seeded from `congregations`
  (p03, FRFRMU-1033) which itself starts from this validated niche — no separate wiring needed
  here.
* **Step 7.0 ("confirm the foundation," `step-07-strategy.md`):** reads `market_validation`
  before confirming the plan's foundation; absent → the step says so and stops instead of
  silently building on an unvalidated niche.
