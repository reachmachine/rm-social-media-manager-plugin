> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 3.11**, during the analysis wait, when an offer exists
> (`offer_stack`/`grand_slam_offer`) and `proof_bank` is missing or the creator asks to add to
> it. This is p29 "Collect Proof & Testimonials"
> (`marketing/rules/process-cards/p29-collect-proof-testimonials.md`, FRFRMU-1067): work the
> ladder top-down, never manufacture, ship with whatever rung exists and keep climbing.

## Step 3.11 — Build the proof bank (p29)

**Ask per `asking-rules.md`.**

**Don't let "I have no testimonials yet" stop anything.** Collect proof from the strongest kind
down to the easiest, record who said it and when, and make sure every claim-carrying reel later
carries at least one real piece of proof.

### 1. Inventory first, never re-ask

Pull first-party proof already on file (intake, `step-01-intake-fields.md`), beta results
(`ask_campaign`, p22/FRFRMU-1057), client wins the creator mentioned, and own reels with `won`
verdicts (FRFRMU-1062 — a real performance number proves the CONTENT, never the offer; label it
`source_event: own_reel`).

### 2. The ladder, top-down — for each rung, what exists and what to ask for

- **Results testimonials** — **exact words only**, permission required, a regulated-niche
  disclaimer flag (health/finance/legal from the intake constraints).
- **About-you** — the accelerator ask: *"would you mind a sentence about working with me?"* to
  people the creator has done business with.
- **Authority endorsement** — a target list; expect most to say no; log the attempt anyway.
- **Statistic** — the agent hunts (web) and cites the source + date; never a number with no
  source.
- **Authority quote** — reinforces the action asked, never invented.

### 3. Testimonial ask drafts — agent drafts, creator approves AND sends

**The plugin never sends anything.** Draft the ask, status `drafted → approved_by_user →
sent_by_user`; a draft that has not been sent is not a proof element yet.

### 4. Give-away-for-review plan (agent proposes, creator approves)

Free copies/sessions in exchange for an honest review; note platform disclosure rules where they
apply.

### 5. The attempt log is honest

"Asked 4, got 0" is a row, not a gap hidden. Every rung gets an attempt entry even when nothing
came of it.

### 6. Save

Creator Brief key `proof_bank` (schema-free — no reserved-key shape check; it is read
defensively by the copywriter's claim-detector, `skills/rm-copywriter/proof-and-claims.md`):

```
{
  "elements": [
    {"id": "proof_1", "rung": "results_testimonial", "text": "<exact words>",
     "who": "<the person's name/handle, on file — never invented>", "when": "<ISO date>",
     "verifiable_how": "url|screenshot|dm_ref", "permission": {"granted": true, "date": "<ISO>"},
     "regulated_disclaimer_required": false, "source_event": "beta", "used_in": []}
  ],
  "attempts": [
    {"rung": "authority_endorsement", "asked_n": 4, "got_n": 0, "date": "<ISO>",
     "note": "no replies yet"}
  ],
  "asks": [
    {"target": "<who>", "draft": "<the ask text>", "approved_by_user": false,
     "sent_by_user": false, "status": "drafted"}
  ],
  "giveaway_plan": null,
  "updated_at": "<ISO date>"
}
```

### What this step refuses to do

Paraphrase-up a testimonial past trimming · manufacture a result, statistic or quote · send an
ask itself (drafts only) · hide a failed attempt instead of logging it · present own-reel
performance as proof of the offer's results.

### Success criteria (falsifiable)

Every rung has at least one element or one logged attempt (including 0-result rows) · every
element carries who/when/verifiable_how · every results testimonial has `permission.granted` ·
the copywriter's `check_claims_have_proof`/`check_price_claims_supported`
(`backend/app/services/reach/plan_validator_checks_foundation_copy.py`) find a `proof:<id>` or a
rewritten line for every claim-carrying reel in the next plan.
