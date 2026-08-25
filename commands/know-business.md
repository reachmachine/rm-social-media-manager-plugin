---
description: "Understand and record the business a plan is for — stage, positioning, funnel assets, goal. Free, never spends credits"
argument-hint: "[@handle, a short business brief, or leave empty to be interviewed]"
---

Understand the business this workspace plans for, and save it. **Reads and writes the profile
— never spends credits.** This is the skill's Step 1, on its own, so it can be redone without
rerunning a whole plan.

What the user gave: $ARGUMENTS

Load the skill's PLAYBOOK **Step 1** and follow it. Do not invent a shorter version.

## Read before you ask

`get_business_profile` and `get_creator_brief` first. Show what is already saved, then ask only
about what is **missing or stale** — re-interrogating a returning client from scratch is the
main thing this command exists to avoid.

## The four things a plan cannot be built without

1. **Who it is FOR** — the account owner's own brand, or a client they manage? Agencies must use
   a **separate workspace per client** (see `/rm-social-media-manager:switch-workspace`).
2. **Stage** — real follower count and how many reels a week they can sustain. Capacity is part
   of the answer: a plan they cannot film is not a plan.
3. **Positioning** — one ownable angle, their own first-party proof, and the ONE audience.
   Without it a plan can only clone the competitor it came from.
4. **Funnel assets + goal** — is there a lead magnet, is auto-DM live, and is the goal reach,
   leads, or authority? Pick ONE goal.

## Rules that matter here

- **Interview, don't hand over a form** (PLAYBOOK Step 1). One question at a time, and react to
  the answers.
- **Cross-check what they tell you against real data** where you can — `get_workspace_stats`,
  and their own reels if any are analysed. If the stated stage and the data disagree, say so
  kindly and fix the record.
- **Save it** with `update_business_profile` and `update_creator_brief`. An interview you do not
  persist gets repeated next session.
- **Positioning is per-workspace; the Instagram handle is account-wide (G223).** If you set a
  handle here, say plainly that it applies to the whole account, not just this workspace.

**Hard limit:** never call a spend or destructive tool here, and never call Apify.
