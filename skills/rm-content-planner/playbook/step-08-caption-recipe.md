> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

> **Load this at Step 8**, once the reel's hook, outline and CTA are settled, to write the
> **caption** for one calendar slot. The three shared ground rules — made-vs-wins, spread beats
> volume, honest small numbers — are defined once in `playbook/step-08-hook-recipe.md`; this
> file uses them and does not restate them.

## Step 8 (caption) — the caption is a second hook, not an afterthought

Until now no step wrote a caption per reel. There was a one-time captions / hashtags / search
framework (Step 8 item 6, `TEMPLATE.md` D3) and nothing else, so every plan either left the
caption to the creator or let the agent improvise one with no evidence behind it.

**Substance conditional (FRFRMU-1032):** when `step-08-join-recipe.md`'s Layer 2 read-map has a
key for this slot (an avatar phrase for reach, a fear/story for nurture, an objection/offer
line for activation), the caption body draws its wording from that citation — this recipe's own
wording rules (below) still outrank on PHRASING. Key absent → the caption is written exactly as
this recipe already specifies, unchanged.

**The evidence here is the cheapest we have anywhere.** Every reel we scrape stores its full
caption text, whether or not that reel was ever analysed. Reading captions costs no credits at
all. Work C.1 → C.4 in order.

### C.1 — Frame by stage

The slot's funnel role already decides the caption's job:

| Funnel role | The caption's job | Shape |
|---|---|---|
| `reach` (TOF) | keep a scroller reading | short, curiosity-led |
| `nurture` (MOF) | add the context the reel had no room for | context, then the value |
| `activation` (BOF) | make the ask impossible to miss | a mini pitch: value recap, ONE proof line, then the instruction spelled out in full — *"DM me the word PLAN and I'll send it over"* |

### C.2 — Read the winners' captions before writing one

You already call **`query_posts_by_tag`** for this slot's funnel-role slice to build the source
table (`playbook/step-03-mcp.md` rule 5a). **Every post it returns carries its caption in the
`content` field** — a whole list in one call, free, no analysis needed. That is where caption
evidence comes from. (`get_post_transcript` also returns a single reel's `caption`, but
do not spend a deep read just to see a caption — the list already gave you all of them.)

From that list, read three things across the winners:

- **first-line patterns** — how the winning captions in THIS niche open;
- **typical length** — how long a caption runs here. There are no house rules on length or
  emoji, so the norm comes from this evidence, is stated per niche, and
  never invented as a global rule;
- **how they echo their CTA** — whether the ask is repeated in writing, and how.

**A caption's first line is a WRITTEN HOOK.** The template-not-words rule applies to it exactly
as it does to a spoken hook: borrow the pattern, write your own words, and the near-clone test
(`RULES_GATE.md` Gate 4) catches a copy.

**Honest small numbers apply here too.** If only three winners in this slice have captions
worth reading, say so and default to the SHORTER shape — a thin sample is not a licence to
assert a niche norm.

### ⚠️ `caption_axis` is NOT the caption — read the right field

There is an analysis field called **`caption_axis`** (`empty` / `minimal` / `descriptive` /
`essay`). **It describes the ON-SCREEN text overlay style the visual pass saw in the video. It
is not the Instagram caption.** An agent that reads it as caption evidence is reading a
different thing entirely and will report the wrong norm with total confidence.

**The Instagram caption text lives in `content`** on every post payload, and in `caption` on
`get_post_transcript`. Those two are the caption. `caption_axis` is not.

### C.3 — Write it

- **First line = the reel's hook, re-hooked in DIFFERENT words.** It is what shows in the feed
  before the "… more" cut, so it gets hook-level care and **must still make sense truncated at
  roughly 125 characters**. Repeating the spoken hook word for word wastes the second chance.
- **Body in the creator's voice**, with the keywords they want to be found for placed where
  they read naturally. That feeds the hashtags / on-platform search row; it is not stuffing.
- **CTA echo — end the caption by repeating the reel's ask, exactly.**
  A viewer who read the caption with the sound off, or who watched without catching the spoken
  ask, still gets it.
  The echo must match the slot's own `cta` and `cta_type` — if the reel asks for a comment and
  the caption asks for a DM, one of them is wrong.
- **Language: the audience's**, per intake — the same rule Step 8 already applies to hooks.
- **Hashtags are the NEXT row's job** — `playbook/step-08-hashtag-recipe.md`. This recipe
  never adds tags.
- **Offer details come from `grand_slam_offer` when it exists** (`step-07-2-offer-stack.md`
  Part F, FRFRMU-1078) — a price, bonus, guarantee or deadline mentioned in the caption reads
  from that one page. No `grand_slam_offer` → this bullet is a no-op.
- **Conditional — the avatar's own words (p02, FRFRMU-1031).** No `avatar` key on the Creator
  Brief → this bullet is a no-op, the body above is unchanged. When it exists, write to the ONE
  named avatar, in language pulled from `avatar.items` tagged `pain_phrase`/`pleasure_phrase` —
  never a crowd ("agencies and coaches"), never marketing-speak that couldn't be typed in a DM
  at 11pm. The critic (`step-11-rules-gate-critic.md`) flags crowd-addressed copy.
- **Conditional — the buying-reason worksheet (p06, FRFRMU-1041).** No `why_people_buy` key →
  this bullet is a no-op. When it exists, an `activation`/`nurture` slot picks ONE answer as its
  value point and ladders it Feature → Benefit → Meaning (`rules/copywriting.md`), citing the
  answer's `item_id` in `reasoning`. **No two activation slots in the same month cite the same
  answer**, and the picks spread across ≥3 of the worksheet's 10 reason types — never every slot
  leaning on money.
- **Conditional — the origin story's caption cut (p10, FRFRMU-1044).** No `origin_story` key →
  no-op. The pinned identity reel's caption may use `origin_story.cuts.caption` (plot +
  transformation) instead of being written fresh.
- **Conditional — the movement's cause-line sign-off (p12, FRFRMU-1046).** No `movement` key →
  no-op. A cause-themed slot may close with the `cause_line`, repeated verbatim — never a
  hashtag-stuffed slogan.
- **A caption body that carries value lines gets flagged `carries_value_lines: true` (p24,
  FRFRMU-1059)** — the planner marks it, the copywriter writes the feature+benefit+meaning lines
  (`skills/rm-copywriter/bullet-recipe.md`). Unflagged captions are unchanged.

### C.4 — The done-test

Before the row is finished:

- the **first line fits the truncation length** and is NOT a copy of the spoken hook;
- the **CTA echo is present and matches** the slot's `cta_type`;
- **no keyword or hashtag stuffing** — the spam threshold our own preprocessor uses is the
  ceiling, not a target;
- **voice and language per intake**;
- the length follows the niche norm C.2 observed, with its count stated when the sample was
  thin.

### Noted for later — do NOT build it under this recipe

A canon of caption FIRST-LINE patterns (the same machinery that already groups hook templates,
pointed at caption first lines) plus length-versus-results norms per niche is buildable
entirely on this free data. It is deliberately **on hold** until the manual read in C.2 proves
too slow at real library sizes. Written down here so nobody re-derives it and nobody builds it
early.

---

