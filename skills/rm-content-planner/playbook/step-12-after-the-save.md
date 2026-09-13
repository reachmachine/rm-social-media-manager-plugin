> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

> **Load this the moment `submit_content_plan` comes back `stored: true`**, straight after
> `playbook/step-12-capture.md`. Two write-backs live here and both need the save to have
> happened first. They are in their own file because they are the easiest part of the whole
> method to forget: the plan is delivered, the creator is happy, and the run ends — with no
> record of how it was built and nothing for next month's plan to read.

## Step 12 (after the save) — the two write-backs that make the NEXT run better

**Ask per `asking-rules.md`.**

Neither of these is for the creator. One is the build trail a reviewer reads months later; the
other is what stops next month's plan repeating this month's ideas. Both are free, neither spends
credits, and both ride the consent the creator just gave.

---

### 1. 🔴 RECORD THE RUN — call `record_content_plan_run`

**This is not optional and it is the step most likely to be forgotten.** The moment
`submit_content_plan` comes back `stored: true`, call it. Until it is called the plan has no
record of HOW it was built — so nobody, including you next month, can answer *"why does this plan
say this?"*.

**It must come AFTER the save,** because it needs the `plan_id` that `submit_content_plan`
returned. There is no way to record a run for a plan that was never stored: **if the creator said
no to saving, there is no run record**, and that is a real gap in what we can review later, not
something to work around by inventing an id.

Send:

- **`plan_id`** — from the `submit_content_plan` reply.
- **`skill_version`** — read `${CLAUDE_SKILL_DIR}/VERSION` fresh, exactly as the save does
  (G113 — that file is the only source of truth, never a version string from memory).
- **`sources_considered`** — every account you looked at while building this plan, whether or not
  it made the cut: `{handle, kept: true|false, reason}`. **The ones you DROPPED matter most.** A
  reviewer reading *"we looked at @x and left it out because its audience is wrong"* learns
  something a list of survivors cannot tell them.
- **`tool_calls`** — **every Reach Machine DATA tool you called this session**, each with a
  one-line plain-English summary of what it returned. **List them all, not only the ones you
  ended up quoting.** The server keeps its own record of the calls it saw and compares it against
  your list, so a call you leave out comes back graded `underreported`. Leave OUT the saving
  tools — `submit_content_plan`, this tool itself, profile and brief updates. They are plumbing,
  not data.
- **`validation`** — the `validate_content_plan` output from Step 11.0, as it came back.
- **`idempotency_key`** — a fresh unique string for THIS run. Not the plan's save key: a
  genuinely new run of the same plan is a new record, on purpose.

**Never pad the tool list to make the grade look better.** The comparison is computed from what
the server actually saw, so an invented entry cannot be talked around — and an honest
`underreported` is worth more than a fabricated `complete`.

**If it fails, retry it the same way as the save** (the key-and-retry rule in
`playbook/step-12-capture.md` already covers this tool): up to three tries, waiting about 2
seconds then about 5, reusing the same key. A repeat comes back `already_recorded` — treat that as
success and stop. A rejection with a stated reason is your input being wrong, so fix what it names
and send it once more rather than looping. If write tools are not enabled on this connection, say
so once and move on. **Never fail the delivered plan over this record** — but do not silently skip
it either: if it could not be written after three tries, say so in one line, because the plan is
saved and its build trail is not.

**Then call `record_build_steps` (FRFRMU-1028) — the per-step trace behind THIS run, not a
summary.** `record_content_plan_run` above is the one-paragraph "what did the run use" record;
this is the finer-grained "which exact step decided which exact reel" chain a person can walk
back later ("why does R3 look this way?"). Send one `BuildStep` per meaningful move you made —
a data pull, a reel selection, an analysis batch, a strategy decision, the critic pass — each
with `seq` (order), `kind`, `inputs` (what you read and how fresh), `action` (plain-English),
`outputs.reel_uids` (which reel(s) it fed, when it fed any), and `provenance` (`data` /
`inferred` / `judgment` — a step that was pure judgment says so, never dressed up as data).
Batch every step from this run into ONE call with a fresh `idempotency_key`, same retry rule as
above. **Honest limit:** there is no frontend "How this was decided" panel yet — this write-back
makes the trace queryable (`get_build_trace`) today, but nobody sees it on the reel profile
until that UI ships. Do the write-back anyway: a trace nobody reads yet still beats no trace to
read once the panel lands.

---

### 2. Write the topic ledger, so next month's plan does not re-pitch this month's ideas

Call `update_creator_brief` with the key **`topic_history`** (`source: "derived"`). The shape is
canonical and defined ONCE, in `playbook/step-05-differentiate.md` §5.1a — read it there before
writing this key for the first time. In short: a **flat** list, newest cycle first, one entry per
topic (never grouped under a cycle), each carrying `{cycle, topic, series?, tier, source}`.

**Why this exists at all:** no Reach Machine tool can read a saved plan back, so without this
ledger the cooldown in Step 5.1 has nothing to read and the next plan can innocently repeat this
one. Writing it here costs nothing extra — `update_creator_brief` is already part of this run —
and it rides the same yes the creator just gave.

- **`tier` starts as `unknown` and is corrected later.** You did not measure these reels; you only
  planned them. Once this cycle has had time to show a result, **Step 5.1f** fills each one in from
  the creator's own analysed reels, or from what they tell you: `won`, `held`, `flopped` or
  `unknown` (FRFRMU-983).
- **Merge, never overwrite — then trim by CYCLE, keep 4.** Read the existing `topic_history` first
  (`get_creator_brief`), add this cycle's entries on top, and keep at most 4 distinct cycles:
  **max_cooldown_cycles (3) + 1 = 4** — one more than the longest cooldown Step 5.1c's dial 1 can
  stretch to, so a topic still serving a 3-cycle ban is never trimmed out from under its own
  evidence. A cycle with many topics still counts as ONE cycle toward the 4.
- **Only on a real save.** If the creator said no, or the save failed after three tries, do not
  write the ledger — a plan they never kept is not one they will remember getting, and Step 5
  falls back to asking them.
- **The same key-and-retry rule applies** as for the save itself.

**Privacy:** the `topic_history` ledger holds only the topics the creator's own plan already
covered — nothing new about them is collected, and it stays scoped to their workspace.

---

### 3. Write the test ledger (FRFRMU-1075) — this cycle's new bets, and last cycle's calls

Call `update_creator_brief` with the key **`test_ledger`** (`source: "derived"`). Same merge
rule as `topic_history` above: read the existing ledger first (`get_creator_brief`), then write
back the WHOLE updated `rows` list — never a partial diff.

- **This cycle's new bets** (designed in Step 7.4) get added as `status: "designed"` rows,
  exactly as written there — variable, control, challenger, metric, sample_floor, disproof.
- **Last cycle's rows that were just closed** (Step 7.4's Loop Gate review — `result` +
  `decision` filled in) get updated in place: `status` moves to `"called"`, and a `scale`
  decision's `promoted_to` is recorded.
- **A row with a result but no decision is never written this way** — that is the exact
  "testing theatre" shape the validator flags; decide before you save, not after.
- **Only on a real save**, same as `topic_history` — no save, no ledger write.
- **The same key-and-retry rule applies.**

**Honest limit:** losers go to `topic_history` today (this write-back). `hook_history`
(FRFRMU-1060) does not exist in code yet — once it ships, a killed `hook_template` bet's
write-back moves there instead. Until then, do not invent the collection or silently skip the
write-back; write to `topic_history` and say, if asked, that the hook-specific ledger is next.

---

**Conditional (p11, FRFRMU-1045) — the living false-belief map.** When `false_beliefs` exists
and the creator pasted new DMs/comments during this run, add them as new rows before the save
above completes; if a core belief stayed "unmoved" across real replies, re-open the core-three
pick (data over the existing map) and say so on record. No `false_beliefs` key → this paragraph
does nothing.

**Conditional (p12, FRFRMU-1046) — the stance red-team check.** When `movement` exists and this
plan carried ≥2 cause-themed or `rocks_at_enemy` slots, read the creator's own per-reel reach
(Step 1.6) and compare those slots to the account's baseline reach-per-follower. A dip on ONLY
the stance reels reads as likely algorithmic down-ranking, not audience rejection — say so on
record, and note it as a data point for the next intensity-dial conversation. No `movement` key
→ this paragraph does nothing.

### 4. 🔴 CLEAR THE RESUME POINTER — this plan is no longer unfinished (FRFRMU-981)

**This is the LAST write-back in this step, done only after all three write-backs above are
finished (or given up on, per their own retry rules) — never before them, and never in
their place.** `planning_progress` exists so Step 1 can offer to resume an UNFINISHED
plan. A plan that just saved is not unfinished any more, so leaving `planning_progress` in
place is a sticky note that never comes down: next session would offer to "pick up" a plan
that already shipped weeks ago.

Call `delete_creator_brief_field` with `key: "planning_progress"`.

**The field's shape, for reference (moved here from `PLAYBOOK.md` to keep the index small).**
`last_completed_step` is a step id, not necessarily an integer: plain `1`…`12` for a top-level
step, or a lettered/decimal sub-step like `"1.6b"` / `"3.7"` / `"12.5"` (FRFRMU-1311 widened
this from the old plain `<int>`) — so a skipped sub-step shows up instead of hiding inside
"Step 1 complete." `status` is one of `"in_progress"`, `"delivered"` or `"abandoned"`, never
left unset (FRFRMU-981): every checkpoint before this step writes `"in_progress"`; this step
is where a successful save clears the field entirely (above); `step-12-capture.md` covers the
declined-save `"delivered"` case, and `step-01-intake.md`'s resume bullet covers the
`"abandoned"` case for an old plan the creator chose not to resume.

**Why last, and why the order matters.** If `record_content_plan_run` or a ledger write
fails partway through, a resume pointer that still says "just saved, write-backs
pending" is real, useful state — clearing it first would erase that trail before the
write-backs it describes have actually happened. Clear it only once all three write-backs
above are done, so a genuinely failed save (`submit_content_plan` never returning `stored:
true`) never reaches this step at all and `planning_progress` is left exactly as it was —
the resume pointer for a plan that is still, honestly, in progress.

**The same key-and-retry rule applies as the other write-backs above.** If the delete
fails, say so once and move on — nothing is lost by leaving a now-stale field in place for
one more session; it does not cause a false resume offer, because Step 1's resume check
(`playbook/step-01-intake.md`) reads `updated_at` and treats anything over 14 days old as
nothing to resume regardless.

**Coordination note (FRFRMU-980): the draft plan is ALREADY gone by the time you reach this
step — nothing to do here.** `save_draft_plan`'s working copy lives in the `content_plans`
collection (not the Creator Brief), and `submit_content_plan` itself deletes the workspace's
live draft the instant the real save above succeeds — a hard, code-level supersede, not an
agent-instructed write-back like the two above. So by the time you load this file at all,
the draft is already superseded; there is no fourth write-back to call for it, and no
ordering to get wrong. Only `planning_progress` needs the explicit clear above.

### 4. The swipe-file winners feed (p28, FRFRMU-1066, conditional — this is the KPI review, not a write-back with an ordering rule)

**Only when this run is a KPI review of a PRIOR plan** (reading back reel verdicts, not a
fresh plan being saved) — a fresh save skips this in one line. For any reel with verdict
`won` (FRFRMU-1062): propose it as a `swipe` candidate with the agent's own read of WHY it
worked, `candidate_why` — the creator confirms or edits before `classic: true` is ever set.
**Views never set `classic` on their own; only a human confirmation does.** Also, once per
review, one occasional ask per FRFRMU-1051 (`deferred` allowed): *"Anything you saw this
month — an ad, an email, a post from any industry — that made you buy or stop scrolling?
Paste it and say why."* Save to the `swipe` brief key (`step-01-intake-fields-2.md`'s shape).

---
