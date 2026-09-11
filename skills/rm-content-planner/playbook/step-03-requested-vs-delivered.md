> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

# Step 3 (continued) — rule 6h: requested versus delivered (FRFRMU-1027)

**Why this rule exists.** On 2026-09-06 the founder said yes to 139 reels over one
evening. 58 were analysed. Nobody said the other 81 were missing — not the plugin,
not the tools — and the founder only found out by counting. The reels were not lost
mid-analysis: most were **never started**, because a batch can be refused at the door
and a refused batch leaves no record at all. Nothing anywhere compared "how many did
we ask for" with "how many came back".

That comparison is now your job, and it is not optional.

## 6h. Keep a running tally, and never call a short run finished

**Keep four numbers for the whole session, across every batch:**

| Number | Where it comes from |
|---|---|
| **Requested** | The `post_urls` you sent, added up over every dispatch. |
| **Delivered** | `succeeded` from `get_pipeline_status` on each finished run. |
| **Failed** | `failed_reels` from `get_pipeline_status` — each one carries a plain-English `reason`. |
| **Refused** | Any batch that came back as a refusal. Its message names the count. |

**After EVERY batch,** read `unanalyzed_count` from `get_pipeline_status`. If it is
above zero, the run is **not** finished. Say so in the same breath as the good news:

> "That batch: 6 of 8 analysed. 2 could not be downloaded — they may be private or
> removed."

Never say "done", "all analysed" or "that's complete" while `unanalyzed_count` is
above zero, no matter what the status word says.

**When the last batch ends, say ONE tally line before anything else:**

> "You approved 139 reels. 58 are analysed. 81 did not finish: 60 were never started
> because the service turned the batch away, and 21 could not be downloaded. Do you
> want me to try the 81 again? That would hold credits for 81 reels only."

Say this even when the shortfall is small. A one-reel gap stated plainly costs
nothing; a gap you skipped is the whole bug.

## What to do about each kind of miss

* **Refused batch (nothing was accepted).** The refusal message says how many reels
  were turned away and what to do:
  * *A run is already active* — poll `get_pipeline_status` on the run it names, once.
    When that run reports completed, partial or failed, send the same batch again.
  * *The analysis service is not responding* — this one does **not** get better by
    waiting, and the message says so. Do not retry it in a loop. Tell the customer
    plainly, add the count to your "refused" tally, and stop dispatching.
  Either way: **nothing was charged and nothing was analysed.** Never let a refused
  batch sit in your notes as a batch that ran.

* **Reels that failed.** Read `retry_hint` and follow it — it already knows whether
  asking again can work.
  * When it says asking again will not help (a private or removed post), do **not**
    offer a retry. Say the posts cannot be reached and offer to pick different reels.
  * When it offers a retry, offer it to the customer with the credit cost for the
    missing reels only — never for the whole original batch.

* **Reels still running.** Not a miss yet. Keep polling (rule 6d).

## Two things that are never allowed

1. **Never invent a reason.** Use the `reason` text from `failed_reels` as written.
   Do not guess at causes, do not mention machines, queues, downloads tiers or error
   codes — none of that is yours to explain and most of it would be wrong.
2. **Never quietly reduce the plan's basis.** If you asked for 139 reels and built the
   plan from 58, say the plan rests on 58 before you present it, and check the
   sufficiency table (`step-03-mcp-sufficiency.md`, rule 2a) against **58**, not 139.
   A plan built on 42% of the data it was scoped for is a different plan.
