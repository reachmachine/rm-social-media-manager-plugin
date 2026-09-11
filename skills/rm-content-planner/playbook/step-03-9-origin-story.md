> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 3.9**, during the analysis wait, after the persona questions
> (`step-01-4-persona-questions.md`) have run. This is p10 "Write the Origin/Epiphany Story"
> (`marketing/rules/process-cards/p10-write-origin-epiphany-story.md`, FRFRMU-1044): the story is
> COLLECTED at intake (the personal-story interview) but never WRITTEN — this step writes it
> once, so every recipe quotes the same story instead of re-deriving a different one each time.

## Step 3.9 — The origin/epiphany story, written once (p10)

**Ask per `asking-rules.md`.**

**Pull, never re-ask.** Start from `personal_story` fragments, positioning item 6, and
`attractive_character.backstory_sentence`/`parables`. Ask ONLY for what is missing from the 8
sections below, one gap at a time, each with a why-line and a niche example.

### Typical gaps and their one question

- **The Wall's body:** *"Where were you when you knew it wasn't working, and what did your body
  do?"* Bar: a place + a physical sensation ("stomach knotted"), not an adjective ("frustrated").
- **The epiphany moment:** *"What did you see, hear or read the moment it clicked?"* An honest
  **"gradual"** is a real answer — never fabricate a lightning-bolt moment the transcript
  doesn't support.
- **The plan:** *"What's the first thing you did the next day?"* An action, not a resolution.
- **Setback + glimmer:** *"The moment it almost died — and what kept you going?"*
- **Achievement, honest:** *"What actually happened, including what you didn't get?"* No
  inflated result, no income claim (Gate 1) — missing the original goal is allowed.
- **Transformation:** *"What do you believe now that the old you would argue with?"* A belief,
  not an outcome — this also seeds p11's false-belief bank.

A declined gap → `status: gap`; a real 5-beat story beats a padded 8-beat one.

### Draft, then three passes

1. **Draft the 8 sections from fragments only** — every sentence traceable to a fragment id.
2. **"Kinda like" pass:** every technical term gets a plain-language bridge ("an executor agent
   is kinda like a contractor who only builds what the architect drew").
3. **Rapport pass:** the opening 10% names ≥2 of: victim of an outside force / in jeopardy /
   likable / funny / powerful — say which two and why.
4. **Domino anchor:** the epiphany's meaning = the Big Domino's belief (`big_domino.headline`
   when it exists; else the positioning sentence).

**Read back, then confirm.** *"Did I get that right? What did I miss?"* Only a confirmed story
becomes canonical — `confirmed_by_user` gates every cut below.

### Cuts — data picks the beat order, the story stays the creator's

`get_content_structures` shows which story/transformation structures this niche proves, with
`n` — the cut follows that beat order:

- `reel_60s` — all 8 beats, compressed.
- `reel_30s` — the existing 4-part pinned structure (who I was → the shift → who I am now → why
  it matters to you).
- `hook_15s` — the Wall line + the shift.
- `caption` — the plot statement + the transformation.

### Save it

Creator Brief key `origin_story`, Foundation-card shape:

```
{
  "card": "origin_story", "title": "Your origin story",
  "status": "confirmed",   # only once confirmed_by_user
  "summary": "<one line: the plot statement>",
  "items": [
    {"item_id": "plot", "label": "Plot", "text": "<character, desire, direction, conflict>",
     "who": "you", "provenance": "FROM-EXPERT"},
    {"item_id": "section_wall", "label": "The Wall", "text": "<place + physical sensation>",
     "who": "you", "provenance": "FROM-EXPERT"},
    {"item_id": "section_transformation", "label": "Transformation",
     "text": "<the new belief>", "who": "you", "provenance": "FROM-EXPERT"},
    {"item_id": "cut_reel_30s", "label": "30s cut", "text": "<who I was...why it matters>",
     "who": "agent", "provenance": "DATA-INFERRED"},
    {"item_id": "cut_caption", "label": "Caption cut", "text": "<plot + transformation>",
     "who": "agent", "provenance": "DATA-INFERRED"}
  ],
  "updated_at": "<ISO date>"
}
```

Repeat the `section_*` item for each of the 8 sections; a gap becomes
`"text": "gap — <why>"`.

### What this step refuses to do

Write a sentence with no fragment id behind it · invent an achievement number the creator never
gave · open a cut with features/proof instead of emotion · re-ask anything already in
`personal_story` · use a cut before `confirmed_by_user = true`.

### Wired in (each does nothing when `origin_story` is absent, or `confirmed_by_user` is false)

`step-08-deliverable.md` Section 00's pinned identity reel uses `cuts.reel_30s` (item
`cut_reel_30s`) instead of re-deriving the 4-part summary each time · `step-08-caption-recipe.md`
may use `cut_caption` · `step-08-hook-recipe.md` may offer `hook_15s` as a story-hook candidate ·
G373 reuse now names sections (Wall → an empathy reel, Transformation → a Big Domino reel).
