---
name: whose-account
description: Step 3 of Reach Machine plugin v2. Finds out (or confirms) whether a workspace's account belongs to the customer's own business or to a client, right after step 2 (choose the workspace).
---

**Work silently.** Never speak before or between tool calls. Show only the
question or result -- nothing about what you are doing.

<!-- rmp-voice-rules:start -->
Voice rules: the ten rules loaded when this session started still apply. Plain words, short bullets, answer first, never name a tool, never narrate.
<!-- rmp-voice-rules:end -->

Load this step's new tools in ONE `ToolSearch` call, query
`select:mcp__plugin_rm-plugin-v2_reachmachine__get_creator_brief,mcp__plugin_rm-plugin-v2_reachmachine__update_creator_brief`.
Earlier steps' tools stay loaded: never load one twice.
Load these only when first needed (one `ToolSearch` each; full name = `mcp__plugin_rm-plugin-v2_reachmachine__` + name): save_business_fact.

<!-- rmp-facts-rule:start -->
A business fact the customer states: `save_business_fact` with `source: "customer"` and their exact words, as the session-start rule says.
<!-- rmp-facts-rule:end -->

# Whose account is this?

**Language.** Customer's language only; use a reply's `say` / `offers` as given.


A hook enforces what can be saved, not this file. This file only tells you what to call
and what to say. This skill is written generically — a later question step can copy the
same four moves: read, ask, save, tick.

- Every `update_creator_brief` call puts the brief fields inside `fields`.
  Leave `skill_version` out -- it is optional.

## 1. Read what is already known

Call `get_creator_brief`. Look for `account_owner_type`.

- **Already "own" or "client":** do not ask. Say `lines.known_own` (or `lines.known_client`) of
  `offers.account_owner_type`. Then tick the checklist box (step 4 below)
  and move on.
- **Missing, empty, or anything else:** it is not known yet — ask.
- **This is the ONLY place this is asked.** Already answered in this chat? Use it, ask nothing.

## 2. Ask

Use `AskUserQuestion` with the question and the two buttons in `offers.account_owner_type`
(ids `own`, `client`), exactly as given.

If they don't pick one, or say something like "not sure": say `lines.retry`, then ask again.
Never guess or save without a real answer.

## 3. Save

Call `update_creator_brief` with `{"fields": {"account_owner_type": {"value": "own"|"client",
"source": "conversation"}}}`. Use the value
the customer actually chose, never a guess.

Then say `lines.saved_own` (or `lines.saved_client`).

## 4. Tick the checklist box

Call `record_checklist_step` to mark this step done. A hook tells you the exact call to
make (including `how`: `answered` if you just asked, `already_known` if step 1 skipped
the question); copy it. Say nothing about this call.

Once the box is ticked, move on to step 4 (the Instagram account we're planning for) —
the `own-instagram-account` skill.

## 5. Changing the answer later

If the customer says this workspace is actually for the other kind of account, ask the
question again (step 2), save the new answer (step 3), and tick the box again (step 4).
