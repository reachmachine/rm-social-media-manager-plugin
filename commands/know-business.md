---
description: "Understand and record the business a plan is for — stage, positioning, funnel assets, goal. Free, never spends credits"
argument-hint: "[@handle, a short business brief, --fresh to restart the interview, or leave empty to be interviewed]"
---

Understand the business this workspace plans for, and save it. **Reads and writes the profile
— never spends credits.** This is the skill's Step 1, on its own, so it can be redone without
rerunning a whole plan.

What the user gave: $ARGUMENTS

Load the skill's PLAYBOOK **Step 1** — `playbook/step-01-intake.md`,
`playbook/step-01-intake-fields.md` and `playbook/step-01-intake-fields-2.md`, and nothing
else from the method — and follow it. Do not invent a shorter version. Every question this
interview asks follows `playbook/asking-rules.md` — those step files cite it, this command
does not need its own copy.

## Read before you ask

**Send `get_business_profile`, `get_creator_brief` and `get_workspace_stats` in ONE message —
they do not depend on each other.** One round-trip, not three. Show what is already saved, then
ask only about what is **missing or stale** — re-interrogating a returning client from scratch
is the main thing this command exists to avoid, UNLESS the creator asked to restart (below).

## Restart intent — when the creator wants to redo this from scratch (FRFRMU-1007)

**Detect it, don't assume it.** Before showing the saved-profile summary above, check
`$ARGUMENTS` and the creator's opening message for a restart request — one of the phrases
below, or the flag `--fresh`. Match ONLY these phrases; on anything looser, ask instead of
guessing: *"do you want me to start the interview over from the top?"*

- "start over" / "start from first" / "start fresh" / "from scratch"
- "re-interview me" / "redo this"
- the flag `--fresh`

**On a restart intent:** skip the saved-profile summary and the single keep-or-change
question. Run the full Step 1 interview (`playbook/step-01-intake.md` rule 2), one question
at a time, exactly like a brand-new business — pre-filling nothing. Offer each already-saved
answer as a suggestion IN the flow instead — *"last time you said X — keep it, or answer
fresh?"* — never silently pre-fill it as if they never had to answer.

**A restart never deletes anything.** It only changes which conversation path runs. The
saved business profile and Creator Brief stay exactly as they are until this interview's
new answers are saved over them (`update_business_profile` / `update_creator_brief`, same
as always).

**If the creator also wants last month's plan set aside (FRFRMU-1006), archive it first —
never say a plan can't be removed.** Call `get_calendar` for the current month to find its
`plan_id`, then `archive_content_plan(plan_id, confirm=true)`. This is a hide, never a
delete: every version, reel and learning stays exactly where it is, and it can be restored
any time from the Content Calendar's Archived tab. Say so out loud, plainly: *"I archived
this month's plan — nothing was deleted, and you can bring it back any time from the
Archived tab. Now let's build the new one."* Never say a plan was hard-deleted, and never
archive silently without telling the creator what happened.

**No restart intent — the default, unchanged.** Show what is saved, and ask only about
what is missing or stale, exactly as the rule above already says.

## The four things a plan cannot be built without

1. **Who it is FOR** — the account owner's own brand, or a client they manage? Agencies must use
   a **separate workspace per client** (see `/rm-social-media-manager:switch-workspace`). If the
   plan's subject changed and this workspace should now hold a DIFFERENT business, that is not a
   normal intake edit — route to `/rm-social-media-manager:repurpose-workspace` first (Step 1
   Rule 0 covers the full decision: upgrade, swap to an existing workspace, or repurpose this one).
2. **Stage** — real follower count and how many reels a week they can sustain. **Offer to fetch
   the real numbers from their own tracked account (once Step 1.6 has added and pulled it) —
   never ask them to type a number you can read** (FRFRMU-1008). Capacity is asked as fixed
   choices, framed by reality, not motivation, never open-ended. Capacity is part of the
   answer: a plan they cannot film is not a plan.
3. **Positioning** — what makes them different from everyone else (their "ownable angle"),
   their own first-party proof, and the ONE audience. Without it a plan can only clone the
   competitor it came from.
4. **Funnel assets + goal** — is there a lead magnet, is auto-DM live, and is the goal reach,
   leads, or authority? Pick ONE goal.

## Rules that matter here

- **Interview, don't hand over a form** (PLAYBOOK Step 1, `playbook/step-01-intake.md`).
  One question at a time, and react to
  the answers.
- **Every answer must clear its quality bar** (Step 1 rule 7 + the bars in
  `playbook/step-01-intake-fields.md`). Vague → reflect the bar back, refine at most twice, then
  mark the field `weak` and move on — never interrogate.
- **Cross-check what they tell you against real data** where you can — you already have the
  workspace numbers from the read above, plus their own reels if any are analysed. If the
  stated stage and the data disagree, say so kindly and fix the record.
- **Save it** — positioning with `update_business_profile` (the only tool that writes it),
  everything else with `update_creator_brief` (your draft positioning wording and its tier go
  under `positioning_notes`, never under `positioning`). An interview you do not persist gets
  repeated next session.
- **Positioning is per-workspace; the Instagram handle is account-wide (G223).** If you set a
  handle here, say plainly that it applies to the whole account, not just this workspace.
- **Only send the machine's timezone when you are confident this is the creator's own computer.**
  In that case, send it in the same `update_business_profile` call, as the `timezone` field, using
  the full IANA name your system reports (e.g. `Asia/Kolkata` — never a short form like `IST`,
  which is refused rather than corrected). Send it again whenever it changes (they travelled) —
  that updates the saved one instead of adding a second. **In a shared, CI, or sandboxed session,
  the machine's clock is the CONTAINER's clock, not the creator's — do not send it.** Say in one
  line that you skipped it, and either ask the creator for their real timezone or leave it as
  whatever is already saved. Never guess it from what you assume their country is, and never treat
  a generic value like "UTC" as a fact about the creator — the server refuses to store it from this
  field anyway (FRFRMU-1130). Without a real saved timezone, posting times show in UTC.

**Hard limit:** never call a spend or destructive tool here, and never call Apify.
