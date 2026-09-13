> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder. The Rigor Rules **§A–§I** are in
> `playbook/rigor-rules.md`.

## Step 1.1 — Crawl the customer's website against a checklist, and STORE it (G234, FRFRMU-1149)

Today's rule (G234, `step-01-intake.md`) fetches a website **once** and the finding lives only
in the conversation — it dies when the session ends. A SaaS business gets a full, re-runnable
`product_dossier` (the block right after this one in `step-01-intake.md`). Every other kind of
business — a gym, a clinic, a dentist, a bakery — gets nothing saved. This step fixes that: read
the pages that answer the founder's **eight things**, save the findings as `website_dossier` in
the Creator Brief, then lead every intake question with what was found instead of asking cold.

### Step A — Ask once, up front, even if the customer volunteered the URL

One message, carrying the plan AND the size, so nobody is surprised how long it takes:

> "Can I read your website before we go on? I'll go page by page — about, offers, results,
> locations — until I have the 8 things I need, then stop. Usually 5-10 pages, about a minute or
> two. It saves you repeating what's already written down."

A **"no"** means: skip it, do not re-ask this session, rely on the conversation alone. Record
`website_dossier_consent: {answer, asked_at}` in the Creator Brief so a resumed session does not
ask twice.

### Step B — Discover pages cheaply, sitemap first

Fetch `<site>/sitemap.xml` first. If it is a sitemap **index**, follow it once. Fall back to the
homepage's own links only when there is no sitemap. A sitemap routinely shows pages the menu
doesn't (offer pages, city landing pages) — don't rely on the menu alone.

**Cross-host redirect rule:** `WebFetch` returns a redirect instead of following it, and
`site.com` → `www.site.com` counts as cross-host. Retry once with the returned URL, and treat
www / non-www as the SAME site in the visited list.

### Step C — The checklist that drives the crawl (the founder's 8 fields)

`offer_price`, `lead_magnet`, `target_audience`, `differentiator`, `proof`, `locations`,
`funnel_assets`, `credentials`. Every field starts `open`. Path words rank a page as likely to
fill a field:

| Path words | Fills |
| --- | --- |
| offer, price, pricing, plans, membership, packages | `offer_price` |
| free, guide, download, trial, consult, webinar | `lead_magnet` |
| about, team, story, method, why | `differentiator`, `credentials`, `target_audience` |
| results, testimonials, reviews, success, case | `proof` |
| locations, contact, find-us, a city name | `locations` |
| thank-you, signup, book, schedule | `funnel_assets` |
| services, programs, classes, faq | `offer_price`, `target_audience` |

### Step D — Stop condition: the checklist is full. NO fixed page cap

Read the highest-ranked page for an open field, extract, mark it `found` or leave it `open`,
then pick the next page for the next open field. Stop when every field is `found` or
`not_found_on_site`, even if pages remain unread. Seven guard rails make "no cap" safe:

1. **Loops.** Same host only. Strip `#fragments` and `?query`. Normalise the trailing slash.
   Keep a visited list. Never fetch a URL twice. A page's links only join the queue if they pass
   guard rail 2.
2. **Pagination traps and blog archives — never fetch:** `blog`, `news`, `post`, `/20xx/`, `tag`,
   `category`, `author`, `page/N`, `?page=`, `feed`, `wp-json`, `privacy`, `terms`, `cookie`,
   `cart`, `checkout`, `login`, `account`, and any file link (`.pdf`, `.jpg`, `.png`, `.mp4`). A
   blog is not where a business states its offer.
3. **200 near-identical location pages.** Group URLs by slug pattern (e.g. `brand-<city>/` or
   `<city>-offer/`). Read **1-2 representatives per group**, then list the rest as locations by
   name from the URL with item status `named_from_url`, never `found`. Honest provenance, no
   fetch — this is the rule that stops "truncated list, then guessed" without opening every page.
4. **Junk vs evidence.** `home-2/`, `landing-page-v2/` are skipped as duplicates.
   `thank-you-signing-up/` is **not opened** but IS evidence: a thank-you page means an email
   capture exists → a `funnel_assets` item "email sign-up (thank-you page exists)" with that URL
   as its source.
5. **When the site simply does not say.** The candidate list is finite (same host, after skips
   and grouping), so the crawl always ends. When every candidate page ranked for a field has been
   read and the field is still open, mark it `not_found_on_site` and let intake ask that question
   the normal way — an honest "the site doesn't say" beats a guess.
6. **Progress check-in — a consent point, not a cap.** After every **6** pages with fields still
   open, one line:
   > "Read 6 pages — found your offer, proof and locations. Still looking for credentials and a
   > lead magnet; 4 likely pages left. Keep going?"

   "Yes" carries on until the checklist is full. **"Just finish" (or any equivalent) suppresses
   every further check-in for the rest of this session** — the crawl then runs straight to
   checklist completion or candidate exhaustion, with no more check-ins asked. A **"stop"** marks
   every remaining open field `not_checked` — deliberately a DIFFERENT word from
   `not_found_on_site`, so a later refresh knows this field still needs a look, not that the site
   was checked and said nothing.
7. **Per-page failure.** A page that times out, 403s, or comes back empty is marked
   `unreadable` with its URL, and the crawl continues. If the **whole** site blocks plain fetches,
   offer the browser method **only if** `mcp__playwright__browser_navigate` is actually in this
   session's tool list, and **only after a second explicit yes** (today's G234 rule, kept). If it
   is not available, say so plainly and ask the customer to paste the key facts — never guess.
8. **Extraction never guesses.** `WebFetch` answers a prompt using a small model, which can fill
   gaps on its own. Every page prompt must ask for **verbatim quotes with the page URL** and an
   explicit "not found" per field. Cap a quote at **200 characters** and each field at **5
   items** — that keeps the whole dossier far under the Creator Brief's 20,000-byte write cap.

### What the customer sees while it runs

The permission message; the check-in line every 6 pages (unless suppressed by "just finish");
then a read-back:

> "Done — read 5 pages. Found: 3 offers on your homepage (5 days for $25, 3 sessions for $7, free
> consultation), 6 results on /results/, 8 locations. Not on your site: credentials. I'll lead
> each question with what I found — correct me where the site is out of date."

### The stored shape — brief key `website_dossier`

Written once per crawl with `update_creator_brief`. The envelope is the normal
`CreatorBriefField`: `source: "website"`, `confidence: "medium"` (a site is often stale). The
`value`:

```json
{
  "site": "https://www.example.com",
  "crawled_at": "2026-09-10",
  "pages_read": ["https://…/", "https://…/results/", "https://…/example-courtenay/"],
  "pages_unreadable": [],
  "checklist": {
    "offer_price":     {"status": "found", "items": [
                          {"text": "Get 5 Days for $25", "page": "https://…/"}]},
    "lead_magnet":     {"status": "found", "items": [{"text": "Book your free consultation", "page": "https://…/"}]},
    "target_audience": {"status": "found", "items": [{"text": "…struggles with consistency …", "page": "https://…/results/"}]},
    "differentiator":  {"status": "found", "items": [{"text": "private areas to train", "page": "https://…/results/"}]},
    "proof":           {"status": "found", "items": [{"text": "lost 60 lbs in 8 months — Joyce P.", "page": "https://…/results/"}]},
    "locations":       {"status": "found", "items": [
                          {"text": "Courtenay", "page": "https://…/example-courtenay/"},
                          {"text": "Victoria", "page": "https://…/example-victoria/", "status": "named_from_url"}]},
    "funnel_assets":   {"status": "found", "items": [{"text": "email sign-up (thank-you page exists)", "page": "https://…/thank-you-signing-up/"}]},
    "credentials":     {"status": "not_found_on_site", "items": []}
  },
  "confirmed_by_creator": {"offer_price": {"answer": "current", "at": "2026-09-10"}}
}
```

**Required:** `site`, `crawled_at`, `pages_read` (a list), `checklist` (a dict with **all eight**
field keys: `offer_price`, `lead_magnet`, `target_audience`, `differentiator`, `proof`,
`locations`, `funnel_assets`, `credentials`). **Optional:** `pages_unreadable`,
`confirmed_by_creator`, and an item-level `status` (its only allowed value is `named_from_url`).
Each field's own `status` is one of `found` | `not_found_on_site` | `not_checked`.
`confirmed_by_creator` is filled in during intake as each question is answered (`current` |
`changed` | `dropped`).

### Re-run rule

The brief's existing 30-day `stale` flag covers time. Two explicit triggers as well: the
customer says the site changed, or a later session finds `not_checked` fields left over from a
"stop". **A refresh REPLACES the value — it never appends** (the same lesson `product_dossier`
already taught the hard way — an appended dossier is the very thing the size cap exists for).
After a refresh, read back only the differences: "your site now says 7 days for $35 — the offer
changed."

### Headless runs

**`WebFetch` is never added to `runner.py`'s allowed tools** — that would auto-approve a fetch
nobody consented to, and a headless run cannot ask permission. A headless run reads a stored
`website_dossier` if one already exists, and otherwise proceeds without one — it never crawls.

### Ask with it, not around it

Once a dossier exists, `playbook/asking-rules.md` §11 governs every intake question that touches
one of the eight fields — lead with the finding, never ask cold. See that file for the full rule
and examples.

**Step 1 continues in `playbook/step-01-intake-fields.md`, and its continuation
`playbook/step-01-intake-fields-2.md`** — the fields this conversation must end up with.
