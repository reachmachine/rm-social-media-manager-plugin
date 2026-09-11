> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

> **Load now:** `${CLAUDE_SKILL_DIR}/TEMPLATE.md` — the fixed output shape (Parts A–E) this
> step writes into. It is NOT loaded earlier in the run; this is the step that needs it.
> This step also quotes `rules/copywriting.md` and `rules/authority.md` — load either one
> only if you need its exact wording.

## Step 8 — What the deliverable MUST contain

> **Output shape is fixed: follow `TEMPLATE.md` (Parts A–E) exactly — same structure every run, for
> every creator.** The items below map into it: strategy first (Part A: overview/positioning, goal +
> funnel objective, target audience, patterns MATCHED, patterns to TEST, pillars + distribution), then
> Foundation (Part B), then the calendar (Part C), then execution + measurement (Part D), then the trust
> layer (Part E). Do not reorder or drop a section.

1. **Section 00 — Foundation** (ships *before* any calendar reel): the one
   positioning sentence — or the "GENERIC — positioning not provided" stamp
   (Step 1) — bio + searchable name field, and the **pinned first 3 reels** that
   define the account. **One of the three pinned reels must be an identity /
   origin-story reel** — the reel that makes a first-time visitor trust this
   creator. Structure it plain: *who I was → the shift that changed me → who I
   am now → why that matters to YOU (the viewer).* Source it from the creator's
   own captured **personal story** (Step 1, `personal_story` in the Creator
   Brief) and/or their transformation story (Step 1 positioning item 6) —
   prefer the personal story when both exist, since it answers "why does this
   matter to them," the stronger trust signal — never invented, and never a
   competitor's story reframed as theirs. If neither was captured, this pinned
   slot falls back to the strongest proof/result reel instead, and the
   deliverable flags that fallback so the creator knows to fill it in later.
   **If `origin_story.cuts.reel_30s` exists (p10, FRFRMU-1044), the pinned identity reel uses
   that cut instead of re-deriving the 4-part summary.** No key → the derivation above, unchanged.
   **If `big_domino` exists (p08, FRFRMU-1040), Section 00 gains one line under the
   positioning sentence: the Domino's `headline`.** No key → unchanged. **If
   `attractive_character` exists (p09, FRFRMU-1043), Section 00 gains a "Profile" line: its
   picked `bio_line`.** No key → unchanged.
   **HARD GUARD — never let invented/placeholder content ship silently.** If ANY
   reel's content had to be filled with a placeholder, an invented example, or an
   unverified claim (the origin story, a result, a testimonial, a number), that
   reel MUST carry an explicit `needs_real_content: true` field AND be listed at
   the TOP of the deliverable under "⚠️ Fill these in before publishing." Do NOT
   present or save an invented reel as if it were final. This exists because a
   real stored plan (6a6241ee) persisted an invented origin script with only a
   buried note — a note is not a guard. (**Shipped 2026-07-27, live in code
   today** — `validate_content_plan`'s `no_unflagged_placeholder` check
   enforces this; see Step 11.0.)
   **A captured `personal_story` doesn't stop at the pinned reel (G373).** If one exists, name at
   least one more reel elsewhere in the calendar — ideally an objection-busting or Big Domino reel
   (`rules/authority.md` Secrets #6/#9) — that explicitly draws on it (e.g. "I used to believe that
   too, until..."). Tag it in the calendar so the story is actually used, not left sitting unused in
   the brief.
2. **Section 00.5 — The month as a funnel** (ships *before* the calendar): lay
   out the journey this month builds — **reach → follow → 2–3 designated
   ACTIVATION reels** that route a warm viewer to the lead magnet via the DM
   automation the creator already has (still gated by the Step 1 funnel-plumbing
   check). State the **ONE conversion action** for the month and work backward
   from it. **Set the month's funnel MIX — the TOF/MOF/BOF ratio — explicitly,
   data-driven and GOAL-CONDITIONED, and state it with the reasoning.** Read
   `funnel_distribution` from `get_content_strategy` as the niche reference (what
   the tracked accounts actually do), but do **NOT** just mirror it — the RIGHT mix
   depends on the goal + stage, not on what competitors post:
   - **Reach goal / cold start (~0 followers):** TOF-heavy (get *seen* first), a
     little MOF (build trust), **minimal/zero BOF** — no audience to convert yet, so
     BOF reels are wasted. (Copying a competitor's 86/10/2 here is the mimicry trap.)
   - **Leads goal:** shift toward MOF + BOF (nurture + convert).
   - **Authority goal:** MOF-heavy (deep educational).
   Then tag every reel with a **funnel role** — `reach` / `nurture` / `activation`
   (= TOF / MOF / BOF) — so the calendar actually HITS the ratio you set. Pick the
   activation reels on the **goal-conditioned** metric (§D) — for a leads goal that's
   saves + comment rate, not raw views. Activation reels still follow the
   stage-appropriate CTA rules from Step 4.
   **Recent rejections (FRFRMU-1030, §7.3b already read this).** If `feedback_history` had
   entries, do not draft a reel that repeats a clustered `reason_code` unchanged — that is
   the whole point of reading it before matching patterns.

3. **The calendar** — per reel: format · intent · topic/niche · angle · **pillar** ·
   **series** (which recurring series, if any) · **moment-tie** (building toward a Step-7.8
   launch/seasonal moment?) · **funnel role** · audience · emotion · hook **template** · full **4-layer
   hook** (spoken / on-screen / visual / sound) · **retention line** ·
   **stage-appropriate CTA** · **effort tag** (heavy = screen-record/build,
   light = talking-head/POV) · **priority rank** · and a **MECHANICAL
   RECEIPT (G74)** in place of a plain "source reel" note:
   - The receipt must be built ONLY from the actual tool results this run
     collected — never written as prose. It names the **source competitor
     (@handle)**, the **specific source reel URL**, the **`n`**, the
     **`median_views`** (never the mean), the **`reliability`** band
     (high/medium/low), and the **provenance tag** from §I (DATA-DRIVEN /
     DATA-INFERRED / JUDGMENT).
   - ✅ **GOOD (mechanical):** *"Curiosity hook × Tutorial. Source:
     @competitorX (instagram.com/p/ABC) + 11 like it in your data. Median
     112k views, reliability HIGH (n=14 in your Tech/AI audience). Tag:
     DATA-DRIVEN."*
   - ❌ **BAD (narrated):** *"Uses a curiosity hook because curiosity hooks
     grab attention and tend to perform well."* — no number, no named
     source, no tool result. That is a **JUDGMENT** call, and it must be
     tagged JUDGMENT, not dressed up to look like data.
   - A recommendation that cannot cite a real tool result gets tagged
     **JUDGMENT** and gets **no data-receipt at all** — it never fakes one.
     (This is §I made explicit, and mirrors `rules/copywriting.md`
     **S14: "never manufacture a results testimonial."**)
   - **The receipt must come from the reel's OWN funnel-role slice (G328).** Cite a ROW of that
     role's **source table** — the small table Step 3 rule 5a builds once per funnel role from
     `query_posts_by_tag` on the tags the reel's role maps to (Step 3 rule 2's role→row mapping).
     A `reach` reel cites a Reach-row source, an `activation` reel cites a goal-row source. A
     receipt built from another role's slice is a wrong-slice receipt: re-source it from the
     right slice, or tag the reel JUDGMENT. Never ship a reach reel wearing a lead-tag receipt.
   - **Do NOT call `get_post_transcript` to build a receipt (FRFRMU-630).** Everything a receipt
     states — @handle, reel URL, `n`, `median_views`, reliability — already comes back from
     `query_posts_by_tag` for a whole LIST in one call. The transcript is only for the hook
     WORDING and the beats; it is pulled **3-5 times per ROLE, at most 12 a plan** (Step 3 rule
     5a), and **many reels sharing one source row is correct**. One deep read per calendar reel
     is the exact mistake this rule exists to stop: it makes a 30-reel plan drag for no extra
     signal, because a plan has three funnel roles no matter how many reels it holds.
   - **The IDEA in the row is not finished until it passes the done-test — see
     `playbook/step-05-differentiate.md` 5.2.** Five boxes: a `topic` receipt is attached, a
     proven hook + structure recipe is attached, the angle is differentiated, it is specific
     enough to film, and it is not on cooldown. The cooldown (5.1) is what stops next month's
     plan quietly re-pitching this month's ideas: a topic the last plans already covered comes
     back only as a named series, or as a **stated sequel** that says why it is back — never as
     an unnoticed repeat.
   - **Which SUBSTANCE fills a slot is its own recipe — load
     `playbook/step-08-join-recipe.md`** before drafting a slot's hook/
     caption/CTA/outline. It joins the data-chosen FORM with the first-party
     substance (avatar/research/story/offer) that slot's funnel role needs —
     "idea from the cards, pattern from the tool" (FRFRMU-1032) — and defines
     the two-receipt shape (`pattern` + `substance`) each block below cites.
   - **How the hook itself gets CHOSEN is its own recipe — load
     `playbook/step-08-hook-recipe.md`** when you fill in a slot's hook. It covers which hook
     channels the reel's format actually has (a silent reel has no spoken line), how to rank the
     proven templates by made-vs-wins, the `hook_template` receipt the row must carry, and the
     month's template rotation test. The 4-layer SHAPE stays here and in `TEMPLATE.md` C1; that
     file is only about the CHOICE.
   - **How the reel gets SHOT is its own recipe — load
     `playbook/step-08-visual-recipe.md`** when you write a slot's shooting direction. It does
     not hand the creator a table of numbers. It hands them **3-5 winning reels from their own
     slice to WATCH**, each with a one-line note, because a person picks up a feel from
     watching far faster than from a distribution. The look itself — lighting, colour,
     wardrobe, location — is the creator's own brand, tagged JUDGMENT, and never cites a
     competitor: copying a competitor's look is mimicry at its most visible.
   - **How the ASK gets chosen is its own recipe — load
     `playbook/step-08-cta-recipe.md`** when you fill in a slot's CTA. It covers which class of
     ask the slot's stage allows, the plumbing check that decides whether an activation ask can
     be made at all (built AND tested, or step it down), why an ask is ranked on **comments and
     not views**, and the `cta_pattern` receipt the row must carry. The one-conversion-action
     rule from item 2 is enforced per slot there.
   - **How the script row gets BUILT is its own recipe — load
     `playbook/step-08-outline-recipe.md`.** It keeps the beats-not-scripts stance and adds the
     process: talk-beats for a speech reel, shot-beats for a silent or music-only one, which
     exemplars' beats may be quoted and which are shape only, the **mandatory mid-video re-hook
     beat**, and the `structure` receipt the row must carry.
   - **Every slot explains itself, LAST — load `playbook/step-08-reasoning-recipe.md`** once the
     rest of the row is filled in. Three lines per slot: the receipts behind it, an expected
     outcome that is a **base rate and never a forecast**, and the goal it serves. A slot that
     cannot say why it is in the plan does not ship. Do this once per slot CLASS (same pillar ×
     funnel role × delivery), not once per slot — a month has about four classes, not sixteen
     separate evidence problems.
   - **Sequence the calendar** so each series lands on its cadence and any launch / seasonal build-up runs
     BEFORE the moment, not after (Step 7.8).
   - **Write every hook / caption in the AUDIENCE'S language**, not assumed English. Ask/detect it (their
     account, Step 1) and write in it. **Shipped (G117) — read it, don't guess:** RM processes
     multilingual reels by translating to English, but it now returns the reel's real spoken
     language too — `original_language` on `get_post_transcript` (top-level field), and under
     `classification.original_language` on `get_posts_detailed`. The transcript text itself may be
     an English TRANSLATION of that language, not a verbatim quote — say so if you quote it. Set
     `meta.language` in the saved plan (Step 12) to the language you actually wrote the hooks/CTAs
     in — the `language_set` check needs it.
   - **Draw from MULTIPLE sources** — the receipts must cite **≥3 distinct competitor accounts**; never
     model the whole plan off one account (fragile + mimicry-adjacent).
4. **Cadence** realistic for the creator's stated capacity (Step 1) — default to
   the **lower end** of what they said they can sustain; anything above is a
   stretch, not the plan. A **batching + repurposing** SOP (one film day → 3–4
   reels → re-cut for Shorts/TikTok), with **light-effort reels batched
   together** so a bad week still ships something. The **priority rank** on
   every reel means the plan degrades gracefully if the week goes sideways,
   instead of collapsing.
   **Total effort ≤ capacity — check the SUM, not just per-reel tags.** Add up each week's effort
   (heavy / medium / light) and make sure it fits what the creator can actually film + edit that week; if
   it's over, cut or reschedule reels — an un-shippable calendar is worse than a smaller one.
   **Plan-size honesty — never pad to hit a number.** If the data only supports fewer STRONG reels than the
   creator asked for (say 6 of 12), **tell them**, and offer in order: (a) **analyse more data** to find
   more strong reels; (b) if they're **out of credits**, offer to **upgrade the plan** and explain the
   benefit (more analysis → more data-backed reels); (c) else **stretch to the number but clearly LABEL the
   extra reels** as lower-confidence "stretch" — never dress a stretch reel up as data-driven.
5. **News = an opportunistic slot**, never calendared (you can't schedule when
   OpenAI ships); keep an evergreen filler ready.
6. **Captions / hashtags / on-platform SEO** framework.
   **The per-reel caption is written in the calendar, not here — load
   `playbook/step-08-caption-recipe.md`.** This item stays the one-time framework; that recipe
   writes each row's own caption: first line as a second hook that survives the feed's "… more"
   cut, a stage-shaped body, and the reel's CTA echoed word for word at the end. It also warns
   about `caption_axis`, which is the ON-SCREEN text style and NOT the Instagram caption.
   Caption evidence is free — every post `query_posts_by_tag` returns already carries its
   caption in `content`, so no extra deep read is needed.
   **The per-reel keywords and tags are also written in the calendar — load
   `playbook/step-08-hashtag-recipe.md`.** Keywords are the meal and tags are the garnish:
   search phrases woven naturally into the caption, the on-screen text and the spoken script,
   plus a functional set of 3-6 tags read from what this niche's winners actually do. That
   recipe carries the honesty rule for this whole row: **we promise relevance and consistency,
   never reach** — nobody outside Instagram's own analytics can measure what a hashtag
   contributed, so a plan never claims tags will get the creator discovered.
7. **Section 04.5 — Distribution: posting time + trending audio.**
   `get_content_breakdown`'s `day_of_week` / `hour_of_day` dimensions give real
   medians — use them, but only as a **soft tie-breaker, tagged data-inferred**,
   never a hard rule, because of two honest caveats you must state to the user:
   (1) the times are in **UTC**, not localized to the audience's own timezone,
   and (2) weekday differences in the data are often flat, so don't oversell a
   small gap. **Sound is now its own recipe — load
   `playbook/step-08-audio-recipe.md`** when you fill in a slot's sound. Two reads exist that
   did not before: `get_trending_audio` bands the sounds RISING across the accounts we track,
   and `get_recurring_audio` shows what this workspace's own analysed reels keep coming back
   to. So the slot prescribes the audio STRATEGY (own voice / reused track / a named rising
   candidate with its numbers), and the creator confirms the exact track in their own
   Instagram panel at posting time — the panel is the final check, not the whole answer. Two
   rules travel with every number: say **"rising among the accounts we track"**, never
   "trending on Instagram"; and quote the coverage figure, because the scraper often gives us
   no sound at all and a sound's absence proves nothing. A pick with no receipt behind it is
   still tagged **JUDGMENT**, and a specific song we never saw in the data is never invented
   (TEMPLATE.md C1 blocks an empty `hook.sound`).
8. **Weekly measurement ritual** with stage-appropriate KPIs, the **mid-month
   tracker** (Step 1.6: saves-per-1k, watch-time %, shares-per-1k per reel) for
   the creator to fill in, and a rule for how that data updates next week's plan.
   **Say which mode this plan is in:** the tracker is manual self-reporting by
   the creator unless their own account is tracked in RM (Step 1.6) — in that
   case the next planning run can read their analysed reels back instead.
9. **Daily community/engagement routine — a real "Dream 100."** Name the actual shortlist (the
   accounts this plan already modelled, Step 3) and give it a method: **serve before you ask**
   (a genuine comment, sharing their best reels to your own story — never drop your own
   link/pitch, reads as spam); a **sustainable cadence** (15-20 min/day across 5-8 accounts,
   rotating weekly — not paid reach, this is how a cold account gets its first real eyeballs).
   Plus a weekly line: check trending audio + format on the accounts you're modelling.
10. **Honest benchmarks:** normalised numbers up top, anchored to the creator's own rolling
    median (Step 1.6) where you have one; mega-view figures labelled "aspirational ceiling".
11. **Section 05 — Receipts: how this plan was built from YOUR data (G74).**
    This is the **QA + conversion summary surface** — it exists so a reviewer
    can tell whether the plan actually used the creator's own RM research (QA),
    and so the creator can feel the plan is built on THEIR competitors and
    THEIR numbers (conversion). Every line in it is **MECHANICAL, never
    narrated** — the same rule as item 3's per-reel receipt. It must contain:
    - **Coverage line:** *"Built from N of your M analysed reels"* — pulled
      from `get_analysis_coverage` (or the total inside `get_content_strategy`).
    - **Which MCP tools actually ran** this session — name them (e.g.
      `get_analysis_coverage`, `get_content_strategy`, `get_content_breakdown`,
      `query_posts_by_tag`, `get_posts_detailed`).
    - **The honest split, as COUNTS, not adjectives:** *"X of the Y calendar
      reels are DATA-DRIVEN (each cites a real lever + n + median), Z are
      DATA-INFERRED, W are JUDGMENT."* The admission **is** the point — never
      inflate it. A plan claiming everything is data-driven reads as marketing
      and gets discounted by anyone who checks.
    - **Name the competitor accounts** the plan actually drew from, by
      @handle: *"these ideas come from @X, @Y, @Z's viral reels."* They are
      the creator's own tracked competitors, so naming them is fine to show
      the creator.
    - **Drive ONE action** (`rules/copywriting.md` S1): e.g. *"start
      with reel #1 — the highest-confidence DATA-DRIVEN pick."*
    - **If ZERO reels are DATA-DRIVEN (or the count is low), give the fix — don't
      just confess.** A workspace whose reach lives in an audience ADJACENT to the
      creator's exact ICP (the on-ramp case) produces 0 data-driven reels — that is
      honest, but it is also a fixable data gap. So the receipts section MUST add a
      concrete **"How to make next month DATA-DRIVEN"** line: *add ≥3 competitors who
      serve your EXACT audience (ICP-matched, not just the same broad niche), analyse
      their winners, and next cycle these reels graduate from inferred to data-driven.*
      This closes the learning loop instead of leaving the creator stuck at "it's all
      a bet." (Found in the real stored plan 6a6241ee: 0 data-driven, honestly owned,
      but no forward fix offered.)

    **The hard rules behind this section, spelled out:** mechanical, never narrated (same test as
    item 3's ✅/❌ example) · **never fabricate a number the tools didn't return** (S14) ·
    **honesty IS the sales mechanism** — "3 of these are my judgment because your data was thin"
    makes the other 7 land as genuinely measured · only cite a row as hard proof if it's reliable
    — a low-n row (§B) is a **bet**, never a DATA-DRIVEN receipt.
12. 🔴 **SAVE THE WORKING COPY — once the calendar rows are drafted (FRFRMU-980).** Once
    items 1-11 are filled in, call `save_draft_plan` with `stage: "calendar_drafted"` (full
    plan so far, Part A included) — SECOND checkpoint write (first is Gate A); free, skip only on Gate A's objection, reachable headless too.
13. **HAND IT OVER — say WHERE the dashboard is (G370).** The plan is delivered as
    `dashboard.html` (see `SKILL.md`, the Deliver step). **Make that file by copying it:**
    `mkdir -p <run folder>`, then `cp ${CLAUDE_SKILL_DIR}/dashboard.html <run folder>/dashboard.html`,
    then ONE `Edit` that changes only the `<script id="plan">` JSON block. Never re-type the
    34 KB file — it is slow, it costs the creator money, and a slip of one character in the CSS
    or JavaScript hands them a blank page. We used to write that file and
    never tell the creator where it landed, which for a non-technical creator is the same
    as never getting it. So, the moment the file is written:
    - **Print the absolute path** — the full path from the drive or root, e.g.
      `A:\work\content-plans\@handle\2026-08\dashboard.html`. Never just the file name,
      never a relative path. Put it **on its own line**, nothing else on that line, so it
      can be copied or clicked.
    - **One short sentence on what is inside it**, e.g. *"your full month — strategy,
      calendar, hooks and receipts."*
    - **Then try to open it in their default browser** (`start` / `open` / `xdg-open`, or
      `mcp__playwright__browser_navigate` with a `file://` URL). **If it will not open, say
      "open this file in your browser" and carry on.** Never fail the delivery over the
      opening step and never loop on retries — the printed path is the part that must
      always happen. **Headless runs (`runner.py`) skip the auto-open** and still print the
      path; a browser popping up on a server helps nobody.

---

