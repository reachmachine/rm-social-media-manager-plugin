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
- **Anchor the honest-benchmarks item (Step 8) to the creator's own rolling
  median**, wherever enough of their own data exists — that's a more honest
  ceiling than a competitor's mega-view.
- **Close the loop.** The weekly measurement ritual (Step 8) should produce a
  tiny tracker — per reel: saves-per-1k, watch-time %, shares-per-1k — for the
  creator to fill in after each reel goes out. The **next** planning run reads
  that tracker back, so the plan actually learns instead of starting from zero
  every time.

---

