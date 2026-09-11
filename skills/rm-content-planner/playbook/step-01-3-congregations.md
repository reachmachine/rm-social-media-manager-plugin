> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 1**, right after `step-01-2-avatar.md`, before Step 2 (discovery).
> **Entry rule: only when `congregations` is missing or the creator says "find my
> communities."** Otherwise skip this whole file in one line. This is p03 "Map Where the
> Dream Customer Congregates" (`marketing/rules/process-cards/p03-map-congregations.md`,
> FRFRMU-1033): dream customers clump together like gold in a vein — find the vein and you
> have a whole cluster, not one person.

## Step 1.6b — Map the congregations (p03)

**Ask per `asking-rules.md`.**

Every question ends in a status: `answered_pass | answered_weak | declined | not_applicable |
deferred`.

**1. Seed keywords (agent-fills)** from the `avatar` card's PQR2 + pain/pleasure vocabulary
(p02, FRFRMU-1031).

**2. Search the veins (agent-fills, cited).** Keyword + "forum"; groups; newsletters; blogs;
podcasts; books; subreddits / Discord / Slack / Telegram / WhatsApp / newsletter platforms.
**Every entry named + linked**, with a rough size/activity note and a date — record a dead
forum honestly (inactive, dated), don't hide it. **An unnamed "Facebook groups exist" fails;
an invented community is a defect.**

**3. Platform preference (ask-user):** *"Where do your best customers actually message you
from?"* — stated with evidence, never assumed.

**4. Rank the veins.** Recommend the ONE to dig first, with a one-line reason; the creator
confirms. **A flat, unranked list fails.**

**5. Few found?** Widen ONE drill-down level (micro-niche → sub-niche) for the SEARCH only —
the avatar itself stays narrow; say plainly the niche gathers in broader rooms.

### 🔴 G332 wall — restated here, unchanged

This map surfaces communities and channels ONLY. **It never adds an Instagram account to the
watchlist, and it never names candidate Instagram accounts from web research** — that stays
Step 2's job, behind its own two explicit-yes gates (the Apify spend gate, then
`add_to_watchlist`). An Instagram handle in this step's output is a defect.

### Attribution honesty

Keywords handed to Step 2 or the hashtag recipe are **community-sourced, never a promise of
reach** — nobody can measure a hashtag's contribution. Never say "these tags will get you
discovered."

### What this step refuses to do

Invent a community, forum or group name · list an unnamed "Facebook groups exist" as a
finding · leave the list unranked · add an Instagram handle to the map · claim a hashtag will
get a reel discovered · add an account to the watchlist directly.

### Save it

Write the result to the Creator Brief as the Foundation card key `congregations`
(FRFRMU-1042 shape):

```
{
  "card": "congregations", "title": "Where the dream customer gathers",
  "status": "confirmed",
  "summary": "<the one vein to dig first + why>",
  "items": [
    {"item_id": "vein_01", "label": "<community name>", "tag": "congregation",
     "text": "<type + size/activity note + date>", "who": "agent",
     "provenance": "FROM-EXPERT", "source": "web:<url>"},
    ...
    {"item_id": "platform_preference", "label": "Where customers message from",
     "text": "<the creator's answer>", "who": "you", "provenance": "FROM-EXPERT"},
    {"item_id": "dig_first", "label": "Rank: dig first", "text": "<vein_id + reason>",
     "who": "agent", "provenance": "JUDGMENT"}
  ],
  "updated_at": "<ISO date>"
}
```

At least 10 named + linked congregations across at least 3 types (`tag: "congregation"`), or
an honest "found N, here is why" note in the summary when the niche is genuinely thin.

## Wire into

* **Step 2 discovery (`step-02-benchmarks.md`):** seeded from this map's hashtags/keywords —
  see that file's "Seed from the congregation map" block. No `congregations` key → today's
  discovery is unchanged.
* **Hashtag recipe HT.1 (`step-08-hashtag-recipe.md`):** slot (1), "the audience's own
  language," draws from this map when it exists, tagged community-sourced. No `congregations`
  key → HT.1 reads only intake, unchanged.
