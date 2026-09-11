> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this during Step 3**, while the pull/analysis is running, when `prospect_research` is
> missing or the creator asks to refresh it. Otherwise skip this whole file in one line. This
> is p04 "Run Prospect Research"
> (`marketing/rules/process-cards/p04-run-prospect-research.md`, FRFRMU-1035): never write a
> reel cold — find out, in the audience's own words, what they want, what they fear, and WHY
> they don't buy.

## Step 3.5 — Run prospect research (p04)

**Ask per `asking-rules.md`.**

Every question ends in a status: `answered_pass | answered_weak | declined | not_applicable |
deferred`.

**1. Pick the niche's 3-5 top books/products (agent-fills)** from `market_validation` (p01) /
`avatar` (p02).

**2. Harvest review quotes (agent-fills, VERBATIM, every one source-linked).** 5-star (what
excites), 1-star (what angers), and **at least 3 findings specifically from 2-4-star reviews**
— the mixed feedback ("it did X, but not Y") is the real gold. **Skipping the mid-star lens
fails this pass.**

**3. Search-engine pass (agent-fills).** Questions people ask, related products, ads running.

**4. Own FAQs/DMs (ask-user).** Reuse the existing "bring a batch of ~20 real questions/DMs,
verbatim" prompt (`step-01-intake-fields.md`). None yet → proceed on public sources, labelled,
and keep the "collect ~20 before next run" rule.

**5. Competitor complaint mining (agent-fills)** → name **at least 1 exploitable gap**, or an
honest "none found."

**6. Synthesize under exactly three headings — wants / fears / objections.** A flat quote dump
fails. Cross-check against the `avatar` card — a contradiction is surfaced, never silently
resolved either way.

**7. Record time spent.** Re-run per campaign / on the 30-day staleness clock.

### 🔴 Data boundary (same as p02)

The pipeline does not read reel comment text or DMs (FRFRMU-904, parked). Comment/DM quotes
come only from the creator pasting or an external source — **never claim the pipeline
collected them.** Analysed reels' CLASSIFICATION tags (intent/angle/hook_promise) ARE a
legitimate source — what competitors PROMISE in hooks = what the audience wants — labelled
`rm_classification`, never presented as a customer's own words.

### What this step refuses to do

Paraphrase a quote and present it as verbatim · invent a source · skip the 2-4-star lens ·
claim the pipeline read comments or DMs · flatten wants/fears/objections into one undifferentiated
list.

### Save it

Write the result to the Creator Brief as the Foundation card key `prospect_research`
(FRFRMU-1042 shape), sharing the ONE quote-store shape p02's `avatar` card uses — never a
second quote system:

```
{
  "card": "prospect_research", "title": "What they want, fear, and why they don't buy",
  "status": "confirmed",
  "summary": "<the top want/fear/objection + the one competitor gap>",
  "items": [
    {"item_id": "want_01", "label": "Want", "tag": "want", "text": "<verbatim quote>",
     "who": "agent", "provenance": "FROM-EXPERT", "source": "review:<url>"},
    {"item_id": "fear_01", "label": "Fear", "tag": "fear", "text": "<verbatim quote>",
     "who": "agent", "provenance": "FROM-EXPERT", "source": "web:<url>"},
    {"item_id": "objection_01", "label": "Objection", "tag": "objection",
     "text": "<verbatim quote>", "who": "you", "provenance": "FROM-EXPERT",
     "source": "user_pasted"},
    {"item_id": "competitor_gap", "label": "Exploitable competitor gap",
     "text": "<the gap, or 'none found'>", "who": "agent", "provenance": "FROM-EXPERT"}
  ],
  "updated_at": "<ISO date>"
}
```

At least 5 sourced quotes per heading (`tag`: `want`/`fear`/`objection`), or an honest count
with the reason when the landscape is thin.

## Wire into

* **Outline recipe (`step-08-outline-recipe.md`):** the `objection` beat's content comes from a
  cited `prospect_research` objection when the card exists. No `prospect_research` key →
  that beat is unchanged (still a label with no content source, exactly as today).
* **CTA recipe (`step-08-cta-recipe.md`):** an activation reel handles the top objection before
  the ask, when `prospect_research` exists. Absent → unchanged.
* **Step 5 differentiate:** the named competitor gap feeds a first-party differentiation angle.
* **Research-exists gate:** `check_research_behind_copy`
  (`backend/app/services/reach/plan_validator_checks_foundation_research.py`) flags a plan whose
  objection beat or activation CTA has no `prospect_research` behind it — advisory today, under
  `PLAN_VALIDATOR_FOUNDATION_MODE`.
