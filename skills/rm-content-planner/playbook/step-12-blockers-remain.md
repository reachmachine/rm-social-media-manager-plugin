> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

## Step 12.5 — When blockers are STILL there after the last round (FRFRMU-1104)

Step 12 §1.5 tells you what to do when the dry-run comes back with **0 blockers**. This file is
the other branch, and it was missing. Step 11 caps the fix loop at 3 rounds and says ship
"capped-and-disclosed" — but never said what "disclosed" actually looks like.

**What went wrong without this rule (real, prod, 2026-09-06).** A plan was saved three times in
one day. Every time, 19 blocking problems were still open. Every time, the Rules Gate record said
all eight gates passed. The third save was titled *"September 2026 — Agent Build Log restart cycle
(final)"*. The creator was told "Saved to your Content Calendar" and nothing else. Nobody at Reach
Machine heard about it until a QA pass found it two days later.

The save itself is fine — the founder's decision (2026-09-04, restated 2026-09-08) is that a plan
with problems can be saved so it can be QA'd. **What is not fine is describing it as finished.**

### The five rules

1. **Report every affected gate as `fail`.** For a gate with automatic coverage — 1, 2, 5, 6, 7, 8
   — your `status` is decided by the dry-run, not by you. If `validate_content_plan` returned a
   blocker under one of that gate's checks and it is still there, the gate is `"fail"`.
   You may not write `"pass"`. List each unresolved item in `rules_gate.unresolved`.
   The server records a `"pass"` written over a live blocker as a **contradiction**, files a Skill
   QA report to the Reach Machine team, and it counts against the plan. You gain nothing.

2. **Tell the creator in plain words BEFORE asking for save consent.** Not after. Say the number
   and what it is: *"I could not clear 13 issues — each of these eight reels needs the template id
   and account spread behind its hook. They will be listed under the plan."* A creator agreeing to
   save must know what they are agreeing to save.

3. **The title must not claim the plan is finished or checked.** Not `final`, `verified`, `clean`,
   `approved`, or `corrected`. "September 2026 — Agent Build Log restart cycle" is the right title
   for a plan with open issues. The status is shown next to the title everywhere, but the title is
   what a person skims first.

4. **After the save, read the reply's `honesty` block back to the creator.** The reply carries
   `honesty = {clean, blockers, gate_trace, headline, qa_report_id}`, plus `data_request` when
   the niche's data was too thin (FRFRMU-1545, not null-checked by this rule — see
   `step-12-capture.md` step 3 for that one, since it fires on every save, not only here). If
   `clean` is `false`, you may not summarise the save as "Saved" — say what `headline` says. Read
   `headline` and `effective_passed`, never `passed`: `passed` is only what you claimed,
   `effective_passed` is what survived the automatic checks.

5. **If a validator message makes no sense to you, `report_gap` it.** A message you cannot act on
   is our bug, not your failure — for example *"needs n≥5 and a median; got n=45, median=29464"*,
   where 45 is clearly above 5. File it with `type: "skill_qa"`, put the exact message in
   `evidence`, and say what you could not work out. Three retry rounds were burned on exactly that
   message before anyone reported it.

### What the server does on its own

Every save that still has blockers, or whose gate record contradicts the checks, raises a **Skill
QA report** for the Reach Machine team automatically — you do not have to file it, and you cannot
prevent it. Three saves of the same month in one day become ONE report with three entries. The
reply's `qa_report_id` is that report. This exists so the underlying cause gets fixed, not to catch
you out.
