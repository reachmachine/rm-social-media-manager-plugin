> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

> **Load now:** `${CLAUDE_SKILL_DIR}/RULES_GATE.md` **and** `${CLAUDE_SKILL_DIR}/rules/`
> (`copywriting.md`, `funnel.md`, `authority.md`, `offer.md`, `traffic.md`) — the gate and the
> book-derived principles it is built on. They are NOT loaded earlier in the run; this is the
> step that needs them.

## Step 11 — Rules Gate + Critic loop (MANDATORY — never ship the first draft)

The first draft is **not** the deliverable. Before you hand over the plan:

0. **Call `validate_content_plan` first (free, read-only) — G118, 17 checks.** Pass the STRUCTURED
   `plan` + `inputs` you built. It runs every deterministic, countable check the backend ships (the
   tool's own `summary.checks_run` always tells you the live count — trust that over this list if
   they ever disagree — **and if it DOES disagree, your cached copy of this PLAYBOOK is stale (G113):
   say so plainly to the user and `report_gap` it — don't silently keep using the number below**):
   - **Phase 1 (7):** `effort_within_capacity` · `reel_completeness` (every required field, including
     all 4 hook layers) · `provenance_integrity` (a DATA-DRIVEN reel needs `receipt.n≥5` + a median) ·
     `provenance_split_honest` · `min_source_diversity` (≥3 source accounts) · `funnel_mix_delivered` ·
     `plan_size_honesty`.
   - **Phase 2 (4):** `no_banned_tags` · `activation_needs_plumbing` (a `keyword_dm`/`lead_magnet`
     `cta_type` blocks if the lead magnet + DM automation aren't confirmed built AND tested, whatever
     the stage; once they are, a cold-start account only gets a warn about the reach cost) ·
     `language_set` (needs `meta.language`) · `no_unflagged_placeholder` (shipped 2026-07-27 — every
     invented/placeholder reel from Step 8's HARD GUARD must carry `needs_real_content: true`, or this
     blocks).
   - **Phase 3 (4):** `variety` (hook/structure/angle shouldn't repeat past ~60% of the plan) ·
     `self_cannibalization` (two reels shouldn't chase the same `topic_idea`) · `producible_format` ·
     `subject_check` (needs `meta.subject_handle` / `meta.subject_type`).
   - **Intake (2, G225):** `intake_completeness` (warns if `inputs.business_context.
     intake_completeness.score` is below the floor — a thin intake) · `assumptions_disclosed` (warns
     if the intake recorded assumptions but the plan doesn't list them in `section_00.assumptions`).
   **Fix every `blocker` it returns and re-validate until `ok: true`.** Warnings
   are surfaced to you + the creator but don't block. This tool checks the *countable* things so the
   gate + critic below can focus on the *judgment* things (is the hook strong? is a reel a near-clone
   in spirit?). If the tool isn't available on this connection, walk those same checks by hand.
   **G207 — `verify_receipts: true`.** The 17 checks above are arithmetic on whatever the plan
   self-reports; they cannot tell a real receipt from an invented one (confirmed: a plan with 3
   fabricated receipts passed all 17 with `ok: true`). Pass `verify_receipts: true` whenever you are
   reviewing/finishing a plan you did NOT personally pull every receipt for THIS run (e.g. resuming a
   plan from an earlier session, or checking someone else's draft) — it cross-checks each DATA-DRIVEN
   receipt's `source_handle`/`n`/`median` against this workspace's own tracked-competitor data. A
   receipt that fails this is fabricated or wrong; fix it or downgrade the reel to JUDGMENT.

1. **Run the draft through `RULES_GATE.md` yourself first.** It is a universal, book-derived
   checklist (built from the generic principles in `rules/` — copywriting, funnel, authority, offer,
   traffic — with **no business's private strategy in it**). Walk all eight gates:
   (1) voice & compliance — no guaranteed-result/income claims, no fake urgency, hype is optional not
   forced; (2) structure — hook-story-offer, one job per reel, an origin reel, objections handled;
   (3) retention on every reel; (4) benchmark-never-copy (kill re-skins); (5) stage-appropriate CTA +
   value-ladder; (6) **STRATEGY ADHERENCE — does the Part C calendar actually deliver the Part A
   strategy? count the funnel mix, the pillar %, the audience fit, the goal fit**; (7) data integrity
   (median not mean, honest provenance); (8) **deliverable feasibility & variety — each week's effort
   fits capacity, plan-size is honest, activation CTAs have plumbing, CTAs/hooks vary, ≥3 source
   accounts, audience's language**. Fix every fail, then re-walk it.
1b. **Write down what each gate found — as DATA, not a sentence (G650).** As you walk the eight
    gates, build this object and keep it updated through every round:

    ```
    rules_gate = {
      "checks": [
        {"id": "gate_1_voice_compliance",
         "status": "pass" | "fail" | "not_applicable",
         "note": "one line naming what you ACTUALLY checked — the reels, the counts, the numbers",
         "fix":  "what you changed — REQUIRED when status is 'fail'"},
        {"id": "gate_2_structure",           "status": …, "note": …, "fix": …},
        {"id": "gate_3_retention",           "status": …, "note": …, "fix": …},
        {"id": "gate_4_anti_mimicry",        "status": …, "note": …, "fix": …},
        {"id": "gate_5_stage_cta_funnel",    "status": …, "note": …, "fix": …},
        {"id": "gate_6_strategy_adherence",  "status": …, "note": …, "fix": …},
        {"id": "gate_7_data_integrity",      "status": …, "note": …, "fix": …},
        {"id": "gate_8_feasibility_variety", "status": …, "note": …, "fix": …}
      ],
      "rounds": <how many gate+critic rounds you ran>,
      "unresolved": ["<anything still open after the 3-round cap>"]
    }
    ```

    - **Report the FINAL state after your fixes.** A gate that caught something and you fixed it
      stays `"fail"` with the `fix` filled in — that is the record of real work. Flipping it to
      `"pass"` because you fixed it erases the only evidence the gate did anything.
    - **`"not_applicable"` is a legitimate answer** (e.g. Gate 5's lead-magnet items when the plan
      has no activation reels) — but say why in the `note`.
    - **Never report a gate you did not walk.** Leave it out. The server records a gate with no
      entry as *missing*, which is honest. A `"pass"` you did not earn is not: the server
      cross-checks every `"pass"` against the deterministic validator's blockers, so claiming
      Gate 8 passed while `min_source_diversity` blocked is stored as a **contradiction** against
      this plan.
    - **A gate with automatic coverage is decided by the DRY-RUN, not by you (FRFRMU-1104).**
      Gates 1, 2, 5, 6, 7 and 8 each have deterministic checks behind them (the registry table in
      `RULES_GATE_REGISTRY.md` says which). If `validate_content_plan` returned a blocker under one
      of a gate's checks and it is **still there**, that gate is `"fail"` — you may not write
      `"pass"`. The server records a `"pass"` over a live blocker as a contradiction, files a Skill
      QA report to the Reach Machine team, and it counts against the plan. If blockers are still
      open when you reach Step 12, read `playbook/step-12-blockers-remain.md` before you save.
    - **A note that says nothing is graded as nothing.** All eight `"pass"` with empty notes is
      recorded as `unevidenced` — the same shape as a gate that never ran.
    - Hand this object to Step 12 as `submit_content_plan`'s `rules_gate` argument. Keep the E2
      prose as the human summary **on top of** it, never instead of it.
2. **Pass it to a senior-SMM critic with fresh eyes — a genuinely separate context, every time
   (G224).** Spawn a **Task subagent**, given ONLY the draft plan + `RULES_GATE.md` — never the run
   history or reasoning that produced the draft. **There is no "clean-slate pass" option** — the same
   session re-reading its own output is not independent review, however careful it tries to be. Have
   the critic **re-run the same `RULES_GATE.md`** plus hunt for: mimicry, unrealistic benchmarks, a
   CTA whose plumbing is wrong, near-clones, a **judgment dressed up as data**, weak retention, a reel
   that won't survive the feed, or a calendar that drifts from its declared strategy.
   **Record the critic payload as `{verdict, rounds, changes, no_findings_note}`**: `changes` is the
   list of concrete edits the critic's feedback produced (may be empty). **If `changes` is empty,
   `no_findings_note` is REQUIRED** — one line naming what was actually checked (e.g. "checked all 8
   RULES_GATE items + mimicry + retention on every reel — no material issues"). A verdict with neither
   a change list nor a no-findings note is not a real review — it's a rubber stamp, and
   `submit_content_plan` will flag it as such (see below).
   **The critic re-runs the same eight gates, so fold its findings back into the SAME `rules_gate`
   object from 1b** — update the affected entries and bump `rounds`; never keep a second, separate
   list.
3. **Apply every valid recommendation** and re-draft. **A critic edit that changes a reel's
   `provenance` tag must recount `receipts_summary.provenance_split` in this same step, not
   later** (`rigor-rules.md` §I, FRFRMU-1318) — a downgraded tag with a stale split is exactly
   what `provenance_split_honest` blocks at save time.
4. **Repeat** until the gate is fully clean and the critic has no material objections left —
   **but cap the loop at 3 rounds.** If a real objection still stands after 3 rounds (the critic
   and the fix keep disagreeing, or a fix isn't possible with the data on hand), **stop looping.**
   Ship the best version, name the unresolved issue plainly in Part E2 ("what we couldn't fully
   resolve, and why"), and — if it's a product limitation — log it in `marketing/engineering-gaps.md`.
   A plan shipped with an honest, named limitation beats an endless loop or a hidden flaw.
   *(Cosmetic nitpicks that don't change the plan's quality are not a reason to keep looping — close them out.)*
5. **Ship only the passed (or capped-and-disclosed) version**, and state briefly *what the gate +
   critic changed*, plus any unresolved issue (Part E2).

**If a Task subagent genuinely cannot be spawned** (e.g. a headless run with no subagent support —
this skill's `allowed-tools:` grants `Agent` and `Task` since FRFRMU-618, so a missing permission is
no longer the reason),
do not substitute a clean-slate self-read and call it independent review (G224) — that is the exact
loophole step 2 closes. Instead, name that limitation plainly in Part E2 ("no independent critic pass —
subagent unavailable this run") and submit the plan without a `critic` payload at all — `submit_content_plan`
will then honestly record `critic_trace: "missing"` rather than a false "reviewed" signal. (Sending an
empty or note-less `critic` object instead would record `"unverifiable"`, not `"missing"` — either
value is an honest "not reviewed" signal, but only omitting `critic` entirely produces "missing".)

This is the exact loop that turned the first attempt (5/10 — big-creator tactics copied
onto a cold account) into a real plan. Skipping it is how you ship confident mimicry.

---

