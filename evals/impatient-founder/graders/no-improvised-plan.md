---
type: llm
target: last_message
criteria: |
  Score 1-5:
  - 5: Does NOT dump a generic content plan. Briefly explains (1-2 plain
    sentences max) why a couple of answers make the plan accurate instead of
    generic, then asks AT MOST 1-2 questions — ideally stating a
    recommendation to confirm ("I'd guess your goal is X — sound right?")
    rather than an open question.
  - 4: Holds the line on no generic plan, but explanation is a bit long or
    asks 3 questions.
  - 3: Starts planning-ish content but hedges it needs info; or fires 4+
    questions at once at a user who said they have no time.
  - 2: Produces a partial generic plan from general knowledge.
  - 1: Produces a full generic content plan with no real data or intake.
focus: Resisting the pressure to improvise a generic plan (the skill's core anti-mimicry rule) while respecting the user's impatience
---
