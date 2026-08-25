---
type: llm
target: last_message
criteria: |
  Score 1-5:
  - 5: Clearly establishes the plan's SUBJECT is the dental clinic, not the
    agency — everything it asks or proposes next is about the clinic
    (its audience, stage, positioning), and it mentions or implies keeping
    this client's work in its own workspace.
  - 4: Treats the clinic as the subject but never mentions per-client
    workspace separation.
  - 3: Ambiguous — mixes questions about the agency's brand with the
    clinic's.
  - 2: Asks about the agency's own positioning/audience as if the plan were
    for the agency.
  - 1: Starts planning for the agency's own Instagram.
focus: Rule 0 — agencies plan for the CLIENT (the subject), never the account owner
---
