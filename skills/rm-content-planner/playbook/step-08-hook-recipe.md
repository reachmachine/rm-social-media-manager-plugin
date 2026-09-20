> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

> **Load this at Step 8**, next to `step-08-deliverable.md`, when you are filling in the
> **hook** for one calendar slot. It is the *choosing* recipe. The *shape* of the hook (four
> layers, all four required) stays in `TEMPLATE.md` section C1.

> **First-plan mode (FRFRMU-1602):** the `bold_stance` just-in-time ask for this recipe lives in
> `playbook/step-08-just-in-time-asks.md` — this file is at its own line budget with no room left.

## The writing recipes — the shared ground rules

Three step files tell you how to WRITE one calendar row, in the order the row is built:

| Row | File | What it chooses |
|---|---|---|
| Hook | `playbook/step-08-hook-recipe.md` (this file) | which opening template, on which channels |
| Outline | `playbook/step-08-outline-recipe.md` | the beats between the hook and the ask |
| Caption | `playbook/step-08-caption-recipe.md` | the written words under the reel |

They share three ground rules. **This file is where the three are defined; the other two
point back here instead of writing their own version.**

**1. MADE is not WINS.** Two different numbers hide behind "this pattern is popular":

- **made** — how many reels *use* the pattern. This is a count of what creators tried.
- **wins** — how those reels actually *did*, read as the **median** of the winners.

A pattern that is made a lot and wins rarely is the niche's wallpaper, not a lever. A pattern
made a handful of times that wins every time is the interesting one. **Always read both, and
say both.** Never rank on "made" alone, never rank on a single blended number, and never read
the mean — one mega-view reel drags a mean anywhere you like. The words to use with the
creator: *"twelve of your competitors' reels open this way, and the typical one gets 40k
views."*

**2. Spread beats volume.** Forty reels from one account is one person's habit. Forty reels
from twelve accounts is a pattern in the niche. Every pattern read carries how many DIFFERENT
accounts it came from, and a pattern dominated by a single account is never presented as a
niche-wide trend.

**3. Honest small numbers.** Below about five reels nothing here is data-driven (§B). Say the
real count out loud, tag the row DATA-INFERRED or JUDGMENT, and carry on — a thin number
stated honestly is useful; a thin number dressed up is not.

---

## Step 8 (hook) — how ONE slot's hook gets chosen

The hook decides whether the reel gets watched at all, so it is the row with the most
evidence behind it. Work H.1 → H.6 in order.

### H.1 — Frame from the slot

The idea, pillar, funnel role, stage and delivery style are already fixed by Steps 4-8; do
not re-open them here. **Delivery sets the hook's PRIMARY channel:** talking-head or voiceover
→ the spoken line leads; text-on-screen → the on-screen line leads.

**When `promise.chosen` exists (`step-07-2-offer-stack.md` Part B, FRFRMU-1078):** the
recurring/pinned hook MAY use it — same hurdle + prize + timing + eliminator words, never a
second promise. No `promise` key → this sentence is a no-op, unchanged from before.

### H.1b — Which hook channels this reel even HAS

Before pulling any evidence, decide which of the four layers this reel can really use. A
silent reel has no spoken line, and inventing one is a lie the creator will have to film.
Derive the available channels from the format + delivery + the audio mode you are planning
for. Reach Machine records an audio mode on every analysed reel, and the values are:
`silent`, `music-only`, `speech-light`, `speech-heavy`, `non-content-speech`,
`sung_narrative`.

| Planned mode | Channels that exist | What carries the hook |
|---|---|---|
| speech-heavy / speech-light (talking-head, voiceover) | all four | the spoken line |
| **music-only** | on-screen + visual + sound | on-screen text — and the **sound choice itself is hook work**, not background |
| **silent** | on-screen + visual only | on-screen text and the first frame |
| sung_narrative / lip-sync | sound + visual lead | the track and what is shown |
| **carousel** | slide-1 text + image only | the first slide |
| **image** | the image + the caption's first line | the picture, then the caption |

**A channel this reel does not have gets an honest written value, never a blank and never an
invention:** write `none — music-only format` (or whichever mode applies). That is a real,
present value, so the all-four-layers check in `validate_content_plan` stays satisfied without
anyone writing a spoken line for a reel that has no speech.

### H.2 — Pull the proven templates for this pillar × stage

Call **`get_hooks_library`** scoped to the accounts this plan models (`usernames`, or a
narrower `scope`; see `playbook/step-03-mcp.md` rule 5 for the scoping and for the known
empty-result bug). Read **`top_templates`**. Each row carries:

- `template` — the reusable opening pattern, in its canonical form;
- `usage_count` — how many reels used it (**made**);
- `unique_accounts` — how many different accounts (**spread**);
- `single_account_dominated` — true when over half came from one account;
- `median_views` — the typical result (**wins**);
- `reliability` — high / medium / low, the sample-size flag.

**Rank the candidates by `usage_count` × `unique_accounts` × `median_views`.** Never by
`avg_views` (the mean, outlier-dragged), and never by any single blended number — the ground
rules above say why. Drop any row where `single_account_dominated` is true unless you are
deliberately modelling that one creator and say so.

**Weight the winners for the slot's stage.** A `nurture` or `activation` slot leans on
templates whose winners are comment-driven; a `reach` slot leans on templates whose winners
carry the viral tags. That is the same made-vs-wins reading as the outline recipe — cross-check
the candidate against the slot's own funnel-role slice (`playbook/step-03-mcp.md` rule 5a's
source table), because the hooks library cannot filter by performance tag on its own.

### H.2b — Ten before one (p23, FRFRMU-1058)

**For each group of comparable slots** (same pillar × stage × delivery): a thickness check first
— empty `top_templates` or every row `reliability: low` → classic shapes (How-To / In-as-little-
as / N Ways / Mistakes / Warning / My Proven Method), labelled FROM-EXPERT, no count, said
plainly in the plan ("hooks use classic shapes — no niche hook data yet"). Otherwise: if the
Creator Brief carries `avatar`/`prospect_research`/`magic_desk`/`promise`, load those phrases
first (persona `voice.avoid[]` applies) — this is the SAME conditional H.4b already runs, not a
second load. Write **ten candidates** across the top 2-3 templates, each recording
`{template_id, language_source: quote_id|phrase_id|promise|none}` in the slot's working notes
(never the deliverable). Shortlist by H.3's channel evidence, pick per H.6's rotation, then write
the four layers (H.4) as today. **Order rule:** the month's hooks are shortlisted before any
outline or caption is written. No substance keys → this block writes from pattern + brief alone,
same as before H.2b existed.

### H.2c — Saturation check (p25 part D, FRFRMU-1060, conditional)

**Only before shipping a "How to X without Y"-shaped hook** (an `n_ways_mistakes` or
`how_to` template family): read `unique_accounts` for that template family from H.2's own
`get_hooks_library` read — no second call. If `unique_accounts` is at or above
`HOOK_SATURATION_UNIQUE_ACCOUNTS_THRESHOLD` (`app/config.py`, never hardcode the number
yourself) **AND** the family's `median_views` is falling cycle over cycle (H.6's own fatigue
count), the pattern still stands (H.6's mechanics are unchanged) but the SURFACE WORDING must
be structurally different from what the niche is already running — say the count in the plan
("14 accounts in this niche are running this shape right now, median falling — using a
different surface wording"). Every other hook shape skips this check in one line.

### H.3 — Channel evidence: which combinations win HERE

Call **`get_content_breakdown`** with the **`hook_channel`** dimension for the same slice.
That returns how often each channel (spoken / on-screen text / visual / sound) appears and how
those reels did. Pick the combination that matches the slot's delivery — do not assume the
niche's most common combination is the right one for this reel.

**Condition the evidence on the same audio mode.** A talking-head winner is the wrong evidence
base for a silent reel's hook. The audio mode is not a filter you can pass, so approximate it
with the filters that exist: `content_delivery` and `content_formats` (for example
`content_delivery=["talking_head"]` for a speech reel, or the b-roll / montage formats for a
music-only one). Say in the receipt note which filter you used to stand in for the mode.

**One data caveat to carry, in plain words:** reels where someone talks over music have not
always had their speech captured, so some spoken hooks in that hybrid class are simply missing
from the evidence. When you read a speech-over-music slice, say the sample may be short rather
than reading the gap as "nobody speaks in this niche".

### H.3b — The nearest proven hooks to THIS idea (`search_exemplars`)

H.2 ranks templates across the whole pillar. This read is narrower: it finds real hooks, from real
analysed reels, whose WORDING is closest to the one idea you are writing. It is free and
read-only, and it is scoped to this workspace unless you widen it (`corpus: "hook"`, `idea`, plus
the `niche` / `funnel_stage` / `content_format` filters when you want to narrow it).

Read the next paragraph carefully. It is the whole reason this read needs a rule of its own.

> Call `search_exemplars` with the idea you are writing for. What comes back is
> the nearest hooks BY WORDING, not by subject — a hook with the same shape
> about a completely different thing scores just as high, and that was measured,
> not guessed. Read `video_topic` on every row before you use it, and drop any
> whose subject does not fit the idea. Say in the plan which reel each hook came
> from (each row's `post_url`), and never present a retrieved hook as your
> own line. If `wording_match_ran` is false, the rows are just reels that passed
> the filters — say so rather than calling them the closest matches.

**A retrieved hook needs a `retrieved_exemplar` receipt, not a bare `post_url`.** The
validator refuses a naked link — it is not a structured receipt. The shape is fixed
(FRFRMU-995), and it earns DATA-DRIVEN on **provenance**, not frequency: this one real
reel demonstrably exists and performed, so an honest `n=1` is a real receipt here, not
a thin one:

| field | what goes in it |
|---|---|
| `kind` | `retrieved_exemplar` |
| `post_urls` | the `post_url` of every retrieved hook you actually cite for this claim |
| `match_band` | that row's `match_band` word (`close` / `near` / `loose`) — never the cosine number behind it |
| `corpus_version` | the answer's `library_version` |
| `embedding_model` | the corpus's current embedding model. `search_exemplars` does not return this yet — read it from admin/config, or ask the operator, until a follow-up ticket adds it to the tool's own answer |
| `n` | how many retrieved posts back this claim — honestly `1` when it is just the one |

Never write `metric_used` on this kind — it is not quoting a typical number, it is
naming one real example.

**In plain words: YOU are the filter, not the search.** The tool hands you candidates, not
answers. Two hooks about completely different things can score the same because they are built
the same way — that was measured on hand-labelled pairs, not assumed. So a row is usable only
once you have read its `video_topic` and decided the subject really fits the idea.

**If the tool is not on this connection, say so and fall back — never read a missing tool as
"no proven hooks exist."** `search_exemplars` can be absent for a plain reason (it is still
being rolled out on this connection) as easily as a real one, and a missing tool looks
identical to an empty answer if you do not check. So: if the call is not available, or fails,
name it in the plan ("search_exemplars was not available this run") and fall back to H.2's
template ranking on its own — the plan is still data-driven, just narrower. Do not present the
absence as evidence that no proven hooks exist for this idea; that is a claim the tool never
made.

### H.4 — Write all four layers

Template borrowed, **words theirs**. The near-clone test in `RULES_GATE.md` Gate 4 bites
hardest here: reusing a proven template is the point, reusing the source's wording is a clone.

The **sound** layer is honest or it is nothing, and it has its own recipe —
`playbook/step-08-audio-recipe.md`. On a music-only or lip-sync reel the sound is doing hook
work, so it is chosen there, deliberately, not filled in here. Naming a specific song we never
saw in the data is never allowed. (Same rule as `TEMPLATE.md` C1.)

### H.4b — Draw from the avatar's own words, when available (p02, FRFRMU-1031)

**Conditional — only when the Creator Brief carries an `avatar` card.** No `avatar` key →
skip this block in one line, H.4 above is unchanged. When it exists: the hook's promise/tension
layer should draw from `avatar.items` tagged `pain_phrase`/`pleasure_phrase` — real audience
words, not generic copy written to a crowd. Cite which phrase item_id the hook used in the
receipt (§H.5). A phrase used in a hook that cannot be traced back to an `avatar` item fails
the "written to ONE named person" critic check. **Conditional (p05, FRFRMU-1037):** when
`magic_desk` also exists, its Q1-4 answers (the fear chain + deepest want) are additional
candidates in this SAME conditional — one avatar-phrase block, not a second one. **Conditional
(p06, FRFRMU-1041):** when `why_people_buy` also exists, its NON-obvious answers (time-saved →
"what else you'd do with it", a removed worry) are nurture-hook promise candidates here too.
**Conditional (p09, FRFRMU-1043):** when `attractive_character` exists, its `voice_descriptors`
and `avoid` words shape the hook's WORDING (never its evidence), and the hook must not use an
`avoid` word. No `attractive_character` key → this sentence does nothing. **Conditional (p10,
FRFRMU-1044):** `origin_story.cuts.hook_15s` (the Wall line + the shift) is a story-hook
candidate for the identity reel, when confirmed. No `origin_story` key → this sentence does
nothing.

### H.5 — The done-test, and the receipt this hook must carry

Before the row is finished:

- all four layers are present — a real line, or the honest `none — [mode] format` value;
- the **primary channel matches the delivery** set in H.1;
- the near-clone test passed;
- **the template receipt is attached.** Its shape is fixed, and the plan validator reads it:

  | field | what goes in it |
  |---|---|
  | `kind` | `hook_template` |
  | `template_id` | the canonical `template` string from `top_templates` |
  | `count` | that row's `usage_count` — the denominator, and it must be a real number above zero |
  | `account_spread` | that row's `unique_accounts` |
  | `median` | that row's `median_views` |
  | `metric_used` | `views` — a hook's job is to hold attention, so views is the matching metric |
  | `language_source` | *(optional, H.2b)* the `quote_id`/`phrase_id`/`promise`/`none` this hook's words came from |

  A receipt with no count is not a receipt. Never invent a field that reads like a score, a
  confidence or a probability — the validator refuses those outright, by name.

- **Interim trust rule — lean on on-screen text, not spoken quotes.** The check that decides
  whether a reel's speech was worth transcribing is currently starved, so newer reels can pass
  it untested and their transcripts are less trustworthy than their on-screen text, which comes
  from reading the picture. Until **FRFRMU-907**'s fix ships, prefer templates evidenced from
  ON-SCREEN text when both are available, and do not quote a spoken hook as verbatim wording
  without checking `transcript_may_be_unreliable` on that reel. **Delete this bullet when
  FRFRMU-907 lands** — it is the only thing keeping it here.

### H.6 — The template test loop: does the chosen template work for THIS creator?

Ranking a template says it works in the niche. It does not say it works for this account. The
month is how you find out.

- **Templates repeat, words never do.** Re-using a proven template across several reels is the
  point. Identical wording twice is a fail, and the near-clone test catches it.
- **Rotate deliberately.** For a month's **comparable** slots — same pillar × stage ×
  delivery, so only one thing changes — rotate the top 2-3 candidate templates instead of
  giving every slot the market's number one. **Label the rotation in the plan** as a test, on
  every slot in it, so a reader can see it was a choice.
- **Judge it on the creator's OWN results.** Compare each test reel against the creator's own
  recent typical (median) views and comments — not against the competitor set. That needs
  their own account tracked and analysed (Step 1.6); scope the read to them with
  `usernames=[their handle]` on `query_posts` or the insight tools.
- **Concentrate, then keep exploring.** Next cycle, the winner takes most of the comparable
  slots — and roughly **one slot in five stays an explorer**, trying a template the account has
  never run. That is how the plan keeps learning instead of settling.
- **Fatigue, on both sides, counted not predicted.** Creator-side: the winner's lift over their
  own median shrinking month after month → rotate it out. Market-side: the template's usage
  count climbing while its median views fall → the niche is wearing it out. Both are counts you
  can show. Never forecast fatigue; report it.

**When there is no own-account data, H.6 degrades — it never fabricates.** No tracked self
account means no verdicts: keep the market-ranked template, say plainly that the plan cannot
yet tell whether it works for THEM, and offer the fix (track their own account, Step 1.6).
With only two posts per template, a verdict is directional and is stated with its count; a
template is only concentrated on after the signal repeats across cycles.

**Say the test to the creator as a strength, in their words:** *"we run your two strongest
opening styles head-to-head this month and double down on whichever YOUR audience responds
to."* That is not indecision — it is the only way the plan learns.

---

