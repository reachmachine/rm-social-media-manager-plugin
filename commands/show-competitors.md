---
description: "List the competitors tracked in this workspace, with how much data each one has. Free, never spends credits"
argument-hint: "[a name/handle to filter by, or leave empty for all]"
---

Show the competitors on this workspace's watchlist. **Reads only — never spend.**

Filter: $ARGUMENTS

1. **Name the workspace first.** `list_workspaces` — state which workspace is active before
   listing anything. The same account can hold several, and a list with no workspace named is
   how someone reviews the wrong client's competitors.
2. **Get the WHOLE list, not the first page.** `search_watchlist` returns only 20 accounts
   per call by default. Ask for `page_size=100`, then keep asking for the next `page` until
   you have as many accounts as the reply's own `total_count` says exist. **Then say the
   number out loud in your answer — "showing 47 of 47".** A workspace tracking 40 accounts
   that is shown 20, with nothing saying so, is how someone decides an account was never
   added and pays to add and analyse it a second time. `get_workspace_stats` for the totals.
3. **Show usefulness, not just names — and surface stale/empty accounts (FRFRMU-1110).** For
   each row `search_watchlist` already returned, read `pulled_posts_count`, `data_age_days`, and
   `stale` (a stale row means the newest reel we hold is over `DATA_STALE_DAYS` old, default 7
   days — refreshing is what tells you whether the account went quiet or our pull is just old).
   `data_age_days` is `null` for a zero-reel row — that is NOT the same as `stale`; a zero-reel
   row is flagged by `pulled_posts_count == 0`, never by `stale`. Use `get_profile_details` for
   deeper detail on one specific account, not to discover staleness — the list already carries it.
   **Render summary-first:** open with ONE line — "N competitors · K hold data older than
   `DATA_STALE_DAYS` days (oldest: `<handle>`, `<data_age_days>` days) · M hold no reels
   (`<handle>`, `<handle>`)." List the stale and zero-reel rows FIRST, each with its plain age
   ("258 days") or "no reels" — every other row just shows its age quietly, no adjective (alert
   fatigue: `DATA_STALE_DAYS` is low and this niche posts daily, so most rows will often be over
   the line — a badge on every row becomes wallpaper). Self rows (`role == "self"`) read "you last
   posted N days ago", never "your data is stale", and are never counted into the stale/zero-reel
   groups or the refresh suggestion below. Make exactly ONE refresh suggestion for the whole
   stale set, with its cost — call `refresh_competitor` WITHOUT `confirm` (server-enforced no-op;
   it returns a cost preview and spends nothing) — never one suggestion per row, and never call it
   with `confirm=true` here. For the zero-reel accounts, one neutral line: "pull them or free the
   seat with `/delete-competitors`" — never actively recommend removal from age or emptiness
   alone (a 0-reel row can be a failed first pull or a private/new account, and age alone cannot
   tell "our pull is old" from "they stopped posting").
4. **Say what is missing.** If several have data pulled but not analysed, point at
   `/rm-social-media-manager:watch-video`. If the set looks thin or off-niche for the creator's
   goal, point at `/rm-social-media-manager:find-competitors`.
5. Judge the set by **FIT, not fame** (PLAYBOOK Step 2.3, in
   `playbook/step-02-benchmarks.md`): brands, media companies, agencies and
   mega-accounts a small creator cannot model are noise even when their numbers look great. Say
   so when you see them, and mention `/rm-social-media-manager:delete-competitors`.

**Hard limit:** never call a spend or destructive tool here, and never call Apify. Removing an
account is a separate, explicit command — never remove one from this view.
