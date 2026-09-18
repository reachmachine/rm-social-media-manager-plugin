> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 2.3**, right after Step 2.2's discovery, before Step 2.4's human-approval
> gate. Split out of `step-02-benchmarks.md` (FRFRMU-1308/1300/1304/1285) to keep that file
> under the 300-line cap.

## Step 2.3 — Which accounts qualify: derived size bands + the escalation ladder

**FRFRMU-1308 supersedes FRFRMU-1305's fixed numbers.** FRFRMU-1305 set a fixed follower floor
for one business. The founder then asked for the same judgment to work in ANY niche:
> *"ensure that the instructions are reusable for all kind of niches"*

So the floor and the bands below are **derived, every run, from the screened candidates
themselves** — never a number carried over from a different niche or a different plan.

### The derivation — four steps, a calculator, no logarithms

**A — Sort and show your work.** Sort the screened candidates by followers, largest first, and
**WRITE THE LIST OUT.** That list is the evidence — show it to the customer and save it.

**B — The ceiling.** Take the follower count of the account at **rank 3** in that sorted list —
not rank 1. Rank 1 is where a mis-identified celebrity, or a fluke mega-account that slipped
past Step 2.2's screening (FRFRMU-1528/1536's real, structural `niche_fit_verdict` has not run
yet at this point — it only computes once a candidate is actually added, at Step 2.4+), lands
and drags the whole judgment upward.

**C — The top edge.** Pick the LARGEST of these five settings that is **at or below** the
ceiling from step B: **1,000 / 10,000 / 100,000 / 1,000,000 / 10,000,000.** Picking from five
fixed numbers, never a formula an agent could get wrong.

**D — Three decade bands, down from the top edge.** Starting at the top edge, step down one
decade at a time for three bands (top edge, top edge ÷ 10, top edge ÷ 100). **The floor of the
bottom band never goes below 500 followers** — an account with fewer than that is not a
credible pattern source regardless of what the math says.

**Worked example.** Run this on a fitness niche where the rank-3 account has 47,000 followers:
the ceiling is 47,000; the largest of the five settings at or below it is 10,000; the three
bands step down from there. The derivation lands on the same top edge the founder named in
FRFRMU-1305 — but reached by running the four steps on THIS niche's own data, not by carrying a
number over from a different one.

**Below 10 screened candidates, do NOT derive at all — climb the ladder instead** (below). A
derivation needs enough candidates for rank 3 to mean something.

### The escalation ladder — for a niche that's too thin to derive from

Each rung is its OWN Apify spend gate — say what you're about to run and **wait for an
explicit yes** before running it, same as any other Apify call (Step 2's spend-gate rule).
Climb in order; never skip a rung to save time.

- **Rung 0 — reword the seed (free, no Apify spend).** Use the trade's own vocabulary instead
  of the generic term — "guitar maker" becomes "luthier." Free because it is just a different
  seed into the SAME angles, not a new tool.
- **Rung 1 — platform surfaces.** Trending reels for the niche — **the one route that actually
  worked in the live run this ladder is built from.** Spend gate: ask before running it.
- **Rung 2 — geography.** Widen the search radius (see Step 2.1a). Spend gate: ask before
  running it.
- **Rung 3 — niche width.** Broaden the niche definition one notch (e.g. "yoga for runners" to
  "yoga"). Spend gate: ask before running it.
- **Rung 4 — audience instead of service.** Search for who the customer is, not what the
  business sells. Spend gate: ask before running it.
- **Rung 5 — outcome instead of profession.** Search for the RESULT the business delivers, not
  the job title. Spend gate: ask before running it.
- **Rung 6 — adjacent authorities.** Accounts one step removed but trusted by the same
  audience. Spend gate: ask before running it.
- **Rung 7 — business model.** Widen across how the business makes money (e.g. franchise vs.
  independent). Spend gate: ask before running it.
- **Rung 8 — language, last.** Only after every other rung — widen to another language the
  audience also reads in. Spend gate: ask before running it.

**Hard stops — whichever fires first, stop climbing:**
- the target is met
- the ladder is exhausted (rung 8 tried and still thin)
- **two consecutive rungs add zero new candidates**
- the customer declines to widen further, or a total scrape cap is reached

An infinite widen is worse than an honest "this niche is too small." Say so and move on.

### FRFRMU-1300 — bands, and three DIFFERENT sentences for a thin one

Fill the top band down. **Never climb the ladder just to fill the smallest band** — a thin
bottom band is often just the honest shape of the niche. When a band is short, say WHICH of
these three it is — never merge them, never use one sentence for another's situation:

- **"Does not exist here"** — the biggest genuine account in this niche is 43k; a 1M+ band is
  the size of the pond, not a gap in your search.
- **"Thin after widening"** — you found 1, the target was 3, you widened through the ladder's
  rungs, and you're going ahead and telling the customer.
- **"Not searched"** — you stopped at rung 3 at the customer's request; rungs 4-8 were never
  run.

### FRFRMU-1304 — local accounts are market intelligence, never pattern sources

Step 2.1a already says the local sample is READ, not ADDED. **Make it enforceable:**
local-tagged accounts (the `local` tag from Step 2.5) are counted and reported in the
`benchmark_breadth` readout — never added to the pattern pool this step's band judgment draws
from. If a local account also independently reads as a genuine niche match under Step 2.2's
screening AND the derived band on its own genuine merits as a NICHE-WIDE candidate, it may be
added — but never on the strength of being local, and confirm the real verdict once it IS added
(`niche_fit_verdict` on `add_to_watchlist`'s response, FRFRMU-1528/1536 — not decided here, only
anticipated). The readout says explicitly: "local accounts are market intelligence, not pattern
sources" whenever a local sample was read this run.

### FRFRMU-1285 — zero winners is a stop, not a line in a table

If the approved benchmark set produces no account that ever reached beyond its own following —
by the account-relative digest and the typical-reel-views gate in `step-02-6-screening.md`, not
`viral_3x` alone (⚠️ read this together with FRFRMU-1303's caveat: a raw `viral_3x` count means
nothing without the typical-reel-views context) — **stop and re-research.** Do not plan on a set
that has never demonstrated it can teach what travels.

**When the customer challenges the set, re-check the numbers before defending it.** In the live
run this ladder is built from, the agent argued instead of looking — re-pull the real numbers
(`search_watchlist`, `get_profile_posts`) and answer with THOSE, not with the original reasoning
restated more firmly.

**Then continue to Step 2.4** for the human approval gate.
