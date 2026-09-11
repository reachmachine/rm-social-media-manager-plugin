---
description: "Reset an existing workspace for a different business — one deliberate operation. Free, never spends credits"
argument-hint: "[new business name / handle, or leave empty to be walked through it]"
---

Reset the **active** workspace so it can plan for a **different business** — clears its saved
Creator Brief, its data-selection working set and its detected niche, in one deliberate step.
**Reads plus a confirm-gated write — never spends credits.**

What the user gave: $ARGUMENTS

## Why this command exists

Before it, an agent could only hand-patch `instagram_handle` and hope to fix the rest of a
repurposed workspace later — leaving the old business's persona, saved answers and detected
niche in place indefinitely (a gym workspace still reading "Solo Coach / Consultant" and
carrying a 22-account AI-automation benchmark set was the incident that opened FRFRMU-1146).
This command is the one deliberate "this workspace is now a different business" operation.
It is a thin wrapper — the decision to offer a swap before a reset lives in the skill's
PLAYBOOK Step 1 Rule 0 (`playbook/step-01-intake.md`), not here.

## 1. Swap first — never jump straight to a reset

**Call `list_workspaces` before anything else.** If the account already owns another
workspace, say so and offer to open it instead:

*"You already have another workspace — '<name>'. I can open that one instead of clearing this
one — your plan keeps one open at a time, and nothing is deleted either way. Or, if THIS
workspace really is the one that should become <new business>, I can reset it. Which?"*

If they want the other workspace, use `keep_workspace_open` (or `switch-workspace` if it is
already open) and STOP here — nothing about this command runs. Only continue below when there
is nothing to swap to, or the customer picks the reset anyway. A swap destroys nothing; a
reset clears saved answers — always offer the free option first.

## 2. State your limits BEFORE proposing anything

Never promise an overwrite you cannot make, and never call persona "cosmetic" — that is false
(`playbook/step-01-intake.md` rule 4) and is the exact mistake this command exists to stop.
Say plainly, before asking for confirmation:

*"I can reset this workspace's saved positioning, its Creator Brief, its data-selection
working set and its detected niche. I cannot change your persona or your onboarding answers —
those are read at the start of every plan, so a wrong one gives you a plan for the wrong
business. Only you can change them, on the web Business Profile page: `<persona_edit_url>`
(from `get_business_profile`)."*

## 3. Read before you reset

Send `list_workspaces` (confirm `is_active` by name — the ticket's own false alarm was an
agent reading a DIFFERENT workspace than the plugin's active one over a second connection),
`get_business_profile`, `get_creator_brief` and `get_workspace_stats` in one message. Show
what will clear (the saved brief field count, e.g. "14 saved fields, including positioning
and a 22-account benchmark set"), what stays (competitors — kept unless you say otherwise;
plans — kept, archivable separately), and what this cannot touch (persona, onboarding
answers).

## 4. Preview, then confirm

Call `repurpose_workspace` **without** `confirm` — it changes nothing and returns a preview
naming the workspace and every field it would clear. **Read that field list out loud,
verbatim — do not paraphrase it** (it is a whole-document sweep precisely so nothing gets
missed; paraphrasing it back as "positioning and a few other things" hides exactly what makes
the sweep worth having). Only after the customer says yes, call
`repurpose_workspace(confirm=true, new_name="<new business name>")`.

**If it comes back `locked=true`:** the reset did NOT run — nothing was cleared. Relay
`message` word for word. If `can_swap=true`, offer `keep_workspace_open` or an upgrade,
exactly as `switch-workspace.md` already does for a locked target. Never retry a locked
reset.

## 5. After a confirmed reset

Relay the result: how many brief fields cleared, that the data-selection working set and the
niche cleared, and that nothing was erased from history — only the live values. Then, since
competitors are NEVER removed by this tool:

*"Your `<competitors_kept>` competitor(s) are still tracked here. They use this workspace's
share of your competitor budget, and since they're still here, this workspace's niche will
re-detect from them the next time it's read. Want me to remove them with `remove_competitor`
(separately confirmed — that one is destructive)?"*

## 6. Run Step 1 fresh for the new business

Continue exactly like `/rm-social-media-manager:know-business --fresh` — a brand-new
interview, pre-filling nothing. Set the new handle with `update_business_profile`, and say
once, plainly, that the handle applies to the **whole account**, not just this workspace
(G223 — same note `switch-workspace.md` and `know-business.md` already give).

## 7. Gate before Step 2, and every closing summary

Before benchmarking, re-read `get_business_profile`. If persona still contradicts the stated
business, say so once more with `persona_edit_url` and stamp the plan **"PROFILE MISMATCH —
persona says '<old persona>'"** at the very top — never proceed silently. Every closing
summary from here on mentions the persona line with the link — never "cosmetic", never "just
a label", never "doesn't feed the plan".

**Hard limit:** never call a spend tool here, and never call Apify. `remove_competitor` is
offered, never bundled automatically into the reset.
