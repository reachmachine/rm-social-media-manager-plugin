# The countable-check registry — the table (split from RULES_GATE.md, FRFRMU-1032)

> **This file holds only the table.** The rules for why the registry exists, what "where it
> runs" means, and how a missing row is treated all stay in `RULES_GATE.md`'s
> "The countable-check registry" section, right above the pointer to this file — read that
> first. `RULES_GATE.md` was carrying both the prose and this ~40-row table and had grown past
> the 300-line skill-file limit; this split moves only the table, so nothing about the eight
> gates or their ids changed.

> **Gate → check mapping (FRFRMU-1104).** The "Where the rule is written" column names the gate
> that OWNS each check, and the server holds the same mapping in
> `backend/app/services/reach/rules_gate_record.py` (`GATE_TO_VALIDATOR_CHECKS`). That is what turns
> a `"pass"` claimed over a live blocker into a recorded contradiction. A blocker-capable check
> missing from the server map can never be caught — which is exactly what happened to
> `anchor_exception`, listed as Gate 6 in this table but mapped to no gate in the code. A backend
> tripwire test now goes red if a blocker-capable check has no gate.

| Check | What it counts | Where it runs | Where the rule is written |
|---|---|---|---|
| Effort ≤ capacity | each week's summed effort vs `capacity.reels_per_week` | validator `effort_within_capacity` (blocker) | Gate 8 · `step-08-deliverable.md` 4 |
| Every field present | every required reel field, all 4 hook layers | validator `reel_completeness` (blocker) | Gate 2 · `TEMPLATE.md` C1 |
| Provenance is earned | a DATA-DRIVEN reel needs `receipt.n ≥ 5` + a median, OR a `retrieved_exemplar` receipt (provenance, honest n=1) | validator `provenance_integrity` (blocker) | Gate 7 |
| Provenance split honest | the claimed split vs the reels' real tags | validator `provenance_split_honest` (blocker) | Gate 7 · `TEMPLATE.md` E1 |
| ≥3 source accounts | distinct `receipt.source_handle` values | validator `min_source_diversity` (blocker) | Gate 8 |
| Plan size honest | strong reels available vs requested size | validator `plan_size_honesty` (blocker) | Gate 8 · `step-08-deliverable.md` 4 |
| No banned claims | guaranteed-result / income tags | validator `no_banned_tags` (blocker) | Gate 1 |
| Placeholders flagged | invented content without `needs_real_content` | validator `no_unflagged_placeholder` (blocker) | Gate 1 · `step-08-deliverable.md` 1 |
| Activation plumbing | `keyword_dm` / `lead_magnet` asks vs built-AND-tested assets | validator `activation_needs_plumbing` (blocker) | Gate 5 · `step-08-cta-recipe.md` CT.2 |
| Receipt kind fits the claim | each receipt's `kind` + per-kind fields + `metric_used` | validator `receipt_kinds` (blocker) | Gate 7 · every recipe's receipt table |
| Anchor exception declared | a week off the declared mix with no anchor | validator `anchor_exception` (blocker) | Gate 6 · `step-12-capture.md` 2 |
| Funnel mix delivered | reach / nurture / activation counts vs the declared % | validator `funnel_mix_delivered` | Gate 6 |
| Cadence by date | dated slots per week vs `cadence.per_week` | validator `cadence_by_date` | Gate 6 · `step-12-capture.md` 2 |
| Pillar mix delivered | slots per pillar vs the declared split | validator `pillar_mix_delivered` | Gate 6 · `TEMPLATE.md` A5 |
| Series consistency | a series keeping the same weekday | validator `series_consistency` | Gate 6 |
| Variety | one hook / structure / angle repeated past ~60% | validator `variety` | Gate 8 |
| Self-cannibalization | two reels chasing the same `topic_idea` | validator `self_cannibalization` | Gate 8 |
| Producible format | each `reel.format` vs `production_capability` | validator `producible_format` | Gate 8 |
| Language set | `meta.language` present | validator `language_set` | Gate 8 |
| Subject check | `meta.subject_handle` / `subject_type` vs the intake | validator `subject_check` | Gate 6 |
| Intake completeness | the intake score vs the floor | validator `intake_completeness` | Gate 6 · `step-01-intake.md` |
| Assumptions disclosed | recorded assumptions vs `section_00.assumptions` | validator `assumptions_disclosed` | Gate 6 · `TEMPLATE.md` A0 |
| Retrieved hook wording clone | a retrieved hook's wording vs the exemplar(s) it cites, alone (no structure/topic needed) | save-time check (`hook_clone_check`, warn only) | Gate 4 · this file |
| Receipts verified | claimed `n` / `median` vs this workspace's real data | save-time check (`verify_receipts`) | Gate 7 · Step 11.0 (G207) |
| Claim backed by call | a claimed `checked_*` status vs this session's real tool-call journal | save-time check (`claim_backed_by_call`) | Gate 7 · `rigor-rules.md` §K (FRFRMU-1539) |
| One conversion action | every `activation` row's ask pointing at the SAME action | gate box | Gate 5 · `step-08-cta-recipe.md` CT.1 |
| Plumbing, ask by ask | each row's ask vs the asset behind it | gate box | Gate 5 · `step-08-cta-recipe.md` CT.2 |
| Caption CTA echo | each caption's ending vs that row's `cta` / `cta_type` | gate box | Gate 5 · `step-08-caption-recipe.md` C.3 |
| Watch-these links | ≥2 exemplar links per row, from the right slice | gate box | Gate 8 · `step-08-visual-recipe.md` V.2/V.4 |
| Tags per row | 3-6 tags, each with a nameable role | gate box | Gate 8 · `step-08-hashtag-recipe.md` HT.3 |
| Sound is deliberate | a real audio entry on every music-led slot | gate box | Gate 2 · `step-08-audio-recipe.md` A.1 |
| Named sound has a receipt | band + count + coverage figure + corpus label | gate box | Gate 7 · `step-08-audio-recipe.md` A.3/A.4 |
| Hook template receipt + rotation | each row's `hook_template` receipt; the month's rotation labelled | gate box | Gate 2 · `step-08-hook-recipe.md` H.5/H.6 |
| Cooldown honored | repeats of the last plans' topics, each a series or a stated sequel | gate box | Gate 8 · `step-05-differentiate.md` 5.1 |
| Idea carries a topic receipt | rows with a `topic` receipt, or a declared test slot | gate box | Gate 7 · `step-05-differentiate.md` 5.2a |
| Reasoning block complete | slots carrying all three Reasoning lines | gate box | Gate 7 · `step-08-reasoning-recipe.md` R.1-R.3 |
| Receipts match provenance | `data_driven` slots lacking receipts — must be ZERO | gate box (leans on validator `receipt_kinds`) | Gate 7 · `step-08-reasoning-recipe.md` R.1 |
| Expected outcome shape | slots whose outcome line is neither a base rate nor "Testing" | gate box | Gate 1 · `step-08-reasoning-recipe.md` R.2 |
| Goal-served totals | goal lines counted by goal vs the funnel mix | gate box (piggybacks validator `funnel_mix_delivered`) | Gate 6 · `step-08-reasoning-recipe.md` R.3 |
| Slot has both receipts | a `pattern` receipt with no `substance` receipt, or the reverse undeclared | validator `slot_has_both_receipts` | Gate 7 · `step-08-join-recipe.md` |
| Substance never DATA-DRIVEN | a `substance_receipt.substance_provenance` of `data_driven` | validator `substance_not_data_driven` | Gate 7 · `step-08-join-recipe.md` |

