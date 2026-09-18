> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 6 — Retention, not just hooks

The hook buys the *test* impressions; **watch-time + replays** decide whether the
algorithm pushes past the follower base. For every reel, save `retention` as an
OBJECT — a real audit (FRFRMU-1544) found this collapsing into a one-line paraphrase
of the hook, which a creator cannot act on:

```
retention: {
  "open_loop":  "<the IDEA the hook plants — a short phrase, NEVER the hook's own
                  wording. If you find yourself copying words from hook.spoken or
                  hook.on_screen, you have the wrong sentence — describe what
                  question the hook leaves open instead.>",
  "rehook": {"options": [
    {"line": "<a SAYABLE line or on-screen text a creator can read at ~40% —
               never a stage direction like 'show the guarantee'>",
     "form": "<the creator's own move — see the catalogue below, NEVER a generic
              universal label>",
     "provenance": "data_driven | data_inferred | judgment",
     "receipt": {"kind": "retention_pattern", "n": <int>, "accounts": <int>,
                 "example_urls": [...]} | null,
     "recommended": true | false}
    /* 3-5 options total, per FRFRMU-1546 — never more than 5 (a long list is
       the same "cannot act on this" problem in a new shape). */
  ]},
  "loop_back":  "<one line — how the ending points back at open_loop>"
}
```
`rehook.options` needs >= 1 real option; `retention_rehook_present` blocks an empty
list, `retention_rehook_distinct_from_hook` blocks a `line` that overlaps too much
with `hook.spoken` / `hook.on_screen` / `open_loop` — the exact bug this ticket
found, now checked mechanically at save time, not just by a reviewer's eye.

**FRFRMU-1546 — build the 3-5 options from `get_retention_patterns`, not from
imagination alone.** Call it (scope = mine | niche | both, matching this plan's
sourcing) and it returns the mid-video re-hook wordings this niche's OWN rewatch-
winning reels actually use — `patterns[{form, n, accounts, rewatch_share,
provenance, recommended, examples}]`, already ranked by real support and capped
at 5. This is the "niche-aware catalogue": a gym's list and a SaaS demo's list are
built from different reels and come out different, because `form` is the
creator's own wording, never a fixed universal label.

- Every pattern the tool returns is real evidence — carry its `provenance`,
  `n`/`accounts` into `receipt`, and its `recommended` flag straight through
  (it is already `true` on at most one option, and only when that option has
  real support — never re-derive or override it here).
- **The tool can return fewer than 3 patterns, or none at all** — a thin or new
  niche genuinely has not analysed enough rewatch-winning reels yet. Fill the
  rest of the 3-5 slots with craft options built from this file's recipe below,
  labelled `"provenance": "judgment"` and `"receipt": null`. Never present a
  craft guess as if the tool found it — that is exactly the dishonesty this
  ticket exists to prevent.
- Never invent a `form` value that is not either (a) one of the tool's own
  `patterns[].form` strings, cited, or (b) a craft option you built yourself
  and honestly labelled `judgment`.

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

