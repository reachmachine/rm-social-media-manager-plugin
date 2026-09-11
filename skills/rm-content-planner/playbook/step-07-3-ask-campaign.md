> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

> **Load this at Step 7**, after the promise (`step-07-2-offer-stack.md` Part B) and the ask
> engine (Step 3 audience-ask variant). **Entry rule: the creator wants to launch/validate an
> offer, OR wants the ask alone and has an audience.** Otherwise skip in one line.

## Step 7.9 — Beta cohort + ask campaign (p22)

**Ask per `asking-rules.md`.**

Find a hot market, ask what they want, give it to them — the offer is defined from demand,
not a guess. **This step ORCHESTRATES existing mechanisms — it builds none of them.**

> **Dependency note (FRFRMU-1078 lane, 2026-09-07):** this step's question ideally comes from
> the audience-ask engine's Tier-1 drafts, when that step has run. **Until then**, draw the
> ONE question directly from the intake `audience_questions` field and any pasted DMs — never
> invent one. Say so plainly if the Tier-1 drafts aren't available yet.

**Eight moves, orchestrating what already exists:**

1. **Who/What lock (agent drafts from the intake positioning, creator confirms):** *"I am
   going to teach [avatar] how to [WHAT]."* Title = the promise (`promise.chosen`) in "How to
   [result] Without [fear]" form, one curiosity framing.
2. **The one question:** *"What's your #1 question about [WHAT]?"* — in the audience's voice.
   Never a survey; never selling during the ask.
3. **Distribution plan — creator approves BEFORE anything posts (public gate):** reels with
   reply-bait CTA (`step-08-cta-recipe.md`'s existing step-down), story stickers, a community
   post ONLY after value posts exist (`value_first_post_ids` required), a landing-page variant
   for accounts with no audience. "Free access when it's done" is recorded as an obligation.
4. **Collect honestly:** answers pasted by the creator. The count is reported AS-IS — 30 is
   30, never rounded to "~100".
5. **Cluster (agent-fills, shown):** 8-10 core questions with counts and example quotes. Each
   cluster also becomes an `audience_questions` entry and a topic in the demand signal.
6. **Curriculum (agent drafts, creator approves):** modules 1:1 to clusters — a module with no
   cluster (`cluster_id`) is flagged "supply-pushing" and dropped or justified.
7. **Beta as a calendar anchor:** a 6-week beta is a `plan.anchors` entry (G707) — a week-3
   check reel/story, a week-6 proof ask.
8. **Proof harvest plan:** who to ask, when (week 6), format. Nothing is claimed as proof
   until the beta actually produced it (Gate 1, S14).

**Guardrails:** never sell during the ask — ask reels carry no offer/price. Join, give, THEN
ask on community channels. Real n only — a conclusion citing a count must match
`responses.count` exactly, never rounded. No fabricated testimonials. The plugin drafts and
schedules; the creator posts, collects and pastes — the plugin never claims to have collected
answers (no DM ingestion, G904).

**Countable rule:** any reel/caption citing a response count must match `responses.count`
exactly. Every curriculum module needs a `cluster_id`. A community distribution entry needs
`value_first_post_ids`.
