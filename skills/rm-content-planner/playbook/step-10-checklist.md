> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 10 — Run checklist

- [ ] Stage + positioning + first-party proof + assets + capacity captured (Step 1)
- [ ] **Creator Brief loaded first (`get_creator_brief`); only missing/stale fields asked; intake saved back with provenance (`update_creator_brief`)** (Step 1, G100)
- [ ] **Intake run as a conversation (1–2 Qs at a time); ICP DERIVED, goal RECOMMENDED, funnel advised — not offloaded to the user** (Step 1, G100)
- [ ] **Stated profile CROSS-CHECKED against actual data; any mismatch surfaced + resolved** (Step 1, G100)
- [ ] **Month's TOF/MOF/BOF funnel ratio set explicitly, data-driven + goal-conditioned (not mirrored from competitors)** (Step 8, G100)
- [ ] **Positioning gate passed** — either captured and saved via
      `update_business_profile`, or the plan is stamped "GENERIC — positioning
      not provided" at the top (Step 1)
- [ ] Workspace + creator subset + coverage OK; viral tier analysed if needed (Step 3)
- [ ] Normalised benchmark mode used, not raw per-account (Step 3.3)
- [ ] **Own-account baseline offered** only after competitors are analysed, and
      "self" account confirmed if the creator has one (Step 1.6)
- [ ] Every idea laddered to the positioning sentence + first-party proof (Step 5)
- [ ] Stage-appropriate CTAs (reply-bait vs keyword-DM) (Step 4)
- [ ] Retention line on every reel (Step 6)
- [ ] **Every reel tagged with a funnel role** (reach/nurture/activation) and
      the month's ONE conversion action stated (Step 8)
- [ ] **Analysis tag subsets chosen PER FUNNEL ROLE (union of rows, budgeted by mix %) — coverage checked per role** (Step 3, G328)
- [ ] **Patterns MATCHED split per funnel role; every reel's receipt cites its OWN role's tag slice** (Steps 7.3 + 8, G328)
- [ ] **Every reel tagged with an effort level and a priority rank** (Step 8)
- [ ] Section 00 + realistic cadence + KPIs + community routine present (Step 8)
- [ ] Benchmarks honest; no clones; no calendared news (Step 9)
- [ ] **Plan size asked + your recommendation given + what a bigger number costs said plainly (no currency, no invented credit number)** (Step 1)
- [ ] **Deep reads (`get_post_transcript`) done PER FUNNEL ROLE into one source table — ≤5 a role, ≤12 a plan, never one per calendar reel; if the ceiling was reached, the creator was told and nothing was silently downgraded** (Step 3 rule 5a)
- [ ] **Every item tagged data-driven / data-inferred / judgment, using the §I
      operational rule (median + n≥§B threshold, audience-matched)** (§I)
- [ ] **Output follows `TEMPLATE.md` (Parts A–E), same shape every run** (Step 8)
- [ ] **≥3 distinct source accounts behind the receipts; no single-source plan** (Step 5 / Gate 8)
- [ ] **Plan-size honest — if data supports fewer strong reels than asked, the creator was told + any stretch reel is labelled JUDGMENT, never padded as data** (Step 7 / Gate 8)
- [ ] **Decision log written (TEMPLATE E3) and included in the saved plan** (Step 12)
- [ ] **`RULES_GATE.md` walked (all 8 gates) — voice/compliance, structure, retention, benchmark-not-copy, CTA/funnel, STRATEGY ADHERENCE (calendar delivers the declared goal/mix/pillars/audience), data integrity, deliverable feasibility & variety (effort ≤ capacity · ≥3 sources · no clones · variety)** (Step 11)
- [ ] **Rules Gate + critic loop run; only the passed version shipped** (Step 11)
- [ ] **Offered to save the plan to the Content Calendar; stored ONLY on explicit consent** (Step 12)
- [ ] **Asked, SEPARATELY, whether to save the planning conversation (`save_planning_transcript`) — a distinct consent from the plan save, defaulting to NO** (Step 12, FRFRMU-1596)
- [ ] **Every slot carries its Reasoning block — receipts, a base rate (never a forecast), and the goal it serves** (Step 8, `playbook/step-08-reasoning-recipe.md`)
- [ ] **Cooldown checked against the last plans' topics; every repeat is a named series or a stated sequel** (Step 5.1)
- [ ] **Last cycle's still-`unknown` topic verdicts settled from real evidence, or honestly left `unknown`** (Step 5.1f)
- [ ] **Run recorded — `record_content_plan_run` called after the save, listing EVERY data tool this session used** (Step 12)

**If any box above cannot be honestly ticked, do NOT ship — go back and fix it, or state the limitation plainly in the plan (Part E) and to the creator. A checklist walked but not satisfied is worse than none.**

---

