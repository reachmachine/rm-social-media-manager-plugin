> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 12 — Capture: save the plan to the creator's Content Calendar

Once the **critic-passed** plan is delivered, offer to SAVE it to Reach Machine so it
lives in the creator's month-organised **Content Calendar** (Plan → Content Calendar),
and — with their permission — helps improve this planner. This is a **free, no-spend
write** (G62).

**🔴 HEADLESS RUNS (G208, `runner.py`) NEVER REACH THIS STEP** — `consent: true` on
`submit_content_plan` means "a human just said yes," and a headless run has no human
to ask. `submit_content_plan` is deliberately NOT in `runner.py`'s allow-list, so an
unattended run cannot call it at all — that is not a bug, it is the point: an
"explicit yes" a headless agent invents for itself would poison the exact dataset
(`content_plans`) a later QA/eval loop reads to judge plan quality against reality.
A headless run's deliverable is the in-chat/rendered plan only. If unattended saving
is ever wanted, it needs a real consent-provenance mechanism (recording WHO/WHAT
said yes, not just a boolean) — that is a product decision for the founder, not an
engineering default, and is not built here.

## 🛑 REVIEW GATE B — the creator reviews the PLAN before you offer the save (FRFRMU-879)

**Ask per `asking-rules.md`** — this gate and the save-consent ask below both follow the shared
asking contract.

**12.0.** Delivery is not the end of the conversation, and the save-consent ask below is NOT
a review — "want me to save it?" answers where the plan is stored, not whether the plan is
right. So, the moment the plan is delivered (path printed, dashboard opened): invite review,
in the founder's spirit — the point is to *share the mistake, find the gap, and fix it*:

> *"Before anything else — look it over. If any part reads wrong (a reel, the mix, a hook,
> the audience), say so and I'll fix that part. You won't lose the rest of the plan."*

Then **END YOUR TURN and wait.**

- **Silence is not approval.** No reply = the plan stays delivered-but-unreviewed and
  nothing else happens. Never treat "they didn't object" as "they approved".
- **Fix the part, keep the plan.** On a correction: change the named reels/decisions and
  their dependents, re-run `validate_content_plan` on the revised plan, and re-check only
  the Rules-Gate items the change touches (update the same `rules_gate` object — Step 11's
  3-round cap does not restart). Never rebuild the plan from scratch over one bad part.
- **Only after the creator has responded to this review ask** do you move to step 1 below
  and offer the Content-Calendar save. Their yes to SAVING is storage consent — it is never
  read as approval of content they did not review.
- Exists while plan quality is an unvalidated prediction — re-check after FRFRMU-880.
  (No headless carve-out needed: headless runs never reach Step 12 at all — see above.)

1. **ASK for consent — explicitly, and WAIT for a yes.** e.g. *"Want me to save this
   to your Content Calendar in Reach Machine? It'll be filed under [Month Year] and
   you can reopen it any time. Saving also lets Reach Machine review plan quality to
   improve the planner — your call."* Storing without asking is not allowed (the same
   discipline as confirm-before-spend, though nothing is spent here). A **"no" ends the
   step cleanly** — the plan is still delivered in-chat.

   **On a "no", mark the plan delivered — do not delete `planning_progress` (FRFRMU-981).**
   There is no `plan_id` to hang a run record on (see `playbook/step-12-after-the-save.md`
   for why that matters), so this was never a successful save, and the plan-lifecycle field
   must say so honestly rather than pretending nothing happened. Call `update_creator_brief`
   with key `planning_progress`, the same shape the checkpoints use, but
   `"status": "delivered"` and `"summary": "plan delivered in-chat, not saved"` — never
   delete the field here. This is deliberately different from a successful save (which
   deletes the field entirely — see `playbook/step-12-after-the-save.md`): a declined plan
   is DONE, not resumable, but a later session should still be told the plan existed and
   was handed over, not asked to "pick up" it as if it were still in progress.

**Re-saving a month that already has a calendar.** Before you build a fresh
plan for a month, call `get_calendar(month)` — if it comes back `found:
true`, this month already has a saved calendar and you are re-running it,
not starting over. Reuse the reel ids it hands you (never invent new ones
for reels that already exist), and never change a reel it marks locked
(already approved or published) — leave that reel exactly as it is and
build around it. When the creator asks you to move a reel to a different
day, write that change back unchanged, not reworded or "improved". Submit
with `base_version` set to the version `get_calendar` returned, so a save
that landed behind your back is caught instead of silently overwritten.
At Review Gate A (Step 7), show the **diff** against the existing calendar
— what changed, what stayed, what's new — never present a re-run as if it
were a brand-new plan the creator has to review from scratch.

1.5. **🔴 ALWAYS run the free `validate_content_plan` dry-run on the EXACT plan you are
   about to send, right before THIS call — every time, not only after a rejection
   (FRFRMU-1029).** **The requirement is tied to the save itself, never to "session"
   (FRFRMU-1318) — resuming from an earlier turn does NOT carry that turn's dry-run
   forward.** A save attempt with no dry-run run immediately before it — a resumed
   session included — is a playbook violation. Read every violation's `fix`
   ({field_path, expected, example}) and apply it — do not guess, and do not paste the raw validator JSON
   at the creator. Once it comes back with 0 blockers, tell the creator "checked: 0
   blockers" in one short line, then move to step 2. This closes the gap a 2026-09-06 QA run hit: three
   retry rounds (no receipt → thin receipt → provenance-split mismatch) that a single
   dry-run — read properly — would have caught in one pass.
   **If blockers are STILL there after Step 11's 3-round cap, do NOT save yet — read
   `playbook/step-12-blockers-remain.md` first (FRFRMU-1104).** The save is still allowed;
   what changes is that the affected gates must be reported `fail`, the creator must be told
   the number in plain words BEFORE consent, the title must not say final/verified/clean, and
   the reply's `honesty` block must be read back to them.

2. **On an explicit yes, call `submit_content_plan`** with:
   - **`plan`** — the **STRUCTURED** plan you just built (a JSON object, NOT the prose /
     rendered version):
     ```
     { meta: { language: "<the plan's language, e.g. 'en' or 'hi-en'>",         ← MACHINE-READABLE
               subject_handle: "<@handle this plan is FOR>",
               subject_type: "self" | "client" },
       section_00, decision_log,
       funnel: { mix: "<plain sentence>", reasoning: "…",
                 counts: { reach: <int>, nurture: <int>, activation: <int> } },   ← MACHINE-READABLE
       prerequisites: [ { what: "dm_automation" | "lead_magnet", by_week: <int>, why: "..." } ],  ← MACHINE-READABLE
       pillars: [ { name, pct: <number>, why } ],                                ← MACHINE-READABLE
       series:  [ { name, cadence, pattern } ],                                  ← MACHINE-READABLE
       anchors: [ { id, name, type: "launch"|"event"|"seasonal"|"holiday",       ← MACHINE-READABLE
                    date: "YYYY-MM-DD",
                    counts: { reach: <int>, nurture: <int>, activation: <int> } } ],
       reels: [ { id, title, format, intent, niche, angle, structure, topic_idea,   ← MACHINE-READABLE
                  funnel_role, audience_segment,
                  emotion, hook: {spoken, on_screen, visual, sound}, retention, cta,
                  cta_type,                                                      ← MACHINE-READABLE
                  date: "YYYY-MM-DD", time: "HH:MM", timezone: "<IANA zone>",     ← MACHINE-READABLE
                  pillar, series, moment_tie,                                     ← MACHINE-READABLE
                  week: <int>, depends_on: "dm_automation" | "lead_magnet",        ← MACHINE-READABLE
                  effort, priority,
                  provenance: "data_driven" | "data_inferred" | "judgment",         ← MACHINE-READABLE
                  receipt: { source_handle, source_url, n: <int|null>,              ← STRUCTURED, not a
                             median: <number|null>, reliability, tag, note },         sentence
                  discovery: { keywords: [str], tags: [{tag, role}] }, caption, hashtags: […], reasoning: {receipts, expected_outcome, goal_served}, needs_disclaimer },  ← MACHINE-READABLE (FRFRMU-1551/1547)
                … ],
       cadence: { per_week: <int>, weeks: <int> },                              ← MACHINE-READABLE
       kpis, captions_seo,
       distribution: { posting_time: { status, tool, scope, timezone,         ← MACHINE-READABLE
                                        quoted: [...], caveat } },              (§K, FRFRMU-1539)
       glossary: [ { term, field, plain, source, example_url } ],   ← MACHINE-READABLE (FRFRMU-1551, TEMPLATE.md D7)
       receipts_summary: { …, provenance_split: { data_driven, data_inferred, judgment } } }  ← COUNTS
     ```
     **Cross-account receipts (G336).** If a reel's pattern is real across MULTIPLE tracked
     accounts (e.g. a hook style with a strong median across 20 reels from several creators — not
     one), write `receipt: { source_handles: ["@a", "@b", "@c"], n, median, ... }` instead of a
     single `source_handle`. Each handle in the list counts toward the ≥3-source-diversity
     requirement, and `verify_receipts` pools the real stored views across every listed handle
     before comparing your claimed `n`/`median`. Use `source_handle` OR `source_handles`, never
     both on the same receipt.
     **Why the machine-readable fields matter (G118).** `validate_content_plan` (Step 11) and the
     save-time check read these fields to enforce the countable guarantees — effort ≤ capacity, ≥3
     distinct `receipt.source_handle`, a DATA-DRIVEN reel must carry `receipt.n ≥ 5` + a `median`, the
     `funnel.counts` the calendar actually delivers, the honest `provenance_split`. **Put the numbers in the STRUCTURED fields, not only in the prose** — a receipt written as a sentence can't be checked,
     so a `receipt` object with `n`/`median` null (and the human line in `receipt.note`) is how you say
     "no data receipt" honestly. Keep the human-readable prose too (the dashboard uses it); the
     structured fields sit ALONGSIDE it. **Include the `decision_log` (TEMPLATE E3)** so the reasoning is written back and QA-verifiable later.
     **`caption`/`hashtags`/`reasoning`/`needs_disclaimer` (FRFRMU-1547)** come from the step-08 recipes and proof-bank's `regulated_disclaimer_required` flag — check against `plan_field_manifest.json`.
     **The Phase 2/3 checks (G118) read these fields — never leave them out:**
     - `meta.language` — the language the hooks/captions are actually written in (Step 3 item 3).
       Checked by `language_set`; missing it means nothing that depends on language can be verified.
     - `meta.subject_handle` + `meta.subject_type` (`self` = the creator's own account, `client` = an
       agency planning for someone else) — who the plan is FOR. Checked by `subject_check`, which
       also compares `subject_type` against `inputs.business_context.subject_type`, and `subject_handle`
       against `inputs.business_context.subject_handle` (G223), when both sides are set (add both fields
       to `inputs` — see below) to catch a plan that drifted onto the wrong account or the wrong client's
       handle.
     - `reel.structure` — the narrative structure this reel uses (the same value you read from
       `get_content_structures` / the breakdown's `structure_type` dimension, e.g. `"listicle"`,
       `"before_after"`, `"pov"`). Checked by `variety`, which warns if too many reels repeat one value.
     - `reel.topic_idea` — the specific idea this reel covers, in a few words (not the niche — the
       actual angle, e.g. `"why most X fail in month 1"`). Checked by `self_cannibalization`, which
       flags two reels chasing the same idea so they don't compete with each other.
     - `reel.cta_type` — **set on EVERY reel now (FRFRMU-1544, founder decision 2026-09-15):** one of
       `get_cta_library`'s 11 values (`no_cta, follow, save, share, comment_open, comment_keyword,
       dm_open, link_in_bio, visit_site, attend_event, watch_more`), chosen per `step-08-cta-recipe.md`
       CT.1's funnel-role table. Checked for VARIETY by `cta_type_variety` (>= 3 distinct across the
       plan). **Separately,** `activation_needs_plumbing` still reads this SAME field for its own
       plumbing-promise check (`"keyword_dm"`/`"lead_magnet"` — a pre-1544 sub-vocabulary, see
       `prompts/COMMS.md` FRFRMU-1544 for a naming gap flagged there, not fixed here).
     - `plan.prerequisites`, `reel.week`, `reel.depends_on` (G129) — if a reel needs something built
       first (e.g. a keyword-DM automation for an activation CTA), **schedule the prerequisite and give
       the reel a later week — do NOT downgrade the CTA to something weaker.** Example: if week-4 reels
       need the dm_automation, add `prerequisites: [{what: "dm_automation", by_week: 1, why: "..."}]`
       and mark those reels `week: 4, depends_on: "dm_automation"`. The validator downgrades to a warn
       (gated, do not post before the prerequisite is tested) instead of blocking. Without a prerequisite,
       or if the prerequisite is scheduled the same week or later than the reel, the validator blocks —
       a plan that cannot be delivered in order is not a plan.
     - `reel.date` + `reel.pillar` + `reel.series` + `reel.moment_tie` — the schedule the calendar
       table already shows, written as real fields so the machine can count them. `date` is the exact
       day (`YYYY-MM-DD`); `time` is the posting time (`HH:MM`) and always travels with the
       `timezone` it is written in — the time is the evidence-backed default, freely movable, and is
       never checked. `pillar` is the content pillar the slot belongs to, `series` the recurring
       series (leave it out if the slot isn't part of one), and `moment_tie` the `id` of the anchor
       in `plan.anchors` this slot builds toward. Declare `plan.pillars` (with each pillar's `pct`)
       and `plan.series` so there is something to count against. Checked by `cadence_by_date` (dated
       slots per week vs `cadence.per_week`), `pillar_mix_delivered` (slots per pillar vs the
       declared split) and `series_consistency` (a series should keep the same weekday — a note, not
       a blocker).
     - `plan.anchors` — the launches, events and seasonal moments this month is built around, taken
       from the creator's intake (`upcoming_moments`). An anchor week is allowed to break the
       declared funnel mix, but only OUT LOUD: give the anchor its own `counts`
       (`{reach, nurture, activation}`) saying what that week is meant to look like, and tie the
       week's slots to it with `moment_tie`. Checked by `anchor_exception` — a week that abandons the
       declared mix with no anchor to explain it **blocks**, and an anchor that declares a mix the
       week doesn't deliver blocks too. A normal week that stays close to the declared mix needs
       nothing.
     - `inputs.business_context.production_capability` — the formats the creator can actually shoot
       (e.g. `["talking_head", "screen_record"]`), from Step 1. Checked by `producible_format` against
       every `reel.format`; without it the check can't verify a reel isn't asking for a format the
       creator can't produce.
   - **`plan_month`** — the calendar month this plan is FOR, as **`YYYY-MM`** (e.g.
     `2026-08`). This is what files it under the right month — get it right.
   - **`title`** — a short human title, e.g. *"August 2026 — <the positioning angle>"*.
   - **`inputs`** — what it was built from, so a later review is diagnosable:
     `{ business_context: {stage, positioning, funnel_assets, goal, subject_type: "self" | "client",
     subject_handle: "<the confirmed per-workspace @handle from Step 1.6>",
     production_capability: [<string>],
     capacity: { reels_per_week: <int> }, requested_plan_size: <int>,
     target_audience_segment, false_beliefs}, data_signature: {analysed_reels_count, competitors_count,
     audience_segments, levers_used: [{lever, winner, median, n, reliability}]} }`.
     **`capacity.reels_per_week` and `requested_plan_size` must be integers** — the validator
     compares the plan's effort + size against them (G118).
     **`false_beliefs` (FRFRMU-1530) — pass the WHOLE card**, unchanged, whenever it exists (no key → leave it out); without it `check_all_three_doubts_covered` (backend) stays silently unable to check.
   - **`critic`** — the Step 11 result: `{verdict, changes: [...]}` (what the critic changed).
   - **`rules_gate`** — the Step 11 structured Rules-Gate record: `{checks: [{id, status, note,
     fix}], rounds, unresolved}`, one entry per gate you actually walked, ids exactly as in
     `RULES_GATE.md`. The server grades it and returns `rules_gate_summary` — read that reply: if it
     says `missing`, `incomplete`, `unevidenced` or `contradicted`, your record has a real problem
     and the plan's stored quality trail is weaker than it looks. **Do not invent entries to make
     the grade look better** — a fabricated `pass` is worse than an honest gap, and the
     `contradicted` grade is computed from the plan itself, so it cannot be talked around. (G650)
   - **`consent: true`** — ONLY because the human just said yes. Never hard-code it true
     without the ask. **Headless/unattended runs never call this tool at all** (see the
     Step 12 headless note below) — an "explicit yes" that never came from a person is
     not consent.
   - **`skill_version`** — read `${CLAUDE_SKILL_DIR}/VERSION` fresh and use its contents
     verbatim (G113 — do NOT hardcode a version string in your own memory; that file is
     the only source of truth, bumped every time this method changes).

3. **Confirm** to the creator: *"Saved to your Content Calendar under [Month Year] — open
   it any time under Plan → Content Calendar."*

   **If the reply's `honesty.data_request` is not null, relay its `message` too, in the same breath — this fires on ANY save, clean or not (FRFRMU-1545).** The niche's data was thin, so the server filed a free request on the business's own credits; don't let the creator learn this only from opening the plan later, e.g. *"...also, your niche was low on analysed data, so I asked our team to pull more — free, ready within [sla_business_days] days."* (Separate from `step-12-blockers-remain.md` rule 4, which fires only when blockers remain.)

   **If the save fails, try again before giving up (G250).** Before your first `submit_content_plan`
   call, make up a short unique `idempotency_key` for this plan — any random string is fine, e.g.
   `plan-2026-08-a7f3c1`. Send that same key on the first attempt and on every retry of that same
   plan. The server uses it to tell a retry apart from a new plan, so retrying cannot create a
   second copy: a repeat comes back with `already_saved: true` and the id of the plan it stored the
   first time. Treat that as success and stop retrying.

   How to retry:
   - **The call errored or timed out** — you don't know whether it landed. Send it again with the
     same `idempotency_key`. Try up to **three times in total**, and wait before each retry so a
     brief outage has time to clear: **wait about 2 seconds before the second attempt and about 5
     seconds before the third.** Stop as soon as one comes back `stored: true` (with or without
     `already_saved`).
   - **It returned `stored: false` with a reason** — read the reason. Missing consent or a rejected
     field is your input being wrong, and sending the identical call again will fail identically.
     Fix what the message names, then send it once more. Do not loop on a rejection.
   - **Write tools are not enabled on this connection** — that is not a transient failure and no
     number of retries will change it. Say so once and move on.

   **If it still hasn't saved after three tries, do not just move on — hand the work back.**
   Never fail the delivered plan over the save, but never let the customer discover the loss on
   their own either. Do all four of these, in this order:

   1. **Say plainly what happened and what it means for them**, in your own words, covering: the
      plan itself is fine, but it is NOT in their Reach Machine library, so it will not appear
      under Plan → Content Calendar. Do not say "saved" or imply it is recoverable from our side.
   2. **Write the complete plan to a file they can open**, using the same full format you used to
      deliver it in chat. Name it so it is obvious, e.g. `content-plan-<Month>-<Year>.md`, and
      tell them the filename **and its absolute path, on its own line** — the full path from the
      drive or root, not just the name (G370: a file they cannot find is a file they did not get).
      This is the step that means their work survives the conversation.
   3. **Give them the `idempotency_key` you used**, and tell them to keep it. Explain why in one
      sentence: if they ask you to save again later, reusing that key means a save that quietly
      succeeded the first time cannot turn into a second copy.
   4. **Offer the next step**: they can ask you to try saving again at any point in this
      conversation, and you will reuse the same key.

   If write tools are not enabled on this connection, skip step 3's promise about retrying — say
   the save is unavailable on this connection, and still do steps 1 and 2.

   **The same key-and-retry rule applies to `report_gap` and `record_content_plan_run`** — each gets
   its own key per logical save, and they report a repeat as `already_logged` / `already_recorded`.
   **`submit_analysis` is different and needs no key**: its save is already keyed to the reel, so a
   repeat is safe on its own and it tells you with `already_analyzed: true`.

4. **The plan is saved — now do the two write-backs. Load
   `playbook/step-12-after-the-save.md`.** Both need the save to have happened first:
   **record the run** (`record_content_plan_run`, so the plan carries a record of HOW it was
   built) and **write the topic ledger** (`update_creator_brief`, key `topic_history`, so
   next month's plan does not re-pitch this month's ideas). Neither is optional, neither
   spends credits, and both are easy to forget once the creator is happy.

**Privacy:** the plan is the creator's own content strategy — stored only on their
explicit yes, scoped to their workspace, used only to review/improve the planner. No
data beyond the plan + the inputs above. The `topic_history` ledger holds only the
topics the creator's own plan already covered — nothing new about them is collected.

---

*Companion: `SKILL.md` (invokes this method) and `runner.py` (runs it headless via
the Claude Agent SDK against the Reach Machine MCP). Product gaps this method works
around are logged in `marketing/engineering-gaps.md`.*

---

