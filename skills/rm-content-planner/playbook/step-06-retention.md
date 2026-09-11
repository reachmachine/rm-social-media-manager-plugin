> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 6 — Retention, not just hooks

The hook buys the *test* impressions; **watch-time + replays** decide whether the
algorithm pushes past the follower base. For every reel specify:

- an **open loop** in the hook,
- a **mid-reel re-hook** (~40% mark),
- a **loop-back ending** so the reel replays.

**Be honest about the evidence — retention is the weakest-sourced lever, and it
matters most.** RM cannot see competitor watch-time, so retention is inferred, not
measured. **Build the recipe DATA-FIRST — derive it, don't default it:** (1) pick which reels to model
retention from by **saves + shares per 1k** — the reels that provably HELD people, not just high-view
ones; (2) **derive the actual open-loop / mid re-hook / loop-back from THOSE reels' beat-structure** where
it's present, instead of applying a generic template; (3) only where no structure data exists, fall back
to the generic recipe as craft. Tag every retention line by which of these it came from:
- **If a real beat structure came back** (`beats` / `segments` / `template_structure`
  from `get_post_transcript`), build the retention line from it and cite it — that is
  the strongest available signal. *(Note: `beats` is often empty even on analysed
  reels — a known bug; when it is, fall back to `template_structure`/`segments`.)*
- **If nothing usable came back, the retention line is SMM JUDGMENT (craft), and it is
  tagged JUDGMENT — never DATA-DRIVEN.** Do not dress a structural guess as data.
- **A defensible proxy for "did this reel actually HOLD people":** shares- and
  saves-per-1k. A reel people save and share held their attention; rank the reels you
  model retention on by that, not just by views. Tag it DATA-INFERRED.
- **The real retention data lives in the creator's OWN analytics.** Once their account
  is tracked (Step 1.6), ask them to report their posted reels' **average watch-time /
  %-watched** from Instagram — that is measured retention for *their* audience, and it
  beats any competitor proxy. Feed it back via the Creator Brief for the next cycle.

---

