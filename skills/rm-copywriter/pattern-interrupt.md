# Pattern-interrupt creative — curiosity line + right-people test (FRFRMU-1069, p31)

For a cold/young `reach` reel whose planner-built matrix cell
(`step-08-visual-recipe.md` V.2b) was picked: write the curiosity line and
prove it stops the RIGHT person, not everyone.

**Meta ad creative is out of scope.** The matrix cell may be exported as an
ad-creative brief for the creator's own use, advisory only — this skill
never produces ad copy or touches ad spend.

## 1. The curiosity line (S28 shape)

Emotional grab → curiosity gap → one CTA. The line uses the matrix cell's
`phrase_source` (the avatar's own words) and names or implies the picked
`visual_concept` — it never explains the gap away (Gate 1's curiosity
rule, unchanged).

## 2. Question-form fallback (fills 1058's thin-data fallback family)

When the data is too thin for a template-driven hook on a reach slot, add
*"Are you tired of ___?"* to the classic-shape fallback list
(`step-08-hook-recipe.md` H.2b) — labelled FROM-EXPERT, filled from the
avatar's own escape phrase, never a generic complaint.

## 3. The right-people test

**A cold reach reel must pre-qualify, not maximise stops.** The right
person recognises themselves (a `you_are` callout, the avatar's own
phrase); the wrong person scrolls on. Self-check + critic, logged
`prequalifies: true|false` with HOW — naming the specific line/visual that
does the qualifying. `prequalifies: false` on a cold-account reach slot is
a hard fail; it cannot ship.

## 4. Fatigue — creative first, not the line

When a cold-reach pattern's lift over the creator's own median shrinks
(H.6 counts it, never predicts it), the refresh order is **creative
(visual) first, then the line, then the template** — FRFRMU-1054's order,
applied here specifically because a reach slot's job is visual attention
first.

## Validator (advisory → hard for the right-people test)

- `check_prequalifies` — **hard.** A cold/young-account `reach` slot with
  `prequalifies: false` cannot carry `status: shippable`.
- `check_visual_rationale_stated` — a picked matrix cell's line/visual
  cites the cell's `visual_rationale`; a line with none fails.
- `check_no_meta_ad_output` — this skill's output never includes an
  ad-platform artifact (campaign, ad set, ad copy targeted at spend) — a
  warning if one appears, since it signals scope creep into 1039's
  server-side Ad Library work.

## Guardrails

- Gate 4: model the visual pattern, never copy a competitor's exact look.
- The reel still pays off the curiosity hook (FRFRMU-1060's `pays_off_at`).
- Sensational or health imagery stays under Gate 1's compliance screen —
  a pattern interrupt is odd/concrete, never shock-for-shock's-sake in a
  regulated domain.
