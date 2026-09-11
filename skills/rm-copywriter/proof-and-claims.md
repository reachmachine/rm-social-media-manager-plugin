# Proof and claims — the claim detector (FRFRMU-1067, p29 part C)

The planner collects proof (Step 3.11, `proof_bank`). **This file is what
YOU do with it: every claim you write must cite a proof element, or it does
not ship as written.** A claim with nowhere to point is not a smaller claim
— it is a rewrite.

## The rule

Before a block (script beat, on-screen line, caption, DM script) ships, walk
its text for a CLAIM — a result, a number, "clients say", a testimonial, a
specific price or earnings figure. For every claim found:

1. **Look it up in `proof_bank.elements`.** A match → cite it as
   `source_ref: proof:<id>` on the block. The plan validator's
   `check_claims_have_proof` / `check_price_claims_supported`
   (`backend/app/services/reach/plan_validator_checks_foundation_copy.py`)
   read this exact reference shape — get the prefix right (`proof:`, not
   `proof_id:` or a bare id) or the reference silently fails to resolve.
2. **No match → rewrite the line.** Either as a process/dream statement
   ("here's the exact process I use with every new client" — no longer a
   claim) or grounded in a cited statistic (`rules/copywriting.md` S14) with
   its own source and date. **Never ship the original claim unbacked.**
3. **`proof_bank` missing entirely** (the planner hasn't run Step 3.11 yet)
   → every claim in the pack is treated as unbacked; rewrite all of them.
   This is the same "absent → fail, not skip" reading the backend check
   uses — a plan with an offer and zero proof collected is not silently
   exempt.

## Exact-words rule (results testimonials)

A `results_testimonial` element's `text` field is quoted **verbatim**. You
may trim it (cut a sentence, shorten with an ellipsis) but never paraphrase,
strengthen, or add a word that was not in the original. An edited-beyond-
trimming testimonial fails `check_claims_have_proof` the same as an
unbacked one — the exact-words rule is absolute (Gate 1, `rules/
copywriting.md` S14).

## Regulated-niche disclaimer

When a cited element carries `regulated_disclaimer_required: true`, the
caption for that reel must carry the disclaimer text (from the intake
constraints, health/finance/legal). A regulated claim shipped without its
disclaimer fails, same severity as an unbacked claim.

## Own-reel performance is never offer proof

A `won`-verdict reel (FRFRMU-1062, `source_event: own_reel`) proves the
CONTENT worked — it is never cited as proof the OFFER works ("this reel got
40k views" is not evidence the program gets results). Do not cite an
`own_reel` element against a price/earnings claim; it is only valid material
for a content-performance claim ("this is one of our most-watched reels").

## The `proof` block skeleton (fills `block-skeletons.md`'s `proof` beat)

The `proof` beat in a reel script reads `proof_bank.elements`, picks the
rung that fits the slot (a `results_testimonial` for an offer/stack reel, a
`statistic` for a nurture/thirsty-content reel), and writes it per the rule
above — exact words, cited, disclaimer where required. No matching element
→ `[GAP: needs p29 proof]` stays, same convention as every other unfilled
block (`block-skeletons.md` §Draft-pass rules).

## Guardrails

- The plugin never contacts anyone and never marks an ask `sent_by_user` —
  that status is set only by the creator, off-platform.
- A `giveaway_plan` is proposed, never executed, by this skill.
- Testimonials and proof are other people's words — never invent a name,
  handle, or quote for a fixture, an example in this file, or a commit
  message. Every real example in `proof_bank` carries `permission.granted`.
