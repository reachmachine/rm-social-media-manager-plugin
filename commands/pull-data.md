---
description: "Pull more reels for competitors already on the watchlist. SPENDS RM credits — only after your explicit yes"
argument-hint: "[@handle(s) to pull, or leave empty to be shown who is thin]"
---

Fetch more reels for competitors already tracked in this workspace. **Spends RM credits.**
Follow the skill's PLAYBOOK Step 3 rules, especially rule 6 (confirm-before-spend).

Who to pull: $ARGUMENTS

## Decide who actually needs it — before quoting a cost

1. `get_workspace_stats` + `search_watchlist` — who is tracked and how much we hold for each.
2. `get_analysis_coverage` — where the data is thin **for the user's goal**, not thin in
   general. Pulling more reels for an account we already have plenty of is wasted money.
3. **Say what pulling does and does not do.** `pull_data` fetches reels; it does **not** analyse
   them. Pulled-but-unanalysed reels appear in no insight. If what they actually want is
   insight, the next step is `/rm-social-media-manager:watch-video` — say so before they spend,
   not after.
4. If a competitor's existing data is merely **stale** rather than thin, `refresh_competitor` is
   the cheaper right tool. Recommend it when it fits.

## 🔴 Confirm-before-spend is a HUMAN gate

Call `pull_data` **un-confirmed first**, show the real cost preview, and **WAIT for an explicit
yes** before calling again with `confirm=true`. Showing a preview and proceeding is not
confirmation. Setting `confirm=true` yourself is never allowed.

**Start small.** Pull one account, read the real charge with `get_credit_usage`, then scale. The
up-front hold is much larger than the final charge — say that plainly so a big hold does not
look like a big bill.

**Series check (G382).** If `get_content_series` shows an `unconfirmed_flags` entry for an
account, ask the founder's question: "This looks like part of a series — want us to check this
account for more?" A yes still goes through this command's normal cost-preview + explicit-yes
flow above — the series check never adds its own way to spend.

## After it runs

`get_pipeline_status` / `get_job_status` to follow it. If it fails, relay the server's own
message — it is written for the user and usually says whether credits were taken. Do not
paraphrase a failure into something vaguer than what the server said.

**Hard limit:** never call Apify here — this command works on accounts already added. Finding
new ones is `/rm-social-media-manager:find-competitors`.
