> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

> **Load this at Step 8**, after the hook is chosen, when you are filling in the **script /
> outline** row for one calendar slot. The three shared ground rules — made-vs-wins, spread
> beats volume, honest small numbers — are defined once in
> `playbook/step-08-hook-recipe.md`; this file uses them and does not restate them.

## Step 8 (outline) — beats, not scripts

**The stance does not change: we write BEATS, never a full script.** A ghost-written script
kills the creator's voice, and a creator reading someone else's sentences sounds like someone
else. A beat names **what a moment does and roughly says**. The words stay theirs.

What was missing was the process: which structure to build on, whose beats to copy the shape
of, how much of that evidence is trustworthy, and what a "script" even means for a reel with
no speech in it. Work S.1 → S.5 in order.

**Substance conditional (FRFRMU-1032):** an `objection`/`story_setup`/`myth_bust` beat's CONTENT
(never its position in the beat order) comes from `step-08-join-recipe.md`'s Layer 2 read-map
when the matching key exists (`prospect_research` for `objection`, `origin_story`/
`false_beliefs` for `story_setup`/`myth_bust`) — cited as that beat's `substance_ref`. Key
absent → the beat's content is unchanged from this recipe's existing rules; the beat vocabulary
itself never gains a new name.

### S.1 — Frame, and branch on the audio mode

The slot already fixes the idea, the hook (from `playbook/step-08-hook-recipe.md`), the
delivery and the planned audio mode. **The audio mode decides what kind of beats you are
writing.** One outline idea, three renderings:

| Planned mode | What a beat is here | Called |
|---|---|---|
| speech-heavy / speech-light (talking-head, voiceover) | what gets SAID, beat by beat | **talk-beats** |
| **music-only / silent** | the visual sequence, plus the on-screen text for that beat | **shot-beats** |
| carousel | one beat per slide | **slide-beats** |

A shot-beat with no on-screen text is not finished. A silent reel has no spoken layer to lean
on, so the words the viewer reads ARE the script.

### S.2 — Pull the proven structure, then read 2-3 exemplars

**First the shape.** Call **`get_content_structures`** for this pillar × stage slice. Read
`types` for the structure mix (which `structure_type` gets made, and how those reels did) and
`examples` for real reels of each type, each with its `url` and `username`. Apply the shared
made-vs-wins rule: a structure everyone makes and nobody wins with is not a lever. Weight the
winners for the slot's funnel role, the same way the hook recipe does.

**Then the beats.** Call **`get_post_transcript`** on **2-3** exemplar winners of the chosen
structure. Read `structure.beats` (each beat has `beat`, `label`, `says`, `on_screen`,
`visual_technique`, `start`, `end`), `structure.template_structure`, `structure.duration_s`
and `retention_hooks`. **These deep reads come out of the existing budget** — 3-5 per funnel
role, at most 12 for the whole plan (`playbook/step-03-mcp.md` rule 5a). Re-use a row of the
source table before pulling anything new.

**⚠️ `says` and `on_screen` are two different fields, on purpose.** `says` is speech only;
`on_screen` is text shown on screen. On a reel with no speech, reading `says` as "what they
said" used to be wrong, and that is why the two names now exist. Never merge them.

#### The trust rules — how much of an exemplar's beats you may actually use

Each exemplar's `structure.structure_grounding` says how much of that breakdown rests on words
that were really heard:

| `structure_grounding` | What it means | What you may do with it |
|---|---|---|
| `speech_grounded` | a full transcript was available | **preferred for talk-beats.** Its beats may be quoted as wording |
| `partial` | only the reel's OPENING was transcribed, so the middle and end are read off the pictures | trust the first beats; treat the middle and the close as shape only |
| `vision_only` | no usable speech at all — everything about what was SPOKEN is read from the pictures | **directional shape only. Never quote a `vision_only` beat as words anybody said** |
| empty | the check did not run (an older reel) | treat it with `vision_only` caution — an absent flag is not a pass |

Two more exemplars to skip outright:

- **an empty structure.** `structure.beats` empty with `beats_status` of `no_beats_recorded`
  or `not_analyzed` means there is nothing to model — pick another reel;
- **a failed analysis.** `degraded: true` means our analysis of that one reel broke, so the
  blanks are missing data, not a reel with no structure. Say the `degraded_note` in plain
  words and move on (`playbook/step-03-mcp.md` rule 5a).

**Honest degrade, not exclusion.** Music-heavy niches may have almost no `speech_grounded`
exemplars. `vision_only` exemplars stay usable as SHAPE — the outline just has to say which
kind it leaned on, so the creator can see the difference between "this is how three reels that
worked were built" and "this is how three reels that worked looked".

### S.3 — Build the outline

A beat list with rough timing, in this order:

1. **Hook, 0-3s** — it comes from the hook recipe. Do not re-invent it here.
2. **Early payoff** — give something real before asking for patience.
3. **3-5 main beats** — the teach steps, the story turns, the demo, whatever the chosen
   structure calls for. The beat vocabulary the data itself uses is worth borrowing:
   `context`, `teach_step`, `demo`, `proof`, `myth_bust`, `objection`, `story_setup`,
   `story_turn`, `list_item`, `transformation`, `punchline`. **Conditional (p04,
   FRFRMU-1035):** when the Creator Brief carries a `prospect_research` card, the `objection`
   beat's content comes from one of its cited objection quotes — cite the item_id. No
   `prospect_research` key → the `objection` beat stays a label with no content source,
   exactly as today. **Conditional (p11, FRFRMU-1045):** when `false_beliefs` exists, its rows
   are the SINGLE owner of `myth_bust`/`objection` beat content — cite the row's `item_id`; this
   supersedes the `prospect_research` reference above for any reel that has a matching row. No
   `false_beliefs` key → unchanged. **Conditional (p05, FRFRMU-1037):** when `magic_desk` exists, the
   `story_setup` beat may draw from `magic_desk.extracted_lines`, cited by line id. No
   `magic_desk` key → `story_setup` stays a label with no content source, unchanged.
   **Conditional (p09, FRFRMU-1043):** `story_setup`/`story_turn` may also draw from
   `attractive_character.parables` (a small true moment, cited by `item_id`); the parable's
   `used_in` list is written back with this reel's id. No `attractive_character` key → unchanged.
4. **A re-hook beat at roughly the 40% mark — MANDATORY.** This is the mid-video re-grab: the
   moment that stops a viewer leaving halfway. It is a real, named beat in the data
   (`re_hook`), and analysed reels carry the creator's own re-grab lines in `retention_hooks`,
   so build it from the exemplars where it was captured, and from the retention craft in
   `playbook/step-06-retention.md` (open loop → mid re-hook → loop-back) where it was not.
   **This beat IS `retention.rehook.options[recommended-or-first].line` (FRFRMU-1544/1546) —
   write it ONCE, here, and the saved `retention` field points at the SAME line.** With 1546's
   3-5 ranked options, "the beat" is whichever option carries `recommended: true`, or
   `options[0]` when none does (an honest thin-data case) — never a line that differs from
   every option in the array. Never write a second, different line into `retention` that only
   summarises this beat — that is exactly how a real audit found the saved field degrading
   into a paraphrase of the hook.
   **The BEAT is mandatory; its craft is not.** Vary the form so the plan does not turn into
   thirty reels all saying "but wait":
   - a new-information tease ("the part nobody mentions is…"),
   - re-posing the opening question with higher stakes,
   - raising the stakes ("get this bit wrong and the first two steps are wasted"),
   - a visual or pace change that resets attention on a shot-beat outline.
   The near-clone test applies to its wording exactly as it does to the hook.
5. **CTA transition** — the outline RESERVES the beat; what the ask actually is belongs to the
   CTA row, not here.

**Offer details come from `grand_slam_offer` when it exists** (`step-07-2-offer-stack.md`
Part F, FRFRMU-1078) — a `demo`/`proof`/`list_item` beat naming a price, bonus or guarantee
reads from that one page. No `grand_slam_offer` → this bullet is a no-op.

**A `list_item` beat that carries value (what the offer/method GIVES the viewer) gets flagged
`carries_value_lines: true` (p24, FRFRMU-1059).** The planner only marks WHICH beats — it never
writes the feature+benefit+meaning lines itself; that recipe lives with the copywriter
(`skills/rm-copywriter/bullet-recipe.md`). A beat with no flag is unchanged, exactly as today.

### S.4 — Voice pass

Re-read every beat in the creator's own language and tone from intake, and in the audience's
language. **Cap each beat at roughly one line.** If a beat has grown into two or three
sentences of finished copy, it has stopped being a beat and become a script — cut it back to
what the moment DOES and roughly says. **Conditional (p09, FRFRMU-1043):** when
`attractive_character` exists, this pass reads its `voice_descriptors`/`avoid` object instead
of the loose intake fields. No key → unchanged.

### S.5 — The done-test, and the receipt this outline must carry

Before the row is finished:

- the **re-hook beat is present**, at roughly the middle of the outline;
- the **beat count fits the planned length** — a 25-second reel does not get eight beats.
  `structure.duration_s` on the exemplars is the sanity check;
- every beat is **filmable inside the slot's effort budget** (light / medium / heavy);
- the **CTA beat is reserved**;
- **shot-beats carry on-screen text per beat** — they have no spoken layer to fall back on;
- **the structure receipt is attached.** Its shape is fixed, and the plan validator reads it:

  | field | what goes in it |
  |---|---|
  | `kind` | `structure` |
  | `structure_type` | the structure this outline is built on |
  | `exemplars` | one entry per exemplar reel: its `post_urls` and its `structure_grounding` flag |
  | `n` | how many reels of this structure the slice held — the denominator, a real number above zero |

  Every exemplar carries its grounding flag, so a reader can see at a glance whether the shape
  came from words that were heard or from pictures that were read.
  A receipt with no count is not a receipt, and no field here may be named like a score, a
  confidence or a probability — the validator refuses those by name.

---

