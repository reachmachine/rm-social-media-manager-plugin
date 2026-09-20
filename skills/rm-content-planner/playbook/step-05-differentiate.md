> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 5 — Differentiate, never mimic

**Ask per `asking-rules.md`.**

**First-plan mode (FRFRMU-1602): ask `ownable_angle` here, before laddering anything to it.**
Only relevant when `step-01-first-plan-core.md` deferred it — outside first-plan mode it is
already captured at Step 1. One question, no bar, no card: *"What do you do differently from
everyone else in your space — the thing a competitor couldn't copy without lying?"* Stuck →
`question-help.json`'s `ownable_angle` entry (`shape: "belief"`) runs §13's belief-draft path.

- Every idea must **ladder to the one positioning sentence** from Step 1.
- Reframe any competitor format around the creator's **first-party proof** ("I ran
  this on my *actual* business — here's the receipt"). That's what a big account
  can't copy back.
- **Reject near-clones.** An RM top reel is a **pattern reference**, not a script.
  If the idea is recognisably "X creator's reel re-skinned", kill it.

**The METHOD — the "Reel Bet" (§A), so differentiation is a procedure, not a guess.** Every reel =
**Proven Pattern × First-Party Topic × Audience Tension:** a pattern (hook + structure + emotion) that's
**proven in the data**, on a **topic drawn from the creator's own proof / demand**, resolving **one real
tension** of the ONE audience. **Never a novel pattern on a novel topic** — that's maximum risk; put the
novelty in the **framing / proof**, never in the pattern or the demand.

**Conditional (p04, FRFRMU-1035):** when `prospect_research` exists, its named exploitable
competitor gap is a candidate first-party differentiation angle. No `prospect_research` key →
this sentence is a no-op.

**Step 5 entry gate (FRFRMU-1032) — the First-Party Topic leg needs BOTH halves before this step
runs:** the substance keys (`step-08-join-recipe.md`'s Layer 2 read-map — avatar/research/story/
offer, or an explicit skip with a reason) AND `get_analysis_coverage` showing the analysed reel
set this strategy actually cites. Substance filled but no analysed data behind it → stamp
**"GENERIC — no patterns."** Data analysed but no substance filled → the existing **"GENERIC —
positioning not provided"** stamp. Both present → the join recipe runs normally.

**The near-clone TEST (concrete, not a vibe).** A reel is a clone if it keeps the source's **hook AND
structure AND topic** — three matches = a re-skin, kill it. Change **at least one** substantially —
**ideally the topic + first-party proof**, so it's unmistakably theirs. *(Same proven hook + structure on a
**different, first-party topic** is fine — that's modelling; same all three is mimicry.)*

---

## 5.1 — The topic cooldown: do not re-pitch last month's ideas

A returning creator's second plan used to be written as if it were their first. Nothing read what
the last plan already covered, so the same topic could come back a month later as if it were new.
The creator notices before we do — *"you already gave me this"* — and the whole plan loses trust.
So **before you generate any ideas, build the cooldown list.**

### 5.1a — Where the list comes from

Work down this table and stop at the first row that gives you an answer. Say in the plan which row
you used, in one line, under the assumptions in Part A0.

| # | Source | How |
|---|---|---|
| 1 | **The topic ledger in the Creator Brief** | `get_creator_brief`, key `topic_history`. Step 12 writes it every time a plan is saved — shape and trim window below. This is the normal path from the second saved plan onward. |
| 2 | **Ask the creator** | No ledger, or it only covers part of the window: ask them plainly — *"what did last month's plan cover, and which of those actually did well for you?"* Their answer is **customer-reported**, and every receipt built on it says so. Never guess it from market data. |
| 3 | **Nothing to read** | First plan for this creator. The cooldown **no-ops**: say in one line that there is no earlier plan, and carry on. A first-plan customer must not be slowed down by this step. |

**The canonical `topic_history` shape — defined once, here.** `playbook/step-12-after-the-save.md`
writes this key; nothing else defines its shape, so read it here and cite it there instead of
restating it:

```
topic_history = [
  { "cycle": "<plan_month, e.g. 2026-09>",
    "topic": "<the topic_id from that slot's topic receipt>",
    "series": "<the series name, or leave it out>",
    "tier": "won" | "held" | "flopped" | "unknown",
    "source": "analysed" | "customer_reported" | "",
    "checked_at": "<ISO date — set only by §5.1f, when no verdict could be read>",
    "plan_id": "<the submit_content_plan reply's plan_id — written at save time>",
    "state": "planned" | "posted" | "archived" },
  … newest first, one entry per TOPIC — never grouped under a cycle
]
```

`tier` uses only the four words from §5.1c's table below. The server enforces this shape on write
(`update_creator_brief`, FRFRMU-982) — a malformed value is rejected, naming what was expected.

**`plan_id` and `state` (FRFRMU-1530) — server-maintained, read-only from here.** Step 12 writes
`plan_id` and `state: "planned"` when it saves an entry; the server changes `state` on its own
from there — to `"posted"` once a real verdict or a confirmed post link happens, to `"archived"`
if the plan is archived before that ever happens — you never write `state` yourself except that
first `"planned"` value. **A missing `state` on an older entry reads as `"planned"`** — this
shape existed before `state` did, and every entry from before this ticket has none.

**`source` and `checked_at` start blank and stay blank until §5.1f fills them in.** A topic is
only ever measured once its cycle has had time to show a result — never at the moment it is first
planned, which is why every fresh entry still starts life as `tier: "unknown"`.

**Reading an older ledger — one release of tolerance.** A workspace may still carry an entry
written before this shape was canonical, nested as `{cycle, topics: [...]}`. If an entry carries a
`topics` array, **flatten it before using it**: read that entry's own `cycle`, then treat each item
inside `topics` as its own flat entry carrying that same `cycle`. Do this defensively for one
release; once no workspace has a legacy entry left, this paragraph can go.

**The honest limit, and say it when it applies.** The ledger only holds plans saved *after* the
ledger existed. A creator whose earlier plans predate it, or who chose not to save, has no row 1 —
they get row 2. That is a real gap in what we know, not a reason to invent a list.

**We cannot read a stored plan back.** There is no Reach Machine tool that returns an earlier saved
plan, which is exactly why the ledger and the question exist. Do not claim to have read one.

### 5.1b — What the cooldown does

A topic on the cooldown list is **excluded from this cycle's shortlist**, with three exceptions:

- **Its `state` is `"archived"` (FRFRMU-1530).** An archived entry **never blocks, full stop** —
  the plan that carried it was archived before anything in it was posted, so nobody's audience
  ever saw the topic. This is not a "bring it back on purpose" case like the two below; it is not
  on cooldown at all. Say so in one line if a topic-heat pick happens to match one: *"this also
  appeared in a plan you archived; it was never posted, so it's fair game."* Silence about an
  archived-plan topic means it is simply fresh — the ledger is a block-list, never an idea source,
  so reusing an archived plan's ideas on purpose only happens if the creator explicitly asks for
  it.
- **It is a named series.** Deliberate repetition is the whole point of a series, so a series topic
  is never on cooldown. Say which series it belongs to.
- **It performed well for the creator.** Then it comes back **on purpose**, written into the plan as
  a decision — *"we are bringing back the pricing teardown because your version did about three
  times your typical views"* — never as an unnoticed repeat. A returning winner with no sentence
  explaining why it returned is a failure of this rule, not a pass. This applies only to `state:
  "posted"` entries — a real result exists to point at. A `"planned"` entry has no result yet.

### 5.1c — How long the cooldown lasts: two dials, a floor and a ceiling

The length is **adaptive**, not a fixed number (founder decision, 2026-09-03). Start at the
baseline and move it with whichever dial fires.

| Situation | Cooldown |
|---|---|
| Baseline — the topic ran, and nothing says it did well or badly | **2 planning cycles** |
| **Dial 1** — it clearly did worse than the creator's own typical result | **stretch to 3** |
| **Dial 2** — the topic is strongly proven in the niche **and** the surviving shortlist is thin | **shorten to 1** |
| Hard bounds | never below **1**, never above **3** |

**These four numbers are starting points, not constants.** They are meant to be tuned once we have
real results to tune them on. They live in this one table on purpose, so tuning them is one edit
here and nowhere else.

**Dial 1 — reading "did well" or "did badly", honestly.**

- **First, read the ledger.** If the topic's `topic_history` entry already carries a settled
  `tier` — §5.1f filled it in last cycle, so it is no longer `unknown` — use that. It is real,
  already-checked evidence, not something to recompute. A ledger `tier` of `flopped` already means
  "landed clearly below it" (the four-words table below), which is exactly this dial's trigger, so
  it stretches the cooldown to 3 with no further comparison needed.
- **Preferred, when the ledger has nothing settled yet:** the creator's own analysed reels. That
  needs their own handle tracked (Step 1.6). Compare a topic's reels against the creator's own
  typical (median) views and comments — never against the competitor set.
- **Fallback:** what the creator told you at row 2 above. Mark it customer-reported.
- **Never from market data.** A topic that underperforms across the niche is **not** the same as a
  topic that underperformed *for them*. Reading one as the other is the single easiest way to
  retire a topic that was actually working for this creator.
- **No signal at all → the flat baseline of 2, and the plan says so.** One line is enough:
  *"we have no results of your own for these topics yet, so every repeat waits two cycles."*

**The four words for how a topic did.** Use these, and only these, so the same word means the same
thing everywhere:

| Word | What it means |
|---|---|
| `won` | beat the creator's own typical result |
| `held` | landed about at their typical result |
| `flopped` | landed clearly below it |
| `unknown` | we have no result for it — the honest default |

*(The month-end review that produces these verdicts is being built separately. If its wording ends
up different, whichever ships second matches the first — one vocabulary, not two.)*

**Dial 2 — the shortlist thinness check.** Call `get_topic_heat` (scope `niche`, or `both` when the
creator's own reels are analysed) and count the topics banded `hot` or `warm` that are **not** on
cooldown. If that count is smaller than the number of distinct topics this plan needs, the
shortlist is thin, and dial 2 shortens the cooldown to 1 for the topics banded `hot`.

### 5.1d — The cooldown yields to honesty

If the shortlist is still too small after dial 2, **say so and widen** — the community lens, the
sequel exception, more analysed competitors. **Never invent a novel pattern on a novel topic to
fill the gap.** A thin month stated plainly is a better plan than a padded one, and §5's Reel-Bet
rule does not bend for a scheduling problem.

### 5.1e — Which dial fired is recorded, not narrated

For every topic you held back or brought back, record which dial fired as a fact on the topic's
receipt — `cooldown_cycles` (1, 2 or 3) and `cooldown_dial` (`baseline`, `own_results` or
`thin_shortlist`), plus `own_result_tier` and `own_result_source` (`analysed` or
`customer_reported`) when you have them. It belongs in the receipt, not as a paragraph in the
creator's face: the creator sees the sequel sentence and the honest "we have no results yet" line,
and a reviewer can check the rest.

### 5.1f — Settle last cycle's verdicts, so `tier` does not stay `unknown` forever

Step 12's ledger write starts every topic at `tier: "unknown"` — an honest placeholder, because at
that moment the topic has only been planned, never measured. Nothing before this fills it back in,
so a topic that clearly won or flopped for the creator could sit as `unknown` for months, and dial
1 above would keep asking the same question it already has an answer to. This is the fill-in — a
cheap, narrow one. The month-end reconciliation that eventually replaces it (FRFRMU-962) is still a
parked idea; this is its usable subset, built only from tools that already ship.

**Which entries.** From the ledger you just read in §5.1a, take every entry whose `tier` is still
`unknown` and whose cycle ENDED at least **14 days** ago (dial — tune this alongside §5.1c's table
once we have real results to tune on). A cycle younger than that stays `unknown`: there has not
been honest time for a real result yet, and leaving it alone is the correct default, not a gap.

**How a verdict is read — in this order, stop at the first row that answers:**

1. **From the creator's own data (`source: "analysed"`).** Needs their own handle tracked (Step
   1.6). Match the entry's topic to their analysed reels — by the topic dictionary's canonical id
   (FRFRMU-944) where it has an assignment, else by the entry's own wording. Compare against the
   creator's own median views for the window, the same "never the competitor set" rule dial 1 uses.
   `won` is about **1.5×** their median or more, `flopped` is about **0.5×** or less, anything else
   is `held` — starting dials, tune them like §5.1c's table once there are real results. This needs
   **at least one** matching posted reel; zero matches is not a verdict, so fall through to row 2
   rather than guess from an empty sample.
2. **From the creator (`source: "customer_reported"`).** The "how did X do?" question §5.1c already
   asks belongs here too — record the answer against the matching entry.
3. **Neither.** The entry stays `unknown`. Stamp `checked_at` with today's date so this entry is
   not re-asked about every single cycle — a repeated question nobody can answer is worse than one
   honest "we still don't know."

**The write.** Carry the corrected `tier`, `source` and `checked_at` onto the matching entries in
the SAME `update_creator_brief(topic_history, …)` call Step 12 already makes this cycle — merge,
never overwrite, same trim-to-4-cycles rule `playbook/step-12-after-the-save.md` states. This is
what makes the fill-in real: the 982 reserved-key validator checks every `tier` this step writes,
the same enforcement it already applies to a freshly-planned entry.

**What this deliberately does not do.** No detection of whether a planned reel was actually
posted — this matches the entry's TOPIC against the creator's analysed reels, never "was this exact
idea filmed." No follower or revenue outcomes — views and comments only, the same evidence dial 1
already reads. It writes nowhere but this ledger. And it is an interim measure only: once
FRFRMU-962's month-end reconciliation ships, its own, more careful pass OVERWRITES these tiers.

---

## 5.2 — The idea done-test: an idea row is not finished until all five boxes tick

An idea used to be able to walk into the calendar carrying nothing. The receipt fields existed on
the slot, but no rule made the **idea itself** prove anything. These five boxes are that rule.

1. **A topic receipt is attached** (the shape is below). No receipt, no slot.
2. **A proven hook + structure recipe is attached** — `playbook/step-08-hook-recipe.md` and
   `playbook/step-08-outline-recipe.md`.
3. **The angle is differentiated** — the near-clone test above passed.
4. **It is specific enough to film.** If the creator could not pick up a phone and shoot it from
   the row as written, it is a theme, not an idea.
5. **It is not on cooldown**, or it carries its series name or its sequel sentence.

### 5.2a — The topic receipt

Read it from `get_topic_heat`, which groups the analysed reels by real topic instead of by their
free-text headlines. The shape is fixed, and the plan validator reads it:

| field | what goes in it |
|---|---|
| `kind` | `topic` |
| `topic_id` | the topic's name, exactly as `get_topic_heat` returned it |
| `viral_instances` | how many reels in this topic went viral — the denominator, a real number above zero |
| `distinct_accounts` | how many different accounts posted them |
| `hit_rate_band` | the band word `get_topic_heat` gave the topic: `hot`, `warm`, `cold` or `low_n` |

**A receipt with no count is not a receipt.** And never invent a field that reads like a score, a
confidence or a probability — the validator refuses those by name.

**One account posting a topic ten times is a habit, not proof the topic travels.** Read
`distinct_accounts` before you read the count, the same spread rule the other recipes use
(`playbook/step-08-hook-recipe.md` ground rule 2 — this file does not restate them).

**`low_n` is not a failure.** On a small library most topics honestly are `low_n`. Say the real
count, tag the row DATA-INFERRED or JUDGMENT, and carry on. The fix for `low_n` is more analysed
reels, never a looser rule.

**Where the topic dictionary is thin.** `get_topic_heat` now returns a `state` field — check it,
not just whether the list is empty. `state: "ok"` (or `"all_low_n"` with real counts) means the
topics are genuinely counted; anything else (`dictionary_not_minted` — grouping is not built on
this environment yet; `dictionary_disabled` — grouping is switched off here; `reels_not_assigned_yet`
— the dictionary exists but matching has not reached these reels yet) means there is nothing usable
to cite. When `state != "ok"`, the interim receipt cites **example reels** instead — the post URLs
and their tags from `query_posts_by_tag`. It is weaker evidence and the row says so, but it is
honest, and it is still a receipt. **Never** read `get_content_strategy.topic_distribution` as a
substitute for a topic receipt in this state — that field is the content-FAMILY (niche) mix, a
different thing wearing a similar name; see `data-quality.md`.

### 5.2b — A brand-new topic is allowed, as a declared test

A topic with no group behind it is valid in exactly one form: a **declared test slot**. It must
carry a **proven** pattern (hook + structure), be tagged `provenance: judgment`, and say in the row
that it is a test. That is the never-novel-pattern-on-a-novel-topic rule from §A, now enforced
through the receipt rather than trusted to memory.

---

