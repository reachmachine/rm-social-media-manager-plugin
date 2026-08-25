---
description: "Check how analysed reels were classified — which tags and categories they landed in, and where classification looks wrong. Free, never spends credits"
argument-hint: "[a tag name, category, @handle, or a specific reel URL]"
---

Check the classifications on analysed reels. **Reads only — never spend.**

What to check: $ARGUMENTS

## How to check it

1. **What does the taxonomy actually allow?** `get_taxonomy_definitions` — the real list of tags
   and categories with their meanings. Read it before judging anything as miscategorised.
   **Never speculate about how a tag is computed**; if the definition does not say, say so.
2. **What is even classified?** `get_analysis_coverage` — only analysed reels carry tags. Unanalysed
   reels are not "uncategorised", they are simply not done yet. Keep those two apart; confusing
   them makes healthy data look broken.
3. **Where did things land?** `get_tag_stats` for volume per tag, `get_content_breakdown` for the
   category split, `query_posts_by_tag` to see the actual reels behind a tag.
4. **Spot-check the reels, don't trust the totals.** Pick a few from a tag and read them —
   `get_posts_detailed`, and `get_post_transcript` for a specific reel. A tag with a healthy count
   can still be full of wrong calls, and only looking will show it.

## What to report

- **Thin or empty tags** — which tags have too little volume to draw conclusions from. This is the
  most actionable output: it tells the user what to analyse next.
- **Reels that look wrongly classified** — name the reel, the tag it got, and why it looks off.
  Be concrete; "some look wrong" is not a finding.
- **Anything the taxonomy has no slot for.** If a reel genuinely fits no listed value, that is a
  taxonomy gap, not a bad reel. Say so plainly and use `report_gap` to record it so it reaches the
  team — do not quietly force it into the nearest label.
- Sample sizes on every count, medians not means (PLAYBOOK Step 3, Step 7).

**Hard limit:** never call a spend or destructive tool here, and never call Apify. To classify more
reels, point at `/rm-social-media-manager:watch-video`.
