> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this at Step 2.2**, right after Step 2's search-radius decision (2.1a), before
> Step 2.3's band derivation. Split out of `step-02-benchmarks.md` (FRFRMU-1307/1312/1298) to
> keep that file under the 300-line cap and give Apify's whole discovery remit one dedicated
> home. **FRFRMU-1315 (2026-09-13) removed three angles from this file** — see below.

## Step 2.2 — Discovery: what Apify is for, and how

**Apify's whole remit, stated once, hard (FRFRMU-1312, founder decision).**
> *"plugin should use apify only for account discovery. apart from that it should only use
> reachmachine. reach machine has a process which is effective"*

| Job | Tool |
|---|---|
| Find candidate handles (keyword/profile search) | Apify |
| Pull a candidate's reels, once approved | Reach Machine (`pull_data` / `run_pipeline`) |
| Judge performance, decide what to analyse | Reach Machine |
| Everything from the watchlist onward (Step 2.5+) | Reach Machine |

**Apify finds handles. Nothing past a handle is Apify's job — and it never touches a reel or
a post to do it, for any reason (FRFRMU-1315, founder decision).**

**A consequence to state honestly, not hide.** An account's best work may be older than the
90-day window Reach Machine pulls, and we will not go back to Apify for it. Say so in these
words: *"Reach Machine can pull their last 100 reels or the last 90 days. This account's
biggest reel is older than that, so we will study their recent work and I will tell you that
is what the plan is based on."*

**Two stages, profile data first (FRFRMU-1307, founder decision).**
> *"is the plugin also scraping the reels in the profile? i think thats not required now. only
> if we finalize a profile we should scrap reels and then verify or take final decision.
> plugin is not supposed to pull any reels. … first only use profile scrapper and check the
> follower and engagement. based on this make a logical decision covering all the edge case."*

- **Stage 1 — screening.** Judging a discovered handle (is it real, and worth learning from?)
  reads `instagram-profile-scraper` ONLY. Follower count, engagement, and `latestPosts` are
  enough to judge a candidate. **No reel scraping to screen a candidate, ever** — never pull a
  candidate's own reel library via Apify to decide whether they belong on the shortlist. This
  is a JUDGMENT CALL on raw profile data, not the FIT filter — the real, structural verdict
  (`niche_fit_verdict`: direct / adjacent / off / unclear, FRFRMU-1528/1536) is computed
  automatically the moment the customer approves adding a candidate, by `add_to_watchlist`'s own
  screen (`screened[].niche_fit_verdict` in its response) — never re-implement that judgment
  here by hand.
- **Stage 2 — only after the customer approves the shortlist** (Step 2.4) do a candidate's
  reels get pulled, and by Reach Machine (`pull_data` → `run_pipeline`, Step 2.8) — **never by
  Apify.**

**🔴 The founder has closed the gap this file used to rely on (FRFRMU-1315, 2026-09-13).**
This section used to argue that a hashtag scrape or a single reel-URL lookup was still
"discovery, not screening" because it only found WHO posted or co-authored a reel, never
judged them. **The founder rejected that distinction, with the mechanical reason it does not
hold: a reel or post obtained through Apify never enters the Reach Machine pipeline, so it is
never processed or tagged — whatever the reason it was pulled.** The product ends up holding
raw data the rest of the system cannot use, and the same work is paid for twice. **The rule is
about the action, not the purpose.** So Apify never touches a reel or a post here, full stop —
no `instagram-hashtag-scraper` call, and no `instagram-scraper` reel-URL lookup. Three angles
that relied on those calls are gone: a hashtag's top posts, a viral reel's own author, and a
viral reel's collaborators/tagged accounts.

Say both stages out loud to the customer, so they know what is being spent and when — this was
tested live and caught a fake account (229,579 followers, 1 post) on profile data alone.

**The angle list, rewritten around what remains (FRFRMU-1315). In the order you run it:**

1. **`discover_accounts` — Reach Machine's own catalog, first.** Free, read-only, and every
   account it returns is already processed and tagged. This is the founder's *"this data can
   be fetched by the plugin"* — it leads every run now.
2. **`instagram-search-scraper` in user mode — keyword search → accounts.** The niche terms
   turn into candidate handles, nothing more (angle E below).
3. **`instagram-profile-scraper` — screen each candidate.** Followers, engagement,
   `latestPosts` (Stage 1 above) — never a candidate's own reel history.
4. **Once the customer approves the shortlist, Reach Machine pulls the reels** through the
   MCP tool (`pull_data` → `run_pipeline`, Step 2.8) — the only path where a reel gets
   processed and tagged.

**Say the cost of this out loud — do not paper over it.** The three removed angles were the
only routes to accounts with PROVEN reach: people who had already gone viral on the exact
terms searched. What remains — keyword search plus profile screening — finds accounts that
are active and on-topic, not accounts already shown to perform. Proof of performance now only
arrives later, at Step 2.6's post-pull screening (the typical-reel-views gate) — not at
discovery. **Tell the customer this plainly whenever a shortlist looks unproven**, for
example: *"This shortlist is active, on-topic accounts. None of them is proven viral yet — we
find that out once we pull their reels."* Never let a shortlist read as already vetted for
performance just because it came out of discovery.

**Find candidates yourself before handing the work back (FRFRMU-1298).** When our catalog
(`discover_accounts`) is empty, do not ask the customer for handles first — and by this point
the free `request_niche_data` collection is already filed (Step 2's opening, FRFRMU-1535); this
Apify pass is the "want it faster?" half, not the only road forward. Run the angles below and
aim for **at least 10 candidates** before you ask for anything. Per FRFRMU-1308 this is a target
to aim at, not a hard number: report honestly when a niche genuinely cannot fill it (see Step
2.3's thin-band sentences), and never invent a handle to reach 10.

**Expand — the remaining discovery angles (run every one that applies, then dedupe across
them).** Same set every run, so discovery is consistent for any account or niche. Each angle
names the Apify tool that does it — call these **bare**, never with a hardcoded `mcp__…`
prefix, because the prefix differs on a customer install — **and put their input at the
ROOT of the call, as an object.** Apify actors do NOT use Reach Machine's `args` box, and
never take a JSON string.

- Reach Machine tool: `search_watchlist` → `{"args": {"page_size": 100}}`
- Apify actor: `instagram-search-scraper` → `{"search": "yoga studio", "searchType": "user", "searchLimit": 20}`
- `instagram-profile-scraper` → `{"usernames": ["humansofny"]}`

`waitSecs` caps at 45. If the validator says *"root: must have required property
`usernames`"* (or `search`), you wrapped the input — unwrap it; the tool is fine.

🔴 **`search` (angle E, `instagram-search-scraper`) takes NO punctuation at all — not
even a hyphen or an apostrophe (FRFRMU-1280).** The actor validates each comma-separated
term against letters, digits and spaces only; a term containing any of
`! ? . , : ; - + = * & % $ # @ / \ ~ ^ | < > ( ) [ ] { } " ' ` (or a backtick) fails
before the search ever runs — confirmed against the live actor, which rejects with
*"Field input.search must match pattern..."*. Multiple terms are still fine, separated
by a comma: `"restaurant, restaurant prague"`. **Legal:** `"semi private personal
training"`. **Illegal:** `"semi-private personal training"` (hyphen). When a niche
phrase naturally has a hyphen or an apostrophe, just drop it — do not substitute an
underscore or any other symbol, that fails the same check.

🔴 **A search that dies part-way still needs an honest outcome, never a silent drop
(FRFRMU-1281).** The `apify` MCP server declares a `timeout` in `.claude-plugin/plugin.json`
(set well above the 317s failure this ticket was born from), but a per-server `timeout`
field is only documented for `.mcp.json` — Claude Code's plugin docs do **not** document
any timeout field for a plugin's own `mcpServers` entry, so do not assume it is honoured
here. If any Apify call (angle E's `search` included) dies or hangs past a reasonable
wait: **retry ONCE with a smaller `searchLimit`** (half of what you tried, minimum 5). If
the retry also fails, **say so out loud** — *"angle E timed out twice, I'm reporting it
as unavailable"* — and list it as unavailable in the "which angles actually ran" line
below. Never silently drop an angle the customer was told would run.

🔴 **Angles A, B and C are gone (FRFRMU-1315) — they scraped a reel or a post to find a
handle.** Hashtag → top posts → authors, viral reel → its author, and collabs/tags on a viral
reel all required `instagram-hashtag-scraper` or a reel-URL lookup on `instagram-scraper`.
Those calls are banned here now, for the reason stated above — never reintroduce them, even
to "just find who posted it".

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

**Report which angles actually ran.** "Ran E; D and F are not available" is a real answer.
Silently running nothing and calling the set complete is not.
*(Opt-in fallback, only if the creator explicitly asks after being told Apify is unavailable:*
propose ~8–15 candidate handles by applying the angle logics above (D, E, F, G) to the seeds +
your knowledge, one line each on why it's a good role model, **labelled unverified**. Invalid
handles cost $0 — Step 2.5 validates them.)

**Then continue to Step 2.3** for the size-band judgment and, if the niche is thin, the
escalation ladder.
