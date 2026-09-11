# Block skeletons — never a cold draft (FRFRMU-1064, p26)

The #1 job is a complete first draft, fast. Every asset is ASSEMBLED from
named blocks the foundation already filled — never started from a blank
page. Each block below names its DEFAULT SOURCE: the card, brief key, or
plan field that fills it. **A block written with no source is a cold
draft.** If the source has nothing for this creator, the block becomes
`[GAP: needs <card>]` — visible, never invented.

Filling every block is the **draft pass** (`mode: draft`, copy pack v1).
Polishing it is a separate pass (`mode: edit`, copy pack v2 — FRFRMU-1065).
**v1 is never overwritten**; editing while drafting fails
(`check_mode_separation`).

## 1. Reel script (talk-beats or slide copy)

Beats run in the PLANNER'S order (`step-08-outline-recipe.md`'s beat
vocabulary: `context`, `teach_step`, `demo`, `proof`, `myth_bust`,
`objection`, `story_setup`, `story_turn`, `list_item`, `transformation`,
`punchline`, `re_hook`) — the copywriter fills words into that order, it
never reorders it.

| block | default source |
| --- | --- |
| hook | the plan's hook line (FRFRMU-1058); a cold-reach slot with a V.2b matrix cell runs `pattern-interrupt.md` (FRFRMU-1069) |
| early payoff | the outline's payoff beat |
| `context` / `teach_step` / `demo` | the stack's fast-win step (FRFRMU-1049) |
| `story_setup` / `story_turn` | story cuts (FRFRMU-1044) / parables (FRFRMU-1043) |
| `objection` / `myth_bust` | belief rows (FRFRMU-1045); a row with `m_type` runs `belief-breaker.md` (FRFRMU-1068) |
| `list_item` | when the planner flagged `carries_value_lines: true`, run `bullet-recipe.md` (FRFRMU-1059) — else a plain teach point, unchanged |
| `proof` | first-party proof (`proof-and-claims.md`, FRFRMU-1067 — cited, exact words, or `[GAP: needs p29 proof]`) |
| `re_hook` | a retention line back to the open loop |
| `transformation` / `punchline` | the promise (FRFRMU-1056) |
| CTA | the plan's ask (one conversion action, FRFRMU-1047 §E) |
| on-screen text | one line per beat, restating its spoken content |

## 2. Carousel

| block | default source |
| --- | --- |
| slide 1 (headline) | the plan's hook line (FRFRMU-1058) |
| slides 2..n (one beat/bullet each) | `bullet-recipe.md` when the slide carries a value line (FRFRMU-1059), else the plain beat |
| last slide | CTA echo + the P.S. twin (see Caption, below) |

## 3. Caption

| block | default source |
| --- | --- |
| first line (written hook, different words from the spoken hook) | hook variants (FRFRMU-1058/1060) |
| body | persona voice + keywords; `bullet-recipe.md` for the value lines when `carries_value_lines: true` (FRFRMU-1059) |
| CTA echo | the plan's ask |
| last line — the **P.S. twin** | the promise or cause line (FRFRMU-1046) — the ONE line a scanner reads if nothing else |

The P.S. twin is not optional: `check_complete_draft` fails a script or
caption missing it.

## 4. Story sequence

| block | default source |
| --- | --- |
| 3-5 sticker/text cards | the reel's beats, condensed |
| question sticker (ask windows only) | FRFRMU-1037 / FRFRMU-1057 |
| link/DM instruction | the plan's ask |

## 5. DM script (only when this reel is the month's conversion action)

| block | default source |
| --- | --- |
| opener | persona voice |
| offer's one page | offer brief (FRFRMU-1055) |
| guarantee shape | FRFRMU-1053 |
| bonus-not-discount line | FRFRMU-1052 |
| trial close(s) | `closes.md` (FRFRMU-1072) — DM-restricted classes (6/9/16) never appear here |
| the ask | the plan's one conversion action |

## 6. Live / webinar script (`live_script` — p33, FRFRMU-1071)

**Only when the creator has a live, webinar or workshop already on the calendar
as an `anchors` entry** (`step-12-capture.md`'s `anchors: [{id, name, type,
date}]`). This skill never proposes running one as a growth tactic — it scripts
the one the creator scheduled. No anchor on the plan → no `live_script` block,
full stop (`check_live_script`'s hard anchor guard, below).

| block | default source |
| --- | --- |
| **opening, 9 beats, word for word** | |
| 1. title | the promise (FRFRMU-1056) — "how to [result] without [pain]" |
| 2. rapport | the five levers, in order (FRFRMU-1046) |
| 3. the Ruler (beginner + experienced) | `big_domino` (FRFRMU-1040) as the goal |
| 4. brief qualify (external + internal result) | `origin_story` (FRFRMU-1044) — never a résumé |
| 5. origin story | `origin_story.cuts` (FRFRMU-1044) — the 60s cut or longer |
| 6. liken it (old way → why hard → why easy) | `false_beliefs` (FRFRMU-1045) |
| 7. one case study, real | `proof_bank` (FRFRMU-1067) |
| 8. transition naming the 3 secrets | `false_beliefs.core_three`, as curiosity headlines, hype stripped |
| **body — per secret (×3)** | |
| state it → bridge story → break old belief → restate as truth | `false_beliefs.core_three` row (FRFRMU-1045) |
| **close** | |
| the running stack, in order | value stack presentation order (FRFRMU-1049) |
| one close before each stack element | `closes.md` (FRFRMU-1072) — DM-restricted classes never used (a live is not a 1:1 surface, but this file's own rewritten wording still applies) |
| guarantee | deliverable shape (FRFRMU-1053) |
| real limits only | FRFRMU-1050 — never fake one to fix a flop |

**Self-checks before this block may ship:**
- `teaches_method` — any line delivering the METHOD (how-to steps of what the
  product does) instead of shifting a belief is flagged and re-cut. A shippable
  `live_script` always has `teaches_method: false`.
- **Trial-close density** — ~1 per minute across the whole script (`closes.md`'s
  long-form density line); the first yes is always about the problem or the
  dream, never money.
- **Compliance pass** — Gate 1 (no income/result claims) on every beat and
  close, same as every other asset type.
- Every beat cites a `source_ref` — a beat with none is a `[GAP: needs <card>]`,
  same convention as every other skeleton block; a `live_script` with a gap in
  the 9-beat opening is not shippable.

## Draft-pass rules

1. **Fill every block from its source, fast — no editing.** A block with no
   source available becomes `[GAP: needs <card>]`, visible on the pack.
2. **Save as copy-pack v1 with `mode: draft`**, and a `source_ref` on every
   block (the brief key, plan field, or `[GAP]` marker it came from).
3. **Block order matches the plan's beat outline exactly.** A draft that
   reorders the planner's beats while "assembling" is a pattern change and
   fails, same as swapping the hook subcategory.
4. **Completeness before polish.** A rough whole passes; a polished
   fragment fails — this is the reel-copy version of the sales-letter rule
   "the P.S. twin is what scanners read."

## Validator (advisory → hard)

- `check_blocks_sourced` — every skeleton block on the pack has a
  `source_ref` or an explicit `[GAP: needs <card>]`. **Hard**: a block with
  neither fails.
- `check_mode_separation` — v1 carries `mode: draft`; any content difference
  from v1 must appear only in v2+ (`mode: edit`), never inside v1 itself.
- `check_complete_draft` — every skeleton block for the asset type is
  present (including the P.S. twin) before an edit-mode version may exist.
- `check_live_script` (FRFRMU-1071) — **hard: the anchor guard.** A
  `live_script` block on a plan with no `anchors` entry fails outright, no
  exceptions — this skill never scripts a live nobody scheduled. Advisory on
  the rest: all 9 opening beats present with `source_ref`s; the body maps to
  exactly the `false_beliefs.core_three` ids; `teaches_method` is `false` on
  anything marked shippable; closes are tagged by surface and none from the
  DM-restricted class appear on a 1:1 surface.
