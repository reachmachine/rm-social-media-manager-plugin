---
name: your-website
description: Step 6 of Reach Machine plugin v2. Reads the business's website and fills the business facts, right after step 5.
---

**Work silently.** Never speak before or between tool calls. Show only the
question or result -- nothing about what you are doing.

<!-- rmp-voice-rules:start -->
Voice rules: the ten rules loaded when this session started still apply. Plain words, short bullets, answer first, never name a tool, never narrate.
<!-- rmp-voice-rules:end -->

Load this step's new tools in ONE `ToolSearch` call, query
`select:mcp__plugin_rm-plugin-v2_reachmachine__start_website_read,mcp__plugin_rm-plugin-v2_reachmachine__get_website_read_status,mcp__plugin_rm-plugin-v2_reachmachine__get_business_facts,mcp__plugin_rm-plugin-v2_reachmachine__start_reviews_fetch`.
Earlier steps' tools stay loaded: never load one twice.
Load these only when first needed (one `ToolSearch` each; full name = `mcp__plugin_rm-plugin-v2_reachmachine__` + name): get_fact_tasks, save_business_facts, cancel_website_read, get_next_fact_task, search_business_knowledge, skip_business_fact, finish_reviews_fetch, choose_product_list_source, start_customer_upload, send_customer_files, get_customer_upload, record_session_event, save_business_fact, answer_question.

<!-- rmp-facts-rule:start -->
A business fact the customer states: `save_business_fact` with `source: "customer"` and their exact words, as the session-start rule says.
<!-- rmp-facts-rule:end -->

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

# Your website

A hook enforces what can be saved, not this file. This file only tells you what to call
and what to say.

**Language.** Every line is in the customer's language. A tool reply's `say`, question or `offers` entry is used exactly as given. A line named `lines.<name>` below is in the `lines` of the last `get_website_read_status` reply: say it exactly, filling its `{holes}` with the value, nothing more.

**Start this step only after step 5's box is ticked. If it is not, go back to step 5.**

## Any time: the customer says stop

Once section 4 has started a read (before it is ticked in section 12), if the
customer says the site is wrong, they have no website, or to stop reading it:

- Call `cancel_website_read(read_id)` right away.
- Say its `say` line ONLY after the tool returns -- never say "stopped"
  first and check later.
- Then ask section 3's question again, and answer it the normal way.

## 1. Wait for step 5

Do not start step 6 until step 5 (how you make money) is ticked, skipped, or already
known.

## 2. Read what is already known

Call `get_website_read_status`.

- **A finished read, less than a month old (`due_for_reread` is false):** call
  `get_business_facts`. If any searchable field is still missing, go to "Fill the facts"
  (section 7) instead of ticking `already_known`. Otherwise do not ask -- say `lines.known`
  (`{host}`, `{date}`, `{n}`). Then tick (section 12).
- **A finished read that IS due for a re-read:** say `lines.reread_due`. Then go straight to section 4 with `https://<host>`.
- **No read yet, `suggestion_source: "instagram_bio"` is set:** do not ask -- say
  `lines.from_bio` (`{site}` = **<suggested_site_url>**), then go straight to
  section 4 with that address. If the customer says that's the wrong site, ask section
  3's question instead.
- **`suggestion_source: "instagram_bio_booking"` is set:** ask `lines.bio_booking`
  as a plain typed message, then go
  to section 4 with what they type.
- **`suggestion_source: "previous_read"` is set:** ask with `AskUserQuestion`: `lines.confirm_site` (`{site}` = **<suggested_site_url>**), buttons `lines.confirm_yes` / `lines.confirm_no`. Yes -- go to section 4 with that address. No -- ask
  section 3's question instead.
- **`suggestion_source: "link_page"` is set** (the bio links a booking or link page;
  we found a site on it): same question, same two buttons and answers.
- **`current_read.status` is `cancelled` or `abandoned`, no finished read exists:**
  treat this exactly like no read yet -- ask (next section).
- **No read yet, no suggestion:** ask (next section).

## 3. Ask

Use `AskUserQuestion` with the question and buttons in `offers.website_question` (in the reply of
`get_website_read_status`) exactly. Button ids: `yes`, `no_website`, `later`.

- **later:** say `lines.skip_later`. Then tick (section 12).
- **no_website:** say `lines.no_website`. Then tick (section 12).
- **yes:** ask `lines.ask_address` as a plain typed message. Then stop and wait.

## 4. Start

- Call `start_website_read(site_url)` with the address the customer typed.
- `not_found` -- say its `say` line, then ask `lines.ask_address` again as a typed message.
- Two `not_found` tries in a row -- ask the section 3 question again instead of a third try.
- `moved` -- the site now redirects to a different address. Ask with `AskUserQuestion`: question = the tool's `say` line exactly, two buttons `lines.moved_yes` / `lines.moved_no`. Yes -- call `start_website_read` again with the tool's `new_site_url`, then continue this section with that result. No -- ask the section 3 question again.
- `social_link` -- the address is a Facebook/Instagram/link-in-bio page, not a website. Say the tool's `say` line, then ask the section 3 question again exactly as written there (same options, same hook capture -- no new mechanism needed).
- Otherwise -- say `lines.reading_bg`. Keep `read_id`.

## 5. Wait in the background

- Start ONE background agent (`website-reader`, `run_in_background: true`) with the `read_id`. Keep its agent name/id.
- It loops `wait_for_website_read`, reading any `browser_pages` with the browser, until `status` is not `reading`.
- Normal end: it returns one line, the final `say`.
- Reply is `RESUME read_id=<id>` instead: send that SAME agent (its name/id, via `SendMessage`) the message `continue` -- never a new or placeholder agent -- then wait again.
- Right after starting it, call `next_actions` once -- your one checkpoint for anything that does not need the read (e.g. reviews). Then carry on with the customer.

## 6. When it reports back

- `robots_blocked` or `failed` -- say the reply's `say` line. A hook then has you ask `AskUserQuestion` with its exact question and buttons (`offers.website_another`, ids `yes` / `no`). Yes -- ask `lines.ask_other_address` as a typed message, then go to section 4. No -- say `lines.take_facts`.
- `read == 0` (a `finished` status with nothing read) -- say `lines.no_pages`.
- If `get_website_read_status`'s `product_list.ask` is true, follow **Product list (shops)** first (at the end of this file).
- Otherwise -- call `next_actions` once (the server starts the fact-filling background task itself); it launches that task -- follow the plan rule above, skip section 7 (and section 9: once the task is done, the server itself asks "What we found ... Anything wrong or missing?" as an `ask`; a typed fix is section 10); it does not (`mode` is not `drive`) -- go to section 7. Do not tick yet: step 6 is done only after the facts are saved (`save_business_facts` leaves nothing missing, or `get_next_fact_task` says done).

## 7. Fill the facts

Fallback only: skip this section whenever `next_actions` launched the fact-filling task -- the task saves the facts, never you.

- Call `get_fact_tasks`. It waits on the server for your pages to finish indexing before answering, so a normal site needs at most one more call. If `available: false` and `reason: "still_indexing"`, say `lines.still_indexing` once, before the first repeat only, then call it again silently up to 4 more times with the same input -- the server switches to what's ready on its own once it has waited long enough, so never say anything about this to the customer. Any other `available: false` (or still indexing after those 4 repeats): stop, save nothing from the website, say `lines.saved_pages`. Do not tick.
- `available: true` with `partial: true`: some pages are still preparing (`pages_still_preparing` says how many) -- normal, not an error; do not retry just because of this. Fill in facts from the fields given, same as below. No need to mention it unless asked.
- For each field, read EVERY passage its `passage_ids` name from the top-level `passages` list before deciding -- do not stop at the first one: found -- add it to `save_business_facts`' `facts` with its `save_template` filled in (value, `page_url`, and an exact quote copied from a passage); not found -- add the field name to `skip`.
- Make ONE `save_business_facts` call with everything from the step above. If that response had `next_fields`, call `get_fact_tasks` again (a big site's response is sent one page at a time) and repeat this step until `fields` comes back empty -- `next_fields` names what to expect next, it is never something to skip.
- A field whose result is `refused`: fall back to the old loop just for that field -- `search_business_knowledge` with a rewritten question (at most 2 rewrites), then `save_business_fact` or `skip_business_fact`.
- Never paste passages into the chat.

## 8. Google reviews

- Call `start_reviews_fetch`. `available: false` with `reason: "ask_first"` -- the customer has not said yes yet, so there is no run plan. Ask with `AskUserQuestion`: question = `question.text` exactly, the options in `question.options`. Then call `answer_question` with `answer.args` plus `value` = the chosen option's `value`. The button with id `no` -- say nothing more, go to section 9. Id `yes` -- call `start_reviews_fetch` again.
- Any other `available: false` -- say nothing, go to section 9.
- `available: true` -- the customer's yes is on record: ask nothing, call the tool named in `run_tool` with `run_input` copied unchanged.
- That call succeeded -- read `dataset_items_step.dataset_id_path` (a dotted path, e.g. `storages.datasets.default.id`) out of its result, then call `dataset_items_step.run_tool` with `dataset_items_step.run_input` plus that value as `datasetId`, unchanged otherwise.
- Whether any of those calls succeeded, failed, or timed out -- call `finish_reviews_fetch` with the `fetch_id`. Say its `say` line exactly, then go to section 9.

## 9. Show what we found

- Call `get_business_facts`.
- One bullet per fact: label, then value.
- A last bullet listing the labels not found on the site.
- Ask if anything is wrong or missing.

## 10. Corrections

- A correction -- call `save_business_fact` with `source: "customer"` and their own
  words in `customer_words`. Show the tool's `say` line.

## 11. Check the Instagram account

Only if step 4 has an account (the checklist `detail` for
`own_instagram_account`).

Compare it with the facts you just found:

- The bio link (`external_url`) against this website's host.
- The name.
- The bio.
- The location.

**They clearly describe different businesses** (another website, another
city, another trade) -- say `lines.mismatch`: fill `{handle}`, `{instagram_value}` (what Instagram shows, for example
its bio link or city) and `{website_value}` (what this website shows) from the facts, each one a few plain words.
Then call `record_session_event` with `kind: "website_mismatch_shown"`,
`detail: {"handle": <handle>, "reason": <that line, max 200 chars>}`. Its reply carries
`offers.website_mismatch`: use `AskUserQuestion` with that question and those buttons exactly
(ids `yes` = same business, `no` = different).

Small differences (a missing city, a short bio) are **NOT** a mismatch --
say nothing and go straight to section 12.

After the answer, copy the `record_session_event` call the hook gives you
(`kind: "website_mismatch_answered"`). If the answer is `no`, ask in plain text which one is right, and save any fact they
correct with `source: "customer"`.

## 12. Tick

Call `record_checklist_step` as the hook tells you. Say nothing about
this call -- it has nothing to report to the customer. If it is refused with
"The server ticks this step itself", stop -- do not call it again.

Then go straight on to step 7 (the `confirm-your-business` skill, or the server's next
question) **without one word about it**: no "step is done", no "next, the business check",
no "loading that step". The customer only ever sees the next real question.

## 12. If the hook offers to read your website again

Used in a later session, only if you skipped step 6 before (`no_website` or `later`).

When a hook tells you to ask the re-offer question (visible in the additionalContext), call
`AskUserQuestion` with the question and buttons in `offers.website_reoffer` exactly (ids `read_now`, `later`).

- **read_now:** ask as a plain typed message for the website address. Then go to section 4.
- **later:** say `lines.reoffer_later`. Then carry on with what the customer asked for.

Ask this once per session, when the hook tells you.

## 13. Monthly re-read

Used only when the hook tells you to check for a re-read (step 6 is already ticked; this
never happens on the same turn as sections 1-12).

Call `get_website_read_status`.

- **`due_for_reread` is false:** nothing to do. Carry on with what the customer asked for.
- **`due_for_reread` is true:** call `start_website_read` with `https://<host>` (`host` from
  `current_read.host`). `moved` -- follow section 4's `moved` bullet. Otherwise wait and fill
  the facts the same way as sections 5 to 7.

A fact the customer told you is never replaced — the tool keeps it.

Say only what changed:

- **Nothing changed:** say `lines.reread_same`.
- **Something changed:** say `lines.reread_changed`. Then one bullet per
  fact whose value changed.

Do not tick anything here — step 6 is already done. Then carry on with what the customer
asked for.

- **If the product list came from an uploaded file:** the website re-read never
  overwrites it (the facts door keeps the higher-ranked file value). Say `lines.list_from_file`
  only (`{date}` from `product_list.last_import.at`).
- **If the choice was "skip":** say nothing about the product list. Never ask again.

## Product list (shops)

Runs right after section 6's report, before section 7 -- only when `product_list.ask` is true.

1. `AskUserQuestion` with the exact `product_list_choice` question and options the server gave you (`extra_q`). Then call `choose_product_list_source` with `choice` = `website`, `product_list`, or `skip`. Say its `say` line.
2. `website` and `skip` -- go to section 7 unchanged. The choice is remembered; this is never asked again.
3. "I'll give you my product list": call `start_customer_upload` with `purpose: "catalogue"`. Show its `accepts` line, then ask in plain text what it tells you to ask (its `say` line). Wait for the customer's answer.
   - Call `send_customer_files` with exactly what they typed, then `get_customer_upload`.
   - **Never open, read, or paste the file** -- the hook sends it for you, and a gate blocks `Read`/`Bash` from touching it while the upload is open.
   - `read` with a `catalogue` block -- say the file's own `say` line.
   - `refused` or `failed` -- say the file's own `say` line. Offer one retry; if it fails again, go to section 7. Never block on a bad file.
4. The step 6 tick rule does not change (facts saved, or `get_next_fact_task` says done). The product list never blocks the tick.
