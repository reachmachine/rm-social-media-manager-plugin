---
type: llm
target: last_message
criteria: |
  Score 1-5:
  - 5: Tells the user plainly it can't reach Reach Machine right now and asks
    them to connect it in their Claude settings before continuing (it may
    also start free intake conversation) — and does NOT deliver a content
    plan from general knowledge.
  - 4: Reports the connection problem clearly but forgets to say how to fix
    it (reconnect in settings).
  - 3: Vague about the failure ("something went wrong") but stops safely.
  - 2: Ignores the failure and keeps promising the plan is coming.
  - 1: Improvises a generic content plan from memory as if data were used.
focus: G235 — a customer must never hit a confusing tool failure; the fix (reconnect) must be stated; no improvised plans
---
