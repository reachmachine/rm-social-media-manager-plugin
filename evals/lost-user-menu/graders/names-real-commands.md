---
type: llm
target: last_message
criteria: |
  Score 1-5:
  - 5: A short menu of what the agent can do (insights/hooks/CTAs, competitors,
    analysis, planning), clearly split into free vs credit-spending, ending
    with ONE recommended next step for this specific user.
  - 4: Menu + cost split present, but no single recommended next step.
  - 3: Lists capabilities but no cost grouping, or overwhelming detail.
  - 2: Vague "I can help with lots of things" without concrete options.
  - 1: Repeats the intro or asks a question without answering.
focus: Does a lost user leave this message knowing their options and next step?
---
