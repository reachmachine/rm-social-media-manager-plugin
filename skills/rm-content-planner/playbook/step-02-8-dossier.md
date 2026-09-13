> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 2.8**, right after Step 2.7's finished-set approval, before Step 3's
> analysis. **Pass 2 of this same step re-runs after Step 3's analysis lands.** This is p07
> "Build a Competitor Dossier" (`marketing/rules/process-cards/p07-build-competitor-dossier.md`,
> FRFRMU-1038): model what already works for each approved competitor, one dated page per
> handle, every claim with a source.

## Step 2.8 — Competitor dossier (p07), two passes

**Ask per `asking-rules.md`.**

**🔴 The G332 wall, restated: this step NEVER discovers, names, proposes or auto-adds an
Instagram account.** It only researches accounts a human already approved in Step 2 (2.4 +
2.7). A competitor mentioned on a rival's bio or page is not a candidate — it is not looked at
for that purpose at all. The one exception (angle G below) still runs through Step 2's normal
human + spend gates; this file never adds anyone on its own.

### Pass 1 — right after 2.7, before any analysis

For each approved competitor, in one dated block:

1. **Where the bio link lands.** Call `get_profile_details` for the handle, read `external_url`.
   Classify the destination in one word: lead magnet / booking / course / waitlist / shop / none
   / link-aggregator (if a link-in-bio tool, list its top links). No `external_url` on record →
   `"landing": "none"`, not a guess.
2. **What they sell.** Apply the existing G372 commercial lens (`step-01-intake-fields.md`) to
   THIS account: bio → website/pricing page → offer, price, promise, funnel step, each with
   `{source, date}`. "Couldn't find publicly" is a real, honest answer. **Always `JUDGMENT`,
   never `DATA-DRIVEN`** — same rule as the G372 scan itself (FRFRMU-364).
3. **Direct or indirect.** `direct` unless the handle was added through angle G below.
4. **Ask-user, once per competitor:** *"Have you bought or trialled [handle]'s product? Paste
   what the upsell path looked like."* → `FROM-EXPERT`, dated. A "no" is a fine answer.
5. **Nationwide or local (FRFRMU-1151).** Read back the breadth tag Step 2.5 set on this
   competitor via `add_competitor_tags` — `niche_wide` or `local` — from `search_watchlist`'s
   `tags` field. `agent`, `JUDGMENT`. Wherever this dossier or the plan cites a pattern from a
   `local` account, label it "local market signal, not a niche pattern".

A pass-1-only block is **INCOMPLETE by definition** — it has at most 2 of the 5 variables
(offer, landing) filled. Say so plainly; never present it as done.

### Pass 2 — after Step 3's analysis lands

Add to the same dated block:

6. **Who they target.** Roll this competitor's analysed reels up to a dominant audience segment
   via `get_content_strategy` — `DATA-DRIVEN`, cite `n`.
7. **What drives their reach (organic only).** `get_format_ranking`, `get_recurring_audio` —
   `DATA-DRIVEN`, cite `n`. **No collab/tag frequency anymore.** Step 2's angle C used to read
   collaborators off an Apify-scraped reel; that angle is gone (FRFRMU-1315 — Apify may not
   scrape a reel or a post, for any reason, because a reel obtained that way never enters the
   Reach Machine pipeline and is never processed or tagged). Say `"not collected"` if a
   customer asks who a competitor collaborates with — never guess it from memory.
8. **Their persistent winners.** Link 2-3 of this competitor's analysed reels that are still
   performing (the swipe file) — no copies, ids/links only.
9. **Paid traffic + paid ad copy — always `"unknown — not collected yet"`.** The server-side
   Proven Ads feature (FRFRMU-1039) is not built. If it ships later and `get_competitor_ads`
   exists, read it here; until then this is never guessed and never left blank — it says
   `unknown` in words. **A dossier that writes anything else for paid traffic — "probably runs
   ads", a made-up count — fails.**

A block with `>=4` of the 5 variables filled (offer, landing, target, organic-reach-and-winners,
plus paid which is honestly `unknown`) reads as **complete for what the plugin can fill today**.
A block with `>=2` real unknowns beyond the always-unknown paid one is marked `INCOMPLETE`.

### Angle G — indirect competitors (opt-in, human-gated, Step 2)

Ask ONCE during Step 2 intake: *"Who else gets your customer's money for the same problem, even
with a different product?"* Take 1-2 named handles. Add them exactly like any other Step 2
account — `add_to_watchlist` (confirm-before-spend, 2.5) then the same 2.4/2.7 human gates — then
tag the item `indirect` with `add_competitor_tags` (an existing tool; **no new watchlist field**).
Never proposed by web search or by reading a rival's page (G332). The dossier's pass 1 reads that
tag back (`search_watchlist` already returns `tags`) to set `"relationship": "indirect"` and
labels the account's patterns "angle imports, not direct benchmarks" wherever the plan cites it.

### Save it

One Creator Brief key per competitor, `competitor_dossier__<handle>` (handle lowercased,
`@`-stripped), in the shape `/settings/profile` renders (FRFRMU-1042):

```
{
  "card": "competitor_dossier", "title": "Dossier — @<handle>",
  "status": "confirmed",   # "hypothesis" while pass 2 hasn't run yet (INCOMPLETE)
  "summary": "<one line: direct/indirect, offer, landing, INCOMPLETE if it is>",
  "items": [
    {"item_id": "landing", "label": "Where the bio link lands",
     "text": "<classification>", "who": "agent", "provenance": "JUDGMENT",
     "source": "get_profile_details.external_url", "date": "<ISO date>"},
    {"item_id": "offer", "label": "What they sell",
     "text": "<offer, price, promise, funnel step, or 'couldn't find publicly'>",
     "who": "agent", "provenance": "JUDGMENT", "source": "<url>", "date": "<ISO date>"},
    {"item_id": "relationship", "label": "Direct or indirect",
     "text": "direct", "who": "you", "provenance": "FROM-EXPERT"},
    {"item_id": "breadth", "label": "Nationwide or local benchmark",
     "text": "niche_wide|local", "who": "agent", "provenance": "JUDGMENT",
     "source": "search_watchlist.tags"},
    {"item_id": "purchase_notes", "label": "Have you bought/trialled this?",
     "text": "<the creator's own notes, or 'no'>", "who": "you", "provenance": "FROM-EXPERT",
     "date": "<ISO date>"},
    {"item_id": "target", "label": "Who they target",
     "text": "<segment>", "who": "agent", "provenance": "DATA-DRIVEN", "used_in": ["n=<count>"]},
    {"item_id": "organic_reach", "label": "What drives their organic reach",
     "text": "<formats/audio/collabs>", "who": "agent", "provenance": "DATA-DRIVEN",
     "used_in": ["n=<count>"]},
    {"item_id": "winners", "label": "Their persistent winners",
     "text": "<2-3 post ids/links>", "who": "agent", "provenance": "DATA-DRIVEN"},
    {"item_id": "paid_traffic", "label": "Paid traffic + ad copy",
     "text": "unknown — not collected yet", "who": "agent", "provenance": "JUDGMENT"}
  ],
  "updated_at": "<ISO date>"
}
```

### What this step refuses to do

Propose, name or auto-add any account not already approved in Step 2 · label a web-read offer
`DATA-DRIVEN` · write anything for paid traffic other than the exact honest `unknown` string
until FRFRMU-1039 ships · store a competitor's private pricing or emails (public pages only) ·
run without a shown cost preview for angle G's `add_to_watchlist` call (it uses the same gate as
every other Step 2 add).

### Refresh

Stale after 30-60 days (the existing benchmark-staleness rule, `step-02-benchmarks.md`). Re-run
pass 1 + pass 2 for a competitor before a plan leans on a dossier line that old.
