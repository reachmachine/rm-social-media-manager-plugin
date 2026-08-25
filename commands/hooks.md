---
description: "Show the hook patterns from your analysed reels — what openings actually hold attention. Free, never spends credits"
argument-hint: "[@handle, a tag name, or a question about hooks]"
---

Show hook patterns from Reach Machine. **Reads only — never spend.**

Narrow to: $ARGUMENTS

1. `get_analysis_coverage` FIRST. Hook data only exists for **analysed** reels. If coverage
   is thin, say so and mark the answer low-confidence — do not answer from a thin slice as
   if it were the whole picture.
2. `get_hooks_library` for the patterns. Scope one account with `usernames=[handle]`, or a
   hand-picked set via `set_data_selection` with `post_urls`.
3. Apply the rigor rules in the skill's PLAYBOOK Step 3 and Step 7: **medians not means**,
   state the sample size behind every pattern, and label each claim DATA-DRIVEN (real n) /
   DATA-INFERRED / JUDGMENT. Use RM's own tag labels; never guess how a tag is computed.
4. If you scoped with `set_data_selection`, **always** `clear_data_selection` before
   finishing — a leaked scope silently corrupts the next read.

**Hard limit:** never call a spend or destructive tool here (`run_pipeline*`, `pull_data`,
`add_to_watchlist`, `refresh_competitor`, `remove_competitor`, `stop_pipeline`) and never call
Apify. If the answer needs new analysis, point at `/rm-social-media-manager:watch-video`.
