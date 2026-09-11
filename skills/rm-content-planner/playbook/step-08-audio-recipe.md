> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

> **Load this at Step 8**, when you fill in a slot's **sound**. The three shared ground rules —
> made-vs-wins, spread beats volume, honest small numbers — are defined once in
> `playbook/step-08-hook-recipe.md`; this file uses them and does not restate them.

## Step 8 (audio) — prescribe the strategy, confirm the exact track at posting time

The stakes on this row swing more than on any other. On a talking-head reel the sound is a bed
under a voice and almost nothing rides on it. On a music-only reel **the sound is doing the
hook's job** — it is a hook layer, not background, and leaving it blank leaves the reel with no
opening at all.

The old rule for this row was simply "trending audio is not in our data — pull it from
Instagram's panel, tagged judgment". That is no longer true. We now have two real reads. Work
A.1 → A.4 in order.

### A.1 — Stakes by mode

The audio mode you are planning for (`playbook/step-08-hook-recipe.md` H.1b) sets how much care
this row needs:

| Planned mode | The sound's job | Stakes |
|---|---|---|
| speech-heavy / speech-light (talking-head, voiceover) | a low bed under the voice | low — say "low bed under the voice" and move on |
| voiceover with no face | a mood bed that carries the tone | medium |
| **music-only** | **the sound IS a hook layer** | **high — deliberate, never defaulted** |
| **sung_narrative / lip-sync** | **the sound IS the content** | **high — the track choice is the reel** |
| silent | none — say `none — silent format` | none |

**A music-only slot never ships with a blank or a default sound entry.** That is the single
most common way this row goes wrong.

### A.2 — The two reads

**(a) What is rising across the accounts we track — `get_trending_audio`.**

It compares a recent window against the window before it and bands every sound:

- **`rising`** — used in a bigger share of recent reels than before;
- **`steady`** — about the same;
- **`fading`** — a smaller share;
- **`low_sample`** — too few DIFFERENT accounts use it to call the direction either way.

Each row also carries `recent_uses`, `distinct_accounts`, `median_views`, `outperforms_niche`
and a `reliability` band. `scope="niche"` reads your own niche; `scope="community"` is the
early cross-niche signal.

🔴 **Say "rising among the accounts we track", never "trending on Instagram".** Our corpus is
the accounts Reach Machine customers follow, and the reply says so in its own `corpus_label`.
Repeat that label; do not upgrade it into a claim about the platform.

🔴 **The undercount caveat travels with every number you quote from this read.** The scraper
very often gives us no sound at all for a reel, so recurrence UNDERCOUNTS — always. Every reply
carries a `coverage` block saying how many of the reels looked at actually told us their sound.
**A sound's absence proves nothing.** Quote the coverage figure wherever you quote a count, and
never read "not in the list" as "nobody is using it".

**When `available` comes back false, the reading could not be run.** Treat that as *unknown*,
say so, and fall back — never as "no sounds are rising".

**(b) The fallback and the workspace's own habits — `get_recurring_audio`.** Sounds that come up
again and again across the reels THIS workspace has analysed, counting only sounds used by two
or more reels. Use it when the rising read is unavailable, and use it to notice what the
creator's own tracked set already leans on. Same coverage caveat, same wording rule.

**(c) Does this niche lean on voice or on sound?** Read the delivery mix among this slot's
winners — `get_content_breakdown` with the `content_delivery` dimension, filtered to the slice.
A niche whose winners are mostly talking-head and voiceover rewards the creator's own voice; one
whose winners are mostly b-roll and montage rewards a strong reused track. That sets the default
stance for the slot; state which way it went and the count behind it.

**One thing we cannot read yet.** Whether a reel used the creator's ORIGINAL audio or reused
somebody else's is recorded when we scrape a reel, but it is not returned by any read tool the
planner can call today. So the voice-versus-sound stance comes from the delivery mix above, not
from an original-versus-reused split. Do not claim the split; say what the delivery mix shows.
(Tracked as a dependency on FRFRMU-917's audio family — delete this paragraph when it lands.)

### A.3 — Prescribe the stable part, confirm the volatile part at posting time

**What the slot carries, written into the plan:**

1. **the audio STRATEGY** — one of: the creator's own voice / a reused track / a specific
   data-backed candidate from A.2(a);
2. **the volume relationship** — "low under the voice", "full, no speech", "beat drives the
   cuts";
3. **the receipt**, whenever a specific track is named (see A.4).

**A named candidate is allowed now, and this is the change.** When A.2(a) returns a track banded
`rising` with a real `distinct_accounts` count, the plan may say: *"three sounds are rising among
the accounts we track in your niche — here they are with the numbers behind them."* That is a
reading, not folklore, as long as the corpus label and the coverage caveat travel with it.

**A `low_sample` track is never named as a pick.** The band exists precisely because too few
different accounts used it to tell rising from noise. It carries no receipt (the plan validator
only accepts `rising`, `steady` or `fading` on an audio receipt), so a `low_sample` track can
only ever appear as a JUDGMENT call — and usually should not appear at all.

**The Instagram panel is now the FINAL CONFIRMATION, not the whole answer.** The creator opens
their own app at posting time and checks two things: the track is still available to their
account, and it still looks fresh. Our data is historical and trends move; their panel is today.

**Only a pick made with no receipt is tagged JUDGMENT.** A pick backed by an A.2(a) row is
DATA-INFERRED at worst, with its numbers attached.

**Never invent a song name.** A sound we never saw in the data does not get named. *"Pick a
rising track from your own trending panel at posting time"* is a complete, honest answer for a
low-stakes slot.

**Licensing takes care of itself, as long as the pick happens inside their own app.** Instagram
restricts some tracks for professional accounts, and the creator's own panel only offers what
their account type may use. So the posting-time step happens **inside the creator's own
Instagram app** — never instruct anyone to source audio from anywhere else.

### A.4 — The done-test, and the receipt a named track must carry

Before the row is finished:

- **every music-only, sung_narrative and lip-sync slot carries a deliberate sound entry** — a
  strategy, not a blank and not a default;
- **no invented song names** anywhere;
- **every named track carries its recurrence receipt AND the coverage caveat**;
- **a posting-time pick with no receipt is tagged JUDGMENT**;
- the stance matches what A.2(c) showed, or the plan says plainly why it deviates;
- the wording says **"rising among the accounts we track"**, never "trending on Instagram".

The receipt shape is fixed, and the plan validator reads it:

| field | what goes in it | where it comes from |
|---|---|---|
| `kind` | `audio_trend` | — |
| `track_id` | the sound's id | `audio_id` on the track row |
| `band` | `rising`, `steady` or `fading` — nothing else is accepted | `band` |
| `coverage_pct` | how many of the reels looked at told us their sound | `coverage.audio_known_pct` |
| `corpus` | who the reading is about, in words | `corpus_label` |
| `count` | reels using the sound in the recent window — the denominator, a real number above zero | `recent_uses` |

A receipt with no count is not a receipt. Never invent a field that reads like a score, a
confidence or a probability — the validator refuses those by name.

---
