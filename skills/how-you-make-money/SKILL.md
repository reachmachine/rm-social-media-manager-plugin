---
name: how-you-make-money
description: Step 5 of Reach Machine plugin v2. Finds out (or confirms) how a workspace's business makes money and what it offers, right after step 4 (the Instagram account we're planning for).
---

**Work silently.** Never speak before or between tool calls. Show only the
question or result -- nothing about what you are doing.

<!-- rmp-voice-rules:start -->
Voice rules: the ten rules loaded when this session started still apply. Plain words, short bullets, answer first, never name a tool, never narrate.
<!-- rmp-voice-rules:end -->

Load this step's new tools in ONE `ToolSearch` call, query
`select:mcp__plugin_rm-plugin-v2_reachmachine__record_session_event`.
Earlier steps' tools stay loaded: never load one twice.
Resumed chat, earlier steps not run here? Add: get_creator_brief, update_creator_brief.
Load these only when first needed (one `ToolSearch` each; full name = `mcp__plugin_rm-plugin-v2_reachmachine__` + name): save_business_fact, get_resume_checklist.

<!-- rmp-facts-rule:start -->
A business fact the customer states: `save_business_fact` with `source: "customer"` and their exact words, as the session-start rule says.
<!-- rmp-facts-rule:end -->

# How you make money

**Language.** Customer's language only; use a reply's `say` / `offers` as given.


**Start this step only after step 4's box is ticked or skipped. If it is not, go back to step 4.**

A hook enforces what can be saved, not this file. This file only tells you what to call
and what to say.

- Every `update_creator_brief` call puts the brief fields inside `fields`.
  Leave `skill_version` out -- it is optional.

## 1. Read what is already known

Call `get_creator_brief`.

- **`revenue_known_say` is present:** say it exactly, word for word -- nothing before or
  after it. Then tick (section 6), **unless `get_resume_checklist` already showed this
  step `done`; then do not tick again.**
- **`revenue_known_say` is not present:** say nothing about it -- skip straight to
  section 2 and ask BOTH questions (2-5).

## 2. Ask how they make money

Use `AskUserQuestion` with ONE question per call (a hook reads only single-question
calls), `multiSelect: true`, with the question and the five buttons in `offers.revenue_model` exactly as given
(ids `product`, `service`, `brand_collaborations`, `other_income`, `not_earning_yet`).

Where no clickable question is possible, ask the same question in plain text and list the
five options; the customer may type one or more, separated by commas.

**If the customer types a full sentence instead** (e.g. "I sell cakes and do catering"): a
hook hands you a confirm question (the server's `offers.revenue_confirm`, ids `yes`, `no`) in that same turn. Ask it EXACTLY as given (plain text if no widget), with the two
options it gives you. The customer may answer by typing the button, its number, or its id -- that counts. After the answer, the
hook tells you the exact next call: on "Yes" save that pick (section 3) and go straight to
section 4 -- never show the five options again; on "No" (or anything else) show the five
options again, once, and take whichever answer the customer gives then. Never guess a pick
yourself.

## 3. Save the picks

Call `update_creator_brief` with ONLY `revenue_model`: `value` = the list of picked values
(`product`, `service`, `brand_collaborations`, `other_income`, `not_earning_yet`), `source: "conversation"`.
Anything the customer typed into "Type something" is not a pick; it belongs in the next
answer.

## 4. Ask what they offer

Ask the question in `offers.revenue_description.say` exactly as given. This is a plain
question the customer types an answer to. Do not use `AskUserQuestion` for this one; type
it as a plain message (a hook only reads the customer's typed reply here). Then stop and
wait. **Never write this answer yourself** — a hook refuses the save until the customer
has replied. If the latest plan gave `suggestion.revenue.revenue_description`, add
`offers.revenue_description.lines.example` under the question, with `{text}` = that text.

If it gives things away or serves the public, that is fine: ask the same question.

**If they say they don't know:** a hook will hand you ONE follow-up question next turn --
ask it exactly as given (`offers.revenue_description.lines.dont_know_follow_up`), then wait again. If they still don't know, a hook closes this step
for you (no description saved, nothing invented) -- just call `record_checklist_step`
exactly as it tells you (`how: "skipped"`) and say `offers.revenue_description.lines.later`. Never ask a third time.

## 5. Save a clean summary

From the customer's reply, write one or two clear lines: what they offer, to whom, and how
they make money. Fix grammar and spelling. Keep their facts (price, who it is for); never
add a fact they did not give. Call `update_creator_brief` with ONLY `revenue_description`
set to that summary. Then say `offers.revenue_description.lines.saved` with `{summary}` = the summary.
Keep the owner's own words and language in `revenue_description`; never translate them to English.

## 6. Log their words, then tick

A hook then gives you an exact `record_session_event` call (`kind: "revenue_described"`,
with the customer's own words). Copy it exactly — never put your summary there. Then call
`record_checklist_step` exactly as the hook tells you (`how` is `answered`, or
`already_known` when section 1 skipped the questions). Say nothing about either call.

Once the box is ticked, move on to step 6 (your website) — the `your-website` skill.

## 7. Changing the answer later

If the customer wants to change how they make money or what they offer, ask both questions
again (sections 2–6).
