---
description: "Find benchmark accounts and add competitors to the watchlist — discovery, shortlist, human-approved add (spends credits only after an explicit yes)"
argument-hint: "[niche, seed @handles, or hashtags to research]"
---

Re-run competitor discovery for this creator. This is a re-entry point into the
`rm-social-media-manager:rm-content-planner` skill's "Step 2 — Find benchmark
accounts" — load that PLAYBOOK section and follow it exactly. Do not invent a
lighter version of it here.

Seeds the user gave: $ARGUMENTS

## Prerequisite gate — check BEFORE discovering anything

Call `get_business_profile` and `get_creator_brief` first. Discovery is seeded
off the SUBJECT's niche, stage and named accounts — without them you'd research
the wrong market.

- **Both empty / missing the niche:** stop. Say "I don't know your business yet —
  let me ask a few questions first," run the skill's Step 1 intake (the expert
  conversation, not a form), save it via `update_business_profile` /
  `update_creator_brief`, THEN come back here.
- **Present but stale-looking** (e.g. follower stage clearly outdated): confirm
  in one line before proceeding — "Your brief says X, still right?"

## Then follow PLAYBOOK Step 2, with these gates intact

1. `discover_accounts` FIRST — free, read-only. If it returns nothing for the
   niche, say plainly that RM holds no verified accounts for it; never invent
   handles as if they were RM data. Use the propose-from-seeds fallback only as
   clearly-labelled unverified suggestions.
2. Cheap pre-filter before spending a cent: drop brands, media, mega-accounts a
   small creator can't model. Rank by FIT, not fame.
3. **The human approves the shortlist** — never add an account they didn't
   approve.
4. `add_to_watchlist` is **confirm-before-spend**: show the cost preview from the
   un-confirmed call and WAIT for an explicit yes before calling with
   `confirm=true`. No yes, no spend — this gate is server-enforced AND yours to
   honour in conversation.
