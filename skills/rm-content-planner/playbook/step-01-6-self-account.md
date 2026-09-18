> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 1.6 — The creator's own account is the strongest signal (once there's something to compare it to)

**Ask per `asking-rules.md`.**

A creator's own past reels — what already worked for **them** — beat a
competitor's pattern at the same sample size. Use that, but only once there's a
workspace to compare against.

- **Capture the subject's own @handle — ASK, don't assume.** **Check the Creator Brief FIRST**
  (`get_creator_brief`, field `instagram_handle`) — that's the value scoped to THIS workspace. Only if
  the Creator Brief has none, fall back to `business_profile.instagram_handle` **and confirm it out
  loud with the subject before trusting it** — that field is shared across every workspace on this
  account, so for a 2nd+ client it's very likely stale (someone else's handle). If neither has one,
  ASK the subject for their Instagram @handle. Then **look at the account** (niche, tone, follower
  count, what they already post) to ground the plan. **Save it to the Creator Brief**
  (`update_creator_brief`, key `instagram_handle`) — this is the authoritative, per-workspace copy.
  Also mirror it to `update_business_profile` for continuity with the web page, but never trust that
  copy back for a different workspace. It's needed for the self-baseline, discovery seeding (Step 2),
  and the bio / pinned reels in the deliverable. Don't ship a plan with a placeholder handle.
- **Guardrail — competitors first, always.** Only recommend adding the
  creator's own account to the watchlist **after** competitors are already
  analysed in the workspace. Never make it the first or only account in a thin
  or empty workspace. **Why, in plain words for the user:** a brand-new
  workspace guesses its niche from whichever accounts are already in it — if
  the creator's own account goes in first, it can set the workspace's niche
  wrong before there's any real competitor data to correct it.
- Once competitors are in place, confirm with the human which watchlisted
  account is theirs (or offer to add it), and treat that account as **"self"**
  in every pull that follows.
- **Weight self-patterns above competitor patterns of the same sample size.**
  If the creator already has 5 reels proving a pattern works for them, that
  beats 5 competitor reels proving it works for someone else.
- **Add the subject's own account to the watchlist and TRACK it.** Once competitors are
  analysed, add the subject's own account with `add_to_watchlist`, passing their handle in
  BOTH `handles` and `self_handle` (confirm-before-spend). Passing `self_handle` is what marks
  the row as theirs, permanently — the tool stores that on the row itself, so it is never
  confused with a competitor even if the handle in the Creator Brief changes later, and it
  never uses up a competitor slot on their plan. The Creator Brief's copy of the handle stays
  for display and search only. **This add is charged like any competitor add** (per-reel add +
  pull rates, plus analysis, at current configured rates). Say so out loud before they confirm:
  "adding your own account costs the same credits as adding a competitor — the scrape and
  analysis cost us the same either way." Then **pull + analyse their reels** (`pull_data` → `run_pipeline` /
  `run_pipeline_by_category`) so RM tags **their** reels by the same levers — then you can see
  **what works and what doesn't for THEM specifically**, not just what works in the niche.
  Scope to them with `usernames=[self]` / `set_data_selection` (Step 3, rule 1).
  **Pull depth — offer their FULL history, not a small sample.** A competitor pull only needs a
  recent sample; the self account's whole point is tracking every reel they've ever posted, so
  the default answer for `pull_data`'s `reel_count` is the server's full ceiling
  (`PULL_DATA_MAX_REELS_PER_PROFILE`, currently 100), not a small number. Ask which they want —
  "full history" or a smaller number — state the exact reel count and credit cost before they
  confirm, and never start the pull without an explicit yes. This is exactly the same
  confirm-before-spend flow as a competitor pull; there is no free tier for it.
  **If the own-account add comes back `limit_reached: true` instead of succeeding** — nothing
  was added or charged. Tell the user both numbers (`current` and `limit`), say the budget is
  shared across every workspace they can currently open, and offer to remove some competitors
  or upgrade — never call it a glitch, never say "try again later". Their own account never
  uses a slot, so this should not happen on a self add; if it does, log it with `report_gap`.
- **Free before paid — read what RM already bought before offering to spend the creator's
  Apify money (FRFRMU-1293/1294).** Once the handle is on the watchlist, call
  `get_profile_details` — free, already-paid enrichment from when the account was added — and
  read `media_count` before considering any `instagram-profile-scraper` call on the same
  handle. `media_count: 0` settles "has this account ever posted (a reel or anything else)"
  outright — no posts at all, so no reels either; say so plainly: *"RM already shows 0 posts
  recorded for this account from when it was added — nothing more to check."* A nonzero
  `media_count` says they post, but not how many are reels — only THEN, and only with the
  creator's explicit yes, is a paid scrape fair to offer: *"RM shows 40 posts logged but can't
  tell reels from the rest. I can check the live profile with one Apify scrape — that's billed
  to your Apify account, not RM credits — or you can just tell me. Which do you prefer?"*
  **Never reach for a paid scrape before this free read**, and never say "I can't tell" about
  something `get_profile_details` can answer — `search_watchlist` alone (no `media_count` on
  its rows) is not enough to conclude that.
  - **Returning session, self account already tracked? `search_watchlist` LOCATES the row —
    it never replaces the `get_profile_details` check above (FRFRMU-1534).** If the handle
    is already saved to the Creator Brief but you don't have the profile id in hand this
    session, call `search_watchlist(search_query=<handle>)`, confirm the returned row's
    `role == "self"`, then take its id straight into the SAME `get_profile_details` read
    above — don't stop at the search result and don't add it as a second, parallel check.
  - **The same `get_profile_details` call also returns `pulled_posts_count` and
    `latest_post_date` — read them too, every time, not just `media_count` (FRFRMU-1534).**
    They tell apart three different states, and each gets its own honest sentence:
    | State | How you know | What you say |
    | --- | --- | --- |
    | A — never posted | `media_count == 0` | "RM already shows 0 posts recorded for this account — nothing more to check." (above) |
    | B — they post, RM hasn't pulled them | `media_count > 0` and `pulled_posts_count` is 0 or null | the paid-scrape offer above |
    | C — RM already holds their posts | `pulled_posts_count > 0` | **read them before anything else (below) — never the scrape offer, and never a "no data" claim** |
    **Hard rule:** the words "this account has zero self-posted reels," "nobody's posted to
    your account," or "we don't have Instagram data from your audience yet" may **never** be
    said in any session without having made this read THIS session — and when you do say it,
    quote the actual `media_count` / `pulled_posts_count` numbers, not a memory of a past
    session. Handle `paywall_active: true` on `get_profile_posts` (below) honestly too — that
    means "posts exist, 0 credits to view them right now," never "no posts."
  - **State C — use what RM already holds, before any "borrow patterns from competitors"
    reasoning.** Call `get_profile_posts` (same `profile_id`) and show, plainly, once: each
    post's date (`publishedAt`), views (`engagement.views`), and RM's friendly tags — per the
    algorithm-confidentiality rule, describe what a tag MEANS, never the formula behind it —
    plus the posting cadence from `account_metrics`. This is the single most relevant "what
    worked for THIS business" signal there is; it does not get skipped because the account was
    added in an earlier session.
  - **Already holding some pulled posts (State C)? Check `reels_count` before offering ANOTHER
    pull — do not just re-offer because the sample is thin (FRFRMU-1563).** A live test on a
    real account (`westcore.courtenay`, `pulled_posts_count: 4`, `media_count: 11`) proved
    "always offer a fresh pull when the sample looks thin" wrong: the paid pull was re-run and
    returned the exact same 4 reels — those 4 were the account's entire history, and the offer
    would have spent real money for nothing. `media_count` counts every post type (photos,
    carousels, reels together), so it is the WRONG field to compare against
    `pulled_posts_count` for this decision — read `reels_count` from `get_profile_details`
    instead (FRFRMU-1295: reels only, `null` means "Apify didn't say," never 0):
    | `reels_count` | What it means | What you do |
    | --- | --- | --- |
    | known, `> pulled_posts_count` | more reels exist than RM has pulled | offer a pull, state the exact new-reel estimate and cost, wait for yes |
    | known, `== pulled_posts_count` | RM already holds every reel this account has | say so plainly — *"RM already holds all N of your reels — nothing more to pull."* — and do NOT offer to spend |
    | `null` (Apify didn't report it) | you cannot tell if more reels exist | say so honestly — *"RM holds N reels; I can't tell if that's all of them without a paid scrape."* — and default to **not** spending; only offer if the human asks |
- **Once the handle is saved to the Creator Brief, benchmark numbers leave the self account
  out automatically.** RM's aggregate "mine" insight numbers — on the insight pages and in the
  agent's own analytics tools — exclude the self account by default, so competitor benchmarks
  stay clean. Saving the handle to the brief (above) is what switches this on; there's no
  separate setting. To look at the self account on its own, scope to it explicitly with
  `usernames=[self]` — that's the self-vs-niche pairing from the rule above.
- **Self-vs-niche GAP ANALYSIS — a top input to the strategy (Step 7).** Compare the
  subject's own analysed reels against the niche medians, lever by lever (hooks, formats,
  topics, ER, funnel roles):
  1. **What already works for THEM** (beats their own median) → **double down**.
  2. **What the niche does that they don't** (a lever the niche wins on that they've never
     tried) → the **opportunity gap** to test.
  3. **What they do that UNDER-performs the niche** → **fix or drop**.
  This gap — "what works in the niche" vs "what THIS account should do next" — is one of the
  strongest strategy inputs. Carry it into Step 7 explicitly.
  - **Cross-check every new topic idea against posts already pulled for the self account
    (FRFRMU-1534).** Before a topic goes into the plan, check it against State C's already-
    read posts (above). A close match to a topic already posted is never re-run blind — call
    it out by name, its date, and its result, then either bring it back **on purpose** as a
    deliberate sequel with something changed (a different hook, a different CTA) or hold it
    with a stated reason. Silence about a topic that already ran is the exact failure this
    ticket exists to close.
- **Anchor the honest-benchmarks item (Step 8) to the creator's own rolling median — quantify
  "enough" from the SERVER's floor, never a hardcoded number (FRFRMU-1534/1563).** State C's
  `get_profile_posts` read already returns `account_metrics.reel_sample_size` (how many reels
  the median came from) and `account_metrics.benchmark_reel_sample_floor` (the configured
  minimum before that median can be judged at all) — read both, every time; never hardcode "5"
  in a sentence, because the server-side floor is the thing that can change, not the playbook.
  `reel_sample_size >= benchmark_reel_sample_floor` makes the self median a DATA-DRIVEN anchor
  — a more honest ceiling than a competitor's mega-view. Below the floor, still show and use
  the median, but label it DATA-INFERRED and say "thin sample" out loud with the two real
  numbers, e.g. *"You have 4 reels — the floor for a real pattern is 5 — too few to call a
  pattern yet, but here's the real signal so far: median 707 views, all four Excellent
  Engagement Rate."* Never present a sample below the server's floor as a settled pattern.
  - **This is a DISCLOSURE gate, not a data-volume gate (FRFRMU-1563).** Being below the floor
    never means "say nothing" or "wait for more data before planning" — it means every
    self-performance claim in this plan downgrades to `judgment` provenance (the exact value
    `record_build_steps` accepts, Step 12) with the real reason written in plain words in that
    step's `inputs`/`action` — e.g. "only 4 of the server's floor of 5 reels are on file for
    this account, so this call is judgment, not a proven pattern." The plan still gets built;
    it just tells the truth about how sure it is. **Re-check this every session** (Step 1.6
    already runs every session per `step-01-intake.md` rule 1) — a floor that was missed last
    month may be cleared this month once more reels post, and the gate must reflect today's
    numbers, not a stale memory of a past shortfall.
- **Close the loop.** The weekly measurement ritual (Step 8) should produce a
  tiny tracker — per reel: saves-per-1k, watch-time %, shares-per-1k — for the
  creator to fill in after each reel goes out. The **next** planning run reads
  that tracker back, so the plan actually learns instead of starting from zero
  every time.

---

