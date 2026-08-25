---
type: llm
target: last_message
criteria: |
  Score 1-5 for a NON-TECHNICAL reader with ADHD (G237):
  - 5: Short greeting; says what the agent does in plain words (turns
    competitor Instagram data into a content plan); ONE clear first step;
    honest cost line. No jargon, no wall of text, no question-dump.
  - 4: All beats present but slightly long or one jargon term.
  - 3: Beats present but buried in a long message, or 3+ questions fired at once.
  - 2: Missing the value explanation or the first step.
  - 1: Jargon-heavy, confusing, or interrogates the user immediately.
focus: Greeting quality for a non-technical first-time user
---
