---
description: "List the competitors tracked in this workspace, with how much data each one has. Free, never spends credits"
argument-hint: "[a name/handle to filter by, or leave empty for all]"
---

Show the competitors on this workspace's watchlist. **Reads only — never spend.**

Filter: $ARGUMENTS

1. **Name the workspace first.** `list_workspaces` — state which workspace is active before
   listing anything. The same account can hold several, and a list with no workspace named is
   how someone reviews the wrong client's competitors.
2. `search_watchlist` for the tracked accounts. `get_workspace_stats` for the totals.
3. **Show usefulness, not just names.** For each competitor give: handle, follower size band,
   how many reels we hold, and how many are **analysed** — an account with 200 reels pulled and
   0 analysed contributes nothing to any insight yet. Use `get_profile_details` for detail on a
   specific one. Flag anything that looks stale or inactive.
4. **Say what is missing.** If several have data pulled but not analysed, point at
   `/rm-social-media-manager:watch-video`. If the set looks thin or off-niche for the creator's
   goal, point at `/rm-social-media-manager:find-competitors`.
5. Judge the set by **FIT, not fame** (PLAYBOOK Step 2.3): brands, media companies, agencies and
   mega-accounts a small creator cannot model are noise even when their numbers look great. Say
   so when you see them, and mention `/rm-social-media-manager:delete-competitors`.

**Hard limit:** never call a spend or destructive tool here, and never call Apify. Removing an
account is a separate, explicit command — never remove one from this view.
