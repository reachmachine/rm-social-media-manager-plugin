> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 1.4**, right after the personal-story interview. F5 (parables) may also
> run again in Phase 3. This is the QUESTION half of p09 "Build the Attractive Character"
> (`marketing/rules/process-cards/p09-build-attractive-character.md`, FRFRMU-1043) — the
> ASSEMBLY half (identity chair, bio line) moves to Phase 4, `step-04-5-persona-assembly.md`,
> after the stage is known.

## Step 1.4 — The persona, questions half (p09)

**Ask per `asking-rules.md`** — this file is one of the sources `asking-rules.md` was seeded
from; its local wording below stays exactly as written.

**Never re-interview.** Every field below reuses `personal_story`, the bold stance
(positioning item 5), and `brand_voice` — it only asks for the GAPS those don't cover.

**The five rules of asking, every field:** (1) ask for the scene, never the abstraction; (2) a
bad/good example pair in the creator's OWN niche before the question; (3) one question, then
read the answer back; (4) a bar checked silently, one refinement prompt, never blocked; (5)
safety before depth — anything declined is never saved, not even as a fragment.

**Every question ends in a status** — `answered_pass | answered_weak | declined |
not_applicable | deferred` — **never `unasked`.** An unanswered question is unblocked (a
sharper example, breaking it into a smaller ask, drafting something for the creator to react
to) before it is ever marked declined/deferred. There is no cap on how many questions this
takes (founder decision 2026-09-06, FRFRMU-1032 — depth over brevity).

### F1 — Backstory confirm

Compress the interview to one sentence (character + desire + conflict). Ask: *"If a stranger
read only this line, would they know you?"* Bar: a yes, or a one-word correction; contains a
specific scene, not a summary.

### F2 — The flaw you'll show (the only door a flaw enters through)

List 2-3 candidate low points **the creator already said** in the interview. Ask: *"Which of
these are you okay showing on camera? Pick any, or none."* Never propose a flaw they didn't
say. Bar: specific, real, not a humble-brag, approved. "None" is a fine, complete answer —
record it and move on; never resurrected later.

### F3 — The stance, tested by a pretend counter-comment

Take the bold stance from positioning. Generate the most likely counter-comment from the
niche's sameness map. Ask the creator to reply in one sentence, the way they actually would.
Bar: the reply HOLDS the position, inside compliance (ideas/methods, never people/groups). A
retreat → rewrite the stance a notch softer to what they'll actually defend;
`defend_publicly_confirmed: true` only on a holding reply.

### F5 — Parables: up to five small true moments

Mine the interview for scenes already there, then ask up to five times: *"One small moment
from the last few weeks that taught you something — not the lesson, the moment: who, where,
what happened."* Bar: a when/who/what, the point in one line, ≤60 words, real. A lesson with
no moment behind it → ask once more for the moment; accept fewer than five.

### F6 — Voice, a read-back test

Keep the existing derive-then-confirm (2-3 descriptors + an avoid-word + an example reel). Add
one test: write ONE hook in that voice, ask *"does this sound like you? which word is off?"*
Bar: a yes, or a named off-word (→ new `avoid` entry).

### Save it (progressive — F4/F7 complete it in Phase 4)

Creator Brief key `attractive_character`, Foundation-card shape:

```
{
  "card": "attractive_character", "title": "Attractive Character",
  "status": "hypothesis",
  "summary": "<one line: backstory confirmed, N flaws approved/declined, voice set>",
  "items": [
    {"item_id": "backstory_sentence", "label": "One-line backstory", "text": "<sentence>",
     "who": "you", "provenance": "FROM-EXPERT"},
    {"item_id": "flaw_1", "label": "A flaw shown on camera", "text": "<flaw, or 'declined'>",
     "who": "you", "provenance": "FROM-EXPERT"},
    {"item_id": "stance", "label": "Stance, tested", "text": "<the held reply>", "who": "you",
     "provenance": "FROM-EXPERT"},
    {"item_id": "parable_1", "label": "Parable", "text": "<when/who/what — the point>",
     "who": "you", "provenance": "FROM-EXPERT", "used_in": []},
    {"item_id": "voice_descriptors", "label": "Voice",
     "text": "<2-3 descriptors> | avoid: <word1>, <word2>", "who": "you",
     "provenance": "FROM-EXPERT"}
  ],
  "updated_at": "<ISO date>"
}
```

### What this step refuses to do

Propose a flaw the creator never said · save a declined flaw or personal detail, even as a
fragment · ask a bare question with no why-line/example pair · cap or skip an unanswered
question instead of unblocking it.
