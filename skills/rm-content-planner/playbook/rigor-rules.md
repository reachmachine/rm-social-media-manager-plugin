> **Playbook rules file.** The Rigor Rules **§A–§K** that every step is held to. The step list,
> and which file holds each step, is in `PLAYBOOK.md`. A "Step N" reference below means that
> step's file in the `playbook/` folder.

## The Rigor Rules (§A–§K) — the full standard every step is held to

*(This is the detail behind the "Rigor Rules" summary near the top. Not an appendix — these are
applied INSIDE the steps, referenced by each step that uses them.)*

A plan is only honest if it separates **data** from **judgment** out loud. Apply
all of these on every run, and **put the confidence + sample size in the output.**

### A. The universal formula — "the Reel Bet"
Every reel = **Proven Pattern × First-Party Topic × Audience Tension.**
- **Proven Pattern** — a hook-template + structure + emotion combo with a high
  *goal metric* in the data (found via cross-tab, §C), with adequate sample.
- **First-Party Topic** — a topic from the **demand-validated candidate set** (the
  niches that already exist in the data), reframed through the creator's own proof.
- **Audience Tension** — one specific pain / desire / identity of the ONE audience
  the reel resolves. Anchor it to the target **audience segment** from the data (§F)
  so the reel speaks to a real, sized segment rather than a vague "everyone".

**Never combine a novel pattern with a novel topic — that is maximum risk.**
Novelty belongs in the *framing / proof*, not in the pattern or the topic-demand.
A plan is a **portfolio of bets**, not a set of guarantees: expect most reels to be
average and a few to carry the reach — that is how the creators in the data operate.

### B. Confidence — label every recommendation
`confidence = f(sample size n, median lift over baseline, recency)`:
- **High** — large n, **median** (not mean) beats baseline, recent.
- **Medium** — decent n or strong median, one caveat.
- **Low / "a bet"** — n below threshold (≈ 5) or mean inflated by one outlier.

Always read **median**, not mean — the mean is survivorship-inflated by a few mega
reels. Show the confidence + n next to each lever in the deliverable. This n≈5
threshold is also the bar for the **DATA-DRIVEN** tag in §I — below it, a
recommendation can never carry that tag, however good the median looks.

### C. Cross-tabs, not single levers
Use `get_content_breakdown` **`group_by`** (e.g. `["angle","structure_type"]`,
`["hook_emotion","structure_type"]`) to find the **combinations** that co-occur in
winners for the goal metric — do not read each lever in isolation. Assign the
highest-goal-metric combo with adequate sample; if thin, fall back to the single
strongest lever and mark it **Low confidence**.

### D. Goal-conditioned selection (keep the goal in mind)
Rank levers / topics by the metric that matches the goal:
- **Reach** → median **views + shares**; favour amusement / skit / relatable-meme;
  CTA = reply-bait or none.
- **Leads** → **comments + saves** + a real CTA; keyword-DM (gated by stage + plumbing).
- **Authority** → **saves + watch-time**; insight / proof / contrarian.

### E. Niche — follow the data for SELECTION, judge the FRAMING (don't mirror shares)
- The data's topic list is the **candidate set** — proven audience demand. Do **not**
  invent topics outside it.
- **Weight by median performance**, NOT by the competitors' raw share (their share
  reflects *their* business, not the creator's).
- Reframe each chosen topic through the creator's positioning + first-party proof.
- Mirroring exact percentages copies competitors' strategy — that is not the goal.
- **A second proven-demand source: the creator's own audience.** Competitor data
  proves a *pattern* works for someone. The creator's own comments, DMs, replies,
  and FAQs prove *demand* — the exact questions their own audience asks, in
  their own words. Ask the creator to bring you a batch of real comments/DMs/
  FAQs and mine them for the recurring questions and topics. Combine both
  sources: a topic that shows up in **both** the competitor candidate set
  **and** the creator's own audience questions is the strongest bet.
- **Tag audience-sourced topics DATA-DRIVEN** (§I) — it's real first-party
  audience data — but **only if the creator actually supplies** the comments/
  DMs/FAQs. If they don't have any to hand over yet, this becomes a
  **JUDGMENT** prompt instead: tell the creator to go collect them (their last
  20 DMs, their most-asked comment questions) before the next planning run.
- This **strengthens**, not contradicts, the anti-mimicry rule above — the
  creator's own audience's real words can never be a competitor clone.

### F. Audience — MODEL THE LEVERS FOR THE TARGET SEGMENT, not just the niche
`get_content_strategy` groups the tracked reels into clean **audience segments** ("Who Are
They Speaking To?", reverse-engineered per reel) with real counts + shares. The whole
strategy — **hook, structure, CTA, topic** — should be modelled **for the creator's ONE
target segment**, not the niche average:

1. **Pick the ONE segment this creator serves** (from Step 1) and read how deep the proven
   material is for it.
2. **Filter the levers BY that segment.** `get_content_breakdown` with
   **`filters.audience=[the canonical macro label]`** (the same label `get_content_strategy`
   shows — matching ignores case/spacing) **DOES return real data**. Pull the audience-specific
   winning **`hook_template`, `structure_type`, `cta_type`, and topic** — so the plan says
   "for THIS audience, X wins," not "for the niche overall."
3. **Sample-size guard (the real limit is n, not the filter):**
   - Segment has **≥ ~5–8 reels** → read it audience-specific and tag by §B (DATA-DRIVEN /
     DATA-INFERRED **on that slice**).
   - **Thinner** → the audience-specific read is **Low-confidence**; **widen** to the adjacent /
     on-ramp audience (or the whole board) for the pattern read and **say so**. Never force a
     3-reel audience slice into a confident claim.
4. **Weight by median WITHIN the segment**, not the segment's raw share (don't mirror what
   competitors post — favour what performs for this audience).

**Correction to the old note:** the audience-macro filter is **not broken** — it returns real
reels; what was thin in testing was *small segments* (e.g. n=10). So audience-specific
modelling of hook/structure/CTA is the **DEFAULT when the segment is deep enough**, with the
widen-and-label fallback above when it isn't.

### G. Honest topic labels
On every reel show the **real data niche** it maps to, separately from the
**reframed idea** — e.g. *idea:* "I replaced a $2k hire with AI" → *data niche:*
"AI tools". Never let a reframed label masquerade as a data value.

### H. Every reel is an experiment
Attach a **hypothesis** + a **kill / scale rule**: after N reels on a pattern, if the reel beats
the account's own rolling median → **scale** it; two consecutive flops on a pattern → **retire** it.
This turns the calendar from a guess into a measured loop.

**The scale/kill METRIC must be stage-appropriate — don't judge every account the same way.**
- **Cold / small account (~0–few-thousand followers):** hour-1 velocity and raw views are near-zero
  **noise** — a good reel can sit for days before it travels. Judge on **saves-per-1k, watch-time %,
  shares-per-1k, and replay rate** against the account's OWN baseline, not on early view count.
- **Established account with real reach:** hour-1 velocity + watch-time vs the rolling median are
  meaningful — use them.
Always compare to **this account's own bar**, never a big creator's numbers (that's the 5/10 trap).

**The structured record (FRFRMU-1075, Step 7.4): every bet above is a `test_ledger` row, not a
paragraph** — variable, control, challenger, metric, sample floor, disproof condition, decided
before the calendar is built. **Sample floor + no peeking:** the floor is set AT DESIGN TIME and
never moved once posts start landing — calling a winner early because it "looks good" at n=1
is exactly the noise this rule exists to filter out; below the floor the only honest call is
`inconclusive`. **Promote the control:** when a challenger scales, it BECOMES the control for its
comparable slots next cycle — the plan records *"control changed from X to Y on [date]"*, so the
next round of bets tests against what actually won, not last quarter's assumption. **The Loop
Gate:** no new bet while a prior cycle's row is still open (`running`, no result) — close it on
the numbers first (§H above), then design the next one.

### I. Tag the PROVENANCE of every recommendation (data vs inferred vs judgment)
The plan is only trustworthy if the human can see what's earned from data and what's
your craft — and if two different runs would tag the same recommendation the same
way. Use this **operational rule**, not a vibe check:

> A recommendation is **DATA-DRIVEN** only when the exact lever choice is backed
> by a **median** with a **stated sample size at or above the bet threshold
> (§B, n≈5)**, read from the **audience-matched slice** (§F — the creator's
> target segment, not the whole board). Anything thinner is **DATA-INFERRED**
> or a **bet** — never DATA-DRIVEN.

Tag every lever, topic, and reel choice with where it comes from, paired with the
confidence (§B):
- **DATA-DRIVEN** — meets the rule above. *"Curiosity × Tutorial, median 112k,
  n=8, from the target-audience slice."*
- **DATA-INFERRED** — a judgment **extrapolated** from the data (thinner sample,
  wrong slice, or a reasonable cousin of a proven pattern). *"Skit wins biggest but
  you're solo, so relatable-POV is the doable cousin of that pattern."*
- **SMM JUDGMENT** — craft with no data behind it: stage translation, framing around
  first-party proof, retention structure, cadence, trending-audio picks. **Names what it
  is grounded on** (§J, FRFRMU-1024) — never a free invention.
Make it legible in the deliverable — a per-row tag or a clear section legend — and
**never let a judgment masquerade as a data claim** (this is §G, enforced on every cell).
A plan that can't tell the human which is which is not senior work.

**This is now checked in code (G118).** `validate_content_plan` (called in Step 11) enforces the
countable half of this rule: a reel tagged **DATA-DRIVEN** must carry a structured `receipt` with a
**sample size n ≥ 5** and a **median**, and the plan's provenance-split counts must be honest. So the
provenance tag is no longer just a promise you make in prose — emit the numbers in the structured
fields (Step 12) or the check flags it. The rule above still governs the *judgment* half (which
tier a borderline call belongs to) — the code checks the arithmetic, you own the judgment.

**Changing a reel's provenance tag updates the summary counts in the SAME edit, never after
(FRFRMU-1318).** `receipts_summary.provenance_split` (Step 12) is a count of the reels' own
`provenance` fields — it is a derived total, not an independent value you set once and forget.
The live incident this rule closes: the Step 11 critic downgraded one reel from `data_inferred`
to `judgment` and the plan's `provenance_split` kept its old numbers, so the honest-split check
(`provenance_split_honest`) correctly blocked the save. Whoever edits a reel's `provenance` —
you, in Step 8, or the critic, in Step 11 — recounts `provenance_split` across every reel and
writes the new totals before moving on, not as a separate later pass.

### J. Data first, judgment last, judgment still grounded (FRFRMU-1024)
The founder, live, 2026-09-06: *"we have to analyze more as we lack data as we need to have
data driven decision. we go to judgement only after analyzing all the videos and judgement
should be based on data."* This ties §B/§I/`step-03-mcp-sufficiency.md` rules 2a-2b into one
stated policy — every step that can reach for JUDGMENT cites this section. The order, always:

1. **Thin slice → analyse more of the RELEVANT un-analysed reels first** — own tracked
   competitors (rule 2a's sufficiency table), then the community/niche scope (rule 2b) —
   never a smaller batch chosen for cost, never a shortcut to judgment while relevant
   un-analysed reels remain that the creator agreed to analyse.
2. **Still thin after BOTH scopes are checked → call `request_niche_data` with the workspace
   niche (FRFRMU-1545).** This is free — Reach Machine's own team collects more, on the
   business's own credits, usually within `sla_business_days`. Call `get_data_request_status`
   first so a second ask on the same niche never files a duplicate job. Then keep going on
   what already exists, labelled honestly (never a pause) — the save reply's `honesty` block
   carries the request back as `honesty.data_request`, and `step-12-capture.md` step 3 is where
   you relay its `message` to the creator, plainly, in the same breath as confirming the save (on
   EVERY save, clean or not — never only when `step-12-blockers-remain.md` also fires). This is a
   rung on the ladder, not a substitute for it: it never replaces
   step 1's own widening, and it never turns a judgment reel into DATA-DRIVEN (§I stays the
   wall).
3. **Judgment only when the relevant reels are exhausted, or the creator declined the
   spend.** Declining is a valid, honestly-labelled path (§I's "SMM JUDGMENT" tag,
   `step-03-mcp-spend-and-progress.md` rule 6g's three options) — it is never a silent
   default.
4. **Even a judgment reel is grounded, never a free invention.** It names the NEAREST real
   data it extrapolates from — an adjacent pillar's proven pattern, the creator's own
   first-party proof, or a community/niche signal (labelled niche-wide, per rule 2b). A
   judgment reel's reasoning (`step-08-reasoning-recipe.md` R.1) carries one line: *"grounded
   on: <the nearest real data>."*
5. **Tell the creator plainly, every time.** *"We need to analyse N more reels for this part
   to be data-driven — here's what that costs — or I mark these reels as judgment, grounded
   on <X>."* Never present a judgment-based reel as if it were proven (§I stays the wall: a
   judgment tag is never relabelled to look like data).

**A server-side backstop also exists (FRFRMU-1545) — `submit_content_plan` auto-files the same
request when the SAVED plan's data-driven share lands below the reliability floor, even if
step 2 above was somehow skipped.** That backstop never depends on this playbook being
followed — it is there so a thin niche is escalated either way. Following step 2 yourself
still matters: it lets you tell the creator about the SLA in the moment, instead of them only
finding out from the saved plan's own record.

**Honest limit — "all the videos" means all RELEVANT reels for the role/slice** (the goal→tag
rows in `step-03-mcp.md` rule 2), never the whole `low_performance` pool — that stays banned
for cost (rule 2's own base-rate sampling rule). "Exhausted" is defined by rule 2a's
sufficiency table and the goal→tag rows, never by "every reel in the workspace."

**The "grounded on" line is NOT a receipt.** It does not make a judgment reel DATA-DRIVEN or
DATA-INFERRED — the tag stays JUDGMENT (§I), and the validator's `n ≥ 5` receipt check is
unchanged. It is a transparency line, so a human reading the plan can see WHERE a judgment
call came from, not a claim that the judgment is now proven.

### K. A claim about a check names its call (FRFRMU-1539)

A saved plan once stated *"no reliable posting-time data at this sample size"* — a specific,
confident claim about the customer's own data — from an agent that had never called the tool
that would confirm or deny it. That is a different, worse failure than a missing analysis: it is
a fact that was invented, not a gap that was left honest.

**The rule.** Any sentence of the shape *"no data for X," "X was checked," "X shows nothing"*
must name the tool it came from and what it found — or the only honest sentence is **"X was not
checked."** This applies to a small, NAMED registry — never free-text judgment about what counts
as "a check":

| Claim | Tool that backs it |
|---|---|
| Posting time | `get_posting_time_performance` |
| Hook channel mix (spoken / on-screen / visual / sound) | `get_content_breakdown` (dimension `hook_channel`) |
| Trending audio | `get_trending_audio` |
| Self-account activity | `get_profile_posts` / `get_content_strategy(scope: mine)` |

Posting time is the one claim with a STRUCTURED, machine-checkable field today —
`distribution.posting_time` (Step 8 item 7, `TEMPLATE.md` D2, Step 12's plan shape) — so the
server cross-checks it against this session's own tool-call record at save time and blocks a
mismatch (`claim_backed_by_call`, RULES_GATE.md Gate 7). The other three rows are enforced here,
in prose, the same way every other rigor rule is: by you, reading this before you write the
sentence. Self-account activity is the SAME claim FRFRMU-1534 already names for "zero self-posted
reels" — one rule, one registry, not two.

**Three different sentences, never blurred:**
1. **Checked it, found a signal** — name the tool, quote the row(s) and their reliability.
2. **Checked it, found nothing usable** — name the tool, say so plainly. This is NOT the same
   sentence as "not checked" — it is a stronger, more useful claim, and it is only honest when
   you actually made the call.
3. **Did not check it** — say exactly that. Never dress it up as either of the two above.
