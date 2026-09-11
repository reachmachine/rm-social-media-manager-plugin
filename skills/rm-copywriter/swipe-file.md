# Swipe file — the warm-up and the citation rule (FRFRMU-1066, p28)

Never start from a blank page. The data half is the product (the tracked
competitors' hooks, CTAs and structures — `correlation-table.md`,
`hook-variants.md`); the human half is the creator's OWN saved finds
(`swipe`, `step-01-intake-fields-2.md`). This file is what the copywriter
does with both before writing a word.

## 1. The warm-up — before every drafting session

Read **3-5 relevant entries** before drafting: the RM top templates for
this slot's pattern (already surfaced by H.2/`correlation-table.md`) plus
any `swipe` entries in the matching folder for this asset type. This is a
reading pass, not a writing one — it primes the vocabulary, it does not
supply the words.

## 2. The citation rule

Any structure borrowed from a `swipe` entry is cited on the block as
`source_ref: swipe:<id>` — same shape family as `proof:<id>`
(`proof-and-claims.md`) and `pattern_ref` (`correlation-table.md`). **The
near-clone test (Gate 4) applies to every swiped structure exactly as it
applies to a data template** — model the structure, never republish the
wording. A block that quotes a swipe entry's wording verbatim fails.

## 3. The RM-library boundary

RM top templates are referenced by their existing ids (`template_id`,
`retrieved_exemplar` post_urls) — they are never copied into `swipe` and
never need a `swipe:<id>` citation; they already carry `pattern_ref`. Only
the creator's OWN saved finds use the `swipe:` prefix.

## 4. The `classic` label — human only, never views

**The agent never sets `classic: true`.** A swipe entry earns the label
only from the creator's own confirmation (the winners-feed flow,
`step-12-after-the-save.md` §4) — a template's `median_views` being high
is a DATA fact about the niche, not a human judgment that a specific saved
ad or post was a classic. Conflating the two is exactly the failure this
ticket exists to prevent.

## Validator (advisory)

- `check_swipe_use` — a `swipe:<id>` `source_ref` resolves to a real entry
  carrying `why_it_worked`; using an entry with `why_it_worked: null` is a
  warning, not a hard fail (a museum-piece screenshot can still inform
  structure, it just isn't a citable "why"). **Hard**: `classic: true` set
  on any entry without `by_user: true` or a confirmed outcome fails —
  the agent marking its OWN template choice a classic from view counts is
  exactly the caught case.
- `check_no_verbatim_swipe_reuse` — a block's wording matches a swipe
  entry's saved text beyond a short shared phrase → fails (Gate 4).

## Guardrails

- The agent never scrapes ads into `swipe` — that is FRFRMU-1039's
  server-side Ad Library work, entirely separate.
- The agent never writes "made me buy" or any first-person claim on the
  creator's behalf — `why_it_worked` is always in the creator's own words
  or explicitly `null`.
- Swiped material is reference, never republished — the same Gate 4 rule
  that governs every proven-template use.
