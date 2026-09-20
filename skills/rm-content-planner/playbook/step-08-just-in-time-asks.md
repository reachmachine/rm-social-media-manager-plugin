> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 8, hook recipe (FRFRMU-1602).** `step-08-hook-recipe.md` is 296 lines with
> no room for its own "ask it here" block, so the `bold_stance` just-in-time ask lives here
> instead — one file, one question, pointed at from the hook recipe.

## First-plan mode: ask `bold_stance` here

**Only relevant in first-plan mode** (`step-01-first-plan-core.md`) — outside it, `bold_stance`
is already captured at Step 1's positioning capture, and this file does nothing.

Right before writing this reel's hook, ask plainly, one line, no bar, no card, accepted as given:

> *"I'm about to write your hooks — what's the one thing you believe that others in your niche
> won't say out loud?"*

Stuck → `playbook/question-help.json`'s `bold_stance` entry (`shape: "belief"`) runs
`asking-rules.md` §13's belief-draft protocol, same as it would for any belief question. Save the
answer the normal way (`update_business_profile`, `positioning` object, item 5) the moment it is
confirmed — it is not parked until Step 13 just because it was asked late.
