> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 4.7**, after the Domino (p08) and the persona assembly (p09) — this
> step's stance and belief inputs come from those. This is p12 "Build the Movement"
> (`marketing/rules/process-cards/p12-build-the-movement.md`, FRFRMU-1046), closing section B
> (Identity & Story). **Staged by proof — a movement without proof is a claim, not a promise.**

## Step 4.7 — Build the movement (p12), staged by proof

**Ask per `asking-rules.md`.**

### Stage 0 — every account, from day one: the themes

1. **Rallying cry.** Draft 3-5 from the Big Domino + positioning — future-based, open-ended (each
   follower reads their own goal into it), **no number, no promised outcome**. The creator
   picks.
2. **Identity phrase — "I'm a \_\_\_\_".** Draft 3, t-shirt test. Treat as a **positioning
   hypothesis**: 2 candidates go into content; the one a follower says back UNPROMPTED (a pasted
   comment/DM, or an audience-ask reply) is promoted to `confirmed`. The market picks, not taste.
3. **Enemy — a METHOD, never a person or a group.** Propose from the sameness map. **Mechanical
   thin-niche test:** count visible competitors (watchlist + `competitor_dossier__*` rows); if
   ≤5 AND the enemy line matches exactly one dossier row's offer/method → **fail, rewrite.**
4. **Intensity dial — ask once.** *"How sharp do you want the stance — 1 clear POV, 2 pointed, 3
   combative (never at people)?"* Record it; the agent never escalates past it.
5. **The five levers vocabulary** (encourage dreams · justify failures · allay fears · confirm
   suspicions · rocks at the enemy): every cause-themed reel names ≥1.

### Stage 1 — needs ONE real, dated, owned win: the 4-minute mile

Ask the creator to confirm a real win (first-party proof, or their own reel that beat their
baseline, Step 1.6). **Never aspirational.** No win yet → the plan says so honestly: *"no owned
win yet — earning one is this month's job."* Never fake one (`no_unflagged_placeholder` already
guards fabricated results).

### Stage 2 — needs Stage 1 + a confirmed identity phrase: the banner

Mini manifesto (identity + 3-5 beliefs from the stance + `false_beliefs`), full manifesto, and
the us-vs-them script (*my name is → I'm part of a group of → what we stand for/against → who WE
are*). Agent drafts, creator edits — these are THEIR beliefs. Told in the structure
`get_content_structures` proves for stance/identity content; `get_theme_lift(dimension=angle)`
for `contrarian_take` checks whether polarity lifts here.

**A manifesto for an account with no confirmed identity and no owned win is a staging
violation — refuse it.**

### Save it

Creator Brief key `movement`, Foundation-card shape:

```
{
  "card": "movement", "title": "Your movement",
  "status": "hypothesis",
  "summary": "<the cause line, or 'themes drafted, no win yet' for a cold start>",
  "items": [
    {"item_id": "cause_line", "label": "Rallying cry", "text": "<future-based, open-ended>",
     "who": "you", "provenance": "FROM-EXPERT"},
    {"item_id": "identity_phrase", "label": "I'm a ___", "text": "<phrase>", "who": "agent",
     "provenance": "JUDGMENT"},
    {"item_id": "enemy", "label": "The enemy (a method)", "text": "<method + thin-niche count>",
     "who": "you", "provenance": "FROM-EXPERT"},
    {"item_id": "intensity", "label": "Intensity dial", "text": "<1, 2 or 3>", "who": "you",
     "provenance": "FROM-EXPERT"},
    {"item_id": "four_minute_mile", "label": "The owned win", "text": "<result + date, or 'none yet'>",
     "who": "you", "provenance": "FROM-EXPERT"}
  ],
  "updated_at": "<ISO date>"
}
```

### What this step refuses to do

Name a competitor or a group as the enemy · promise a result in the cry or manifesto · fake a
win · escalate past the recorded intensity dial · draft a manifesto before Stage 1 + a confirmed
identity.

### Wired in (each does nothing when `movement` is absent)

`step-08-caption-recipe.md` (an optional cause-line sign-off slot) · `step-07-strategy.md` 7.5/
7.7 (the cause theme, bounded by the funnel mix) · `step-12-after-the-save.md` (at the KPI
review, compare stance-reel reach-per-follower to the account baseline — a dip on ONLY the
stance reels reads as likely algorithmic down-ranking, not audience rejection) · Gate 2 (the
proof-reel checkbox, batched `RULES_GATE.md` edit).

## Step 4.8 — the hidden-story hunt (p25 part A, `hook_facts`, FRFRMU-1060)

Once per plan, after the identity/story cards above are in place: mine `origin_story.cuts`
(1044), `attractive_character`'s parables (1043), `false_beliefs`'s bridge stories (1045), and
`offer_stack`'s fast-win step (1049) for surprising TRUE facts — a number, a timeframe, an
unlikely-character detail the creator takes for granted. Then ask **one** question, per
FRFRMU-1051's question contract: *"What do people say 'wait, really?' about when you tell them
how you work?"* ❌ "I'm good with AI" ✅ "I ship a product alone that used to take a team of
four — and I don't write the code myself."

Save every fact found (mined or asked) as `hook_facts`:
`[{fact, kind: number|timeframe|character|contrast, source, owned_by_user: bool}]`. This key is
schema-free (no reserved-key shape check, unlike `hook_history` below) — it is read defensively
by the copywriter's `hook-variants.md`, which never invents an element without one. No facts
found yet → say so plainly ("none yet — story/offer needs work, see Step 3.9/Step 7.2") rather
than manufacturing one.

**The copywriter (`skills/rm-copywriter/hook-variants.md`) turns `hook_facts` into hook
variants and writes `hook_history` (FRFRMU-1060, a reserved Creator Brief key,
`backend/app/mcp/creator_brief_reserved_keys.py`) at the test-loop review — this step never
writes `hook_history` itself.**
