> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

> **Load this at Step 8**, when you write the **shooting direction** for one calendar slot. The
> three shared ground rules — made-vs-wins, spread beats volume, honest small numbers — are
> defined once in `playbook/step-08-hook-recipe.md`;
> this file uses them and does not restate them.

## Step 8 (visual direction) — show them reels to watch, don't hand them numbers

Until now the only visual guidance a slot carried was the hook's first-frame cue. Everything
else — how to frame it, how fast to cut, how much text on screen — was either missing or
invented.

**The answer is not a table of numbers. It is a short list of reels to watch.** A creator learns
more from thirty seconds of watching three winning reels in their own niche than from being told
"single-frame composition, sparse overlay, 2-3 cuts". Watching is how a person picks up a feel;
a distribution is not. Work V.1 → V.4 in order.

### V.1 — Frame the slot

Three things are already decided before this row starts, and none of them get re-opened here:

- **the shot type** comes from the slot's delivery and format (Step 7's format mix);
- **the first frame** comes from the hook's own visual layer (`TEMPLATE.md` C1, chosen in
  `playbook/step-08-hook-recipe.md`);
- **the ambition** is bounded by the slot's **effort budget** — a light-effort reel does not get
  a three-location shoot.

### V.2 — Pull 3-5 reels to WATCH

This is the row's main output. Filter the plan's own source reels down to this slot and hand the
creator the links.

**The filter:** the slot's **format** × **delivery** × **funnel stage** × **niche**, with the
winner tags matched to the slot's own funnel role (`playbook/step-03-mcp.md` rule 5a's source
table). Every read that builds that table already returns each reel's `url`, so this costs no
extra call and no credits.

**What the plan prints, per exemplar:**

- **the link**, so it can be tapped;
- **one short line saying what is on screen**, so the creator can choose which two to open
  instead of opening all five.

The line beside each link says where it came from:

- **when the read gives you the reel's own stored "what's on screen" sentence, use it** —
  *"[link] — woman at a kitchen counter, mid-demo"*;
- **when it does not, write the line from the classification the read DOES return**
  (`content_delivery`, `content_format`, `video_topic` on `get_posts_detailed`) and say so —
  *"[link] — talking-head tutorial about meal prep (from its labels, not a description of the
  shot)"*.

⚠️ **Today it is always the second form.** The one-sentence visual description IS stored for
every analysed reel, but no read tool the planner can call returns it yet. So do not go looking
for a field that will not arrive, and do not pass a label-built line off as a description of the
shot. (Tracked as a dependency on FRFRMU-917's visual family — when it lands, the first form
becomes the normal one and this warning goes.)

**The sentence to say to the creator:** *"watch these three to feel how this slot should be
shot."* That is the whole instruction.

**Honest small numbers apply.** Two exemplars is the floor. With fewer than two, say so and drop
the watch-these list for that slot rather than padding it with a reel from the wrong slice.

### V.2b — Pattern-interrupt matrix (p31, FRFRMU-1069, conditional)

**Only for `reach` reels on a cold/young account** (`funnel_role = reach` AND stage is
cold-start/young, per Step 4's stage ladder) — every other slot skips this in one line. Build a
small matrix: **3 avatar phrases** (the "escape"/"instead" phrases from `avatar.items`,
FRFRMU-1031, or `prospect_research` quotes, FRFRMU-1035) × **2-3 visual concepts** from
`get_visual_patterns` — what the niche's data shows stops a scroll, with its own `n`. That is
≥6 combinations. Each cell records `{phrase_source, visual_concept, visual_rationale, hook_
subcategory}` — the rationale names WHY it interrupts (odd / concrete / unexpected next to the
niche's usual look), never "looks good". Picks rotate per H.6's test loop; the rest stay
candidates in the slot's working notes, same convention as H.2b's ten hooks (FRFRMU-1058). No
`avatar`/`prospect_research` key → this whole block is a no-op, unchanged from before.

### V.3 — The direction sheet

Per slot, in this order, and short enough that a creator with a phone can act on it:

| Line | Where it comes from | Tag |
|---|---|---|
| shot type | delivery + format (V.1) | follows the plan |
| first frame | the hook's visual layer | follows the hook row |
| **watch these** | V.2's 3-5 links, each with its one-line note | the receipt |
| look and feel — lighting, colour, wardrobe, location, styling | **the creator's own brand** | **JUDGMENT, always** |

**Why the look is deliberately NOT read from the data.** Lighting, colour, wardrobe, location
and overall styling are brand identity. They are the most visible thing about an account, so
copying a competitor's look is mimicry at its most obvious — and it is also the thing a viewer
notices first when two accounts look the same. These lines come from the creator's own brand
intake, are tagged JUDGMENT, and **never cite competitor evidence.** A direction sheet whose
wardrobe line points at a competitor reel has failed, not passed.

**Production tools fill execution, not direction.** Where the creator uses an AI production tool
to shoot or edit, that is how the direction gets executed. It does not change what the direction
says, and the plan never assumes a tool the creator did not say they use.

### V.4 — The done-test

Before the row is finished:

- **at least two exemplar links are attached**, each one a winner in the slot's own
  format / delivery / funnel-role slice, each with its one-line note;
- **the look lines are tagged JUDGMENT** and cite no competitor;
- **nothing is unlabelled** — every line is either "watch these" evidence or a tagged judgment
  call;
- **the direction is filmable inside the slot's effort budget**, and short enough to read in one
  breath. A twelve-line art-department brief for a phone shoot is a fail, not thoroughness;
- the direction does not contradict the hook row's on-screen plan.

The receipt shape is fixed, and the plan validator reads it:

| field | what goes in it |
|---|---|
| `kind` | `visual_exemplars` |
| `post_urls` | the 3-5 links, exactly as shown to the creator |
| `subject_descriptions` | the one-line note beside each link, in the same order |
| `count` | how many reels the slice held before you picked from it — the denominator, a real number above zero |

A receipt with no count is not a receipt, and a "watch these" claim with no links attached is
not evidence. Never invent a field that reads like a score, a confidence or a probability — the
validator refuses those by name.

---
