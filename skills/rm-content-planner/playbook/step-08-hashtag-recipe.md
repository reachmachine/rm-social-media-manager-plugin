> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

> **Load this at Step 8**, after the caption is written, to build the **discovery layer** for
> one calendar slot — the search phrases and the tag set. The three shared ground rules —
> made-vs-wins, spread beats volume, honest small numbers — are defined once in
> `playbook/step-08-hook-recipe.md`; this file uses them and does not restate them.

## Step 8 (discovery) — keywords are the meal, tags are the garnish

No step ever produced hashtags or search keywords for a specific reel. There was only the
one-time framework in Step 8 item 6 and `TEMPLATE.md` D3, so every row's tags were improvised —
and hashtags are where old folklore leaks into a plan faster than anywhere else. "Use 30 tags."
"Build a hashtag ladder." "These tags will get you discovered." None of that is measurable and
some of it is simply not how the platform works any more.

Work HT.1 → HT.4 in order.

### The honest stance — read this before writing a single tag

**1. Discovery has moved to SEARCH.** What people type into the search box is matched against
the caption, the on-screen text and the spoken words. That is where the reel gets found. A
hashtag still helps the platform place a reel in a topic, but its share of the work is small
and shrinking. So the main output of this row is **keywords woven into the content**, and the
tag set is small and functional.

**2. Attribution honesty — the sentence that must survive every future edit of this file.**
**Nobody outside Instagram's own analytics can measure what a hashtag contributed to a reel's
reach.** Not us, not any tool. So this recipe promises **relevance and consistency, never
reach.** *"These tags will get you discovered"* is a banned claim shape — the same class as a
guaranteed-result claim in `RULES_GATE.md` Gate 1, and it fails for the same reason: we cannot
back it.

### HT.1 — Keywords first

The keywords are the phrases the audience actually types when they are looking for this. Build
the short list for THIS reel from three places:

- **the audience's own language**, captured at intake (Step 1) — their words, not the
  industry's. **Conditional (p03, FRFRMU-1033):** when the Creator Brief carries a
  `congregations` card, draw this slot's keywords from its named communities' vocabulary
  instead of intake alone, tagged **community-sourced** — never presented as measured reach
  ("these tags will get you discovered" is a defect). No `congregations` key → this bullet is
  unchanged, intake only;
- **the topic's confirmed name.** `get_topic_heat` returns each topic under the name it was
  confirmed with in the dictionary (`topic`). Use that name, not a synonym you preferred;
- **phrases that recur in the winners' captions** for this slot's slice. You already have every
  one of those captions from the `content` field on the posts the plan pulled
  (`playbook/step-08-caption-recipe.md` C.2) — free, no extra call.

**Then place two or three of them, naturally, in three places:** the caption body, the
on-screen text, and the spoken script. "Naturally" is not a soft word here — a keyword that
does not fit the creator's own sentence gets **cut, not shoehorned**. The caption recipe
outranks this one on wording, and its no-stuffing ceiling applies to keywords exactly as it does
to tags.

### HT.2 — Read what the winners actually do with tags (free)

**Call `get_hashtag_norms` (FRFRMU-1551) — do not read captions by hand.** A real audit found a
delivered plan with zero hashtags on all 8 reels; the manual read this bullet used to ask for is
exactly the kind of step that quietly does not happen. One free call returns:

- **`median_tag_count`** — the niche's own norm. This is descriptive: it is what these creators
  do, not what they should do;
- **`recurring`** — tags that recur across MULTIPLE accounts, already ranked spread-first (a tag
  used forty times by one account is that account's signature, not the niche's norm — the tool
  does this ranking for you);
- **`thin`** — **true below 5 captions read (founder decision, 2026-09-15).** When `thin` is
  true, do NOT present `median_tag_count`/`recurring` as a settled niche norm. Say the real count
  out loud — *"no niche tag norm yet — read from 3 captions"* — and default to **3-4** relevant
  tags instead of chasing the 3-6 range in HT.3 below.

**Where the spam ceiling is.** Our own caption preprocessor flags a caption as tag-spam when the
tags outnumber roughly **one for every three words of real caption body**. That ratio is a
CEILING, never a target.

### HT.3 — Build the set: 3 to 6 functional tags

Each tag in the set has a job. If you cannot say which job a tag does, it does not go in.

| Role | How many | What it is |
|---|---|---|
| **niche** | 1-2 | what this account is about, the same on most reels |
| **topic** | 2-3 | what THIS reel is about, changes reel to reel |
| **series** | 0-1 | the recurring series this reel belongs to, if the plan named one (Step 7) — the same tag every time, so the series becomes findable as a set |

**Never hijack an off-topic trending tag.** Putting a viral tag from another subject on this
reel is the tag version of mimicry: it fails relevance, it teaches the platform the wrong thing
about the account, and it earns nothing. If a tag does not describe this reel, it is out.

Stay inside the niche norm from HT.2 and under the spam ceiling. When the norm and the 3-6 range
disagree, follow the niche norm and say so — this niche is the evidence, the range is the
default.

### HT.4 — The done-test

Before the row is finished:

- the tag count is **within the niche norm AND under the spam ceiling**;
- **every tag is relevant to this reel** — and each one's role (niche / topic / series) can be
  named;
- the keywords appear **naturally** in the caption, the on-screen text and the spoken script,
  and none of them broke the creator's voice;
- the **series tag is the same on every reel of that series**;
- **no reach promise appears anywhere** in the row or the plan's discovery section;
- **write it into the reel's `discovery` field (FRFRMU-1551)**: `{keywords: [...], tags: [{tag,
  role}, ...]}` — a tag/keyword set that lives only in the chat is a tag/keyword set the
  dashboard cannot render and the customer never sees. This is the exact "zero hashtags on any
  reel" bug a real audit found: the recipe ran, the output had nowhere to land.

---
