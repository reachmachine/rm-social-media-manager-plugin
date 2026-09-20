# RULES GATE — run EVERY draft plan through this before showing the user

> **What this is.** A universal, book-derived checklist. After you draft the plan (TEMPLATE.md) and BEFORE
> you show it to anyone, run it through every check below. Anything that fails gets fixed, then you re-run
> the gate. This runs INSIDE the critic loop (PLAYBOOK Step 11) — draft → gate + critic → fix → repeat until
> clean → only then show the user.
>
> **This gate is GENERIC.** It is derived only from the marketing books in `rules/` (copywriting, funnel,
> authority, offer, traffic) and platform-compliance basics. It contains **NO business's private strategy**
> — no specific ICP, offer, price, or brand belief. That is deliberate: a gate carrying one company's
> strategy would corrupt the plan for every other business that uses this skill. Judge the plan against the
> creator's OWN positioning + data, never against anyone else's playbook.

---

## Gate 1 — Voice & compliance (HARD — a fail here blocks the plan) · `gate_1_voice_compliance`
The books teach great STRUCTURE but often in a hype VOICE. Keep the structure, fix the voice. Fix any reel where:
- [ ] **Guaranteed-result / income / outcome claims** appear ("you WILL get X", "make $Y", "guaranteed
      results"). Ad platforms ban these and they destroy trust. → promise the **PROCESS + the DREAM**, never
      the outcome. *(offer Ch 15, copywriting compliance)*
- [ ] **Fake urgency / fake scarcity** ("only 3 spots!" when untrue, invented countdowns). → use REAL
      deadlines/limits only, or drop it. *(offer Ch 12-13)*
- [ ] **Hype-as-required-style** ("secret", "weird trick", "insane", ALL-CAPS energy) is forced on every reel.
      → hype devices are OPTIONAL tools; default to calm, plain, specific. A proof point beats an adjective.
- [ ] **Manufactured testimonials / fake proof.** → never invent a result or a testimonial. *(copywriting S14)*
- [ ] **Medical / financial / legal guarantees** the creator can't back. → soften to process + example.
- [ ] **Reach promised from hashtags or keywords** ("these tags will get you discovered", "this
      hashtag set will grow your reach"). Nobody outside Instagram's own analytics can measure
      what a tag contributed, so this is an unbackable claim in exactly the same way as a
      guaranteed result. → promise **relevance and consistency**, never reach.
      *(`playbook/step-08-hashtag-recipe.md`)*
- [ ] **Price-competition claims** ("cheaper", "cheapest", "affordable", "discount", "lowest
      price", "for less money", "pay less"). → never compete on price; sharpen the
      category-of-one claim, or add a bonus, never a discount. *(offer Ch 2/3/14, FRFRMU-1048)*
- [ ] **Outcome-tied guarantees** ("double your leads or money back") — a guarantee's promise
      must be in the deliverable shape (If you don't get [a DELIVERABLE] by [Y], we [Z]), never
      tied to a result (leads, sales, revenue, followers, weight, income). → reword to the
      deliverable, or drop the guarantee. *(offer Ch 15, FRFRMU-1053)*
- [ ] **Expected outcome is a base rate, never a forecast — countable, per slot.** Read every
      slot's "expected outcome" line. It must be one of exactly two shapes: a counted record
      (**"median X across N accounts"**, paired with its "your own results will differ" framing)
      or the words **"Testing"** for a deliberate experiment. Count the slots that are neither.
      A predicted number for THIS post ("this will get ~100k"), a chance of going viral, or any
      outcome we cannot observe (conversions, sales, what people replied) fails here. This is a
      flag for your own review pass, not a word-matching machine — read the line and judge it.
      Fix = replace the forecast with the base rate you actually have, or say "Testing".
      *(`playbook/step-08-reasoning-recipe.md` R.2)*

## Gate 2 — Structure (is each reel built on a proven pattern?) · `gate_2_structure`
- [ ] Every reel follows **hook → story/value → offer/CTA** (the reel spine). *(traffic Secret #3)*
- [ ] Every reel has ONE job and ONE ask — not three. *(copywriting S1)*
- [ ] The hook speaks to the **viewer's** fears/desires (their FRED / PQR2), not the creator's features.
      *(copywriting S8/S13)*
- [ ] **Sound is deliberate wherever it does hook work.** Every music-only, sung-narrative or
      lip-sync slot carries a real audio entry — a stated strategy, never a blank and never a
      copy-pasted default. On those reels the sound IS the opening, so a blank entry means the
      reel has no hook. *(`playbook/step-08-audio-recipe.md` A.1)*
- [ ] There is an **identity / origin** reel somewhere — `origin_story.cuts.reel_30s` when one
      exists, else the epiphany-bridge/proof fallback. *(authority Secret #6, p10 FRFRMU-1044)*
- [ ] Common **objections/false-beliefs** are addressed as content, not ignored — all three
      doubt types (Vehicle/Internal/External) covered when `false_beliefs` exists. *(authority
      Secret #9, p11 FRFRMU-1045)*
- [ ] The plan builds toward ONE core belief / big idea over the period — the `big_domino`
      headline when one exists. *(authority Secret #5, p08 FRFRMU-1040)*
- [ ] **Movement, when staged (p12, FRFRMU-1046):** a plan claiming a "here's what's possible"
      proof reel cites `movement.four_minute_mile`, or honestly says "no owned win yet."
- [ ] **Production-fit is an ON-RAMP, not a filter.** The early calendar leads with formats the creator can
      execute well now, BUT no market-proven format is silently dropped for lack of skill — each is surfaced with
      a **production path** (learn it / AI tool or avatar / outsource the edit / a doable adjacent format hitting
      the same driver). The plan follows the MARKET, ramped to the creator's ability — never the reverse.

## Gate 3 — Retention (does each reel earn watch-time, not just the click?) · `gate_3_retention`
- [ ] Every reel has a real **retention object** (FRFRMU-1544): `open_loop` (the IDEA the hook plants,
      never its wording) → `rehook.options` (a SAYABLE line at ~40%, checked by `retention_rehook_present`
      and `retention_rehook_distinct_from_hook`) → `loop_back`. A hook with no body-retention fails.
- [ ] **Retention is tagged honestly.** It is **SMM JUDGMENT** (never DATA-DRIVEN) unless it was built from a
      real beat structure the tools returned; shares/saves-per-1k may support it as DATA-INFERRED. RM can't see
      competitor watch-time — a structural guess must not be dressed as data.

## Gate 4 — Benchmark, never copy (anti-mimicry) · `gate_4_anti_mimicry`
- [ ] No reel is a competitor reel **re-skinned**. Each one is **benchmarked** (pattern extracted) then
      **modelled** into the creator's own version, reframed through their first-party proof.
- [ ] **The near-clone test:** a reel that keeps the source's **hook AND structure AND topic** (three
      matches) is a clone → rewrite it. At least one must change substantially — ideally the topic +
      first-party proof. (Same hook + structure on a *different, first-party* topic is fine.)
- [ ] **For a RETRIEVED hook (`search_exemplars` was used), wording alone is enough — no
      conjunction needed.** The three-match test above assumes an organic hook, where matching an
      exemplar on hook AND structure AND topic all at once is a real coincidence. A retrieved hook is
      different: you were HANDED the exemplar's exact wording, so wording that stays too close to it is
      a clone on its own, whatever the topic — the three-match test would let a verbatim hook on a
      different topic through, and that is exactly the gap this line closes. `check_hook_clone`
      (FRFRMU-991) runs this mechanically at save time and warns with the source `post_url`; it never
      blocks the save. Rewrite the wording, or confirm you meant to reuse your own reel.
- [ ] Great copy leaves clues — model the *pattern*, never clone the *content*. *(copywriting S12)*
- [ ] **Written to ONE named person, not a crowd (p02, FRFRMU-1031).** When `avatar` exists,
      copy addressed to a demographic label ("agencies and coaches") instead of the named
      avatar fails here.
- [ ] **Speech, not marketing-speak (p02, FRFRMU-1031).** A phrase that couldn't be typed in a
      DM at 11pm — hype-adjacent, generic, or reading like ad copy — fails, even if it cites an
      `avatar` phrase item.
- [ ] **The LOOK is never borrowed.** Lighting, colour, wardrobe, location and styling are the
      creator's brand identity, so every one of those lines is tagged JUDGMENT and cites no
      competitor reel. A direction sheet whose wardrobe or location line points at a
      competitor's reel as evidence fails here — that is mimicry at its most visible. The
      "watch these" exemplar links are fine: they are for feel, not for copying a look.
      *(`playbook/step-08-visual-recipe.md` V.3)*

## Gate 5 — Stage-appropriate CTA & funnel (traffic → owned) · `gate_5_stage_cta_funnel`
- [ ] CTAs match the account's stage: **reply-bait / no-CTA** is the default when reach is thin.
      **keyword-DM / lead-magnet** requires the automation to be **built AND tested** — that is the
      hard gate, at every stage, because a promise the creator can't keep is worse than no CTA.
      Thin reach on top of working plumbing is a **caution, not a bar**: it usually gets few
      responses and can cost reach, but it is the creator's call to make. *(funnel)*
- [ ] **CTA variety = wording AND the ask itself** (2026-09-15, FRFRMU-1544): >= 3 distinct `cta_type`s per plan (`cta_type_variety`, `cta_wording_variety`).
- [ ] **Every CTA carries readable words** (FRFRMU-1549): an object-shaped `cta` holding no text reads as present to code but says nothing to the customer; only a `no_cta` row may have none. (`cta_has_words`)
- [ ] The plan moves rented reach toward **owned traffic** (followers → email/DM list) over time.
      *(funnel Secret #5, traffic Secret #5)*
- [ ] The month maps to a **value ladder** with ONE conversion action worked backwards. *(funnel Secret #2)*
- [ ] **Every activation row names its rung on the value ladder** — the rung exists and is
      fulfillable today; the month ascends (bait → frontend → ...), never the backend cold.
      *(FRFRMU-1047)*
- [ ] **One conversion action, counted across the activation rows.** List every `activation`
      reel and read its ask: they must all point at the SAME conversion action. Three
      activation reels sending people to three different places is three half-built funnels,
      not a month. Fix = pick the one the plan declared and re-point the others.
      *(`playbook/step-08-cta-recipe.md` CT.1)*
- [ ] **Plumbing, ask by ask.** For each row asking for a keyword comment, a DM, a bio link, a
      site visit or event attendance, the thing behind it exists and was **tested**. Not
      tested = step the ask down and say why in the row, or schedule the automation as a
      prerequisite in an earlier week. *(`playbook/step-08-cta-recipe.md` CT.2)*
- [ ] Cold traffic is matched to its **awareness level** — you don't hard-pitch strangers. *(traffic Secret #19)*
- [ ] **Caption CTA echo — countable.** Every reel row has a caption, and that caption ENDS by
      repeating the reel's own ask. Check it against the row's `cta` / `cta_type`: a reel asking
      for a comment whose caption asks for a DM is a contradiction, and a caption with no echo
      loses every viewer who read instead of listened. Fix = make the echo match the row's CTA.
      *(`playbook/step-08-caption-recipe.md` C.3)*

## Gate 6 — STRATEGY ADHERENCE (does the calendar deliver the strategy it declared?) · `gate_6_strategy_adherence`
*The plan states a strategy in Part A — this gate proves the Part C calendar actually EXECUTES it. A plan
that contradicts its own strategy fails.*
- [ ] **Subject:** is the whole plan about the correct SUBJECT (for an agency/manager, the CLIENT — not
      the account owner)? Positioning, audience and voice must be the subject's, never the owner's.
- [ ] **Goal:** does every reel serve the stated primary goal (Part A1)? A "reach" plan full of hard-sell
      BOF reels fails; a "leads" plan with no activation reels fails.
- [ ] **Funnel mix:** does the calendar's actual reach/nurture/activation counts match the declared TOF/MOF/BOF
      %? Count them. If A1 says 80/20/0 but the calendar is 50/30/20, fix one of them.
- [ ] **Goal-served lines add up to the declared mix — countable.** Every slot's Reasoning block
      names the goal it serves (Reach / Engagement / Leads). Count those lines by goal and check
      the totals against the funnel mix you just counted. They are the same slots described two
      ways, so a disagreement means one of the two is wrong. An anchor-week slot cites its
      declared exception instead. Fix = correct whichever count is wrong.
      *(`playbook/step-08-reasoning-recipe.md` R.3)*
- [ ] **Audience:** does every reel serve the ONE target audience (Part A2)? Flag any off-audience reel.
- [ ] **Pillars:** does the reel distribution match the declared pillar % (Part A5)? Count per pillar.
- [ ] **Patterns:** are the levers used in the calendar the ones named in A3 (matched) and A4 (to test)? No
      orphan reel built on a lever the strategy never mentioned.
- [ ] **Positioning:** does every reel ladder back to the A0 positioning sentence — the
      `big_domino` when one exists (p08, FRFRMU-1040)?
- [ ] **Persona, when it exists (p09, FRFRMU-1043):** no reel contradicts `attractive_character`'s
      stance or uses a declared `avoid` word.
- [ ] **Positioning maturity:** if the account is young/unproven (positioning_status = hypothesis), does the
      month **test 2–3 distinct angles** rather than over-commit to one unproven line? A confirmed positioning
      may concentrate on one; a hypothesis may not.
- [ ] **Concentrate-vs-diversify is REASONED, not defaulted:** the pillar split fits THIS account's situation
      (has it found a repeatable hit yet? goal, stage, data confidence, capacity) and the reasoning is stated.
      No one-size ratio — a no-hit-yet account concentrates to find the vein; a proven account diversifies.
- [ ] **Format mix + recurring series:** the strategy states a **format %** (7.6) that fits what the
      creator can produce, and **1–2 recurring series** (7.7) — and the calendar delivers them.
- [ ] **Conflicts resolved by the PRIORITY order:** where data, positioning, and goal disagree, the plan
      follows **constraints/compliance > positioning > goal > raw data** — a viral pattern never overrides
      who they are, what they can't do, or the goal.

## Gate 7 — Data integrity (is "data-driven" actually true?) · `gate_7_data_integrity`
- [ ] Every recommendation reads **median**, not mean (mean is outlier-inflated).
- [ ] Every DATA-DRIVEN tag meets the bar: a median + a sample size at/above the threshold (n≈5), from the
      audience-matched slice. Anything thinner is DATA-INFERRED or JUDGMENT — never DATA-DRIVEN.
      **One earned exception (FRFRMU-995):** a `retrieved_exemplar` receipt (a real reel, found by
      `search_exemplars`, cited by `post_urls`) earns DATA-DRIVEN on **provenance**, not frequency — the
      reel demonstrably exists and performed, so an honest `n=1` is a real receipt here, not a thin one.
      This carve-out is scoped to that one kind; every other kind still needs the full n≥5 bar.
- [ ] No **judgment dressed as data** — every claim either cites a real tool result or is tagged JUDGMENT.
- [ ] **Receipt slice matches funnel role (G328):** every reel's receipt cites only source reels
      from the tag slice its funnel role maps to (PLAYBOOK Step 3's role→row mapping). A `reach`
      reel citing a receipt built from a slice its role doesn't include (e.g. `hidden_gem` /
      `comments_driven_post`) fails — and vice versa for `activation` reels citing reach-only
      slices. Overlap is fine: a tag shared by both rows (e.g. `high_reach_high_engagement`)
      is a legitimate cite for either role. Fix = re-source from the role's slice, or downgrade
      the reel to JUDGMENT.
- [ ] **A named sound carries its own receipt and its caveat.** Any row naming a specific track
      cites an `audio_trend` receipt (band, count, coverage figure, corpus label). The wording
      says **"rising among the accounts we track"**, never "trending on Instagram", and the
      coverage figure appears wherever a count does — the scraper often reports no sound, so a
      sound's absence proves nothing. A track with the `low_sample` band is never named as a
      pick, and any pick with no receipt behind it is tagged JUDGMENT.
      *(`playbook/step-08-audio-recipe.md` A.3/A.4)*
- [ ] **Every slot has a complete Reasoning block — countable, per slot.** Count the slots
      carrying all three lines: the receipts behind it, the expected outcome, and the goal it
      serves. A slot missing any one of them cannot explain itself, and a slot that cannot
      explain itself does not ship. Fix = write the missing line, or cut the slot.
      *(`playbook/step-08-reasoning-recipe.md` R.1-R.3)*
- [ ] **Receipts match provenance — the count must be ZERO.** Count the slots tagged
      `data_driven` that do not carry the receipts for the claims they make. That count must be
      zero. A `judgment` slot must carry the tag and no faked receipt; nothing is left
      unlabelled. A slot whose claims outrun its receipts is the whole-plan honesty problem seen
      one slot at a time. Fix = attach the real receipt, or re-tag the slot honestly.
      *(`playbook/step-08-reasoning-recipe.md` R.1)*
- [ ] **Every idea carries a topic receipt — countable, per row.** Count the rows: each one cites a
      `topic` receipt (`topic_id`, `viral_instances` above zero, `distinct_accounts`,
      `hit_rate_band`) read from `get_topic_heat`, or the honest interim form (example reel URLs +
      tags) where the topic dictionary is still thin. The only row allowed no group behind it is a
      **declared test slot**, which must say it is a test and be tagged JUDGMENT. Fix = attach the
      receipt, downgrade the row to a declared test, or cut it.
      *(`playbook/step-05-differentiate.md` 5.2/5.2a)*
- [ ] The provenance split (Part E1) is honest COUNTS, not inflated.
- [ ] **Copy has research behind it (p04, FRFRMU-1035).** An `objection` beat or an
      `activation` reel with no `prospect_research` card anywhere in the plan is copy written
      cold — `check_research_behind_copy` flags this mechanically (advisory today, under
      `PLAN_VALIDATOR_FOUNDATION_MODE`); fix = run Step 3.5, or cut the beat's objection claim.
- [ ] **Judgment is grounded — the count must be ZERO (FRFRMU-1024).** Count the `judgment`
      slots with no "grounded on: <data>" line (`rigor-rules.md` §J). Fix = name the nearest
      real data it extrapolates from, or re-source it as data-backed.
- [ ] **No slot is library-only or research-only, and no substance is DATA-DRIVEN (FRFRMU-1032).**
      A `pattern` receipt with no `substance` receipt is trending but not about the product;
      substance with no pattern is a bet (declared Step 7.4 test only); substance is always
      `first_party`/`from_expert`, never a frequency claim. `check_slot_has_both_receipts` +
      `check_substance_not_data_driven` flag these. Fix = run `step-08-join-recipe.md`.
- [ ] **A "checked X" claim names its call (§K).** `distribution.posting_time`'s `checked_*` status needs a real `get_posting_time_performance` call this session (`claim_backed_by_call`), or say `not_checked`.

## Gate 8 — Deliverable feasibility & variety (the calendar must actually SHIP) · `gate_8_feasibility_variety`
- [ ] **Total effort ≤ capacity:** each week's summed effort (heavy/medium/light) fits what the creator can
      actually produce — no un-shippable weeks.
- [ ] **Plan-size honesty:** if the data supports fewer strong reels than requested, the creator was told +
      offered (more data / upgrade / labelled stretch) — **no reel padded to hit a number** or dressed as
      data-driven when it's a stretch.
- [ ] **Activation plumbing:** no keyword-DM / lead-magnet reel appears unless the funnel assets exist
      (Step 1) and there's reach to convert (Step 4). Cold accounts = reply-bait only.
- [ ] **Variety / no fatigue:** CTAs vary (not every reel "comment X"); hook types vary across the plan; no
      two of the creator's OWN reels are near-identical (self-cannibalization).
- [ ] **Cooldown honored — countable, topic by topic.** Take the cooldown list Step 5.1 built and
      check it against this plan's topics. Count the repeats. Every repeat must be one of three
      things: a **named series**, a **stated sequel** (the row says in plain words why the topic is
      back and what result brought it back), or a mistake. Anything else is a topic re-pitched by
      accident — the thing the creator notices before we do. A plan with **no** cooldown list must
      say which row of Step 5.1a it used and why there was nothing to read; silence here is a gate
      fail, not a pass. Fix = drop the repeat, name the series, or write the sequel sentence.
      *(`playbook/step-05-differentiate.md` 5.1)*
- [ ] **≥3 distinct source accounts:** the receipts draw from at least three competitors, not one (a
      single-source plan is fragile + mimicry-adjacent).
- [ ] **Watch-these links — countable, per row.** Every reel row's shooting direction carries at
      least **two** exemplar links from that slot's own format / delivery / funnel-role slice,
      each with its one-line note. Count them. And the direction must be filmable inside the
      row's effort budget — a twelve-line art-department brief for a phone shoot fails here.
      Fix = pull the links from the right slice, or say the slice was too thin and drop the list.
      *(`playbook/step-08-visual-recipe.md` V.2/V.4)*
- [ ] **Audience language:** the hooks/captions are in the audience's language, not assumed English.
- [ ] **Tags — countable, per row.** Every reel row carries **3-6 tags**, each one relevant to
      THAT reel, with its role nameable (niche / topic / series). Count them. A row above the
      niche's own tag-count norm, above the caption spam ceiling, or carrying an off-topic
      trending tag fails. The series tag must be identical on every reel of that series.
      Fix = cut the tags that describe no part of this reel.
      *(`playbook/step-08-hashtag-recipe.md` HT.3)*

## The countable-check registry — ONE list, so nothing is checked twice or not at all

> **Why this table exists.** Countable checks are now written across a dozen recipe files. Built
> independently they drift: the same rule ends up counted two different ways in two places, or a
> rule everybody assumed was covered turns out to be covered nowhere. This table is the single
> list. **A check that exists in a recipe but not in this table is treated as unbuilt** — add the
> row when you add the rule. Same single-door principle as the read gate.
>
> **"Where it runs" is the important column.** Three different things can enforce a rule and they
> are not interchangeable. A **validator check** is code: `validate_content_plan` runs it and a
> blocker-capable one stops the plan (Step 11.0). A **gate box** is you, walking this file, and it
> is recorded in the `rules_gate` object. A **save-time check** runs when the plan is stored. If a
> row says "gate box", nothing in the code will catch it for you.

**The table itself — every row, in full — lives in `RULES_GATE_REGISTRY.md`, right next to this
file.** It was split out 2026-09-07 (FRFRMU-1032) purely to keep this file under the 300-line
skill limit; nothing about the checks, their names, or which gate owns them changed. Open that
file for the actual list — this file only explains what the columns mean and the rule above
("a check that exists in a recipe but not in this table is treated as unbuilt").

## How to run the gate
1. Draft the plan in the TEMPLATE shape.
2. Walk Gate 1 → 8. For each failing item, note the reel/section and the fix.
3. Apply the fixes and re-draft.
4. Re-run the gate. Repeat until **every box passes**.
5. **Record the result twice — as data AND as prose.**
   - **As data:** build the `rules_gate` record described in PLAYBOOK Step 11 — one entry per gate,
     using the eight ids above — and send it to `submit_content_plan` (Step 12). This is what makes
     the gate auditable later: a gate you never walked shows up as missing, and a `pass` you claim
     over a real blocker is recorded as a contradiction. (G650)
   - **As prose:** the short human verdict + what changed, in Part E2 — on top of the record, not
     instead of it.
6. Only a gate-passed plan is shown to the user.

**A fresh-eyes critic (PLAYBOOK Step 11) runs this same gate — never let the plan's author be the only one
who checked it.**
