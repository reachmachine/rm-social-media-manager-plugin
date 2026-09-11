> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 7 — Build the STRATEGY (Part A) — commit it BEFORE the calendar

**This is the step that actually builds the strategy.** Until now you gathered raw
material (Step 3 levers) and the rules for shaping it (Steps 4–6). Now — **before writing
a single calendar reel** — turn that into a **stated strategy**: the decisions the whole
calendar then executes. Write it as **TEMPLATE Part A**, in this order, each decision with
its reasoning + provenance (§I):

7.0. **First, confirm the FOUNDATION with the data you now have — before the strategy.**
   a) **Confirm & sharpen the POSITIONING (drafted in Step 1).** Reverse-engineer the subject's
      **actual** audience from their own reels (`get_content_strategy` on self) and **check it
      against the IDEAL audience** they named in Step 1 — if they differ, surface the gap and let
      the creator choose (a creator who says "founders" but whose reels pull "students" *has* a
      positioning problem — caught by data, not opinion). Confirm **what they demonstrably OWN**
      (from their own top reels), and **sharpen the differentiation against the niche WHITE-SPACE**
      (what everyone else says → say what they don't; this closes the third circle you couldn't
      finish in Step 1). Lock it — save via `update_business_profile`, status `confirmed` (or a
      sharpened `hypothesis` for a young account). Everything below ladders to THIS.
   b) **Read the self-vs-niche GAP (Step 1.6).** What already works for THIS account (double
      down), the niche's proven levers they haven't tried yet (the opportunity to test), and what
      they do that under-performs (fix/drop). The strategy below is built to **close that gap**,
      not copy the niche. **When `benchmark_breadth` exists (FRFRMU-1151) and `local_field` is
      `weak`, Part A's overview carries the `opportunity` sentence as a named opportunity; when
      `active`, one line on which patterns the active local rivals use; no key → nothing changes.**
7.0b. **Advisory offer layer (FRFRMU-1078) — advisory for every goal; selling only when
   goal ∈ {leads, sales} (FRFRMU-1148).** Load `playbook/step-07-1-offer-position.md` here: it
   maps the value ladder for every account, reach included, and Part A must carry its section E
   "Your offer advice" whenever `value_ladder` was saved. Only a paid ask in the calendar waits
   for goal ∈ {leads, sales}; nothing below this line changes.
7.0c. **The profitable promise, light version (FRFRMU-1078, p21) — EVERY account, reach-goal
   included.** Load `playbook/step-07-2-offer-stack.md` Part B here: it mines the audience's
   own hurdle/prize words and drafts one promise (with a true eliminator, soft timing) so the
   bio and the recurring/pinned hook carry the SAME promise. No `promise` key saved yet →
   today's bio/hook path is byte-identical.
7.0d. **Confirm the validated market exists (p01, FRFRMU-1013).** Read the Creator Brief key
   `market_validation` before anything else in this step is treated as final. **Missing →
   say so plainly and STOP this step** (the rest of Part A depends on a checked niche, not a
   guessed one); resume once Step 1.5 (`step-01-1-market.md`) has run. Present → nothing else
   here changes.
7.0e. **Confirm the Big Domino against self-data, when `big_domino` exists (p08, FRFRMU-1040) and
   `status` is still `hypothesis`.** Read `get_content_strategy` / `get_theme_lift` on this
   account's own reels — the candidate whose desire slot resonated is promoted to `confirmed`,
   on record. No `big_domino` key → this line does nothing.
7.1. **Goal & funnel objective.** State the goal (reach / leads / authority) plainly, the
   **ONE conversion action** for the period, and the **funnel mix (TOF/MOF/BOF %)** —
   goal-conditioned and stage-aware (§D), with the reasoning. Never mirror competitors'
   mix.

   **When `value_ladder` exists (Step 7.0b, FRFRMU-1078), the conversion action names its
   rung** and follows the temperature rule there (cold → bait, warm → frontend, backend only
   to buyers) — the ladder never overrides this mix, only which rung the sales slots point at.
   No `value_ladder` → this paragraph is a no-op, unchanged from before.

   **Role-ordering rule (FRFRMU-1032), additive — never overrides the mix above.** Once the
   funnel mix is set, reach slots run earliest in the month (they build the tension the later
   slots resolve), nurture slots run once that tension exists, activation slots run last (they
   need the trust nurture built). This orders WHICH ROLE lands on which week inside the
   already-declared mix — it does not change the mix's counts.

   **Read the base before you state the %.** Run **Recipe A** in
   `playbook/step-03-data-recipes.md` — the four quadrant readings plus the
   conversion-reality read — and write those numbers into Part A with their counts. That
   reading is the descriptive base, not the answer: the goal, the stage and the rulebook
   are the overlay that sets the actual %, and the reasoning must name at least one
   deliberate difference from the base (or one deliberate agreement with it, and why).
   A quadrant that came back thin or `low` reliability is stated as low-confidence and the
   rulebook carries that part of the decision on its own.
7.2. **Target audience.** The ONE segment this serves (from Step 1), how much proven
   material actually targets it, and — if that slice is thin — the honest **on-ramp** (which
   adjacent audience carries the reach and how the plan bridges to the real target) (§F).
7.3. **Patterns MATCHED — modelled FOR THE TARGET AUDIENCE.** The proven **hook, structure,
   CTA and topic** you'll USE, each read on the **target-audience slice** (§F — filter by the
   audience macro; widen + mark low-confidence if the segment is thin), cross-tabbed (§C),
   with **n + median + reliability + provenance tag** and one line on why it fits this subject.
   The plan should say "for YOUR audience, this hook/structure/CTA wins," not "the niche does X."

   **Split the matched patterns PER FUNNEL ROLE (G328).** One pattern set per role in the mix —
   reach patterns (from the Reach-row slice) for `reach` reels, nurture patterns for `nurture`
   reels, activation patterns (from the goal's own row) for `activation` reels — each with its
   OWN n + median + reliability + provenance tag, read on that role's tag slice × the target
   audience. Never present one blended pattern set: a `hidden_gem` lead pattern is not evidence
   for a reach reel, however high its n.
7.3b. **Read recent rejections before matching patterns (FRFRMU-1030).** `get_creator_brief`
   carries a reserved `feedback_history` field — the last few reel rejections (each
   `{reel_uid, reason_code, reason_text, at}`) rolled up automatically when the creator
   pressed X on a calendar reel. If it has entries, say the pattern out loud before 7.3:
   *"you rejected 3 call-out hooks last month → fewer this month"* — a `reason_code` cluster
   (3+ of the same code) is a real signal 7.3's pattern picks should route around, not a
   coincidence to ignore. No `feedback_history` key, or an empty list, means nothing here —
   say nothing about it.
7.4. **Patterns to TEST** — 2–4 bets framed as experiments: hypothesis + kill/scale rule
   (§A/§H). This is how the plan learns.
7.4. **Patterns to TEST — design the tests (FRFRMU-1075, §H).** 2–4 bets, each written down
   as a `test_ledger` row BEFORE the calendar is built, never as a loose paragraph:
   `{id, cycle, variable, control, challenger, metric, sample_floor, disproof, status:
   "designed"}`. **One variable per row** (`hook_template | topic | structure | cta |
   format | caption_first_line | post_time`) — a row that changes two things at once is a
   launch, not a test, and is labelled that way. `control` is the account's current best
   (or the niche's #1 template when there is no history yet); `metric` is the
   **stage-appropriate** one from §H (saves-per-1k for a cold account, never raw views);
   `sample_floor` is how many posts before a call is allowed; `disproof` is the plain-words
   kill line — *"if the challenger doesn't beat the control on saves-per-1k across 3
   posts, we retire it."* **The first bet is always the hook** (highest leverage), then
   CTA/offer, then structure/format. Control and challenger land on comparable calendar
   slots (same pillar × stage × delivery, §H.6) — the row records their `reel_uid`s once
   the calendar assigns them.

   **The Loop Gate, at the same moment.** Before adding any new bet, read the previous
   cycle's `test_ledger` rows (`get_creator_brief`). A row still `"running"` with no
   `result` is an open loop. State the count at the top of Part A — *"2 open loops from
   August — closing them first"* — and close them (below) before trusting a new bet's
   slot. No `test_ledger` key yet → nothing to gate, this is cycle one.

   **Close last cycle's loops on the numbers, right here, before designing new ones.**
   For every `"running"` row: read the creator's own reel data (Step 1.6 if tracked, else
   the pasted tracker — `baseline.source` says which, never guess), fill `result`
   (`{n, control_value, challenger_value, delta}`), and decide: `kill` / `scale` /
   `inconclusive`. **Never call a winner below `sample_floor`** — that call is
   `inconclusive`, which is an honest outcome, not a failure. A `scale` decision makes the
   challenger the control for its comparable slots next cycle (`promoted_to`, recorded as
   *"control changed from X to Y on [date]"*); a `kill` decision writes the loser to
   `topic_history` with a note (`hook_history`, FRFRMU-1060, once it exists — until then
   this is the only write-back). A row with a result but no decision is testing theatre —
   never leave one that way.
7.5. **Content pillars & distribution** — 3–4 pillars laddered to the positioning, and the
   **% split**, with the **concentrate-vs-diversify decision REASONED to this account**
   (has it found a hit yet? goal, stage, data confidence, capacity — no one-size ratio).
   **Every pillar candidate MUST carry a lift citation.** Run `get_theme_lift` (dimension
   `sub_niche`, `intent`, `angle` or `hook_category`) and quote the ratio with the counts
   behind it, e.g. "differentiating: lift 3.7, n=213/8900" or "table stakes: lift 1.1".
   Lift says how much harder this watchlist leans on a theme than the wider community —
   a pillar built on a lift near 1 is a pillar everyone already owns.
   Read it honestly:
   - `lift_ratio: null` with `low_n` means there is **not enough data to compare yet** —
     say that, and pick the pillar on positioning and capacity instead. Never fill the gap
     with a number of your own.
   - `absent_in_community: true` means nobody else in the observed community does it. That
     is the strongest differentiation signal there is, and also pure hypothesis — treat it
     as a bet (§7.4), not a proven pillar.
   **Conditional (p11, FRFRMU-1045):** when `false_beliefs` exists, "belief-breakers" is a
   candidate pillar with a one-to-one belief→reel map — its share stays bounded by this
   section's own mix, never a separate quota. No `false_beliefs` key → this sentence does nothing.
   **Conditional (p12, FRFRMU-1046):** when `movement` exists, the cause line is a standing
   theme here too, bounded the same way. No `movement` key → this sentence does nothing.
   - When the tool warns that a side was **picked for analysis because it did well**, or
     that the community pool is thin, repeat that caveat in the plan.
   Lift is **one** input beside account-spread, repeatability and business fit — the highest
   lift is not automatically a pillar, and it never overrides the tie-breaker below. It
   measures how OFTEN a theme appears, never how well it will do.

   **When `offer_stack` exists (`step-07-2-offer-stack.md` Part A, FRFRMU-1078):** the plan
   may add a fast-win reel and — BOF, warm audience, fulfillable rung only, never on a cold
   account's first plan — a running-stack reel. No `offer_stack` → this paragraph is a no-op.
7.6. **Format MIX — data × what they can produce.** Set the format distribution (talking-head /
   tutorial / skit / b-roll…) from the **winning formats in the data** (for the goal + audience,
   `get_content_breakdown` on `content_delivery`/`content_formats`) **∩ what the creator can actually
   film** (production capability, Step 1) + capacity. State it as a % (e.g. "60% talking-head · 30%
   tutorial · 10% skit") with the reasoning — don't leave format to ad-hoc per-reel choices.

   **Pick it with Recipe B, not with one read.** `playbook/step-03-data-recipes.md` sets
   this mix from the GAP between what the market MAKES and what actually WINS — the same
   reads twice, the second one filtered to stage-matched winner tags. Popularity is not
   effectiveness: a delivery everyone makes and nobody wins with is the niche's wallpaper.
   State both distributions, the winner tags you used and the counts, then the delta
   reasoning, then the %. The receipt for a delivery decision is a `delivery` receipt:
   `made_share`, `wins_share`, `winner_tags`, `n`.
7.6b. **POST TYPE — reel vs carousel vs image.** A separate decision from 7.6: that one is HOW a
   reel is shot, this one is WHAT KIND OF POST the slot is. Start from `get_format_benchmark` —
   the mix the tracked accounts were actually observed posting, with the middle like and comment
   counts per type. Say "observed posts", never "their posts": we see only the recent posts each
   profile refresh catches, so how complete it is depends on refresh cadence against how often
   they post. Types are compared on likes and comments only — images have no view count, so a
   view comparison would always make images look worst for a reason that has nothing to do with
   how they did.
   Read the three answers differently:
   - `state: insufficient_data` — there is not enough history to describe a mix. Say so, and set
     the post type from this playbook's own rules. Do NOT infer a mix from the counts.
   - `absent_in_window: true` on a type — nobody was observed posting it. That is a finding
     ("this niche posts reels only") AND it leaves no evidence either way, so a slot of that type
     is a hypothesis to TEST (§7.4), never a proven bet.
   - `low_n: true` — only a handful were seen. Quote the number with the caveat.
   For the content itself, prefer recycling reels that already proved themselves over inventing
   new ideas per type. Once the creator's own results start coming in, those take over from the
   benchmark — their audience beats the competitors' audience.
7.7. **Recurring SERIES — 1–2, from the strongest repeatable pattern.** From 7.3, pick the proven pattern
   (hook × structure × topic) that is both high-performing **and** sustainable, and turn it into a named,
   repeatable series with a cadence ("every Mon: I automate one thing"). Series build a return habit and
   cut ideation load. Data picks *which* pattern to seriesify; the name + cadence are craft.

   **Shape the name with MAGIC (`step-07-2-offer-stack.md` Part E, FRFRMU-1078):** Avatar +
   Goal (+ Container) — "Owner-Operator Tuesdays" beats "Monday Tips". Data still picks WHICH
   pattern becomes a series; this only shapes the NAME.
   **Conditional (p11, FRFRMU-1045):** when `false_beliefs` exists, the origin → vehicle →
   internal → external order (Secret #12) is a 4-reel series option. No key → this sentence does
   nothing. **Conditional (p12, FRFRMU-1046):** when `movement` exists, a named weekly cause
   series (e.g. "every Friday: one thing the old way got wrong") is an option once the data
   supports the pattern. No `movement` key → this sentence does nothing.
7.8. **Business-calendar alignment — sequence toward their real moments.** Map the plan to the creator's
   **upcoming launches / promos / seasonal moments** (from Step 1; ask if not captured), e.g. two weeks of
   nurture before a launch. The agent MAY **web-search** for relevant seasonal / timely moments in the
   niche to seed this. Never *calendar* breaking news — that's the opportunistic slot (Step 8).

**Three rules that govern the whole strategy:**
- **Tie-breaker when inputs conflict:** **constraints/compliance > positioning > goal > raw data.** A viral
  pattern NEVER overrides who they are, what they can't do, or the goal.
- **Own your confidence:** if Step 3 came back thin, say so at the strategy level — "this is bets, not
  measured data" — don't only tag it per reel. State it per role/slice using Step 3's sufficiency
  table (`step-03-mcp-sufficiency.md` rule 2a, FRFRMU-1019): a role/slice below the reliable tier is
  labelled directional here, not "accurate" — quote the tool's own `confidence.sentence`, never a
  paraphrase.
- **Reels don't grow alone:** note the supporting content they need — Stories that drive to the reel +
  collabs (the Dream 100, Step 8).

**Gate before the calendar:** if you cannot state 7.1–7.8 cleanly, you are not ready to
build reels — go back to Step 3. The calendar (Step 8) must **execute this stated
strategy**, and the Rules Gate's **strategy-adherence** check (Step 11) verifies the
calendar actually delivers the goal / funnel mix / pillars / audience you set here. A
strategy built explicitly here is what makes that check meaningful.

## 🛑 REVIEW GATE A — present the strategy and STOP (FRFRMU-879)

**Ask per `asking-rules.md`.**

The "Gate before the calendar" above checks YOU are ready. This gate checks the strategy
with the HUMAN — the founder's rule: the agent is not a dictator, and Part A is the
judgement the whole calendar then executes.

Once 7.0–7.8 are stated cleanly, present Part A to the creator **as decisions with
reasoning, not a wall of data**: the positioning as 7.0a sharpened it (including the lock
you just saved — they have not seen it yet), the goal + funnel mix, the ONE target audience
(and the 7.0a data-vs-stated gap if there was one), the matched patterns with n / median /
provenance, the pillars and the format mix — each with one line of WHY. Then ask them to
look it over, invite pushback plainly (*"tell me what looks wrong — I'll fix that part, not
start over"*), and **END YOUR TURN. Do not build a single calendar reel in the same
message.**

- **Silence is not approval.** Only an affirmative go-ahead moves you to Step 8. No reply =
  the run stays stopped at this gate; there is nothing that rolls forward on its own.
- **A correction revises the named decision AND its dependents, never the whole run.** A
  changed target audience re-slices the 7.3 pattern reads; a changed goal redoes 7.1 and the
  7.3 metric; a corrected positioning re-saves via `update_business_profile`. Keep everything
  the correction does not touch.
- **Disclose the working copy, once, right here (FRFRMU-980).** Before you present Part A,
  say in one line: *"While we work, I keep a working copy of this plan so we can pick this up
  if we get interrupted — it's replaced the moment we save for real, and deleted on its own
  after 14 days if we never finish. Say so if you'd rather I skip that."* This is disclosure,
  not a second consent ceremony — the SAME affirmative go-ahead that approves Part A covers
  it, unless the creator objects to the working copy specifically.
- **On an explicit objection to the working copy, do not call `save_draft_plan` for the rest
  of this session (FRFRMU-980).** The strategy gate itself still works exactly the same way —
  only the working copy stops being kept. On the affirmative go-ahead with no objection, call
  `save_draft_plan` with `stage: "strategy_approved"`, `plan_month` (already known since Step
  5's cooldown ledger), the approved Part A strategy plus `inputs` (business_context +
  data_signature) — so a new session can read the strategy back WITHOUT re-calling the data
  tools that produced it. This is a free, non-spend write; it needs no separate confirm gate,
  only the disclosure above. **🔴 Send `plan_month` on this call (FRFRMU-1030) — it is what the
  server checks a `calendar_drafted` save and the final `submit_content_plan` against; omitting
  it does not skip the gate, it just makes the month-match check unable to catch a mismatch.**
- **Server enforces this gate too (FRFRMU-1030).** `save_draft_plan(stage: "calendar_drafted")`
  and a first `submit_content_plan` for this month are REFUSED if this checkpoint (with a
  go-ahead recorded) does not already exist. A pre-stated blanket instruction ("build the full
  plan") given before Part A existed does not satisfy this — the ONLY thing that does is the
  affirmative reply to the presented Part A, above.
- **Headless runs (`runner.py`) skip this gate** — nobody is there to answer. Same carve-out
  as the progress checkpoints. (`save_draft_plan` is still reachable headless at Step 8's own
  checkpoint below — only this gate's OWN write point needs a human's go-ahead first.)
- Exists while the strategy read is an unvalidated prediction — re-check after FRFRMU-880.

---

