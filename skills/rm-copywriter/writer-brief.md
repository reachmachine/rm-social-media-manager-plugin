# Writer brief — export for a hired human, and the paste-back path (FRFRMU-1070, p32)

*"If the creator hires a human scriptwriter or editor, hand them a complete brief
built from the foundation — the customer, the offer, the promise, the proof — and
treat what comes back as a first draft to check, never as final."*

**This skill never hires, pays, contacts, or evaluates a person.** It renders a
brief the creator can send, and it runs a human's draft through the same checks
every AI-drafted copy pack gets. The audition itself, references, and payment
are the founder's/HR's call — out of scope here (`p32-audition-brief-copywriter.md`
line 67-68: "in this system the agent IS the default copywriter; this card
activates when the founder chooses human specialists").

## A. `export_writer_brief(plan_id, slot_ids[] | all, audience: vetted | unvetted)`

Renders one Markdown brief per reel (never per month — a month brief risks the
20 KB/field cap). **The seven input categories, each pointing at a named
foundation key — no category, no ship:**

| # | category | reads from | `vetted` gets | `unvetted` gets |
| --- | --- | --- | --- | --- |
| 1 | market / who they are | `avatar` (avatar portrait + 5 pain/pleasure phrases, FRFRMU-1031) | full | full |
| 2 | benefits (what they get) | the offer's value stack (FRFRMU-1049) | full stack + values | the offer name only |
| 3 | payoffs (the transformation) | `promise` (FRFRMU-1056) | full | full |
| 4 | motivation (why now) | `why_people_buy` (FRFRMU-1041) | full | full |
| 5 | emotional impact | `avatar` fears/tension + `big_domino` (FRFRMU-1040) | full | full |
| 6 | reason to buy | the offer page one-liner (FRFRMU-1055) | full page | name + price only |
| 7 | buy-now / limited bonus | scarcity/urgency (FRFRMU-1050) + the bonus (FRFRMU-1052), **only on an activation slot** | full | full |

Plus, on every brief regardless of category: the slot's pattern constraints
(hook template + `hook_subcategory`, beat order, length, CTA type — read off
the plan's own receipts, never re-decided here), voice + avoid-words
(`attractive_character`, FRFRMU-1043), the proof elements allowed for any claim
in this brief (`proof_bank`, FRFRMU-1067 — ids + exact words only, per
`proof-and-claims.md`'s exact-words rule), and the compliance lines (Gate 1: no
income/result claims; the intake's regulated disclaimer if one applies).

**A category with nothing filed becomes `[GAP: needs <card>]`** — the same
convention `block-skeletons.md` uses. A brief is still exportable with gaps; it
is never exportable with an invented answer standing in for one.

**Storage:** `writer_briefs__<plan_id>__<reel_uid>`, written with
`update_creator_brief` (the same schema-free store `copy_pack` uses —
`creator_brief_reserved_keys.py` reserves neither this prefix). Shown on the
reel profile (FRFRMU-1062) as **"Brief for a writer — copy."**

## B. The `vetted` / `unvetted` audience filter — hard rule

`audience: unvetted` (someone not yet hired, e.g. an audition candidate) NEVER
receives:

- the competitor dossier (`competitor_dossier__*`) or any line drawn from it,
- the offer's value-ladder internals (rung prices, the full stack breakdown —
  category 2 collapses to the offer NAME only),
- unreleased items from the product dossier (G408 rule — nothing not yet shipped),
- the creator's private story fragments marked `declined` or `private`
  (`origin_story`/`false_beliefs` items with those flags are dropped, not
  summarised).

`audience: vetted` (someone the creator has already decided to hire) gets the
full brief, categories 1-7 in full. **This filter runs BEFORE the seven
categories are assembled, not as a redaction pass afterward** — an unvetted
brief is built from a smaller read, never a full brief with lines blacked out
(a blacked-out line can still leak in a diff or a copy-paste).

## C. Audition spec (advisory only)

When the creator is deciding whether to hire, this skill may propose **ONE
reel's brief** as the small paid test (an email-teaser-sized asset) — never a
whole month, never more than one slot. The hiring, payment, reference calls
and plagiarism screen for the CANDIDATE are the founder's/HR's process; this
skill supplies nothing but that one brief. No name, contact detail, or
evaluation of a candidate is ever stored here — that would be PII this skill
has no business holding.

## D. Paste-back — a human draft is v1, `author: external`, never final

*"Paste the writer's draft"* → stored as the copy pack's **v1**
(`mode: draft`, `author: external`, same `copy_pack__<plan_id>__<reel_uid>__v1`
key family `SKILL.md` already defines) → runs, in order:

1. **Block check** (`block-skeletons.md`'s `check_blocks_sourced` — does it
   cover the skeleton? a beat the draft skips is still a gap, not silently
   accepted because a human wrote it).
2. **Truth check** (`proof-and-claims.md` — invented numbers, invented people,
   an unbacked claim; a human's own words are not exempt from this).
3. **Near-clone check (Gate 4) + a quick search-engine check of distinctive
   sentences** (advisory — the card's own plagiarism test; this skill flags,
   it does not adjudicate).
4. **The seven-check QA pass** (`qa-checklist.md`, FRFRMU-1065) → **v2**.

**An external draft never ships raw.** `author: external` on a pack blocks
`shippable`/`approved` until a QA record with all seven checks exists — the
same rule an AI-drafted v1 already follows, just checked against the field
`author` as well as `mode`.

## Guardrails

- The plugin never hires, pays, contacts, or evaluates people; it packages
  inputs and checks drafts, nothing more.
- No PII about a writer (name, contact detail, rate, portfolio) is ever
  stored by this skill — the brief and the hiring conversation are the
  creator's, off-platform.
- Confidential strategy stays out of an `unvetted` brief — least privilege,
  not a courtesy.
- **Never quote a dollar figure or mention COGS to a creator** (G368 /
  FRFRMU-360) — a brief that names a price cites the offer's own stated price
  field, never an internal cost.

## Validator (advisory)

- `check_writer_brief_complete` — **warning.** All seven categories present
  (filled or an explicit `[GAP: needs <card>]`); a category silently missing
  (no row at all) is a warning, not a hard fail — the brief is still useful
  incomplete.
- `check_unvetted_excludes` — **hard.** An `unvetted` brief containing a
  `competitor_dossier__*` line, a value-ladder internal, an unreleased
  product-dossier item, or a `declined`/`private` story fragment fails
  outright — no matter how small the leak.
- `check_external_draft_qa` — **hard.** A copy pack with `author: external`
  marked `shippable`/`approved` with no seven-check QA record on it fails.
