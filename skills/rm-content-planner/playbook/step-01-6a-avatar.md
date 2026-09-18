> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 1**, right after `step-01-5-market.md`, before `step-01-6-self-account.md`.
> **Entry rule: only after `market_validation` is confirmed (p01, FRFRMU-1013), and only when
> `avatar` is missing or the creator says "check my avatar."** Otherwise skip this whole file in
> one line. This is p02 "Define the Dream-Customer Avatar"
> (`marketing/rules/process-cards/p02-define-dream-customer-avatar.md`, FRFRMU-1031): good
> marketing enters a conversation already happening in the customer's mind — so this step
> writes to ONE named person, never a crowd.

## Step 1.6a — Define the dream-customer avatar (p02)

**Ask per `asking-rules.md`.**

Every question ends in a status: `answered_pass | answered_weak | declined | not_applicable |
deferred`, never `unasked`.

**A. Name + trait list + picture (agent drafts, user confirms).** From the intake answers plus
`market_validation`, draft a NAMED avatar: name, situation, what they value, where they are
(e.g. "grown to five figures, has a message, values growth over money"). A written description
stands in for the picture. **A demographic table alone FAILS** — "small business owners,
25-45" is not an avatar.

**B. Micro-niche drill-down (agent proposes, user picks).** Starting from the validated niche
(p01): propose sub-niche → micro-niche, deliberately excluding who doesn't fit. G648 test:
*could this avatar belong to 100 other businesses?* → if yes, narrow it and redraft.

**C. PQR2 — Problems, Questions, Roadblocks, Results, 5-10 per letter (agent fills + ask-user).**
Sources available today: (1) web research — forums, Q&A sites, reviews, groups/hashtags, cited;
(2) competitor reel transcripts/captions/on-screen text via `get_post_transcript` — the niche's
problems as competitors already address them, free, already-analysed; (3) **ask-user** for the
ones only they hear (DMs, sales calls). Reuse the FRFRMU-894 intake quality bar: **2 per letter
is a weak pass that triggers ONE refinement pass, never silent acceptance.**

**D. Exact words, both directions — at least 12 pain + 12 pleasure phrases, EVERY ONE sourced.**
This is the crown jewel and the constrained one.
* 🔴 **Data boundary:** the pipeline does not surface reel-comment text and has no DM data
  (FRFRMU-904, parked). Comment/DM quotes come ONLY from the creator pasting them or an
  external source — **never claim the pipeline collected them.**
* Sources that work today: web research (forums/reviews/Quora, cited); competitor
  captions/transcripts via `get_post_transcript`; the creator's own pasted DMs/comments; the
  creator's own past-self phrases ("our mess becomes our message" — first-party only; can't
  recall → skip honestly, never write their memory for them).
* **Every phrase carries a `source` tag**: `web:<url>` | `reel_transcript:<post_url>` |
  `user_pasted` | `user_recalled`. **An unsourced "typical" quote is a defect — reject it.** A
  phrase that could not be typed in a DM at 11pm is marketing-speak, not speech — reject that
  too.

**E. Searcher vs Scroller, per channel (agent fills).** For Instagram Reels the avatar is a
SCROLLER (interrupted, not searching) → attention must be earned with Hook-Story-Offer. Record
per channel — a Reels-only creator gets one line, not a generic global note.

**F. Write to that one person.** Primary avatar first; a secondary avatar only when messaging
truly diverges. Re-confirm on the brief's 30-day staleness flag (`CREATOR_BRIEF_STALE_DAYS`).

### What this step refuses to do

Save a demographic table as the avatar · accept a PQR2 letter with fewer than 2 entries without
refining · save a pain/pleasure phrase with no `source` tag · invent a "typical customer" quote
· claim the pipeline read Instagram comments or DMs · write a memory the creator couldn't
recall.

### Save it

Write the result to the Creator Brief as the Foundation card key `avatar`, in the
`/settings/profile` shape (FRFRMU-1042). `status` is `"confirmed"`, or `"hypothesis"` while
PQR2/phrases are still thin. `provenance` is one of the four card-wide values
(`FROM-EXPERT` for a web/user-supplied phrase, `DATA-DRIVEN` for a reel-transcript-sourced
phrase, `JUDGMENT` for the agent's own drafted trait line) — the finer per-ticket detail lives
in the extra `source` field, which the shape check does not require but does not forbid either:

```
{
  "card": "avatar", "title": "Dream-customer avatar",
  "status": "confirmed",
  "summary": "<name + one-line situation>",
  "items": [
    {"item_id": "trait_line", "label": "Name + situation", "text": "<the drafted avatar>",
     "who": "agent", "provenance": "JUDGMENT"},
    {"item_id": "micro_niche", "label": "Micro-niche", "text": "<sub-niche -> micro-niche>",
     "who": "you", "provenance": "JUDGMENT"},
    {"item_id": "pqr2_problems", "label": "Problems (5-10)", "text": "<list>",
     "who": "agent", "provenance": "FROM-EXPERT"},
    {"item_id": "pqr2_questions", "label": "Questions (5-10)", "text": "<list>",
     "who": "agent", "provenance": "FROM-EXPERT"},
    {"item_id": "pqr2_roadblocks", "label": "Roadblocks (5-10)", "text": "<list>",
     "who": "agent", "provenance": "FROM-EXPERT"},
    {"item_id": "pqr2_results", "label": "Results (5-10)", "text": "<list>",
     "who": "agent", "provenance": "FROM-EXPERT"},
    {"item_id": "pain_phrase_01", "label": "Pain phrase", "tag": "pain_phrase",
     "text": "<verbatim phrase>", "who": "you", "provenance": "FROM-EXPERT",
     "source": "web:<url>"},
    {"item_id": "pleasure_phrase_01", "label": "Pleasure phrase", "tag": "pleasure_phrase",
     "text": "<verbatim phrase>", "who": "agent", "provenance": "DATA-DRIVEN",
     "source": "reel_transcript:<post_url>"},
    {"item_id": "channel_mode", "label": "Searcher vs Scroller",
     "text": "Reels: scroller — Hook-Story-Offer", "who": "agent", "provenance": "JUDGMENT"}
  ],
  "updated_at": "<ISO date>"
}
```

**A `pain_phrase`/`pleasure_phrase` item with no `source` field, or with `provenance:
"JUDGMENT"`, is unsourced and must be rejected — an unsourced phrase never reaches this list.**
The `pqr2` lists ALSO get written to the existing Positioning schema
(`Positioning.pqr2`, `update_business_profile`) so the field the plugin already has stays
filled — this is not a new schema, only a fill.

## Wire into

* **Hook recipe (`step-08-hook-recipe.md` §H.4b):** hooks draw promise/tension from
  `avatar.items` tagged `pain_phrase`/`pleasure_phrase`, cited in the receipt. No `avatar` key
  → that block is a no-op, the hook recipe is unchanged.
* **Caption recipe (`step-08-caption-recipe.md` §C.3):** captions write to the named avatar in
  their language. No `avatar` key → unchanged.
* **Critic (`step-11-rules-gate-critic.md` / `RULES_GATE.md`):** two lines — "written to ONE
  named person, not a crowd?" and "does the copy read as speech, not marketing-speak?" — batched
  into the single `RULES_GATE.md` edit made once this lane's step files are all in.
