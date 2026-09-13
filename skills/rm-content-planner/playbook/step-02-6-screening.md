> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 2.6**, right after Step 2.5 adds the shortlist, before Step 2.7's
> finished-set approval. Split out of `step-02-benchmarks.md` (FRFRMU-1303) to stay under the
> 300-line cap.

## Step 2.6 — Filter on REAL metrics AFTER adding — the honest catch

The true numbers (`follower_count`, `median_er`) only exist once tracked. **One
`search_watchlist` call already gives you most of them** — every account in its list comes back
with `follower_count`, `median_er`, `engagement_rate` and `pulled_posts_count`. So read the
list, and do **not** call `get_profile_details` once per shortlisted account: that is 8-15
separate round-trips to fetch numbers you were already handed. Ask for `page_size=100`, sort
`follower_count_desc`, and let the server narrow the set with the `min_followers` /
`max_followers` / `has_follower_count` filters; keep asking for the next `page` until you have
as many accounts as the reply's own `total_count` says exist.

### The benchmark gate — typical reel views vs follower count

**Founder decision, 2026-09-12, corrected 2026-09-13 (FRFRMU-1303): an account only qualifies
as a pattern source if its TYPICAL REEL's views are a healthy share of its follower count.**

The first version of this gate read `avg_views` (a plain mean across every post the account
ever posted). Run against the real dev watchlist, it rejected 77 of 89 accounts — including
MrBeast, 86.9M followers, posting daily. His stored history is one genuine 23.4M-view reel and
a pile of "Follow me for 10k" bait under 6,000 views each; the mean of those numbers describes
nothing. **Read `median_reel_views`, not `avg_views`**, off `get_profile_posts`'s
`account_metrics` block — it is already the median, already reels-only, computed server-side
because the MCP surface cannot tell a photo from a reel (nothing here has to).

**Three fields, already computed for you — never compute this by hand:**
- `median_reel_views` — the account's typical reel's views. `null` with `pulled_posts_count`
  also 0 means no reel is pulled yet (step 1 below). `null` with `pulled_posts_count > 0` means
  reels ARE pulled but this metric hasn't been computed for them yet (a re-pull or a
  derived-metrics backfill is needed) — treat that the SAME as a thin sample (step 3), never as
  0 and never as a fail.
- `reel_sample_size` — how many reels that median came from. Also null in both cases above.
- `benchmark_reel_sample_floor` — the minimum sample size before you may judge the account at
  all (env-configured, do not hardcode a number of your own).
- `benchmark_views_per_follower_floor` — the minimum `median_reel_views / follower_count` ratio
  for THIS account's own follower-count band (also env-configured — views-per-follower falls
  steeply as an account gets bigger, so one flat bar would reject every large account).

**The steps, in order, per surviving account:**
1. If `pulled_posts_count` is 0 — nothing to measure yet. Re-run this gate for that account
   right after 2.8 pulls its reels, not now.
2. Call `get_profile_posts` and read `median_reel_views`, `reel_sample_size`,
   `benchmark_reel_sample_floor`, `benchmark_views_per_follower_floor` off `account_metrics`.
3. **`reel_sample_size` is null OR below `benchmark_reel_sample_floor` → cannot be assessed
   yet.** Say so plainly and keep the account provisionally — never coerce a null into 0 or
   read it as a fail. A median of 1-2 reels (or no computed median at all) is not a "typical"
   figure. Re-check once more reels are pulled, or once a re-pull/backfill has run.
4. Otherwise compute `median_reel_views / follower_count` and compare to
   `benchmark_views_per_follower_floor`. **Below the floor → the account is not a pattern
   source.** Remove it (`remove_competitor` is free) and go find another, quoting the REAL
   numbers in one line the customer can follow — e.g. *"@handle's typical reel gets 4,000
   views against 48,000 followers — under a tenth of its audience — so it cannot teach us what
   travels. Removing it."*
5. Confirm the cleanup with `get_workspace_stats`.

**Never fabricate the floor or the sample-size cutoff.** Both numbers came from the tool's own
reply — quoting a number you invented, even a plausible one, breaks the honesty this whole gate
exists for.

### Incumbents get screened too (FRFRMU-1302)

New candidates are screened hard by this same gate. Accounts already on the watchlist are
**NOT** automatically exempt — the benchmark set only ever grows, so an account added months
ago and never re-checked can quietly stop earning its place. Run this gate on the EXISTING
watchlist too, not just new adds — the natural moment is Step 2's own "stale set" trigger (a
refresh after ~30-60 days, or when the niche has visibly moved).

Read the existing set off the SAME ONE `search_watchlist` call this gate already makes (no
extra round-trips), apply steps 1-4 above unchanged, and where an incumbent fails the
views-per-follower floor, **propose its removal** rather than silently keeping it —
`remove_competitor` is free. This grows the benchmark set in one direction only: accounts join
when they pass the gate, and leave when they stop passing it — the set is never a one-way
ratchet that only adds.
