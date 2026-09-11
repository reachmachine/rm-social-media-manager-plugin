# QA checklist — polish & QA before it ships (FRFRMU-1065, p27)

A confused viewer says no. Before any copy pack can be marked shippable,
seven checks run, and each is logged pass/fail/n-a on the pack:
`qa.checks[] = {check, pass|fail|na, note}`. **"Looks good" with no record
is not a pass** (the same G650 principle the planner's rules-gate critic
already applies to the plan). The result is copy-pack **v2** with
`mode: edit` — it **never overwrites v1** (FRFRMU-1064's draft).

Instagram safe-zone numbers live in ONE place so they never drift out of
sync across checks:

```
SAFE_ZONE_CONFIG = {
  top_ui_overlap_px: 250,      # camera icons / stories row
  bottom_ui_overlap_px: 320,   # caption / like-comment-share bar
  caption_truncation_chars: 125,  # step-08-caption-recipe.md's own number
}
```

## The seven checks

1. **Mechanics** — grammar, spelling, punctuation, formatting (line breaks
   in captions; no wall of text).
2. **Device / safe zones** — on-screen text stays inside `SAFE_ZONE_CONFIG`;
   caption first line ≤ `caption_truncation_chars`; a subtitle line exists
   for every spoken beat; carousel text is legible at phone size.
3. **Scan path** — read ONLY the hook + on-screen lines + caption first
   line + CTA echo + P.S. twin. Does the gist survive? Log the scan text
   used for the check.
4. **Muted watch** — every spoken beat has an on-screen equivalent; a
   music-only/silent reel still carries its message in text + visual.
5. **Second eyes** — an independent critic pass (never the drafting run)
   re-runs Gate 1 + Gate 4 + these seven checks. Verdict logged as data,
   same shape as the planner's Step 11 critic:
   `{verdict, changes, no_findings_note}`.
6. **Outsider test** (gate-bound assets only — activation reels, DM
   scripts, offer captions): ask-user, *"Who could read this who doesn't
   know your business? Paste what they said was unclear."* Bar: "pretty
   good" is not a pass; "where do I get that?" is. No outsider available →
   the critic substitutes, logged `substitute`; a real outsider runs on the
   next asset. Never silently skipped — `deferred`/`declined`/`substitute`
   is always recorded (FRFRMU-1051).
7. **The you-flip** — count `I` / `me` / `my` / `we` / `our` OUTSIDE story
   beats (`story_setup`/`story_turn` are exempt — a first-person story beat
   is not a you-flip violation). Rewrite to second person; log the count
   before and after; target near zero outside story sections.

## Edit pass rules

- Edit pass = copy-pack **v2**, `mode: edit`. v1 (draft, FRFRMU-1064) is
  never overwritten — both versions persist under the same
  `copy_pack__<plan_id>__<reel_uid>__v<version>` key family.
- QA fixes never change the planner's pattern, CTA type, or beat order —
  the same constraint the draft pass holds.
- The critic in check 5 is a SEPARATE Task subagent given only the pack and
  the gates — never the same run that drafted it. A critic pass authored by
  the drafting run is not independent and fails.

## Validator — `check_qa_record` (advisory → hard for activation assets)

A pack marked shippable/`approved` must have all seven checks logged, and
**none may be `fail`**. Remove that rule and a pack with
`mechanics: fail` can still ship — that is the Rule 3 target for this
ticket.

## Flop diagnosis — trigger only, order lives elsewhere

`rules/copywriting.md` S23 says: when a reel flops, rewrite the hook first,
before scrapping the idea. **This ticket's original five-step order is
SUPERSEDED by FRFRMU-1076's eight-item flop-diagnosis checklist — FRFRMU-1076
is the one owner of the diagnosis order.** This skill keeps ONLY the
trigger wiring: when a reel's verdict is `lost` (read from the reel
profile, FRFRMU-1062), the copywriter hands off to
`${CLAUDE_SKILL_DIR}/flop-diagnosis.md` (FRFRMU-1076, shipped) and writes
the resulting diagnosis note onto the reel profile and
`hook_history` (`hook-variants.md` §E, FRFRMU-1060, shipped — the entry's
`audience_note` carries the diagnosis).
It does NOT implement a second diagnosis order here —
two owners for the same decision is exactly the failure mode this note
exists to prevent.
