---
description: "Show the content strategy Reach Machine reads out of your analysed data — pillars, mix, what is working. Free, never spends credits"
argument-hint: "[@handle, a goal (reach / leads / authority), or a strategy question]"
---

Show the strategy view from Reach Machine. **Reads only — never spend.**

Focus: $ARGUMENTS

1. **Scope first, if you are narrowing.** Pass `usernames=[handle]` to all three calls in
   point 2, or call `set_data_selection` **on its own and wait for it to come back** — a read
   that travels alongside the scope change can still answer for the old set.
2. **Send `get_analysis_coverage`, `get_content_strategy` and `get_content_breakdown` in ONE
   message — they do not depend on each other.** All three come back in a single round-trip
   instead of three.
3. **Read coverage before you write the answer.** Strategy read off thin data is a guess
   wearing a suit — if coverage is thin, say so plainly and mark it low-confidence.
   `get_content_strategy` is the strategy view; `get_content_breakdown` shows how the mix
   splits by niche/category.
4. **This shows what the DATA says, not a plan.** A real plan needs the business context —
   stage, positioning, funnel assets, goal. If the user wants the plan itself, point them at
   `/rm-social-media-manager:workflow_plan`, which runs the full method including intake.
5. Apply the skill's PLAYBOOK rigor rules (Step 3, Step 7) and its stage-translation rule
   (Step 4) — load ONLY `playbook/step-03-mcp.md`, `playbook/step-07-strategy.md` and
   `playbook/step-04-stage.md`, never the whole method: tactics that travel for a big account often backfire for a small one. Label
   every claim DATA-DRIVEN / DATA-INFERRED / JUDGMENT.
6. If you scoped with `set_data_selection`, **always** `clear_data_selection` before finishing.

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

**Hard limit:** never call a spend or destructive tool here, and never call Apify.
