> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 4 — Translate for the account's STAGE (the anti-trap layer)

**Ask per `asking-rules.md`.**

The single biggest failure mode: copying a scaled tactic onto the **wrong-stage** account. Everything the
data shows comes from creators who already have reach — so read the account's **stage** (from Step 1) and
pick the right translation. **This is a LADDER, not a cold-start-only rule** — the correct move flips as the
account grows (the same CTA that hurts a 500-follower account is right for a 50k one).

**The data helps with SIZE-FAIRNESS — via the `cross_account` mode.** RM's tags / viral % are computed
**per follower-tier** when you read the tag/coverage tools in **`cross_account` mode** (Step 3 rule 3,
verified in the engine) — so a size-fair comparison exists there: model reels from **the account's own
size band**, not a 10M celebrity's raw views. *(The deeper normalized / community lenses exist in the
engine but aren't exposed via the MCP yet — G116; and the lever tools take no mode selector, so lean on
`cross_account` on the tag tools + judgement.)* That covers the *benchmark* layer as far as the tools
allow; the ladder below covers the *tactical* layer (CTA, cadence, funnel, concentrate-vs-diversify).

| Stage (Step 1) | CTA | Focus | Cadence / KPIs |
|---|---|---|---|
| **Cold-start (0–~1k)** | **Default to reply-bait** — a keyword-DM CTA on a tiny audience usually gets very few replies and costs reach. **Only use keyword-DM if the lead magnet + DM automation are confirmed built AND tested** — recommend against it anyway unless the creator has a real reason, and say plainly it will get fewer replies at this size. | Find ONE working hook; reach-first; **concentrate** | 3/week; judge by hour-1 speed / watch-time / saves-per-1k, **not raw views** |
| **Growing (~1k–10k)** | Keyword-DM **only once a reel clears ~5–10k AND the freebie + auto-DM exist**; else reply-bait | Double down on early hits + start light nurture; begin diversifying pillars | build cadence; add follower-growth + save/share rate |
| **Established (~10k–100k)** | Keyword-DM works; run **activation / offer reels** | Diversify pillars; weight authority + nurture; can push offers | judge by **leads / sales**, not just reach |
| **Large (100k+)** | Full funnel — big-creator tactics apply directly (the data *is* them now) | More formats / cadence; protect the winners | leads / sales / retention |
| **Stalled / plateaued (any size, flat)** | Same CTA as its size row | **The problem isn't reach volume — it's a stale pattern:** test NEW hooks/angles/formats, check if the positioning drifted | watch the **trend**, not the absolute |

**Harden it — the gaps this exposes (handle each):**
- **Stage ≠ follower count alone.** Read the size band *together with* **engagement/reach health** — a 5k
  account with dead engagement is really acting like a cold-start. Mis-stage the account and the whole row
  is wrong.
- **Detecting "stalled."** Read the **trend** of the creator's OWN recent reels (Step 1.6 / Step 3): flat or
  declining views / follower growth over recent posts = stalled → use the stalled row, whatever the size.
- **Goal ↔ stage mismatch.** A cold-start account with a **leads/sales** goal is premature — flag it and
  steer to **reach first** (you can't harvest leads with no audience). Catch it here, before building.
- **Very small / new accounts → the size-tiered tags are UNRELIABLE** (thin data; the per-account viral
  tags over-fire on 2–4-post accounts — G109–G112). For a cold-start, lean on the **`cross_account`
  (follower-tier)** view + judgment; don't over-trust "their own top 1%."

## Step 4.8 — the 5-question sales-readiness check (p33, FRFRMU-1071)

**Every account WITH an offer** gets this — one read-only screen over keys already filed, no new
questions to the creator, never a reason to block the plan. It answers the founder's own test:
*"can this foundation pitch yet?"* When an account has no offer, skip this step entirely — there is
nothing to pitch.

For each of the five questions, point at the filed answer or write **"unanswerable — \[card\]
incomplete."** An unanswerable question is never invented an answer:

1. **New opportunity** — `why_people_buy` (FRFRMU-1041) + the offer name (FRFRMU-1054). Unanswerable
   without either → "unanswerable — p06/p19 incomplete."
2. **The Big Domino** — `big_domino` (FRFRMU-1040). Unanswerable when empty → "unanswerable — p08
   incomplete."
3. **The special offer** — the value stack + names + promise + guarantee (FRFRMU-1049/1054/1056/1053).
   Unanswerable when the stack is empty → "unanswerable — p15-p18 incomplete."
4. **The origin story** — `origin_story` (FRFRMU-1044), the 8-beat form or a cut. Unanswerable when
   empty → "unanswerable — p10 incomplete."
5. **The three false beliefs + bridge stories** — `false_beliefs.core_three` (FRFRMU-1045).
   Unanswerable when fewer than three core rows exist → "unanswerable — p11 incomplete."

**Shown as** *"Can your foundation pitch yet? N of 5"* — in the plan's Part A (TEMPLATE.md's A0b)
and on the Foundation UI (FRFRMU-1042). This never blocks a content plan; it only names the
missing card so the creator (or a later session) knows exactly what to fill next.

---

