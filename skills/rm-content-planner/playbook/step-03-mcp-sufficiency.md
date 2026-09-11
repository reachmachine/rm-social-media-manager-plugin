> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 3 (continued) — rule 2a: is this ENOUGH data for a reliable read? (FRFRMU-1019)

**Ask per `asking-rules.md`.**

Split out of `step-03-mcp.md` rule 2 because that file is at the 300-line ceiling. This
rule runs immediately after rule 2's coverage check, before ANY batch size is chosen or
any spend is proposed.

**2a. Never ask the creator to pick a raw reel count — translate need into reliable vs
directional, every time (founder decision 2026-09-07, FRFRMU-1019).** The founder, live:
*"if this question is asked to user they wont know what to answer… did the skill take
into account if that will help us get the result as the sample size is never checked at
all."* A normal creator has no basis to answer "analyse 8, 23, or pause?" — that is a
statistical judgement, not theirs to make blind. The maths lives in the backend
(`get_theme_lift`'s `confidence` block, per row) — you never compute a tier yourself,
you only read the one it already gives you and quote its `sentence` field verbatim.

**The three tiers — the WHOLE creator-facing contract. Quote ONLY these three shapes,
verbatim from the tool's `confidence.sentence` field. Never compute or paraphrase a
tier yourself, and never let a p-value, a confidence interval, or a raw confidence
percentage reach the creator — if you ever find yourself typing one, stop and use the
sentence the tool gave you instead:**

- **Proven** (`confidence.tier == "proven"`) — the pattern's views genuinely beat the
  niche baseline, whole interval and all. Cite it as a reel's reason freely.
- **Promising** (`confidence.tier == "promising"`) — looks good but could still be luck.
  Use it ONLY inside a reel you explicitly label an experiment (§H) — never as a plain
  reason on an ordinary reel.
- **Not enough data** (`confidence.tier == "not_enough_data"`) — never cite this as a
  reason for anything. Read `confidence.n` and `confidence.n_to_proven` (when present)
  to build the gap line below.

**Build the sufficiency table before proposing a batch.** For each funnel role in the
plan's mix crossed with the target-audience slice: call `get_theme_lift` for the
dimension that role's pattern needs, read `confidence.n` (have) against `confidence.tier`
(reliable now or not), and when a pattern is `promising`, read `confidence.n_to_proven`
(gap) and quote the spend it costs from the tool's own preview (never invent a number).
Lay it out as a table, one row per role × slice, e.g.:

> *"For a reliable read on your reach reels I need roughly 8 more analysed reels in the
> reach group for your audience; you have 3 landing as 'not enough data yet'. Nurture:
> already reliable. Closing the reach gap is about 5 reels, roughly N credits in assist
> mode (rule 6a). A plan built on the 3 you have now would be directional, not reliable —
> which do you want?"*

**Then give exactly two options, never a raw count:** (a) close the gap — spend the
quoted credits, or (b) proceed now — the plan is honestly labelled directional for that
role/slice (§I provenance tags: DATA-INFERRED, never DATA-DRIVEN, for anything built on a
`not_enough_data` pattern). Record whichever the creator picks in `planning_progress`
(via `update_creator_brief`), the same way rule 6f already records a freshness choice, so
a resumed session does not re-ask a question already answered.

**Batch sizing follows the sufficiency table, not the price.** Rule 6e's "about 8 reels
per dispatch" is still the practical ceiling for one chat batch — it decides how many
DISPATCHES a spend takes, never whether to spend or how much. The sufficiency table above
decides the TOTAL; 6e only decides how that total is chunked. Cost-first sizing ("how many
would you like to analyse?") is retired — replaced by the table.

**Carry the verdict into the deliverable.** Step 7's "Own your confidence" section states,
per role/slice, whichever tier the sufficiency table landed on when the plan was built —
this is the same discipline rule 6f already applies to a stale-data choice; a thin-data
choice earns the plan section a low-confidence label the same way.

**Where this sits relative to rule 2's coverage check:** rule 2's `get_analysis_coverage`
pass is the first, cheap look ("is there anything here at all"); this rule 2a is the
second, statistical look ("is what's here enough to trust"). See `rigor-rules.md` §J
(FRFRMU-1024) for the overarching "data first, judgment last, judgment still grounded"
policy this rule serves.

**2b. Widen to community/niche data BEFORE judgment — never assert "diminishing returns"
without a number (founder decision 2026-09-07, FRFRMU-1020).** The founder, live, after
the plugin proposed stopping at ~18 unanalysed competitor reels and going to judgment for
3 of 8 reels: *"on what basis is the remaining 18 reels are diminishing returns? why is
the plugin going ahead with judgement and not based on data? … why did we build this
entire tool if we have to rely on judgement and not data?"* A 94-account niche index and
thousands of community-analysed posts sat unused while the plugin reached for judgment.

**The order of widening, every time a slice is thin — each step said out loud, not
silently skipped:**
1. **Own tracked competitors** (rule 2's default scope, `scope='mine'`). This is what
   rule 2a's sufficiency table already checks.
2. **The community/niche scope** — `scope='niche'` or `scope='both'` on the insight
   tools, plus `get_analysis_coverage`'s `community_per_account` / `community_cross_
   account` analysis modes for the counts. Report what is there BEFORE using it: *"Your
   own competitors give me 3 nurture reels. The community/niche pool holds N analysed
   posts I can also read from (scope: niche) — I'll use those too, and label them
   niche-wide, not your tracked set."* A pattern sourced from this scope is real DATA
   (an analysed reel), from a DIFFERENT pool than the creator's own competitors — the
   receipt must say which scope it came from (§G honest labels), never blur the two.
3. **Adjacent audience slice** (§F) — only after step 2 is also thin.
4. **Judgment** — the true last resort, only when steps 1-3 are all genuinely exhausted,
   and even then grounded per `rigor-rules.md` §J (FRFRMU-1024).

**Honest limit on step 2, today (verified in code, 2026-09-07):** `scope='niche'` reads
the workspace's community PICKS — accounts the creator hand-picked in the browser
(`community_picks`) — not the whole niche-wide pool. No picks means an empty niche frame,
same as no data at all. If picks are empty, SAY SO plainly ("no community picks yet, so
the niche scope has nothing to add") rather than silently treating step 2 as exhausted.
The whole-niche population (reading every analysed post in the niche, not just picks) is
a bigger backend build (FRFRMU-1020's full architecture) and is NOT live yet — do not
claim or imply it is.

**Any "stop analysing" call must carry a before/after number, never a bare assertion.**
Compare the top-3 pattern ranking (or the median) from BEFORE the last analysis batch
against AFTER it, using two consecutive `get_theme_lift` / `get_content_breakdown` reads:
*"the last 8 reels changed the top-3 hook patterns by 0 places and the median by 4% —
more of this slice is unlikely to change the plan."* No such number, no such claim — say
"I don't have a marginal-value read yet" instead of "diminishing returns."
