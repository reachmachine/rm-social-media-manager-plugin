> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

> **Load this at Step 8**, last, after every other row of a calendar slot is filled in. It is
> the row that makes the slot explain itself. The other recipes each PRODUCE their half of the
> evidence; this one consolidates it into three lines the creator can actually read.

## Step 8 (reasoning) — every slot explains itself, or it does not ship

A slot that cannot say why it is in the plan is a guess wearing a calendar row. Three lines, on
every slot, in this order. They are short on purpose: the full evidence stays in the slot's
receipts, and this block is the human-readable summary that sits on top of them.

**Batch the work by slot CLASS, not by slot.** A month has roughly four classes of slot (same
pillar × funnel role × delivery), not sixteen separate evidence problems. Read the evidence once
per class and write the Reasoning block from it; only the slot-specific numbers change. Doing it
per slot is the same reads over and over, and the creator waits for it.

---

### R.1 — Receipts: the evidence bundle

**One summary line per claim the slot actually makes.** Not twelve lines on every slot —
only the rows this slot really used. The twelve kinds, and which recipe produces each:

| Claim in the row | Receipt kind | Written by |
|---|---|---|
| the topic | `topic` | `playbook/step-05-differentiate.md` 5.2a |
| the hook | `hook_template` | `playbook/step-08-hook-recipe.md` H.5 |
| the retrieved hook | `retrieved_exemplar` | `playbook/step-08-hook-recipe.md` H.3b |
| the beats | `structure` | `playbook/step-08-outline-recipe.md` |
| the delivery style | `delivery` | `playbook/step-07-strategy.md` |
| the format mix | `format` | `playbook/step-07-strategy.md` |
| the funnel mix | `funnel` | `playbook/step-03-data-recipes.md` Recipe A |
| the ask | `cta_pattern` | `playbook/step-08-cta-recipe.md` |
| the sound | `audio_trend` | `playbook/step-08-audio-recipe.md` |
| the shooting direction | `visual_exemplars` | `playbook/step-08-visual-recipe.md` |
| the posting time | `schedule` | `playbook/step-08-deliverable.md` item 7 |
| what the reel is ABOUT | `substance` | `playbook/step-08-join-recipe.md` |

**The rule, and it is the whole point of R.1:** a slot tagged **`provenance: data_driven` must
carry the matching receipts**; a slot tagged **`judgment` must carry the tag** and no faked
receipt. Nothing is left unlabelled. **A slot whose claims outrun its receipts fails the gate** —
that is the "a gate you never walked shows up as missing" lesson, applied one slot at a time
instead of once for the whole plan.

**A `judgment` slot's Reasoning block ALSO carries one line: "grounded on: <the nearest real
data>"** (`rigor-rules.md` §J, FRFRMU-1024) — an adjacent pillar's proven pattern, the creator's
own first-party proof, or a labelled community/niche signal. This is additive and NOT a receipt: it
does not make the slot data_driven or data_inferred, and the validator's `n ≥ 5` check on receipts
is unchanged. Its only job is transparency — the human reading the plan can see WHERE a judgment
call came from instead of it reading as a free invention.

**Where the receipts actually live.** Full receipts sit on the slot in the saved plan; the
Reasoning block shows the one-line summary. The gate counts that a receipt is PRESENT for each
claim made — it does not reward writing more.

**Field names are fixed, not invented.** Every receipt carries `kind` and, where the claim leans
on a single number, `metric_used` (`views`, `comments`, …). The per-kind fields are the ones
`backend/app/services/reach/receipt_kinds.py` declares, and the validator checks a receipt against
the claim it backs. Two of those checks bite hardest here: a `cta_pattern` receipt quoting views
is refused (an ask's job is responses), and any field NAMED like a score, a confidence or a
probability is refused outright.

---

### R.2 — Expected outcome: a base rate, never a forecast

This is the line most likely to turn into a promise, so it has only **two allowed shapes**.

**Shape 1 — the counted record.**

> *"Posts of this class ran a median of **X views** / **Y comments** across **N accounts**. Posts
> of this class, across N accounts — your own results will differ, and they are what tunes next
> month's plan."*

The second sentence is not optional. Without it a base rate reads as a promise, however carefully
the first sentence was worded.

**Shape 2 — the declared test.**

> *"**Testing** — no market evidence behind this one. It is a deliberate experiment."*

Use it for a novel topic, a hook-test explorer slot, or a format slot that is a hypothesis. Saying
"testing" out loud is stronger than dressing a guess in a number.

**Banned outright — these are not style notes:**

- **Any predicted number for THIS post.** "This will get about 100k views." We cannot know that.
- **Any probability of going viral.** "High chance of virality", "80% likely to hit."
- **Any outcome the data cannot observe.** Conversions, sales, revenue, DMs, what people replied.
  We cannot read comment text and we cannot see DMs, so a conversion claim is invented, not
  measured. The comment COUNT on a reel is measurable; what those comments said is not.

**When there is no base rate to quote**, that is shape 2, not a softened forecast. "Should do
well" is a forecast with the number taken out.

---

### R.3 — Goal served

One line saying which job in the plan this slot does. Map the slot's `funnel_role` onto the
canonical goal words:

| `funnel_role` | Goal served | Said to the creator as |
|---|---|---|
| `reach` | **Reach** | "get seen by people who don't know you" |
| `nurture` | **Engagement** | "build trust with the people who already found you" |
| `activation` | **Leads** | "ask for the one action this month is built around" |

Two additions:

- **An `activation` slot names the ONE conversion action it serves** — the same one every other
  activation slot in the month serves (`playbook/step-08-cta-recipe.md`). Three activation slots
  pointing at three destinations is three half-built funnels.
- **An anchor-week slot cites its declared exception** — the `moment_tie` anchor whose own counts
  say what that week is meant to look like. An anchor week may break the declared funnel mix, but
  only out loud.
- **If `big_domino` exists (p08, FRFRMU-1040), add a `belief` field: the ONE belief this slot
  plants (`reach`/`nurture`) or the ONE objection it knocks down (`activation`) — never two.** No
  key → no `belief` field, R.3 is exactly the table above.
- **If this slot's outline has a `myth_bust`/`objection`/`story_setup` beat citing a `false_beliefs`
  row (`step-08-outline-recipe.md`'s Substance conditional — the beat's own `substance_ref`), add a
  `belief_row` field carrying that SAME `item_id`.** This is the field
  `check_all_three_doubts_covered` (backend, FRFRMU-1045) reads to confirm the plan's three
  confirmed core rows each got a reel — it was never written before FRFRMU-1530, so that check
  could never fire. Never invent a row here that the beat doesn't already cite. No such beat → no
  `belief_row` field, R.3 is exactly the table above.

---

### R.4 — The done-test for this block

Before the slot is finished:

- all three lines are present;
- every claim in R.1 has its receipt, and the `provenance` tag matches what is really there;
- R.2 is one of the two allowed shapes, with no banned phrase in it;
- R.3 names a goal, and an activation slot names the conversion action.

**It has to read like a person wrote it.** One short line each, in the creator's language, no
field names and no tag vocabulary in the customer-facing copy. A three-line block that reads as a
data dump has failed even when every box ticks — the creator is the reader, not the validator.

---
