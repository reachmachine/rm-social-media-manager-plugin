> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 3 rule 5b — DATA RECIPES: run the reading BEFORE you state a number

These are the named readings behind the percentages a plan declares. They are **free** —
every call here reads data that has already been analysed and spends no credits. Step 3
rules 1-5a (`playbook/step-03-mcp.md`) still apply to all of them: scope the data the same
way every run, check coverage first, read medians not means, and mark a thin slice
low-confidence instead of forcing a confident claim.

**Three rules that govern every recipe on this page.**

1. **A recipe never decides — it describes.** The reading is the **base**: what this market
   actually does. The rulebook, the goal and the account's stage are the **overlay** that
   decides. The number you publish is the overlay's, never a copy of the market's (Step 7,
   "never mirror competitors' mix"). The overlay reasoning must name at least one
   deliberate difference from the base, or one deliberate confirmation of it — "we match
   the market here, on purpose, because…". Agreeing by accident is mimicry.
2. **Both halves go in the receipts** — the base numbers AND the overlay reasoning. That is
   what lets the Rules Gate follow the whole chain: data base → declared % → the actual
   reel counts in the calendar (`RULES_GATE.md`, Gate 6, "Funnel mix: count them").
3. **Ask for one dimension at a time, and read `warnings`.** When part of a request could
   not be answered the way you asked it, the answer's **`warnings`** list says so in plain
   words and points at the reading that does work. Repeat what it says rather than working
   around it. An empty `warnings` with an empty result really does mean "no matching
   reels" — that is the difference between "there is nothing there" and "we could not ask
   that", and you must not report one as the other.

### Recipe A — the funnel mix, one performance quadrant at a time (feeds Step 7.1)

**Why not just read the whole market's funnel split.** Reach itself favours top-of-funnel
content: the reels that travel furthest are the broad ones, so a single market-wide
top/middle/bottom split is already bent toward the top before you read it. Reading INSIDE
one performance quadrant holds that bend still — everything in the quadrant was selected
the same way — so the stage mix within it is readable.

**The calls.** Coverage check first (rule 2). Then four reads, one per quadrant:

```
get_content_breakdown(filters={"performance_tag": ["<tag>"]}, dimensions=["funnel_stage"])
```

with `<tag>` being `high_reach_high_engagement`, then `hidden_gem`, then `reach_only`, then
`low_performance`. Then one **conversion-reality** read —
`get_content_breakdown(filters={"intent": ["sell"]}, dimensions=["cta_type"])` — which
shows which asks this niche's selling reels actually make.

**What to record, per quadrant.** Each stage's `percentage` and `reliability`, and `valued`
out of `total_reels` — `valued` is how many reels actually HAD a funnel stage, and it is the
denominator the percentages are computed over.

**Quote the counts, never a bare percentage.** "hidden_gem winners here run about 40%
middle-of-funnel, from 213 reels that had a stage out of 244" is a reading. "40% MOF" is a
number with no evidence behind it. `get_content_strategy` reports the same honesty for its
own funnel split as `funnel_considered` / `funnel_excluded` / `funnel_total`: reels our
analysis could not place in the funnel are left OUT of the percentages, so never present a
split as if it covered every reel.

**When a quadrant is thin** — few reels, or `reliability: low` (§B/§F) — mark that
quadrant's reading low-confidence and let the overlay lean fully on the rulebook for it.
A thin quadrant is not a small finding; it is no finding.

**How to cite it.** The funnel base has a typed receipt kind now, `funnel`, for the mix you
declare at Step 7.1:

| field | what goes in it |
|---|---|
| `kind` | `funnel` |
| `stage_shares` | the declared TOF/MOF/BOF percentages — the overlay's number, never a copy of the base |
| `funnel_considered` | reels that HAD a funnel stage — the `valued` count behind the percentages |
| `funnel_excluded` | reels our analysis could not place in the funnel, stated honestly, even when it is 0 |
| `window` | the time window the quadrant reads covered |

**No producer builds this for you.** Nothing in the live pipeline constructs a `funnel`
receipt automatically yet — this schema exists ahead of the automated data source that
would fill it in for you. Fill the fields yourself from the quadrant reads above, from the
real counts, never from a guess.

**When a reading is too thin to back a real claim, say so — never invent a split.** A
quadrant marked low-confidence above ("When a quadrant is thin") is a quadrant with no
honest `funnel` receipt to write. When every quadrant that matters here is that thin, do
not force one out of a guess: state in the plan that the funnel base was too thin to cite,
tag the slot `judgment`, and lean on the rulebook overlay alone.

### Recipe B — delivery mix: what the market MAKES vs what actually WINS (feeds Step 7.6)

**The recommendation is the GAP between the two, not either one on its own.** What a niche
makes a lot of is what is easy to make, and that is not the same as what works. Read both
and the useful sentence writes itself: "everyone here makes voiceover reels; the ones that
actually get comments are talking-head."

**Two reads, same filters both times, then compare.** Coverage check first (rule 2).

1. **MADE — what this market produces for that slot.**
   ```
   get_content_breakdown(filters={"funnel_stage": ["bof"], "niche": ["<niche>"]},
                         dimensions=["content_delivery"])
   ```
   `content_delivery` is the axis that tells reels apart by HOW they are shot —
   talking-head, voiceover, text-on-screen. It is not the narrative structure, and it is
   not the media type.
2. **WINS — what worked in that same slot.** The same call plus `"performance_tag"` in the
   filters. **The winner tags must be STAGE-MATCHED**, from the goal → tag table in Step 3
   rule 2 (`playbook/step-03-mcp.md`). Bottom-of-funnel wins on comments and DMs, never on
   views — reach picks top-of-funnel reels, so judging a bottom-of-funnel slot on views
   measures the wrong thing. So bottom of funnel uses `comments_driven_post`,
   `excellent_er`, `hidden_gem`; top of funnel uses `viral_2x`, `viral_3x`.
3. **Compare the two shares** and say what changed. A delivery that is made often and wins
   rarely is the niche's wallpaper. One that is made rarely and wins often is the opening.

**When it comes back thin, widen in this order** — drop the `niche` filter first, then the
community lens — and mark the reading low-confidence (§B/§F). Three filters at once
(stage × niche × winner tags) is where a sample collapses, so quote the counts at each
step rather than reporting the last one that survived.

**Name the recipe so it can be produced.** For each delivery worth recommending, one more
read — `get_content_breakdown(filters={"content_delivery": ["<value>"]},
dimensions=["structure_type"])` — turns a bare label into something a creator can film:
"talking-head tutorial", not "talking-head". Then intersect with what this creator can
actually shoot (Step 1 production capability — an on-ramp, never a filter) and the capacity
ledger, and state the mix as a % reasoned to THIS account.

**How to cite it.** Receipt kind **`delivery`**: `made_share`, `wins_share`, the
`winner_tags` you actually used, and `n`. All four are required — a wins share with no made
share beside it hides the very gap the recommendation rests on.

**Not this tool:** `get_theme_lift` cannot answer the delivery question. It compares themes
(niche, sub-niche, intent, angle, hook category) between the watchlist and the wider
community, and has no delivery axis at all. It belongs to the pillar decision in Step 7.5.
