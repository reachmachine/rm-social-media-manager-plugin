# Flop diagnosis — the 8-item checklist, in order (FRFRMU-1076, p64)

*"When a reel flops, don't throw it away — check eight things in order, fix
the first one that fails, and measure that one fix. Most flops need one fix,
not a rebuild."*

**This is the single owner of the flop-diagnosis order.** `qa-checklist.md`
(FRFRMU-1065) originally sketched a 5-step order; this ticket SUPERSEDES it —
`qa-checklist.md` now keeps only the trigger wiring (hand off here on a `lost`
verdict) so there is one owner, not two disagreeing orders.

## A. Trigger — honestly, on the account's OWN bar

A reel gets diagnosed when its verdict is `lost` (read from the reel profile,
FRFRMU-1062 — below the account's OWN median on the stage-appropriate metric,
after the sample floor), **or** the creator asks *"why did this flop?"*.

**A cold account's reel is never flagged on hour-1 views.** The stage-metric
rule (`rigor-rules.md` §H) applies here exactly as it does everywhere else —
noise on a thin account is not a diagnosis.

## B. The eight checks, in order — one verdict + one line of evidence each

Each item gets `pass | fail | n/a` plus **one line of evidence** — a receipt,
a beat, a proof id. **"The reel feels weak" is not a verdict.** `n/a` is for
an item that genuinely does not apply to this reel type (a reach reel has no
price to check).

1. **Hook** — is there one? about THEM, not the creator? a clear
   benefit/curiosity? Evidence: cite the hook line + its receipt
   (`hook-variants.md`, FRFRMU-1058/1060); compare against this month's
   winning hooks.
2. **Offer clarity** (activation/nurture reels) — does the viewer know what
   they get, how, when, what it costs? Evidence: the offer brief
   (FRFRMU-1055).
3. **Reason to act now** — a REAL bonus / REAL deadline / REAL limit present?
   Evidence: FRFRMU-1050. **Never fake one to fix a flop** — the fix for this
   item is a real scarcity fact or nothing.
4. **Emotional driver** — fear, desire, curiosity, pain, pleasure,
   satisfaction, dissatisfaction — is one actually present in the first 5
   seconds? Evidence: cite the opening beat (`promise` FRFRMU-1056 /
   `magic_desk` tension FRFRMU-1037).
5. **Bullets / value lines** — features or benefits + meaning, not a flat
   feature list? Evidence: `bullet-recipe.md` (FRFRMU-1059).
6. **Price vs perceived value** (activation reels only) — too high, or
   "selling dollars for dimes"? Evidence: the value-stack multiple
   (FRFRMU-1048/1049).
7. **Visuals** — on-screen text legible / in safe zone, a strong first frame,
   a pattern-interrupt on a cold-account reel? Evidence: `qa-checklist.md`'s
   safe-zone check (`SAFE_ZONE_CONFIG`) + `pattern-interrupt.md`
   (FRFRMU-1069) for the matrix cell.
8. **Proof** — a real proof element present wherever a claim is made?
   Evidence: `proof-and-claims.md` (FRFRMU-1067).

## C. Fix the FIRST failure only — one change, one test

Stop at the first `fail`. The copywriter drafts **exactly ONE change** for
that item — copy-pack **v+1** (`block-skeletons.md`'s versioning). Two items
changed in the same version is not a fix, it is a rewrite wearing a fix's
name, and the re-test becomes uninterpretable (the p63 one-variable rule).

The planner writes **one** p63 test-ledger row (FRFRMU-1075's shape):
variable = the failing item, control = the flopped version, challenger = the
fix, metric + floor + disproof carried over from the original slot. **If the
FRFRMU-1075 ledger key does not exist yet on this branch** (it is being built
in a parallel lane), this step becomes `[GAP: needs FRFRMU-1075 ledger key]`
on the diagnosis block — never an invented ledger shape.

The reel keeps its `reel_uid` (FRFRMU-1063) and its full history — a fix is a
new version of the SAME reel, never a new one.

## D. Re-test, then escalate to rebuild only if it still lags

Re-test on the same metric and floor the original slot used. **Rebuild is
recommended only when every applicable item passes the checklist AND the
re-tested numbers still lag.** The agent recommends a rebuild; the creator
decides — the agent never scraps an idea on its own. The recommendation must
cite the completed (all-pass) checklist and the numbers, not a hunch.

## E. Where it lives

- The diagnosis block on the reel profile (FRFRMU-1062 §6, "what we learned")
  — the 8 verdicts + evidence, the one item fixed, and the ledger row.
- The p63 ledger row (FRFRMU-1075).
- `hook_history` / `topic_history` entries where the fixed item was the hook
  (`hook-variants.md` §E's `audience_note` carries the diagnosis).

**Open word question, not resolved here:** `topic_history` uses the verdict
word `flopped`; the reel profile and this file use `lost`. One word for both
ledgers is a founder call this file does not make on its own
(`creator_brief_reserved_keys.py`'s own docstring names the same open item).

## Guardrails

- Headline first, always — item 1 is checked before anything else, no
  skipping ahead because "the hook is obviously fine."
- One fix at a time (the p63 one-variable rule) — no exceptions for a flop
  that "obviously" has two problems; fix the first one, re-test, then move
  to the next `fail` if the first fix didn't clear it.
- Item 3's fix always obeys FRFRMU-1050 — never a fake deadline or limit to
  rescue a flop.
- Stage-appropriate trigger only — never hour-1 views on a cold account.
- The creator decides rebuilds; the agent never scraps an idea alone.
- "Feels weak" is never a verdict — every item carries evidence.

## Validator (advisory)

- `check_flop_diagnosis` — a `lost` reel that was rewritten must have an
  8-item diagnosis block with evidence, or the rewrite is flagged. **The
  rewrite must change exactly one item** — a copy-pack version bump touching
  two or more of the eight items' source material fails this check. A
  rebuild recommendation with no completed (all-pass) checklist attached
  fails. A fix that adds a scarcity/deadline claim not present in
  FRFRMU-1050's real-limits record fails.
