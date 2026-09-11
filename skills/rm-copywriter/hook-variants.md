# Hook variants — permutation generators, truth check, payoff, ledger (FRFRMU-1060 parts B-F)

The planner (Step 4.8) hunts for the creator's surprising TRUE facts and picks
ONE hook line (`step-08-hook-recipe.md` H.2b/H.4, FRFRMU-1058). **This file is
what YOU do with that line: write several variants inside the LEGAL framework
row (`correlation-table.md`), check every element is owned, and log every
variant's result.** Part A (the hidden-story hunt that fills `hook_facts`) and
the H.2 saturation count are the planner's — this file never mines facts on
its own, it only uses what `hook_facts` already holds.

## B. Permutation generators — S29's two shapes, filled ONLY from `hook_facts`

Alongside the data templates and the fallback families (`step-08-hook-recipe.md`
H.2, `rules/copywriting.md` S6), two FROM-EXPERT permutation shapes
(`rules/copywriting.md` S29) are legal generators when the slot's
`hook_subcategory` allows them (`correlation-table.md`'s `unlikely_character`
and `result_minus_pain` rows):

| shape | slots the elements fill | legal for |
| --- | --- | --- |
| Unlikely Character + Timing + Result | an unlikely subject, a timeframe, a concrete result — in that order | `results`, `twist` |
| Result + Timing − Pain | the after-state, the timeframe, the friction removed, named explicitly | `transformation`, `shortcut` |

Every filled slot cites the `hook_facts` entry it came from:
`{fact_id, kind}`. A shape with an empty slot and no matching fact is not
written — note the gap instead of inventing a filler ("no owned fact for the
timeframe slot yet").

## C. Truth check per element — the hard line

**Every hook element that is a number, a timeframe, a named person, or a
result must resolve to a `hook_facts` entry with `owned_by_user: true`, or a
first-party `proof:<id>` (FRFRMU-1067).** No match → the element is rewritten
without it (a vaguer, still-true line) or the whole variant is dropped — never
shipped with an invented element. This is the "former janitor" rule: a
borrowed or made-up detail dressed as the creator's own is a fabrication, not
a hook.

Practically: before a variant is added to `hook_variants[]`, walk every
number/timeframe/person/result token in its text and confirm each one traces
to a source. A variant with even one untraceable element **fails** — this is
`check_hook_facts_true` (§G).

## D. Saturation — read only, planner-owned

The planner's H.2 already states the `unique_accounts` saturation count for
any "How to X without Y"-shaped hook when the data is thick enough to compute
it (`step-08-hook-recipe.md` H.2c). This file reads that count if present and
requires a structurally different SURFACE WORDING (not a new pattern) for a
saturated shape — it never recomputes the count itself.

## E. The losers ledger — `hook_history` (FRFRMU-1060, now shipped)

At the KPI review (Step 12 equivalent for a copy pack — when a test-loop cycle
closes, per `step-08-hook-recipe.md` H.6), write ONE `hook_history` entry per
tested variant via `update_creator_brief`:

```
{ cycle, hook_id, template, result_vs_own_median, verdict: won|held|lost,
  audience_note }
```

`backend/app/mcp/creator_brief_reserved_keys.py` checks this shape on write —
a malformed entry is rejected before it reaches storage, the same guarantee
`topic_history` gets. **Losers are never deleted.** A `lost` entry keeps its
`audience_note` ("may fit [segment]") so a later plan can try it on a
different slot instead of re-testing a known loser blind.

## F. Payoff check — every curiosity hook pays off

A curiosity hook's open loop must be closed by a named beat. When you place
the hook in the outline (per `block-skeletons.md`'s beat table), record
`pays_off_at: <beat_id>` on the reel's hook block, naming the `early payoff`
beat or a later beat that actually delivers what the hook teased. A curiosity
hook with no `pays_off_at` is clickbait debt — `check_hook_payoff` (§G) fails
it.

## G. Validator (skill-level, advisory → hard for the truth check)

Same convention as `block-skeletons.md`'s checks — described here, pinned by
this skill's own tests, never registered in the backend plan validator (a
copy pack is not a plan).

- `check_hook_facts_true` — **hard.** Every number/timeframe/person/result in
  a shipped hook variant traces to an `owned_by_user: true` `hook_facts` entry
  or a `proof:<id>`. An invented element fails, even if the rest of the line
  is fine.
- `check_hook_payoff` — every curiosity-shaped hook variant carries
  `pays_off_at`; a curiosity hook with none fails.
- `check_hook_history_written` — when a test-loop cycle closes (H.6), every
  tested variant this cycle has a matching `hook_history` entry; a variant
  silently dropped from the ledger instead of logged `lost` fails.

## Guardrails

- Truth absolute (same as `SKILL.md`'s guardrails) — an unowned element is
  never shipped, not even as a "just this once" exception.
- The framework shape is a generator, never a replacement for the plan's
  chosen pattern — `correlation-table.md`'s precedence order still applies.
- A losing hook is data, not a failure to hide — the ledger keeps it.
