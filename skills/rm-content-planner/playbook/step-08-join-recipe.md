> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

> **Load now:** with the other Step 8 recipes, BEFORE filling a slot's hook, caption, CTA or
> outline — this file decides WHICH foundation-card material each block reaches for once the
> FORM (Layer 1) is already chosen.

## Step 8 (join) — Idea from the cards; pattern from the tool (FRFRMU-1032)

**Ask per `asking-rules.md`.**

**The founder's own words, recorded verbatim as this recipe's acceptance intent:** *"idea comes
from here while the pattern comes from our tool."* `step-05-differentiate.md`'s Reel Bet already
says the same thing structurally — **Proven Pattern × First-Party Topic × Audience Tension** —
and the near-clone test already treats a proven pattern filled with first-party substance as
**modelling**, never mimicry. This file is the missing mechanical join between the two: it is a
recipe, not a principle, because an agent follows procedures, not intentions.

## Layer 1 — the pattern (already specified, unchanged)

The hook template, structure, CTA type/placement, angle, intent, format, timing, and topic
DIRECTION are chosen from data — `step-03-data-recipes.md`, `step-03-mcp.md` §C/§F,
`step-07-strategy.md` 7.3, and each `step-08-*-recipe.md`. **Nothing in this file changes WHICH
form is chosen.** Substance never overrides a form choice — you fit the story into the proven
template, never the reverse.

## Layer 2 — the read-map: which card, which field, which tag

For each substance-bearing foundation card, read this table before drafting a slot. **Absent →
skip honestly, never invent.** Every read is cited `card` + `field` + `substance_provenance`
(`first_party` the creator's own confirmed fact, `from_expert` the card's method — NEVER
`data_driven`, see the two-receipt shape below).

| Card | Brief key | Field read | Provenance | Floor |
|---|---|---|---|---|
| Avatar (p02) | `avatar` | `items[].text` tagged `pain`/`pleasure` | `first_party` | ≥12+12 phrases |
| Congregations (p03) | `congregations` | `items[].text` (niche vocabulary, seeds) | `first_party` | ≥10 congregations |
| Prospect research (p04) | `prospect_research` | `items[].text` tagged `want`/`fear`/`objection`/`gap` | `first_party` (`review:<url>`/`web:<url>`/`user_pasted` as the finer tag) | ≥5 quotes/heading |
| Big Domino (p08) | `big_domino` | the headline belief | `from_expert` | one stated belief |
| Origin story (p10) | `origin_story` | `cuts.reel_30s` or a longer cut | `first_party` | the 8-beat form filled |
| False beliefs (p11) | `false_beliefs` | `core_three` rows | `first_party` (the belief) | ≥3 core rows |
| Proof bank (p29) | `proof_bank` | `elements[]` (exact words) | `first_party` | ≥1 permissioned element |
| Offer (p15-p21) | offer brief keys (FRFRMU-1049-1056) | name / promise / stack line | `from_expert` | the offer brief exists |

## Layer 3 — the join, per slot

**1. Which substance type, by funnel role** (the founder's own slot-filling rule):

| Slot role | Topic DIRECTION (Layer 1, data) | SUBSTANCE (Layer 2, this file) |
|---|---|---|
| **Reach** | the proven/trending direction for the reach slice | `avatar` **wants** + the creator's own take/proof on that direction (modelling, not a clone) |
| **Nurture** | nurture-slice patterns (comments-driven, etc.) | `prospect_research` **fears** + `origin_story`/`false_beliefs` — the tension and the story |
| **Activation** | activation-slice patterns, CTA types that convert | `prospect_research` **objections** (handled before the CTA) + offer/`proof_bank` |

**2. Order of operations, every slot:** choose the FORM from data first (template, structure,
CTA type/placement, angle, timing) → THEN select the substance that fits that form and role →
THEN draft, with the caption recipe's wording rules (`step-08-caption-recipe.md`) outranking on
phrasing. Reversing this order — picking a template because it "fits the story" — is a Layer 1
violation, not a join decision.

**3. The two-receipt shape — both mandatory when substance material exists (Layer 2 present).**
Every slot carries:
- one **`pattern` receipt** — the existing FORM receipt (`hook_template`/`structure`/
  `cta_pattern`/etc, `receipt_kinds.py`), unchanged, stored on `reel.receipt`.
- one **`substance` receipt** — `{kind: substance, card, field, substance_provenance, n: 1}`
  (`receipt_kinds.py`'s twelfth kind), stored on `reel.substance_receipt`.

A slot with a pattern receipt and no substance receipt is **library-only** — "trending, but
nothing about your product," the founder's original complaint, and `check_slot_has_both_receipts`
(`plan_validator_checks_foundation_join.py`, advisory) flags it. A slot with substance and no
proven pattern is **research-only** — allowed ONLY as a labelled Step 7.4 test, never presented as
proven; the same check flags an undeclared one. **A substance receipt tagged `data_driven` is a
validator failure on its own** (`check_substance_not_data_driven`) — substance is never a
frequency claim.

**4. The near-clone test still applies at the join** (Gate 4, `step-05-differentiate.md`): same
hook + structure + topic as a source reel is a clone regardless of a substance receipt sitting
next to it. First-party substance is what turns a proven pattern into modelling — it does not
waive the three-match test on its own.

**5. Three commercial jobs, not just reach.** Where the goal calls for them, nurture and
activation slots must carry nurture/sell substance (fears+story; objections+offer) — a plan
whose foundation cards are filled but only its reach slots consume them is the same failure in a
different shape (RED per the acceptance intent above).

## Guardrails

- **Substance is real, never invented.** Every field cited above traces to a confirmed, filed
  foundation key — no drafted-but-unconfirmed phrase, no imagined quote (the card's own
  ask-user/agent-drafts-then-confirms split already enforces this upstream).
- **"The wait is the budget."** While competitor analysis runs, do the Phase-3 substance intake
  instead of idling on `get_job_status` — Phase 3 needs no data.
- **Step 5 entry gate** (`step-05-differentiate.md`): substance keys (or explicit skips with
  reasons) AND `get_analysis_coverage` showing the analysed set the strategy cites — absent
  either half, the matching GENERIC stamp applies.
- **Role-ordering rule** (`step-07-strategy.md`): reach slots lean earliest in the month, nurture
  and activation slots run once the reach/tension groundwork is laid — additive to the existing
  funnel-mix rule, never overriding it.

## Validator (advisory, `PLAN_VALIDATOR_FOUNDATION_MODE`)

- `check_slot_has_both_receipts` — a slot with a pattern receipt and no substance receipt (or the
  reverse, undeclared) is flagged. Guarded: [] on a plan with no substance material filed at all.
- `check_substance_not_data_driven` — a `substance_receipt.substance_provenance` of `data_driven`
  fails outright. Guarded the same way.
