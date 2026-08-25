---
description: "Size the market and pick the segment to target — TAM, sub-segments, where the creator can realistically win, and (G372) how the niche's leaders operate commercially. Free of RM credits"
argument-hint: "[the niche, audience, or offer to size]"
---

Do real market research so the target segment is a decision, not a vibe. **Spends no Reach
Machine credits.** Follow the skill's PLAYBOOK **Step 1 market-sizing rule (G233)** — it already
sanctions `WebSearch` for exactly this.

What to size: $ARGUMENTS

## 🔴 This is the ONE place web search is allowed — and only for market facts

Web search is legitimate here: market size, audience counts, pricing norms, competitor
landscape, and — since G372 — a quick read on how the niche's leading players actually operate
commercially. It is **never** allowed for finding benchmark Instagram accounts (G332) — that is
`/rm-social-media-manager:find-competitors`, which uses Apify. Do not blur the two.

## How to do it

1. **Start from the business.** `get_business_profile` + `get_creator_brief`. Sizing a market
   without knowing the offer and the stage produces a number nobody can act on. If they are
   empty, route to `/rm-social-media-manager:know-business` first.
2. **Size it top-down AND bottom-up, then compare.** Top-down: published market size, then the
   share that plausibly fits this offer. Bottom-up: reachable audience × realistic conversion ×
   price. **When the two disagree by a lot, say so** — that gap is the most useful output here,
   not something to average away.
3. **Break it into sub-segments** and score each on: size, how reachable they are on Instagram,
   ability to pay, and how well this creator's actual proof fits. Recommend ONE beachhead
   segment and say what you are deliberately NOT targeting.
4. **Cross-check against our own data where it exists.** `get_taxonomy_definitions` and
   `get_tag_stats` show which niches Reach Machine actually holds data for. A segment we have no
   competitor data for is harder to plan against — flag it.
5. **See how the niche's leaders operate, briefly (G372).** A quick scan of the niche's top 3-5
   players — their offer, price point where public, promise, and the funnel step they lead
   with — each cited with a source and a date. Full method, and why this stays a quick scan and
   never a full teardown: PLAYBOOK Step 1's "Niche commercial landscape" bullet. This step must
   **never** be used to find or suggest Instagram accounts to add — that stays Apify-only, in
   `/find-competitors` (G332).

## Rigor — this one is mostly judgment, so label it

- **Cite a source and a date for every external number**, and say when a number is an estimate.
- Label conclusions **JUDGMENT** unless real data backs them. A TAM built from web sources is
  **never** DATA-DRIVEN in this skill's sense — that label is reserved for claims with a real
  sample size from analysed reels.
- **State what would change your answer.** A market call no evidence could overturn is a guess.
- Give ranges, not false precision. "Roughly 40–80k businesses in India" beats "62,431".

**Hard limit:** never call a spend or destructive tool here, and never call Apify.
