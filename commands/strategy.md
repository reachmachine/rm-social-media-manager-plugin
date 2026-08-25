---
description: "Show the content strategy Reach Machine reads out of your analysed data — pillars, mix, what is working. Free, never spends credits"
argument-hint: "[@handle, a goal (reach / leads / authority), or a strategy question]"
---

Show the strategy view from Reach Machine. **Reads only — never spend.**

Focus: $ARGUMENTS

1. `get_analysis_coverage` FIRST. Strategy read off thin data is a guess wearing a suit —
   if coverage is thin, say so plainly and mark it low-confidence.
2. `get_content_strategy` for the strategy view. `get_content_breakdown` for how the mix
   splits by niche/category. Scope with `usernames=[handle]` or `set_data_selection`.
3. **This shows what the DATA says, not a plan.** A real plan needs the business context —
   stage, positioning, funnel assets, goal. If the user wants the plan itself, point them at
   `/rm-social-media-manager:workflow_plan`, which runs the full method including intake.
4. Apply the skill's PLAYBOOK rigor rules (Step 3, Step 7) and its stage-translation rule
   (Step 4): tactics that travel for a big account often backfire for a small one. Label
   every claim DATA-DRIVEN / DATA-INFERRED / JUDGMENT.
5. If you scoped with `set_data_selection`, **always** `clear_data_selection` before finishing.

**Hard limit:** never call a spend or destructive tool here, and never call Apify.
