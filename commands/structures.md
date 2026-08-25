---
description: "Show content structures from your analysed reels — how winning reels are built beat by beat. Free, never spends credits"
argument-hint: "[@handle, a tag name, or a question about structure]"
---

Show content structures from Reach Machine. **Reads only — never spend.**

Narrow to: $ARGUMENTS

1. `get_analysis_coverage` FIRST — structures only exist for **analysed** reels. Thin
   coverage means say so and mark the answer low-confidence.
2. `get_content_structures` for the shapes. Scope one account with `usernames=[handle]`, or
   a hand-picked set via `set_data_selection` with `post_urls`.
3. For any structure worth copying, pull a real example so the user sees the actual beats:
   `query_posts_by_tag` to find the reels, then `get_post_transcript` for one of them.
4. Apply the skill's PLAYBOOK rigor rules (Step 3, Step 7): medians not means, sample size
   stated, claims labelled DATA-DRIVEN / DATA-INFERRED / JUDGMENT. Structure advice must
   respect the anti-mimicry and stage rules (Step 4, Step 5) — a structure that works for a
   big account is not automatically right for a small one.
5. If you scoped with `set_data_selection`, **always** `clear_data_selection` before finishing.

**Hard limit:** never call a spend or destructive tool here, and never call Apify. If the
answer needs new analysis, point at `/rm-social-media-manager:watch-video`.
