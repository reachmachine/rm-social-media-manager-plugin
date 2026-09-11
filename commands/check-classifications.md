---
description: "Check how analysed reels were classified — which tags and categories they landed in, and where classification looks wrong. Free, never spends credits"
argument-hint: "[a tag name, category, @handle, or a specific reel URL]"
---

Check the classifications on analysed reels. **Reads only — never spend.**

What to check: $ARGUMENTS

## How to check it

1. **Send these four reads in ONE message — they do not depend on each other:**
   `get_taxonomy_definitions`, `get_analysis_coverage`, `get_tag_stats` and
   `get_content_breakdown`. One round-trip, not four. What each one is for:
   - **What does the taxonomy actually allow?** `get_taxonomy_definitions` — the real list of
     tags and categories with their meanings. Read it before judging anything as
     miscategorised. **Never speculate about how a tag is computed**; if the definition does
     not say, say so.
   - **What is even classified?** `get_analysis_coverage` — only analysed reels carry tags.
     Unanalysed reels are not "uncategorised", they are simply not done yet. Keep those two
     apart; confusing them makes healthy data look broken.
   - **Where did things land?** `get_tag_stats` for volume per tag, `get_content_breakdown`
     for the category split.
2. **Then open the reels behind a tag** — `query_posts_by_tag`. This one waits on purpose:
   which tag is worth opening usually depends on what `get_tag_stats` just showed. If the user
   already named the tag, it can travel in the message above.
3. **Spot-check the reels, don't trust the totals.** Pick a few from a tag and read them —
   `get_posts_detailed`, and `get_post_transcript` for a specific reel. Ask for all the
   spot-checks you want in one message. A tag with a healthy count can still be full of wrong
   calls, and only looking will show it.

## What to report

- **Thin or empty tags** — which tags have too little volume to draw conclusions from. This is the
  most actionable output: it tells the user what to analyse next.
- **Reels that look wrongly classified** — name the reel, the tag it got, and why it looks off.
  Be concrete; "some look wrong" is not a finding.
- **Anything the taxonomy has no slot for.** If a reel genuinely fits no listed value, that is a
  taxonomy gap, not a bad reel. Say so plainly and use `report_gap` to record it so it reaches the
  team — do not quietly force it into the nearest label.
- Sample sizes on every count, medians not means (PLAYBOOK Step 3, Step 7 — load ONLY
  `playbook/step-03-mcp.md` and `playbook/step-07-strategy.md`).

**Benchmark lens — say which creators the answer came from.** These reads default to the
accounts on your watchlist only. The pattern tools (`get_content_strategy`, `get_hooks_library`,
`get_cta_library`, `get_content_structures`) take `scope`: `mine` is your watchlist, `niche` is
the wider community pool, `both` combines them. The tag and post tools (`get_tag_stats`,
`get_avg_scores`, `query_posts_by_tag`) take `analysis_mode`, whose
`community_per_account` and `community_cross_account` values widen the pool the same way.
**When a finding is about to drive a recommendation, read it again through the wider lens and
compare** — a casual "just show me the list" answer stays on one lens. Label every answer with
the set behind it and how many reels that is ("your 15 tracked accounts, 212 analysed reels"),
and quote the count the wider read actually returns instead of assuming it is bigger. If the
wider view is not available here — the community tools are not offered, or the pool comes back
empty — say so plainly; never quietly fall back to the watchlist after being asked for the
wider picture. Full detail: `playbook/step-03-mcp.md`.

**If something in the answer looks wrong, do not explain it away.** Say the likely
reason in plain words, say what can still be trusted, and report anything we do not
already know about. The known signatures and the exact wording: `data-quality.md`.

**Hard limit:** never call a spend or destructive tool here, and never call Apify. To classify more
reels, point at `/rm-social-media-manager:watch-video`.
