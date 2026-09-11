> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 2 — Find benchmark accounts (Apify discovery — runs for EVERY plan)

**Ask per `asking-rules.md`.**

**Trigger:** after Step 1, ALWAYS check the benchmark set — `get_workspace_stats` +
`get_analysis_coverage`. An empty workspace needs a full set; a populated one should
still be **refreshed** (niches drift, accounts go stale). Never plan off a thin or
stale benchmark set.

**The SUBJECT drives discovery.** Seed everything off the subject's niche from Step 1
(their handle, topics, hashtags, and the 2–3 accounts they named) — for an agency
that finds the **client's** competitors, not the agency's.

**Seed from the congregation map, when it exists (p03, FRFRMU-1033).** If the Creator Brief
carries a `congregations` card, run the Apify hashtag/search angles (below) on ITS named
hashtags and keywords first — a grounded first pass instead of a guessed niche word. Tag these
seeds `web_research` provenance. No `congregations` key → seed from the niche label alone,
exactly as today.

**The honest state of discovery — TWO sources, in this order.**

1. **`discover_accounts` FIRST — free, read-only.** It returns only accounts Reach Machine
   has **already collected real data for**. It does NOT search Instagram, so it comes back
   empty for any niche we have not covered yet. Empty is normal, not an error.
2. **Then Apify, for a LIVE Instagram search** — the plugin ships an `apify` MCP connection
   and the creator signs into **their own Apify account** (browser sign-in, no token to
   paste). This is what actually powers angles A–F below against real Instagram.

   🔴 **Say the sign-in path OUT LOUD, in these words, the first time discovery runs in a
   session — do not keep it to yourself (G366).** Tell the creator: *"Instagram search runs
   through Apify, which is a separate one-time sign-in from Reach Machine. Run `/mcp`, pick
   the `apify` server, and sign in in the browser. If you don't have an Apify account,
   making one at apify.com is free. There's no API key to paste and no `.env` file."* Then
   wait for them. Never let a creator meet the STOP rule below without first having been
   told how to get past it.

🔴 **Apify spends the creator's OWN money, and Reach Machine cannot see or stop it.** RM
credits, the spend ceiling and every confirm-before-spend guard in Step 3 rule 6 govern
**RM** tools only. An Apify scrape is billed by Apify to the creator directly. So treat
every Apify call as a spend gate you enforce yourself: say which angles you plan to run and
roughly how many scrapes that is, and **WAIT for an explicit yes**. Never run a batch of
Apify calls off one vague approval.

🔴 **If Apify is not connected, STOP — do not substitute anything (G332, founder decision
2026-08-19).** A generic web search is NOT a valid substitute. If `discover_accounts` is
empty and Apify is unavailable, unreachable, or the creator declines the spend, say plainly
that you cannot do Instagram discovery right now and why — then stop. Do **not** quietly run
a web search and present its results as benchmark accounts. Do **not** invent handles. The
propose-from-seeds fallback below is **opt-in only**: offer it in one line, and use it solely
if the creator explicitly asks, labelled to their face as **unverified suggestions, not Reach
Machine data**. Any run that degrades from a live source must say so out loud, every time —
never silently.

**The Step 2 flow:**
2.0. **Order by cost (FRFRMU-1034).** Do NOT bootstrap discovery by analysing a guessed seed
   twice — that pays for analysis (the slow, expensive step) twice and a bad first guess gets
   amplified on the second round. Sequence instead: **(a) web-first seeds** from the
   congregation map when it exists (2.1 below); **(b) pull + analyse that set ONCE** (2.8);
   **(c) refine for FREE from the winners** (2.9) — captions, in-caption hashtags and
   transcripts of reels you already paid to analyse cost nothing extra to read; **(d) expand
   only when the data says coverage is thin**, never as a habit (see 2.9's expansion note).
2.1. **Seed** from the subject — niche, handle, named accounts, core hashtags.
2.1a. **How WIDE to search — decide it, and SAY it, before any Apify call (FRFRMU-1151).**
   Benchmarks exist to harvest PATTERNS, not just to find people nearby — a hook or a
   structure that works in one city works in another. So the search radius is a real
   decision, not an afterthought. Using what Step 1 already knows (is the business tied to
   a place, and which country?), pick one of three settings:

   | Business | Setting | What it means |
   |---|---|---|
   | Online / no fixed place | `niche_wide` | The niche across the creator's country; no place words in any seed |
   | Tied to a place (any town size) | `niche_wide` **+ local sample** | Nationwide seeds for patterns, PLUS one or two local scrapes for market intel |
   | Creator insists on local only | `local_only` | Allowed, never the default — say in one line why it teaches fewer patterns |

   **Say the choice inside the existing spend-gate sentence above** ("say which angles you
   plan to run … and **WAIT for an explicit yes**") — do not ask a second time. Example:
   *"I'll search fitness across Canada for patterns — angles A, B, E, about 5 scrapes — plus
   one local search for Courtenay to see who's active near you. OK?"* If the country isn't
   known yet, ask once: *"You're in Canada — search Canada-wide?"* Never guess the country
   silently.

   **Two seed lists, same tools, same yes.**
   - **Niche-wide seeds** = the niche hashtags/keywords with the place word REMOVED
     (`#semiprivatetraining`, "semi-private personal training").
   - **Local seeds** = place + niche, e.g. `instagram-search-scraper` →
     `{"search": "Courtenay gym, Comox Valley fitness", "searchType": "user", "searchLimit": 10}`
     and `instagram-hashtag-scraper` →
     `{"hashtags": ["courtenayfitness"], "resultsType": "reels", "resultsLimit": 10}`. Same
     root-shape rule as every Apify call in 2.2 below — no `args` wrapper.
   - The local sample is capped at about **6-10 accounts read** — one or two extra scrapes,
     inside the same yes.

   **The local sample is READ, not ADDED — this keeps "no new spend" true.** Adding an
   account costs RM credits and one of the 25 competitor slots. Instead run
   `instagram-profile-scraper` → `{"usernames": ["<local candidate handles>"]}` and only COUNT from the reply:
   accounts found, how many posted in the last 60 days, how many use reels at all, median
   followers. **If a post's date or type is missing from the reply, write `unknown` — never
   infer it** (same honesty rule the dossier already applies to paid traffic). Only a local
   account that also passes 2.3's FIT filter becomes a benchmark.

   Two more honesty rules:
   - A place-word search can return accounts that are not actually local — count only the
     ones whose bio/location text confirms the place, and say the confirmed number ("6
     found, 4 confirmed local").
   - The local field may be alive on Facebook, not Instagram — the sentence always says
     **"on Instagram"**.
2.2. **Expand — the STANDARD discovery angles (run every one that applies, then dedupe across
   them).** Same set every run, so discovery is consistent for any account or niche. Each angle
   names the Apify tool that does it — call these **bare**, never with a hardcoded `mcp__…`
   prefix, because the prefix differs on a customer install — **and put their input at the
   ROOT of the call, as an object.** Apify actors do NOT use Reach Machine's `args` box, and
   never take a JSON string.

   - Reach Machine tool: `search_watchlist` → `{"args": {"page_size": 100}}`
   - Apify actor: `instagram-hashtag-scraper` → `{"hashtags": ["yoga"], "resultsType": "reels", "resultsLimit": 20}`
   - `instagram-search-scraper` → `{"search": "yoga studio", "searchType": "user", "searchLimit": 20}`
   - `instagram-profile-scraper` → `{"usernames": ["humansofny"]}`
   - `instagram-scraper` → `{"directUrls": ["https://www.instagram.com/reel/<id>/"], "resultsType": "posts", "resultsLimit": 1}`

   `waitSecs` caps at 45. If the validator says *"root: must have required property
   `hashtags`"* (or `usernames`), you wrapped the input — unwrap it; the tool is fine.

   - **A · Hashtag → top posts → authors** — the accounts winning on the subject's core niche
     hashtags. → `instagram-hashtag-scraper`
   - **B · Viral reel → its author** — the highest-view reels on those hashtags/keywords, then add
     who made them (proven performers, not just active accounts). → `instagram-hashtag-scraper`
     to find them, `instagram-scraper` for the reel's owner.
   - **C · Collabs & tags on a viral reel** — its coauthors + tagged accounts (`coauthorProducers`
     + `taggedUsers`); check each for relevance and add the fits. → `instagram-scraper`
   - **D · Similar / related accounts** — Instagram's own "related profiles" off each strong seed.
     🔴 **NOT covered by the bundled Apify tools.** Say so if you skip it; do not fake it by
     guessing which accounts are "related".
   - **E · Keyword search** — the niche terms → more accounts + hashtags.
     → `instagram-search-scraper`
   - **F · Trending-audio page** *(optional)* — accounts riding a niche's trending audio now.
     🔴 **NOT covered by the bundled Apify tools.** Same rule as D — skip it and say so.
   - **G · Indirect competitors — ask, never search.** Ask ONCE: *"Who else gets your customer's
     money for the same problem, even with a different product?"* Take 1-2 named handles from
     the creator only — never proposed by web search or by reading a rival's page (G332). Same
     2.4/2.5/2.7 gates as any other add, then tag the item `indirect` with `add_competitor_tags`
     so the dossier (`step-02-8-dossier.md`) and the plan can label its patterns "angle imports,
     not direct benchmarks".
   **Report which angles actually ran.** "Ran A, B, C, E; D and F are not available" is a real
   answer. Silently running two angles and calling the set complete is not.
   *(Opt-in fallback, only if the creator explicitly asks after being told Apify is unavailable:*
   propose ~8–15 candidate handles by applying A–F logics to the seeds + your knowledge, one line
   each on why it's a good role model, **labelled unverified**. Invalid handles cost $0 —
   Step 2.5 validates them.)
2.3. **Cheap PRE-filter — BEFORE spending a cent.** From the scraped/known metadata,
   drop brands, media companies, agencies, mega-accounts a small creator can't model,
   off-niche and inactive accounts. Rank by **FIT** (right size band, reels-active,
   niche match, engagement signal). **Benchmark for FIT, not fame** — a 10M celeb is
   mimicry bait (same anti-mimicry, stage-aware thinking as Step 4/Step 5).
2.4. **The human approves the shortlist** — never add an account the human didn't
   approve. A **human gate**, same weight as every other approval here.
2.5. **Add** with `add_to_watchlist` — it validates each handle on Instagram and only
   charges for real ones. **Confirm-before-spend is a human gate:** show the cost
   preview and WAIT for an explicit yes before `confirm=true` (same rule as Step 3.6).
   **Tag the breadth (FRFRMU-1151), same pattern as angle G's `indirect` tag.** Right
   after each confirmed add, call `add_competitor_tags(handles=[...], tags=["niche_wide"])`
   or `tags=["local"]`, merge mode — no new field, the existing 5-tag-per-competitor cap
   applies (`indirect` can sit beside it). **Read `dropped_over_cap` back and say so** if a
   customer's hand-made tags push the breadth tag out of the 5 slots.
2.6. **Filter on REAL metrics AFTER adding — the honest catch.** The true numbers
   (`follower_count`, `median_er`, `avg_views`) only exist once tracked. **One
   `search_watchlist` call already gives you most of them** — every account in its
   list comes back with `follower_count`, `median_er`, `engagement_rate` and
   `pulled_posts_count`. So read the list, and do **not** call `get_profile_details`
   once per shortlisted account: that is 8-15 separate round-trips to fetch numbers
   you were already handed. Ask for `page_size=100`, sort `follower_count_desc`, and
   let the server narrow the set with the `min_followers` / `max_followers` /
   `has_follower_count` filters; keep asking for the next `page` until you have as
   many accounts as the reply's own `total_count` says exist. Of the three numbers
   above only `avg_views` is missing from the list — call `get_profile_details` just
   for the few accounts where `avg_views` is genuinely what decides keep-or-drop.
   Then **drop the bad benchmarks** — `remove_competitor` is free, so cleanup costs
   nothing. Confirm with `get_workspace_stats`.
2.7. **Show the FINISHED set back to the customer — a second human gate, not just the
   shortlist one (G238).** After 2.6's filtering, list the surviving benchmarks for the creator —
   handle, why it was kept (the fit reason from 2.3, plus its real metrics from 2.6) — and ask
   plainly: *"Here's your final benchmark list — does this look right to you?"* Then:
   - **If they say yes** — move on to 2.8.
   - **If they object to one** (e.g. "that account isn't really like me") — ASK why, then decide
     for real: if their reasoning holds, drop it (`remove_competitor`, free) and say so; if you
     still think it belongs, SAY YOUR REASONING BACK to them plainly (the real metric or fit signal
     that kept it) rather than silently complying OR silently ignoring them. Never just remove an
     account to avoid a disagreement, and never keep one without explaining why once challenged.
   - **If the set looks thin or off after this conversation**, treat it like Step 2's other edge
     cases — widen the niche, re-run discovery, and say so — don't proceed on a set the human
     doubts.
   - **Group the readout by breadth, and save `benchmark_breadth` (FRFRMU-1151).** List the
     surviving set as "nationwide (18) / local (2)" using the 2.5 tags. Save a plain Creator
     Brief field (`update_creator_brief`, **not** a Foundation card — there is no allowlisted
     card shape for this) named `benchmark_breadth`:
     `{"value": {...}, "source": "derived", "confidence": "high"}`, value holding `decision`,
     `country`, `local_market`, `niche_wide_count`, `local_found`, `local_confirmed`,
     `local_active_60d`, `local_using_reels`, `local_median_followers`, `local_field`
     (`weak | active | not_sampled`), and `opportunity` — one plain sentence carrying the
     numbers, e.g. *"Of the 6 gyms in Courtenay posting on Instagram, 4 have not posted in 60
     days and none uses reels — that is an open lane."* **`local_field` is `weak`** when fewer
     than half the confirmed local accounts posted in the last 60 days, **or** none of them
     uses reels — say so, because a weak local field IS the opportunity, not a data gap.
2.8. **Pull + analyse — same confirm gate.** `pull_data` → `run_pipeline` (or
   `run_pipeline_by_category` for the viral tier), the confirm-before-spend gate on
   every call. Check `get_analysis_coverage` after — and show the plain-English tag
   digest (Step 3 rule 7, FRFRMU-1017) once the pull completes, before any
   analysis-spend decision.

2.9. **Refine from winners (free), then decide on expansion (FRFRMU-1034).** Once 2.8's pull +
   analysis is done, read the winners' `content` captions (in-caption hashtags included — HT.2
   in `step-08-hashtag-recipe.md` already reads these), and `get_post_transcript` for their
   spoken words — all free, already paid for. Feed anything in-niche back into the
   `congregations` keyword list, tagged `winner_data` provenance, and list any adjacent handles
   you noticed (mentions, collab partners, recurring shared tags) as CANDIDATES ONLY — they
   still go through 2.4's human gate and 2.5's spend gate like any other account, never added
   directly from this step. **Expansion is manual, on request — never automatic.** A second
   discovery round is not run by default; only run one if the creator asks for more competitors,
   or once a sample-size sufficiency check exists (tracked separately, FRFRMU-1019 — not built
   on this branch) and reports thin coverage. Bounded by the plan's competitor cap
   (FRFRMU-1010) either way — seed well the first time.

**Quoting a healthy account's cadence — say the rhythm, not just the count.** When you tell the
creator what a good account in their niche sustains, quote **how often AND how steadily**.
`get_profile_posts` returns `posting_consistency` in its `account_metrics` block, right next to
`post_frequency_weekly`: **lower means more regular** (about 0.2 is clockwork, about 0.6 is
normal, 1.0 and above is bursty). Two accounts both posting "3 a week" can be completely
different to copy — one posts Monday, Wednesday and Friday; the other posts nine reels in three
days and then goes quiet for three weeks. So write *"3 a week, clockwork"* or *"3 a week on
average, but bursty"*, never a bare "3 a week". It comes back empty for accounts we hold too few
posts for — then give the frequency and say the rhythm is not known yet. It describes a rhythm,
it does not grade one: a bursty account may be running campaigns on purpose.

**Step 2 edge cases:**
- **Tiny niche** — if A–F discovery + the fallback yield too few FIT accounts (say < 5), **widen to
  the nearest adjacent niche** and **tell the user you did**; never force a plan on 2–3 competitors.
- **Operational limits** — only ONE pipeline run per workspace at a time (if one's active,
  `stop_pipeline` it or wait), a run caps at **25 reels** (re-call `run_pipeline_by_category` until
  `remaining_after_this_run` is 0). **In assist mode dispatch about 8 reels at a time, not 25** —
  see rule 6e in `playbook/step-03-mcp-spend-and-progress.md`. Spend tools **refuse when credits
  are short** (relay it). If you
  can't analyse everything you'd like, **proceed on what's already analysed and SAY SO** — don't stall.
- **Dead accounts** — an account that validates on add but returns no usable reels (private, deleted,
  inactive) → drop it like a bad benchmark (`remove_competitor`, free).
- **Stale set** — treat a benchmark set as stale if it hasn't been refreshed in ~30–60 days or the
  niche has visibly moved; re-run the discovery angles then.

**Then continue to Step 3** with a fresh, fit benchmark set.

---

