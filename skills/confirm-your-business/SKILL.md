---
name: confirm-your-business
description: Step 7 of Reach Machine plugin v2. Reviews what we know about the business and lets the customer confirm, correct, or add more.
---

**Work silently.** Never announce or describe any action you take or are about to take -- only the server's own `say` lines and the customer's own words.

Load this step's new tools in ONE `ToolSearch` call, query
`select:mcp__plugin_rm-plugin-v2_reachmachine__get_business_review,mcp__plugin_rm-plugin-v2_reachmachine__answer_business_review`.
Earlier steps' tools stay loaded: never load one twice.
Load these only when first needed (one `ToolSearch` each; full name = `mcp__plugin_rm-plugin-v2_reachmachine__` + name): save_business_fact, get_fact_tasks, save_business_facts, start_customer_upload, send_customer_files, get_customer_upload.

The server writes every word. Say `say`/`lines` exactly as given -- never invent, reorder,
or shorten them.

## Loop

Every "go to step 1" below: if the `answer_business_review` reply has a `next`, that IS step 1's result -- use it and do not call `get_business_review`. No `next` -- call it.

1. Call `get_business_review`.
2. `ready: false` -- say `say` once, then keep going with whatever the customer already
   asked for. Never wait, sleep, retry, or call this again yourself this turn -- the
   hook offers step 7 again once it is ready.
3. `stage: "fill"` -- same as your-website section 7: read the passages, save what you find
   with `save_business_facts`, then go back to step 1.
3b. `stage: "table"` -- send `question.text` exactly as a plain typed message (no `AskUserQuestion`). Call
   `answer_business_review(answer: "table", text: <their WHOLE reply, exactly as typed>)`. Say its `say`.
   Their reply named files (not `no files`, not numbered rows): do these in order before step 1, once per file:
   1) `start_customer_upload(purpose: "business_doc")`, 2) `send_customer_files`, 3) `get_customer_upload` until it
   says read, 4) `facts_to_update: true` -- `get_fact_tasks(scope: "upload")`, then `save_business_facts`
   (`source: "file"`, exact quote). Then go to step 1.
3c. `stage: "reviews"` -- `AskUserQuestion`: `question.text` (it names the cost) with its 2 options. Call
   `answer_business_review(answer: "yes"|"no")`, follow its `next_tool`. Go to step 1.
4. `stage: "who_buys"` -- ask `question` (its text holds the story; 2 options: right/fix) and
   each of `targeted_questions` (one at a time, each 3 options or fewer).
   - Call `answer_business_review(answer: "right"|"fix")`. Say its `say` line.
   - For EACH targeted question, call `answer_business_review(answer: <chosen opts value>,
     targeted_audience: <that question's own "audience">)` -- one call per question.
   - Any answer that changes something ("fix", or a targeted pick naming another audience)
     -- follow that call's `save_hint`: ask what's different, then `save_business_fact`
     (field: `audience_map`, source: `customer`).
   - Go to step 1 once every question above has its own answer.
5. `stage: "top_earner"` -- ask `question`. It can carry up to 8 options: show the first 3
   plus a something-else button, and accept any typed reply as the answer (the server matches it).
   Call `answer_business_review` with the chosen value or the typed text. Go to step 1.
5b. `stage: "how_buy"` -- ONE `AskUserQuestion`, `multiSelect: true`, the `question.multi_options` labels. Call
   `answer_business_review(answer: <picked labels joined ", ">)`; a typed "1, 3" goes as typed. "Other" -- add
   `text`: their own words. A reply with `question` -- ask it, call again with `answer: keep_answer` + `text`.
   Say any `advice`. Go to step 1.
6. `stage: "summary"` -- ask `question` (its text holds the summary; button ids `all_good`, `change`, `add`). Add no reply text before it.
   - `all_good` -- call `answer_business_review(answer: "all_good")`.
   - `change` -- ask what's different, call `save_business_fact`, then
     `answer_business_review(answer: "change")`.
   - `add` -- call `answer_business_review(answer: "add")`. Its own `question` offers
     two buttons, type it / send a file or folder:
     - typed text -- call `save_business_fact` with the best-fitting field. a "doesn't apply to me" reply ->
       `status: "not_applicable"`, no items. A note fitting no field -> `other_1`..`other_3` (one item: `label`, `text`).
       Keep the owner's own words and language in the item text and `customer_words`; never translate them to English.
     - a file or folder -- call `start_customer_upload(purpose: "business_doc")`, then
       `send_customer_files`, then `get_customer_upload`. Say only each tool's own `say`.
       `facts_to_update: true` -- `get_fact_tasks(scope: "upload")`, then one
       `save_business_facts` (`source: "file"`, exact quote) for what the file says. Never skip.
   - Go to step 1.
7. `stage: "open_question"` -- say `say`+`question.text`; `answer_business_review
   (answer: <reply>)`. Go to step 1.
8. `stage: "done"` -- say the final `say` line. Stop.

Never mention tools, steps, the plugin, or any internal field name.
