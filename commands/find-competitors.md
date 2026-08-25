---
description: "Find benchmark competitors on Instagram — our catalog first, then a live Apify search. Apify bills YOUR Apify account; adding accounts spends RM credits"
argument-hint: "[niche, seed @handles, or hashtags to search from]"
---

Find modellable benchmark accounts. This is the skill's **Step 2** on its own — load that
PLAYBOOK section and follow it exactly, including the discovery angles A–F.

Seeds the user gave: $ARGUMENTS

## Prerequisite gate — before searching anything

`get_business_profile` + `get_creator_brief`. Discovery is seeded off the **subject's** niche,
stage and named accounts. Without them you research the wrong market. If the niche is missing,
stop and route to `/rm-social-media-manager:know-business`.

## Source order — catalog, then Apify

1. **`discover_accounts` FIRST — free.** It returns only accounts Reach Machine already holds
   real data for. **Empty is normal**, not an error, and not a reason to invent anything.
2. **Then Apify, for the live Instagram search** — angles A–F in PLAYBOOK Step 2.2, using
   `instagram-hashtag-scraper`, `instagram-search-scraper`, `instagram-scraper` and
   `instagram-profile-scraper`. Name these tools **bare** — the prefix differs on a customer
   install, so a hardcoded one points at nothing.
   **Angles D (related profiles) and F (trending audio) are not available** with these tools.
   Skip them and say you skipped them.

## 🔴 Two separate spends, two separate gates

**Apify spends the user's OWN money, and Reach Machine cannot see or stop it.** RM's credit
ceiling and confirm-before-spend cover RM tools only; Apify bills the user's Apify account
directly. So:

- Before any Apify call, say **which angles** you will run and roughly **how many scrapes** that
  is, and **WAIT for an explicit yes.** Never fire a batch off one vague approval.
- `add_to_watchlist` is a **separate** RM spend with its own gate: show the un-confirmed cost
  preview and wait for another explicit yes before calling with `confirm=true`.

## Not connected yet? Tell them how — in one short block (G366)

Apify is a **separate, one-time sign-in**, not part of the Reach Machine login. The plugin
already carries the connection, so nobody types a URL. Say this to the user, in their words:

- Run **`/mcp`**, pick the **`apify`** server, and sign in in the browser window it opens.
- **No Apify account yet? Making one at apify.com is free** — Apify gives new accounts free
  usage credit, and heavy searching is what starts costing.
- **There is no API key to paste and no `.env` file to fill in.** If anything asks you for a
  token, that is not this.
- Reach Machine's own server (`reachmachine`) signs in the same way, from the same `/mcp`
  list — they are two separate sign-ins.

Say it once, plainly, and then wait. Do not run discovery while the sign-in is still pending.

## 🔴 If Apify is not connected, STOP (G332)

A generic web search is **NOT** a substitute for either source. If `discover_accounts` is empty
and Apify is unavailable, unreachable, or the user declines the spend: say plainly that you
cannot search Instagram right now and why, then **stop**. Do not web-search and present the
results as benchmark accounts. Do not invent handles.

Offer the propose-from-seeds fallback in one line only — and use it solely if the user
explicitly asks, labelled to their face as **unverified suggestions, not Reach Machine data**.

## Then finish the funnel properly

3. **Pre-filter before spending** (Step 2.3): drop brands, media companies, agencies,
   mega-accounts a small creator cannot model, off-niche and inactive accounts. Rank by **FIT,
   not fame**.
4. **The human approves the shortlist** (Step 2.4) — never add an account they did not approve.
5. **Validate before you trust** (Step 2.5): a handle that came from a guess must be checked
   against real metrics before it counts as a benchmark.

When accounts are added, point at `/rm-social-media-manager:pull-data` to fetch their reels.
