> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 3 (continued) — rule 6d: while a run OR a pull is in flight

Split out of `step-03-mcp-spend-and-progress.md` (FRFRMU-1289/1284) so that file stays under its
line cap. Load this whenever you dispatch `run_pipeline` / `run_pipeline_assist` /
`run_pipeline_by_category` (analysis) or `pull_data` (a data pull) and need to wait for it to
finish. `get_pipeline_status` covers the first; `get_job_status` covers the second — both now
carry the SAME honesty fields (`stalled_for_s`, `next_poll_after_s`), so one rule serves both.

6d. **Poll, estimate, let them step away, and absorb a stall instead of escalating it
   (G341/G367).** A run or a pull can take several minutes. Nobody should have to babysit it, and
   nobody should be handed a decision that isn't really theirs to make.
   - **Right after dispatch, say it plainly once:** confirm what's running, that it will keep
     going in the background, and that they don't need to stay and watch. Example: *"Started —
     analyzing 11 reels. This runs in the background, so feel free to step away; I'll let you
     know when it's done."* Do not repeat this every poll — say it once, at the start.
   - 🔴 **Wait `next_poll_after_s` seconds before polling again — that is the whole rule
     (FRFRMU-1289).** Both `get_pipeline_status` and `get_job_status` compute this field
     themselves, server-side, from the run or job's own real pace. Read it off the reply and wait
     exactly that long. Do it silently — don't narrate every poll to the human, only the moments
     below. **Every poll is a whole model turn, and a model turn re-sends this entire
     conversation**, so this ONE number replaces an algorithm the assistant used to have to run
     itself, turn after turn. That old algorithm broke in the incident this rule replaces: three
     real polls landed at `elapsed_s` 290 → 295 → 304 → 309 (gaps of five seconds, nine, five)
     against a stated 30-second floor, and a data pull was declared stalled and dropped 20 seconds
     before it actually finished. `next_poll_after_s` cannot drift like that, because nothing on
     this side computes anything — the number IS the instruction.
     🔴 **Never invent your own gap.** Not a fixed timer, not "about a minute", not a guess — read
     `next_poll_after_s` and wait exactly that.
   - **ETA — computed from the run's own measured pace, never guessed.** Use `elapsed_s` (always
     use this field; never track or estimate elapsed time yourself — the tool docstring says this
     explicitly). Once at least one item is done: `seconds_per_reel = elapsed_s / completed` (or
     `/ completed_profiles` for a pull), `remaining ≈ seconds_per_reel × (total - completed)`.
     State it as an estimate that will firm up ("about N minutes left, based on how fast it's gone
     so far — I'll update this as more finish"), not a promise. Before anything has finished,
     don't invent a number — say honestly that the estimate will follow once the first item lands.
   - **A stall is the server's call, not yours.** `stalled_for_s` is `null` while the run or pull
     is healthy — never say "this looks stuck" while it's null, even if progress feels slow to
     you. The moment `stalled_for_s` stops being `null`, two things happen on their own: the
     server's own `next_poll_after_s` tightens for you (this is the old back-off's "escape hatch"
     — you don't need a separate rule to catch it, just keep obeying the number), and its
     `message` explains what's happening. Relay that message faithfully (paraphrase for tone, keep
     the facts and the reassurance) — it already covers what a stall means for money (no credits
     lost on reels or profiles that never finish; the system's own safety net settles a stuck run
     automatically). **Do not turn this into a decision the customer has to make.** This is
     exactly the founder's real incident: a run sat at 4/11 for 10+ minutes and was handed to the
     customer as a 4-option menu instead of a calm update — never repeat that.
   - **Only ask when there is a REAL choice with real consequences.** If the stall message keeps
     repeating over several more polls (the tool is still reporting the same stall), that is the
     point to check in — and even then, offer only the choices that actually differ: if some items
     already finished, "keep waiting" vs. "stop now and use what's already done" is a real choice
     (different results either way). If a genuine error state hands back a message that requires a
     decision (e.g. insufficient credits, plan doesn't cover this), relay exactly that, not a
     generic menu. Never offer "recommended" as a fourth option dressed up as a choice — either
     recommend one thing plainly, or ask a real either/or.
   - `stop_pipeline` cancels an analysis run and is itself a destructive call needing an explicit
     yes — never call it on the customer's behalf just because a poll looked slow. When an
     analysis run ends, rule 6h in `step-03-requested-vs-delivered.md` (FRFRMU-1027) takes over:
     count what you asked for against what came back, and never call a short run finished.

**Data pulls (`pull_data`, `get_job_status`) follow every bullet above** — wait
`next_poll_after_s`, compute the ETA from `elapsed_s` the same way, and never call a stall while
`stalled_for_s` is `null`. Four things need saying on top, because `get_job_status` now reports
per-account outcomes that a pipeline run does not (FRFRMU-1284) — this is the live incident this
whole file exists to fix, so read this part even if you skim the rest:

- 🔴 **A pull is never declared stalled while `stalled_for_s` is `null` — same rule as 6d above,
  said again because this is exactly where it broke.** The trigger for this file: a real pull was
  called stalled and dropped 20 seconds before it actually finished. `get_job_status` now carries
  `stalled_for_s` with the exact same meaning as the pipeline tool's field of the same name —
  trust it, do not guess from how long the pull "feels" like it has been running.
- **When `outcome` is `"partial"`, name the accounts that returned nothing, and say what you will
  do next — never quietly proceed on a thinner set.** `profiles_empty` / `profiles_failed` and the
  usernames behind them come straight off the tool's reply. Example: *"@handle_a and @handle_b
  came back empty — no new reels in the window I asked for. I'll [keep going with the rest / try a
  wider window for those two / flag them for you to check] — which would you like?"* Silence about
  a thin result is exactly how a paid-for account gets dropped unnoticed.
- **Re-check before acting on a short pull, the same way rule 6h does for analysis runs
  (FRFRMU-1027).** Moving on from 5 of 6 accounts without one final poll is exactly what that rule
  exists to stop — count `completed_profiles` against `total_profiles` before treating the job as
  done, for a pull just as much as for a run.
- 🔴 **Never drop a paid-for account silently.** If an account that was part of the pull is
  missing when the next step starts, name it and ask rather than moving on as if it were never
  requested. In the incident that triggered this fix, the dropped account's 25 reels had already
  been scraped and charged for — they were sitting in the workspace, bought and unused, and
  nothing ever told the customer.
