> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 4.6**, after Step 3's analysis lands — the pattern for a belief-breaker
> reel cannot be chosen before the reels are analysed; the beliefs can (the founder's exact
> point, dependency-audit 2026-09-06). Completes p11 "Map False Beliefs + Build a Story Bank"
> (`marketing/rules/process-cards/p11-map-false-beliefs-story-bank.md`, FRFRMU-1045) — the MAP
> half already ran at `step-03-10-false-beliefs-map.md`.

## Step 4.6 — Does belief-breaking work here? What form? (p11, form join)

**Refuses to run without `get_analysis_coverage` showing an analysed set** — the form is chosen
from data, never from taste.

### 1. Does it lift?

`get_theme_lift(dimension=angle)` for `myth_busting`, with `n` and reliability.

- **Strong lift** → belief-breakers run as a full pillar (7.5 reads this).
- **Weak lift** → the three doubts are STILL covered (Secret #10 — never optional), but in the
  form the data prefers: a `demo` reel for the Internal doubt, a `proof` reel for Vehicle.

### 2. What form

Hooks library → `myth_buster` hook shapes. `get_content_structures` → the proven beat order for
a belief-breaker (typically hook → `myth_bust` → `story_setup` → `story_turn` → `proof`). **The
belief and the story are the creator's; the form is the data's.**

Near-clone test (Gate 4) applies exactly as it does to any reel — model the structure, never
quote a competitor's myth-bust line.

### Save it

Merge into `false_beliefs` (same key from the map step): add
`{"item_id": "form", "label": "Form this niche proves", "text": "<lift + structure + hook shapes>", "who": "agent", "provenance": "DATA-DRIVEN", "used_in": ["n=<count>"]}`.

### What this step refuses to do

Choose a form before `get_analysis_coverage` shows an analysed set · quote a competitor's
myth-bust line verbatim · skip the three-doubts coverage because the lift is weak.

### Wired in (each does nothing when `false_beliefs` is absent)

`step-08-outline-recipe.md` S.3 (`myth_bust`/`objection` beats read rows by `item_id` — the
SINGLE content owner; `prospect_research` and `magic_desk` reference these, never a second list)
· `step-07-strategy.md` 7.5 (belief-breakers as a bounded pillar) and 7.7 (the origin → vehicle
→ internal → external 4-reel series option) · `check_all_three_doubts_covered` (advisory
validator — a plan with only "does it work" reels and no Internal/External doubt reel is
flagged) · `step-12-after-the-save.md` (the living-map paragraph).
