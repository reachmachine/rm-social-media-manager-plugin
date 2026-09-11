---
description: "Show the hook patterns from your analysed reels — what openings actually hold attention. Free, never spends credits"
argument-hint: "[@handle, a tag name, or a question about hooks]"
---

Show hook patterns from Reach Machine. **Reads only — never spend.**

Narrow to: $ARGUMENTS

1. **Scope first, if you are narrowing.** For one account, pass `usernames=[handle]` to both
   calls in point 2. For a hand-picked set of reels, call `set_data_selection` with
   `post_urls` **on its own and wait for it to come back** — a read that travels alongside
   the scope change can still answer for the old set.
2. **Send `get_analysis_coverage` and `get_hooks_library` in ONE message — they do not depend
   on each other.** Both come back in a single round-trip instead of two.
3. **Read coverage before you write the answer.** Hook data only exists for **analysed** reels.
   If coverage is thin, say so and mark the answer low-confidence — do not answer from a thin
   slice as if it were the whole picture. `get_hooks_library` holds the patterns themselves.
4. Apply the rigor rules in the skill's PLAYBOOK Step 3 and Step 7 — load ONLY those two
   files, `playbook/step-03-mcp.md` and `playbook/step-07-strategy.md`, never the whole method: **medians not means**,
   state the sample size behind every pattern, and label each claim DATA-DRIVEN (real n) /
   DATA-INFERRED / JUDGMENT. Use RM's own tag labels; never guess how a tag is computed.
5. If you scoped with `set_data_selection`, **always** `clear_data_selection` before
   finishing — a leaked scope silently corrupts the next read.

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

**Hard limit:** never call a spend or destructive tool here (`run_pipeline*`, `pull_data`,
`add_to_watchlist`, `refresh_competitor`, `remove_competitor`, `stop_pipeline`) and never call
Apify. If the answer needs new analysis, point at `/rm-social-media-manager:watch-video`.
