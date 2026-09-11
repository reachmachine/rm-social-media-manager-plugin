> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 3.10**, during the analysis wait (no data needed for this half — the
> founder's exact point, dependency-audit 2026-09-06). The FORM the beliefs take is decided
> later, at `step-04-6-false-beliefs-form.md`, after Step 3's analysis lands. This is the MAP
> half of p11 "Map False Beliefs + Build a Story Bank"
> (`marketing/rules/process-cards/p11-map-false-beliefs-story-bank.md`, FRFRMU-1045) — this key
> is the SINGLE owner of objection/myth-busting content; p08 and p05 reference these rows, they
> never keep a second list.

## Step 3.10 — The false-belief map (p11)

**Ask per `asking-rules.md`.**

**List every reason a viewer thinks "this won't work / I can't / something outside me will
stop me" — trace where each came from — and answer each with a short true story, never an
argument.**

### 1. Seed, never re-ask

Pull from `prospect_research` objections (p04), PQR2 `roadblocks`, the interview's Q6 ("what
were you sure about that turned out backwards"), the magic desk Q10, pasted DMs, audience-ask
replies. Draft **≥10 rows (target 20+)**, each with its source. A row with no source is
`inferred` and must be confirmed before use.

### 2. Columns — belief, experience, self-story (agent-drafts in the prospect's voice)

The belief in the PROSPECT'S OWN words, never marketing-speak ("I tried a chatbot once and it
broke on the one thing that mattered" — not "prospects fear reliability"). Ask-user only where
the experience is real and personal (the founder's own past belief), with a why-line and
example.

### 3. Sort Vehicle / Internal / External, then propose the core three

One per bucket, with a one-line reason each; the creator confirms. **An empty External bucket
→ look again** (time, money, algorithm fears) before accepting the map as done.

### 4. Attach a bridge story to every row

From `origin_story` sections (p10), `attractive_character.parables` (p09), a client's story
(**ask-user**, told AS the client's, never as the creator's own), or a public story. No story →
`story_wishlist`. **A core belief never ships unanswered.**

### 5. Curiosity headline per core belief — hype stripped

Structure kept, no "secret", no "steal", no dollar figure (Gate 1).

### 6. Read back, confirm, save

Creator Brief key `false_beliefs`, Foundation-card shape:

```
{
  "card": "false_beliefs", "title": "What stops them, answered",
  "status": "confirmed",
  "summary": "<N rows, core three picked, M with a story>",
  "items": [
    {"item_id": "row_1", "label": "Vehicle belief", "text": "<belief, prospect's voice>",
     "who": "agent", "provenance": "JUDGMENT", "source": "prospect_research:objection_02"},
    {"item_id": "row_1_story", "label": "Bridge story for row 1",
     "text": "<ref: origin_story.section_wall, or the story itself>", "who": "agent",
     "provenance": "JUDGMENT"},
    {"item_id": "core_vehicle", "label": "Core — Vehicle", "text": "row_1", "who": "you",
     "provenance": "FROM-EXPERT"},
    {"item_id": "core_internal", "label": "Core — Internal", "text": "row_N", "who": "you",
     "provenance": "FROM-EXPERT"},
    {"item_id": "core_external", "label": "Core — External", "text": "row_M", "who": "you",
     "provenance": "FROM-EXPERT"}
  ],
  "updated_at": "<ISO date>"
}
```

Repeat the `row_N`/`row_N_story` pair per row (≥10).

### 7. Tag each row's M (p30, FRFRMU-1068)

Every row gets `m_type: myth|misconception|mistake` — a mistake is "the old way did X wrong", a
misconception is "people wrongly believe X", a myth is "X is flatly false". **The belief-breaker
pillar orders candidates mistake → misconception → myth by default** (mistakes are the
strongest — nobody wants to be the one making one) **unless this niche's own `myth_busting`/
`call_out` angle lift says otherwise** — data wins on order, this rule only sets the default. The
copywriter (`skills/rm-copywriter/belief-breaker.md`) reads `m_type` and the row to write the
script; it never re-tags a row.

### What this step refuses to do

Save a row with no source and no `inferred` flag · write a headline with "secret"/"steal"/a
dollar figure · pass a client's story off as the creator's own · leave a core belief with no
story ref.

### Success criteria (falsifiable)

≥10 rows, all four columns filled or `story_wishlist` · all three buckets non-empty, exactly
three `core: true` · every PQR2 roadblock and p04 objection appears as a row or is dropped with
a stated reason.
