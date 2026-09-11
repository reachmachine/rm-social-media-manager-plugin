> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 3 — Use the RM MCP correctly (tool-usage rules)

0. **Check for a leftover selection from an earlier session BEFORE you scope anything
   (FRFRMU-1120).** `get_data_sources` returns `selection_health` — `active`, `saved_scope`,
   `saved_count`, `unresolved`. If `active` is true and it is not what you meant to scope this
   run to, say so out loud and call **`clear_data_selection`** before reading anything else. A
   saved selection only narrows the scope it was saved for (never a mismatched `scope='niche'`
   call) and any tool applying it now says so in its own `notes` — but the safest habit is
   still to clear a leftover set rather than rely on every tool remembering to mention it.
1. **Workspace + subset — scope the data DELIBERATELY, the SAME way every run (this is the
   standard; do it identically for every account + niche).** Confirm the active workspace.
   Filter competitors to the **right modelling set** — solo creators for a personal brand;
   move corporate brands + media to a "news radar" (topic ideas), never model reel structure
   on them. **How to scope — use these tools every time:**
   - **One account** (the creator themselves, or a single competitor): pass **`usernames=[handle]`**
     to any insight tool (`get_content_strategy` / `get_hooks_library` / `get_content_structures` /
     `get_cta_library` / `get_content_breakdown`), OR call **`set_data_selection(scope='mine',
     filters={usernames:[handle]})`** so every following read defaults to it.
   - **A hand-picked GROUP of videos:** `set_data_selection(filters={post_urls:[…]})` (or
     `get_content_breakdown` with `filters.post_urls`).
   - **A profile's full post list + cadence:** `get_profile_posts(profile_id)` (the watchlist UUID,
     not the @handle).
   - **Reset when done:** call **`clear_data_selection`** before the next step, so a scoped set never
     silently leaks into an unrelated read.
   **Standardising the SCOPE does NOT lower quality — that is the point.** Inside *any* scope the same
   rules always apply: cross-tabs (§C), **median** not mean, audience-weighting (§F), provenance tags
   (§I), and the **sample-size guard** — a thin scope → widen + mark low-confidence (§B), never forced
   into a confident claim. Same rigour, any account, any niche, any business, whoever runs it.
2. **Coverage before insight — and analyse the subset each FUNNEL ROLE needs (G328).** Call
   `get_analysis_coverage` (it breaks down by performance tag). RM's insight tools only
   see **analysed** reels, so spend the analysis budget on the reels that teach **this
   goal** — not always "viral." Map the goal → the tag subset below, check its coverage,
   and if it's thin, analyse **that subset first** via `run_pipeline_by_category` /
   `query_posts_by_tag` (small **calibration batch** → read the **real** cost from
   `get_credit_usage`, the worst-case *hold* is ~20× the real charge, then scale). This
   feeds the strategy you build in Step 7.

   **Goal → tag subset to analyse — HEALTHY TAGS ONLY** (these are the tags the audit
   confirmed classify reliably; the buggy ones are DEFERRED below until their fix ships):

   | Goal | Analyse (healthy tags) | Anti-pattern |
   |---|---|---|
   | Reach / awareness | `viral_3x`, `viral_2x`, `high_reach_high_engagement`, `high_views`, `reach_only`\* | `low_performance` |
   | Engagement / community | `high_reach_high_engagement`, `excellent_er`, `good_er`, `comments_driven_post`, `hidden_gem`, `polarizing` | `reach_only` |
   | Leads / DMs / conversions | `comments_driven_post`, `excellent_er`, `hidden_gem` | `reach_only` |
   | Authority / saves | `hidden_gem`, `excellent_er`, `utility_content` | `reach_only` |
   | Sales / direct response | `excellent_er`, `high_reach_high_engagement` | `low_performance` |
   | Shareability / word-of-mouth | `shares_driven_post`, `high_reach_high_engagement`, `viral_2x` | — |
   | Retention / watch-time | `top_25_rewatch_driven`\*\* | — |
   | Repost / quick wins | `hidden_gem`, `good_er` | — |

   \* `reach_only` under the **reach** ROLE only — study it for what triggers the *initial view*
   (hook / topic / first frame), but weight `high_reach_high_engagement` higher, because
   engagement is what *sustains* reach. For every other role's slice `reach_only` is an anti-pattern.

   \*\* `top_25_rewatch_driven` is now LIVE (G107 shipped 2026-07-25) — the rewatch/share driver is
   decided **per post** now, not by one dataset-wide correlation (G112), so a real per-post receipt is
   possible again. **Caveat you must state plainly:** the tag only exists on reels analysed AFTER the
   2026-07-25 deploy — older reels won't carry it until a re-tag backfill runs, so don't assume every
   reel has it; check for it, don't guess it in. **`rewatch_driven` itself stays off the map** — cite
   `top_25_rewatch_driven` only (see the deferred list below for why).

   **Apply the table PER FUNNEL ROLE, not once per plan (G328).** The plan's goal is the
   PARENT; every reel also carries a funnel-role SUB-GOAL — `reach` / `nurture` /
   `activation` (Step 8, item 2) — and a reel's data must come from the slice that matches
   ITS role, not the plan's headline goal. Map each role to a row of the table above:

   | Funnel role (sub-goal) | Which row of the table to use |
   |---|---|
   | `reach` (TOF) | ALWAYS the "Reach / awareness" row — whatever the plan goal is |
   | `nurture` (MOF) | "Engagement / community" row by default; "Authority / saves" row when the plan goal is authority |
   | `activation` (BOF) | The plan goal's own row (leads → "Leads / DMs / conversions"; sales → "Sales / direct response"; authority → "Authority / saves"). A reach-goal plan keeps minimal/zero BOF (Step 8, item 2) — any activation reel it does contain sources from the "Leads / DMs / conversions" row, never the Reach row (activation is conversion by nature) |

   **What to analyse = the UNION of those rows, budgeted by the mix %.** Take every role the
   plan's mix will contain, union their rows' tags (a tag shared by two roles — e.g.
   `high_reach_high_engagement` — counts ONCE), and split the analysis budget roughly by the
   mix. Worked example: a 40/35/25 Leads plan spends ~40% of the analysis budget on the Reach
   row (`viral_3x`, `viral_2x`, `high_reach_high_engagement`, `high_views`, `reach_only`) and
   ~60% on the Engagement + Leads rows (`comments_driven_post`, `excellent_er`, `hidden_gem`,
   `good_er`, `polarizing` — the shared tags dedupe). Because the rows overlap, a plan
   analyses ~1.5–2 subsets' worth of tags, not 3 — the mix-% budgeting keeps cost
   proportional, and the calibration-batch + confirm-before-spend gates (rules 6/6a) still
   cap every spend.

   **Which mix, this early?** Step 3 runs before the real TOF/MOF/BOF mix is set (Step 7.1 /
   Step 8 item 2). Budget from the goal-conditioned DEFAULT mix directions already stated in
   Step 8 item 2 (reach goal → TOF-heavy; leads → shifted toward MOF+BOF; authority →
   MOF-heavy) — do not invent a different prior. When Step 7.1 finalises the real mix, if it
   adds a role or materially grows one whose slice coverage is thin, come back through this
   rule for that role: coverage check → calibration batch → confirm gate → top-up. Never
   silently keep building on the provisional slice.

   **Anti-patterns are per-ROLE too.** The `reach_only` footnote above already works this
   way: study `reach_only` under the `reach` ROLE only (what triggers the initial view); for
   `nurture`/`activation` slices it stays an anti-pattern. Same for the rest of the
   anti-pattern column — read it against the role's row, not the plan goal's row.

   **Check coverage PER ROLE.** `get_analysis_coverage` breaks down by tag — read it per
   role's tag set. One role's slice can be healthy while another's is thin; a thin role
   slice widens + gets marked low-confidence (§B/§F) for THAT role's reels only.

   **This is coverage — "is there anything here." Before sizing any batch, also run rule
   2a in `step-03-mcp-sufficiency.md` — "is it ENOUGH to trust" (FRFRMU-1019). Never ask
   the creator to pick a raw reel count; that rule turns coverage into a reliable/
   directional choice instead.**

   **Illustration vs control — two different jobs.** 3–5 flop reels show what failure looks
   like (illustration; still fine, still cheap). They can NEVER tell you whether a winning
   pattern is *distinctive* or just *common* — for that you need a base RATE from a bounded
   random sample (~40/account, config-driven), because `low_performance` is ~62% of posts and
   a hook present in the winners AND in 15 of 40 flops is the niche's wallpaper, not a success
   pattern. Analysing the whole 62% stays banned (cost) — the sample is the statistically
   correct middle.

   **The base-rate layer is live** (founder decision 2026-09-02): per account in the modelling
   set, `run_pipeline_by_category(category='low_performance', usernames=[handle])` — the
   backend draws the bounded random sample itself, and the normal confirm-before-spend gate
   (rules 6/6a) STILL applies; never bypass it. Then read the `flop_base_rate.summary` on each
   pattern and treat `discriminates: false` patterns as non-recommendations even if their
   winner numbers look strong; cite the summary sentence ("appears in 8 of 10 winners, 15 of
   40 flops") on any receipt that uses the pattern. A `discriminates: null` means the flop
   sample is still too small to judge — say so rather than guessing. (Fields can be absent on
   an older stored payload for a short while; scoped per-account reads compute live and always
   carry them once flops are analysed.)

   **What each tag means (reason with the MEANING; only ever SHOW the friendly label — never a
   formula, §7). 🔴 AGENT REASONING ONLY — never quote this block, its numbers or its percentiles
   to the creator (FRFRMU-1017); the user-facing label→meaning table with no numbers is in rule 7
   of `step-03-mcp-spend-and-progress.md`, use that one when talking to a person:**
   `viral_3x`/`viral_2x`=each account's top ~1% / ~5% by views (account-relative) ·
   `high_reach_high_engagement`=lots of views AND engagement (the best of both — a clean, reliable tag) ·
   `high_views`=top-quartile views · `reach_only`=reaches but doesn't make them interact ·
   `hidden_gem`=low views but high engagement (underrated) · `low_performance`=below average on both ·
   `comments_driven_post`=comments drove it (the DM/lead gateway) · `shares_driven_post`=shares drove it
   (word-of-mouth) · `excellent_er`/`good_er`=engagement rate in **your set's** top-10% / top-25%
   (RELATIVE to the competitors you track — NOT an absolute industry %) · `utility_content`=save-worthy /
   useful · `polarizing`=divisive, drives comments/debate.

   **⛔ DEFERRED/BANNED tags — do NOT use in the map or on a receipt:**
   `high_reach` & `high_engagement` (G109 — silently dropped from the best posts) ·
   `rewatch_driven` (kept off-limits on purpose — see the retention row above: its narrower sibling
   `top_25_rewatch_driven` is the live, citable tag now, `rewatch_driven` itself is not) ·
   `high_roi` & `highly_efficient` (G108/G111 — collinear with `excellent_er`, use ER instead) ·
   `needs_improvement` & `likes_driven_post` (G111 — fire on ~65% / ~82% of posts, uninformative) ·
   `unhealthy_account`/`*_account` (G110 — account-level, unreliable from missing data; do not filter
   benchmark accounts on it in Step 2). **When a gap closes, move its tag(s) from here into the map above.**
3. **Right benchmark lens — pick the `analysis_mode` that answers your actual question.**
   `query_posts`, `query_posts_by_tag`, `get_tag_stats`, `get_avg_scores` (plus
   `get_analysis_coverage`) all take an `analysis_mode` with **FOUR** real values (verified against
   the live tool schema). **None of the four normalize for follower count** — a small account's best
   post can still look weak next to a huge account's, in any `cross_account` variant:
   - **`per_account`** (default) — each post ranked only against that SAME account's own posts.
     Never compares across accounts by size.
   - **`cross_account`** — every tracked post ranked against every other TRACKED post — comparable
     across your watchlist, but skewed toward whichever tracked account posts the most / biggest.
   - **`community_per_account`** — same as `per_account`, but the ranking pool also includes your
     niche's community picks as extra context, not just this account alone.
   - **`community_cross_account`** — same as `cross_account`, but the pool is your tracked accounts
     PLUS your niche community — bigger and more representative than `cross_account` alone, though
     still not follower-normalized.
   Prefer `cross_account` (or a `community_*` variant once niche picks exist) over raw `per_account`
   mega-views for a size-fairer read, then apply the Step 4 stage ladder on top for the rest of the
   fairness work. **The lever tools take no `analysis_mode` at all** (`get_content_breakdown`,
   `get_content_strategy`, `get_hooks_library`, `get_content_structures`, `get_cta_library`) — that's
   expected, not a bug: they aggregate classification fields, not performance tags (G116).
4. **Pull the levers — and MODEL THEM FOR THE TARGET AUDIENCE.** `get_content_strategy`,
   `get_content_breakdown`, `get_hooks_library`, `get_content_structures`, `get_cta_library`.
   Read by **median** per dimension value (not the outlier-inflated mean). **Filter the
   breakdown by the target-audience macro** — `get_content_breakdown` with
   `filters.audience=[segment]` — so the winning **hook / structure / CTA / topic** are the
   ones that work for THIS audience, not the niche average. Apply the **§F sample-size guard**:
   if the segment is thin (< ~5–8 reels), widen to the adjacent/on-ramp audience or the whole
   board and mark it low-confidence. Note the split: a high-volume **base** lever vs. a
   huge-reach **swing** lever.
5. **Hooks — pull ALL templates, find what went VIRAL, and REASON.** From
   `get_hooks_library` pull every hook **template + category with its view performance**;
   identify which templates/categories have **gone viral** (highest **median** views for the
   goal + target audience), and for each winner write a one-line **reason it works** that you
   carry into Step 7 (patterns matched) AND every calendar reel's 4-layer hook + receipt —
   **never a hook without a "why this, here."** Then `query_posts_by_tag` (the tags of the ROLE
   the reel will serve — the rule-2 role→row mapping above) →
   `get_post_transcript` on the top reels for the exact wording and the **retention** data
   (`beats` / `segments` / `template_structure` — the watch-time proxy, since RM can't scrape
   competitor watch-time). **Pull those transcripts ONCE PER ROLE and re-use them — rule 5a below.**

   **The hooks library is TAG-BLIND (G116):** `get_hooks_library` cannot filter by performance
   tag, so in a leads-focused workspace its winners are silently dominated by lead-pattern
   reels. Before citing a hook winner on a reel's receipt, cross-check it against that reel's
   ROLE slice — against the role's **source table** (rule 5a), which you already built, not a
   fresh per-reel transcript pull. A hook that only wins in the wrong role's slice is not a
   receipt for this reel.

   **Call `get_hooks_library` scoped, not blind.** Pass `usernames` (the tracked profiles this plan
   actually cares about) or a narrower `scope` — don't rely on one wide, unfiltered call. **If
   `top_templates` comes back empty on a workspace you know has analysed data** (check
   `get_workspace_stats` or `get_analysis_coverage` first if you're unsure), **that is G52, a known
   backend bug — not "this workspace has no hook data."** Do not silently proceed as if there's
   nothing to learn. Instead: (a) call `report_gap` once, briefly describing the empty result and the
   filter you used, so engineering has a live example; (b) re-query with a DIFFERENT filter (a single
   `usernames` entry, or `scope="niche"` instead of `"mine"`) before concluding the hooks layer is
   genuinely thin. Only after a re-query still comes back empty should you treat it as real absence of
   data and say so plainly in the deliverable's receipts section (not silently downgrade to
   judgment-only without a note).
5a. **Deep reads are PER FUNNEL ROLE, not per reel — build a SOURCE TABLE and cite it
   (FRFRMU-630).** `get_post_transcript` reads **ONE** reel (its own schema says so) and hands
   back a lot of text: the whole transcript, the caption, the on-screen text and the full beat
   breakdown. All of it then sits in this conversation for the rest of the run — the drafting,
   the rules gate, and up to three critic rounds (Step 11). One deep read per calendar reel
   would make a 30-reel plan roughly three times heavier than a 10-reel plan for no extra
   signal, because a plan has only **three funnel roles** however many reels it holds.

   **Do it this way instead.** For EACH funnel role in the plan's mix (`reach` / `nurture` /
   `activation`): `query_posts_by_tag` on that role's tag row, then `get_post_transcript` on
   **3-5** of that slice's top reels. Write each one into a small **source table** you keep in
   the conversation — one row per source reel:

   | role | @handle | reel URL | n | median views | reliability | the hook, in one line | structure / beats, in one line |

   That table is the only thing you carry forward. Once a row is written the full transcript is
   **dead weight**: do not re-read it, do not quote it back, do not fetch it again (the same
   discipline as rule 6e). Every calendar reel in that role then cites a ROW of this table.
   **Several reels citing the same row is correct and expected**, not a weakness — a receipt says
   where the pattern came from; it is not a claim that one source reel produced one idea.

   **🔴 A reel whose analysis failed says so — never fill in the blanks.** A
   `get_post_transcript` answer can come back with `degraded: true`. That means our analysis of
   that ONE reel broke (`degraded_stages` names the step, e.g. `transcription`), so the
   transcript, on-screen text and beats are empty because we have **no data** — not because the
   reel was silent or had no structure. When you see it:
   - do **not** quote a hook, a transcript or a structure from that reel, and do not guess one;
   - pass on the `degraded_note` line in plain words ("that reel's analysis failed at
     transcription, and the team has been told") and pick a different reel for the source table;
   - our team is told automatically — you do not need to report it, and you should not tell the
     creator to report it either.

   Lists behave differently on purpose. `get_posts_detailed` and `get_content_breakdown` leave
   broken reels OUT and tell you how many with `excluded_broken_reels`. If that number is above
   zero, say so when you cite the list ("12 reels, 2 left out — their analysis failed") rather
   than presenting the list as the complete set.

   **🔴 A receipt needs NO transcript at all.** Every field a receipt states — @handle, reel URL,
   `n`, `median_views`, reliability — already comes back from `query_posts_by_tag`, which returns
   username, url, engagement (views / likes / comments / shares) and tags for a whole LIST in one
   call. The transcript is only for the exact hook WORDING and the beat structure. So never call
   `get_post_transcript` just to write a receipt (Step 8 item 3).

   **🔴 The ceiling — at most 5 deep reads per role, and at most 12 for the whole plan.** There
   are always three roles, so this number does **not** grow when the creator asks for a bigger
   plan. **Check the source table BEFORE every new pull:** if a row for that role already covers
   the pattern, re-use it — a new pull has to earn its place.

   **What happens AT the ceiling — never silently.** If a role's table is full and a reel truly
   cannot be served by any row in it, do NOT quietly pull a 13th and do NOT quietly downgrade the
   reel. In this order:
   1. **Re-use the closest row and keep the receipt.** Its numbers come from `query_posts_by_tag`,
      which is not capped, so the receipt stays real. The reel's **hook wording** is now borrowed,
      so tag that hook layer **DATA-INFERRED**, never DATA-DRIVEN.
   2. **If the reel really needs its own wording, ASK** — one real either/or, in the style of rule
      6d: *"I've done the 12 deep reads this plan budgets. Reel N needs one more to be fully
      data-backed. Pulling more is free and spends no credits — it just adds a couple of minutes
      and a lot more text to our chat. Want me to, or shall I mark that reel's hook as my own
      judgement?"* Do what they say, and say which you did.
   3. **If nobody can answer** (a headless run), tag that hook layer **JUDGMENT** and name it in
      Part E2, "what we couldn't fully resolve" — an honest named limitation, never a hidden one.

   **This ceiling is NOT rule 6e's ~8-reel batch — do not merge the two numbers.** Rule 6e sizes
   an *assist-mode analysis dispatch*: that spends RM credits and drops 8 keyframe images per reel
   into the chat. This ceiling is on *free* transcript reads while drafting — no credits, just text
   and time. Different tool, different cost, different reason. They are independent numbers that
   happen to land close together.

5b. **DATA RECIPES — the named readings that must be RUN before a mix is stated.** They
   live in `playbook/step-03-data-recipes.md` (free reads, no credits): Recipe A sets the
   funnel mix by reading one performance quadrant at a time, Recipe B picks the delivery
   mix from what the market MAKES against what actually WINS. Load that file whenever
   Step 7 needs a % — a mix stated without its recipe is a guess with a number on it.

5c. **`search_exemplars` — the nearest proven hooks to ONE idea, by wording, not by category.**
   Free, read-only, scoped to this workspace unless widened. It answers a narrower question than
   `get_hooks_library` above: not "what template wins across the pillar" but "what real hooks,
   from real analysed reels, read closest to the exact line I am writing." Full recipe —
   including the absence fallback — lives in `playbook/step-08-hook-recipe.md` H.3b; this file
   is only the catalogue entry.

**Step 3 continues in `playbook/step-03-mcp-spend-and-progress.md`** — rules 6-8: confirm-before-spend, assist mode, the Sonnet sub-agent, credits not dollars, run progress, and Step 3's edge cases. Load it before any tool that spends credits.
