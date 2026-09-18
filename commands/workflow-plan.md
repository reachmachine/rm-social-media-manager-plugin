---
description: Build a full content plan — runs the complete rm-content-planner method end to end
argument-hint: "[@handle or a short business brief]"
---

Invoke the `rm-social-media-manager:rm-content-planner` skill and follow it
exactly, end to end — intake first, then the PLAYBOOK, **one step file at a time**
(`PLAYBOOK.md` is the index; load `playbook/step-NN-*.md` as you reach each step, never
all of them up front). Do not improvise a
plan or skip steps.

If the user provided arguments, treat them as the starting input for Step 1's
intake (a handle, a goal, or a short business brief): $ARGUMENTS
