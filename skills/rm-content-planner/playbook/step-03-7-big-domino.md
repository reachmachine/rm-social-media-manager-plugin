> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 3.7**, during the analysis wait, AFTER `step-03-5-prospect-research.md`
> (p04) and `step-03-6-magic-desk.md` (p05) have run — their answers supply the deepest-desire
> slot below, the weakest source is drafting this at intake alone. Re-confirmed with data at
> Step 7.0e. This is p08 "Define the Big Domino"
> (`marketing/rules/process-cards/p08-define-big-domino.md`, FRFRMU-1040): the ONE belief a
> viewer must accept for every smaller objection to fall away.

## Step 3.7 — The Big Domino (p08)

**Ask per `asking-rules.md`.**

### 1. Draft 2-3 candidates (agent-fills, no new questions)

Fill the template from what is already on record:

*If people believe that* **(new opportunity** — ownable angle + bold stance) *is the key to*
**(deepest desire** — PQR2 `results` + p05 Q4 + p04 wants) *, and that this is only attainable
through* **(vehicle** — the creator's own method/offer)*, then every smaller objection falls
away.*

### 2. The 3-part validity test (agent-fills, one-line verdict each)

1. **Differentiated, or mainstream?** — cite the sameness map (what everyone else in the niche
   claims).
2. **A new opportunity, or "the same thing, better"?**
3. **Blue ocean, or could a viewer buy this belief from 100 other accounts?**

"Passes, trust me" is not a verdict — each line needs a reason.

### 3. Truth check — the CREATOR answers, never the agent (ask-user)

Ask verbatim: *"Can what you sell actually deliver this belief for a typical customer? Yes /
mostly / no."* **The agent never answers this itself — an eval fails on it.** "Mostly" → narrow
the claim (not the ambition) until the answer is yes.

### 4. Pick the ONE — branches on account maturity

- **Established / `confirmed` positioning** — the creator picks; `status: confirmed`.
- **Young / `hypothesis` positioning** — keep 2-3 candidates as the angles the month tests (the
  existing hypothesis cycle). `step-07-strategy.md` 7.0e promotes the winner once the creator's
  own data shows which desire resonated — data picks, not taste.

### 5. Headline (agent-fills, Gate-1 safe)

Promises the **process and the dream** — never a result-in-N-days. "Only attainable through" is
positioning, not an income claim.

### 6. No candidate passes

Say so plainly: *"this reads as an improvement offer, not a new opportunity."* This is a WARNING
in A0 (same style as the "GENERIC — positioning not provided" stamp), never a stop — the plan
still runs on today's positioning.

### Save it

Creator Brief key `big_domino`, Foundation-card shape (FRFRMU-1042):

```
{
  "card": "big_domino", "title": "The Big Domino",
  "status": "hypothesis",   # or "confirmed" once the creator/data picks one
  "summary": "<the headline, or 'no candidate passed the validity test yet'>",
  "items": [
    {"item_id": "candidate_1_statement", "label": "Candidate 1 — statement",
     "text": "<if X then Y only through Z>", "who": "agent", "provenance": "JUDGMENT"},
    {"item_id": "candidate_1_validity", "label": "Candidate 1 — validity",
     "text": "<3 one-line verdicts + reasons>", "who": "agent", "provenance": "JUDGMENT"},
    {"item_id": "truth_check", "label": "Can you actually deliver this?",
     "text": "<yes/mostly/no + the creator's own words>", "who": "you",
     "provenance": "FROM-EXPERT", "date": "<ISO date>"},
    {"item_id": "headline", "label": "Headline",
     "text": "<process + dream, Gate-1 safe>", "who": "agent", "provenance": "JUDGMENT"}
  ],
  "updated_at": "<ISO date>"
}
```

Repeat the `candidate_N_*` pair for each candidate (2-3 total). Once one is promoted to
`confirmed`, `summary` becomes its headline and `status` flips.

### What this step refuses to do

Answer the truth check itself · present a hypothesis as `confirmed` · write a headline promising
a number in a timeframe · invent a validity verdict with no reason ("passes, trust me").

### Wired in

`step-08-deliverable.md` Section 00 (a headline line, conditional) · `step-08-reasoning-recipe.md`
R.3 (each slot's `belief` field, conditional) · `step-07-strategy.md` 7.0e (data-confirms a
hypothesis Domino). Every one of these does nothing when `big_domino` is absent.
