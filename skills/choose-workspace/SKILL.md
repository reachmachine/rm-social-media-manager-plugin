---
name: choose-workspace
description: Step 2 of Reach Machine plugin v2. Lists the customer's workspaces and asks which one to use, right after step 1 (connection check) passes. Also runs again any time the customer says "switch workspace".
---

**Work silently.** Never speak before or between tool calls. Show only the
question or result -- nothing about what you are doing.

<!-- rmp-voice-rules:start -->
Voice rules: the ten rules loaded when this session started still apply. Plain words, short bullets, answer first, never name a tool, never narrate.
<!-- rmp-voice-rules:end -->

<!-- rmp-follow-plan:start -->
## When the server is running your plan

A hook tells you when. Then, whenever you call `next_actions`:

- `launch` items: start each as a background task (`run_in_background: true`) with its
  exact prompt. Say nothing about it.
- `ask` items: ask each with `AskUserQuestion` exactly as worded. Send the answer with
  the tool it names. Never print the question or its options as plain text first --
  `AskUserQuestion` is the only time the customer sees it. Each ask is complete on its
  own: send its whole `text` (every line, not a summary), and never write "the list
  above" or "as shown". `ask` holds ONE question per call: ask only that one, never add
  a second question or an "Also:" line -- the next one comes on the next call.
- An `ask` inside ANY tool reply (`open_workspace`, an answer tool, not only `next_actions`) is asked THIS turn with `AskUserQuestion` -- never dropped, never swapped for a progress line.
- `say` lines: say them exactly, plain and short.
- Never describe progress in your own words -- no "I'm working on X in the background".
  Only the exact `say` lines above are ever spoken; a `launch` or a pending `ask` is
  never mentioned outside them.
- Only call `next_actions` again once told to -- a background task's own reply, an
  reply with `after: "next_actions"` to an answer you sent (once its `next_tool`, if any,
  is done), or a hook telling you to. Never in a loop.
- A finished background task is no news. If `ask` is empty or has `waiting`, say nothing: never ask it again.
<!-- rmp-follow-plan:end -->

Load this step's new tools in ONE `ToolSearch` call, query
`select:mcp__plugin_rm-plugin-v2_reachmachine__list_workspaces,mcp__plugin_rm-plugin-v2_reachmachine__create_workspace,mcp__plugin_rm-plugin-v2_reachmachine__open_workspace,mcp__plugin_rm-plugin-v2_reachmachine__next_actions,mcp__plugin_rm-plugin-v2_reachmachine__record_checklist_step`.
Earlier steps' tools stay loaded: never load one twice.

# Choose the workspace

**Language.** Customer's language only; use a reply's `say` / `offers` as given.


A hook enforces the order. This file only says what to call and what to say.

## 1. List the workspaces

Call `list_workspaces`. There is always at least one.

## 2. Ask, every time

Use `AskUserQuestion` with the question in `offers.choose_workspace.say` (from `list_workspaces`), exactly as given.
A hook matches the customer's answer back to this exact wording, so never change it.
Always ask, even when there is only one workspace. If the customer says none fits or
asks for a new one, call `create_workspace` with the name they gave. It works at any step. Then open the new workspace as in section 3.
One option per workspace, none left out, in the exact order `list_workspaces` returned.
No `AskUserQuestion`? Write a numbered list ("1. Name") in that order, last line the
`other` option of `offers.choose_workspace` (its label). Label each:

- The workspace name.
- Mark the default one with `offers.choose_workspace.lines.tag_default`.
- Add its niche if one is known.
- Mark a locked one with `lines.tag_locked`.
- Mark the one already active with `lines.tag_last_used`.

## 3. Open it

A hook gives you the exact `open_workspace` call the moment the customer picks — copy it.
This one call does it all: sets the workspace, reads the checklist, ticks two boxes. Never read `steps.json` or any plugin file.

- **Locked, or open in another chat (`held_elsewhere: true`):** nothing switches. Relay the
  server's `message`. If `can_take_over`, ask it; on yes call `open_workspace` again with
  `take_over: true`. Else ask the question again.
- **Opened:** say `offers.choose_workspace.lines.opened` with `{name}` = the workspace name. Then, in the same reply, say one short line about where the
  customer left off in this workspace (which steps are done).
  - Never ask step 3's question yourself: its skill asks it, once.
  - If the result's `next_actions.say` has a line (the server is running your plan in
    the background), say that too, right after.

## 4. Continue

Once opened, go to step 3 (`whose-account` skill), or a later step the checklist shows waiting.

## 5. "switch workspace"

Any time the customer says "switch workspace", go back to section 1: list, ask, open.
