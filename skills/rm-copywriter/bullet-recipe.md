# Bullet recipe — feature + benefit + meaning (FRFRMU-1059, p24)

**Never list what a thing IS.** Say what it does, then what that means to the
person: *"it [does this], so you can [get this], which means [the
feeling]."* This runs on any block the planner flagged
`carries_value_lines: true` (`step-08-outline-recipe.md` S.3's `list_item`
beats, `step-08-caption-recipe.md` C.3's body) — an unflagged block is not
this recipe's job.

## 1. Feature inventory

Pull from `offer_stack.deliverables` / `bonuses` (FRFRMU-1049/1052) when an
offer exists. For a non-offer reel, the flagged beat's teach points are the
"features" (what the method/step does).

## 2. Why-drill ×3 per feature

Ask "why does that matter?" three times. The THIRD answer is the meaning —
it must land in love/status/relief territory, specific to the avatar
(FRFRMU-1031), never a restated benefit:

1. *It has a prompt library.* Why does that matter? → *So you write faster.*
2. Why is that important? → *So you're not stuck starting from a blank page
   every session.*
3. Why is that a big deal? → *Which means your evenings are yours again,
   not spent staring at a cursor.* ← the meaning.

## 3. Write the line

*"It [feature], so you can [benefit], which means [meaning]."* Anchor the
feature to something concrete — a number, a step, a timestamp
(`rules/copywriting.md` S9) — never a vague adjective.

## 4. Overproduce, then cut

Write **2× the lines needed** (10-12 for 5-6 kept). Keep the best; the cut
list stays in the pack's working notes, same convention as the hook
candidates (FRFRMU-1058) — auditable, never shown to the creator as-is.

## 5. Spread check

The kept lines cover **≥2 reason types beyond money** (p06's 11 buying-
reason types, FRFRMU-1041) — an all-money set of bullets is a warning, not
a fail, but it is flagged.

## 6. Honesty screen on the meaning clause

The "which means" clause must be a real, deliverable feeling — never a
guaranteed outcome. ✅ *"which means your evenings are yours again"* — ❌
*"which means you'll never lose a client again"* (Gate 1's wording rule,
applied to the clause specifically, not just the headline claim).

## 7. One promise per asset

Every kept line serves the SAME promise (FRFRMU-1056) — bullets don't
scattergun three different pitches inside one reel.

## Validator (advisory)

- `check_bullets_three_layers` — **hard.** Every line on a
  `carries_value_lines: true` block has all three layers (a feature clause,
  "so you can"/equivalent, and "which means"/equivalent). A two-layer line
  (feature + benefit, no meaning) fails.
- `check_bullets_overproduced` — the pack's working notes show 2× the kept
  count was written; 6 written for 6 kept fails.
- `check_bullets_spread` — warning-only: fewer than 2 non-money reason
  types across the asset's kept lines.

## Guardrails

- The copywriter never decides WHICH beats carry value — only the
  planner's `carries_value_lines` flag triggers this recipe.
- Meanings are cited to their source (`offer_stack`/`why_people_buy` item
  id), never invented from the agent's own vocabulary.
- The meaning clause passes the Gate 1 screen — no guaranteed outcomes, no
  income promises, even a soft one.
