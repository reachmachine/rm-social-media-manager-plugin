---
name: own-instagram-account
description: Step 4 of Reach Machine plugin v2. Finds out (or confirms) the Instagram handle of the account the workspace is planning for, right after step 3 (whose account this is).
---

**Work silently.** Never speak before or between tool calls. Show only the
question or result -- nothing about what you are doing.

<!-- rmp-voice-rules:start -->
Voice rules: the ten rules loaded when this session started still apply. Plain words, short bullets, answer first, never name a tool, never narrate.
<!-- rmp-voice-rules:end -->

Load this step's new tools in ONE `ToolSearch` call, query
`select:mcp__plugin_rm-plugin-v2_reachmachine__add_to_watchlist`.
Earlier steps' tools stay loaded: never load one twice.
Load these only when first needed (one `ToolSearch` each; full name = `mcp__plugin_rm-plugin-v2_reachmachine__` + name): refresh_competitor, change_own_account, record_session_event, save_business_fact, get_resume_checklist.

<!-- rmp-facts-rule:start -->
A business fact the customer states: `save_business_fact` with `source: "customer"` and their exact words, as the session-start rule says.
<!-- rmp-facts-rule:end -->

# Your Instagram account

**Language.** Customer's language only; use a reply's `say` / `offers` as given.


A hook enforces what can be saved, not this file. This file only tells you what to call
and what to say. This skill is written generically — a later question step can copy the
same four moves: read, ask, save, tick.

## 1. Read what is already known

The `get_resume_checklist` result from step 2 already carries a `detail` on the
`own_instagram_account` step when this workspace has its own account. Never call
`search_watchlist` for this, and never use the profile's Instagram field (founder
decision 2).

- **`detail` present:** do not ask. When a hook gives you a line to say, say it exactly,
  word for word, then make the call. If a hook tells you to refresh first (the numbers are
  stale), call `refresh_competitor` with that one handle first. The server decides if a
  free refresh actually runs — if it says the numbers were checked recently, just carry on.
- **no `detail`, but `suggested_handle` is set (`suggestion_source: "website"`):** ask
  with `AskUserQuestion`, the question and buttons in `offers.instagram_suggested` exactly as given
  (`{handle}` = the suggested handle; ids `yes`, `no`).
  - **`yes`:** go to section 3 (show the price) with that handle.
  - **`no`:** ask normally (section 2).
- **nothing on file:** say nothing about it — ask (next section). Never say what was or was not there, or why you ask.

## 2. Ask

Ask the question in `offers.own_instagram_account.say`, exactly as given. This is a
plain question the customer types an answer to, not a multiple-choice question.

## 3. Show the price, then wait

Call `add_to_watchlist` with `handles` = [the handle they typed or confirmed above],
`self_handle` = the same handle, and `confirm` = false. Read the cost from the result's
own message. Say `offers.own_instagram_account.lines.price` with `{handle}` and `{cost}` filled.
Then stop and wait for the customer's answer. Never confirm in the same message.

## 3a. If it's already on your competitor list (RMP-185)

If the preview's message says the handle is already on your competitor list, say that
message exactly as the price question instead of the template in section 3 -- this makes
it your own account instead of adding a new one, so skip "We'll read its follower and post
count". Then wait for a yes and confirm the normal way (section 4).

## 3b. If the check flags it, ask once

If the preview's `screened` entry has `verdict: "flagged"` (a bakery typed for a salon counts) or `niche_fit_verdict: "off"`, the
preview's message IS the question (reason, price, numbered yes / no).
Say it exactly, once, then wait (a button question instead: `offers.own_account_mismatch`, ids `yes`, `no`). Skip the section 3 price line. Copy a hook's log payload exactly.

- **1 or yes:** one yes covers the account AND the price. Call `add_to_watchlist` with the same
  `handles` and `self_handle`, `confirm` = true AND `include_flagged` = true. No new preview.
  Log an answer only when a hook gives you its payload.
- **2:** ask for the handle again. Never add a flagged own account without that yes.

## 3b2. Wrong handle after it was added (RMP-23)

If the customer says the account just added is the wrong handle: `change_own_account` with
`wrong_handle` = true, `new_handle` = that handle. Say its message, then ask for the handle (section 2).
Never ask whether it is the same business renamed.

## 3c. If Instagram has no data at all, ask before adding (RMP-175)

If the preview's `screened` entry for this handle has `verdict: "not_found"`, Instagram found
nothing for it — no follower count, no post count. Say the tool's `say`/`message` exactly, for
example that it could not find that handle on Instagram. Do not show a price;
none was given, because nothing would be checked or charged yet. Then call `AskUserQuestion` with
the question and buttons in `offers.instagram_not_found` exactly (ids `fix`, `add_anyway`).

- **`fix`:** ask for the handle again (section 2).
- **`add_anyway`:** call `add_to_watchlist` again with `confirm` = true AND `add_anyway` = true.
  This still costs the same credits as any other add.

## 4. Add

After the customer says yes, call the same `add_to_watchlist` again with `confirm` =
true. Do not explain, do not guess, do not offer to check again on your own — only section 3c's
`add_anyway` answer may set `add_anyway`. Do not tell the customer the account was added yet.
The hook gives you the exact line to say once the numbers are read (section 5). If the add went
through with `add_anyway` = true, that line will say plainly that no numbers are available yet —
say it exactly as given, never invent a follower or post count.

## 5. Tick the checklist box

The hook gives you one line to say first (the server's `lines.plan_for` or `lines.added`: the handle, followers, posts, date).
Say that line exactly, word for word, as its own message, then make the tick call.
Never shorten it and never say the add in your own words instead.

Call `record_checklist_step` exactly as the hook tells you (`how` is `answered` after an
add, `already_known` when section 1 skipped the question). This also writes the session
log entry. If `get_resume_checklist` already showed this step `done`, do not tick it
again. Say nothing else about this call.

Once the box is ticked, move on to step 5 (how you make money) — the
`how-you-make-money` skill.

## 6. After a refresh, log it

When a hook tells you to call `record_session_event` with `kind: "profile_refreshed"`,
copy that payload exactly. Say nothing about this call. No checklist tick for a refresh.

## No Instagram (RMP-281)

If the customer says they have no Instagram account or want to skip, call
`AskUserQuestion` with the question and buttons in `offers.skip_instagram` exactly (ids `no_instagram`, `add`).

- **`no_instagram`:** call `record_checklist_step` exactly as the hook tells you
  (`how` will be `no_instagram`). Say ONLY `offers.skip_instagram.lines.final`.
  This is final. Never ask about Instagram again. Then move to step 5.
- **`add`:** ask for the handle again (section 2).

## An older "skipped" step 4

When a hook gives you a re-offer question (`offers.instagram_reoffer`), ask it word for word with `AskUserQuestion`.
On `add`, run step 4 normally. On `later`, say `offers.instagram_reoffer.lines.later` and move on.

## Changing the account (RMP-113)

If the customer already has an own account added here and types a DIFFERENT handle
(or `add_to_watchlist` comes back with `self_account_already_set`), call
`change_own_account` with the new handle. The server tells you what it is — never
guess yourself. If its `message` says "One Instagram account per workspace", say that line
as given. A second business needs another workspace.

- **`path: "rename"` (same business, new name):** it already applied. Say one short
  line, exactly like the tool's `message`. Move on, nothing else to do.
- **`path: "ask"`:** ask with `AskUserQuestion` the question and buttons in `offers.change_own_account`
  (`{new_handle}`, `{old_handle}` filled; ids `same_business`, `different_account`). Call
  `change_own_account` again with `same_business: true` or `false`.
- **`path: "rename"` with `requires_confirmation: true`:** the customer said "same
  business" but the tool needs one more yes first. Say the `message` as your
  question, wait for a clear yes, then call again with `same_business: true,
  confirm: true`.
- **`path: "different_account"`:** say the `message` in plain words. Ask with `AskUserQuestion`
  the question and buttons in `offers.change_own_account_reset` (ids `yes`, `no`), and wait. On `yes`, call again with `same_business: false, confirm: true`.
  After that, add the new handle the normal way (section 2 above) — a normal
  charged add, same price as any first add.
- **`path: "not_found"`:** say the account could not be checked on Instagram.
  Nothing changed — ask for the handle again.
- **`path: "none"`:** that is already the account being planned for — nothing to do.
