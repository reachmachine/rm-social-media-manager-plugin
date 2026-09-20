> **Playbook reference file — load only this one, whenever `asking-rules.md` §11 says "check
> every source we already hold."** The full step list, and which file holds each step, is in
> `PLAYBOOK.md` (small, always loaded). This file is the field-by-field map §11 points at — it
> is not a numbered step, and it never restates §11's own rule, only what to check and how to
> word the read-back.

## The map (FRFRMU-1609) — which tool answers which question, before you ask it

**A fact the creator paid credits to put in our database is never asked for cold.** For each
question below: call the tool, check the freshness signal, then use the matching read-back
wording. If the tool comes back empty (most often because the self account is not on the
watchlist yet — Step 1.6's guardrail keeps it off in a thin workspace, see
`step-01-6-self-account.md`), that is the NORMAL case, not an error — fall through to
`website_dossier.checklist`, then to the plain ask, exactly as §11 says.

**How to tell fresh from stale — do not guess:**

| Data comes from... | Freshness field | Stale when older than |
|---|---|---|
| the watchlist / pulled posts (`search_watchlist`, `get_profile_posts`) | `data_age_days` / `stale` on the `search_watchlist` row | `DATA_STALE_DAYS` (env, default 7 days) |
| the Creator Brief (`get_creator_brief`) | the field's own `stale` flag | `CREATOR_BRIEF_STALE_DAYS` (env, default 30 days) |
| `get_profile_details` alone, with no matching `search_watchlist` row in hand | `updated_at` (NOT `last_validated_at` — that field is documented as not reliably updated) | treat as stale past the same `DATA_STALE_DAYS` window |

A field with no freshness signal at all (nothing returned, or the tool never ran this session)
is ABSENT, never treated as fresh-by-default.

### The five questions

| Question | Call this | Read this field | Fresh read-back | Stale read-back | If absent |
|---|---|---|---|---|---|
| Follower count | `search_watchlist` (find the row with `role: "self"`), then `get_profile_details(profile_id)` | `follower_count` | *"You're at about 1,300 followers — right?"* | *"Last time we looked you were at 1,300 followers — still about right?"* | Ask normally: *"What's your current follower count?"* |
| Post count | `get_profile_details(profile_id)` | `media_count` (every post type) and `reels_count` (reels only, `null` = Apify didn't say — never read as 0) | *"RM shows 40 posts logged, 11 of them reels — sound right?"* | *"As of our last check you'd posted 40 times — still about right?"* | Ask normally |
| Posting cadence | `get_profile_posts(profile_id)` (needs ≥2 stored posts) | `account_metrics.post_frequency_weekly` / `.post_frequency_monthly`, with `cadence_source`/`cadence_window_days` for how it was computed | *"You're posting roughly 3 times a week — right?"* | *"You were posting about 3 times a week last time we looked — still the rhythm?"* | Ask normally |
| Topics already posted about | `get_profile_posts(profile_id)` | `posts[].tags` (RM's own tags on each stored post) aggregated across the returned posts — describe what a tag MEANS in plain words, never the scoring formula behind it (the algorithm-confidentiality rule, unchanged) | *"Your reels lean toward [topic A] and [topic B] already — still the main things you post about?"* | same wording, plus *"— as of [latest_post_date]"* | Ask normally |
| Their own top reels | `get_profile_posts(profile_id)` | `posts[]` sorted by `engagement.views` (fall back to `.likes` if views is null) descending, top 1-3 | *"Your best reel so far is the one from [date] at [views] views — still one you're proud of?"* | same wording, plus a note that newer reels may exist if `pulled_posts_count` is older than the account's `latest_post_date` | Ask normally |

**Worked precedent — don't duplicate it, reuse its shape.** `step-01-intake-fields.md`'s
"Account stage" field (FRFRMU-1008) already runs this exact recipe for follower count +
cadence, one field at a time, because the founder ruled stage must never be asked before Step
1.6 has had its chance to check the account first. That field's own wording
(*"Your account shows about 4,300 followers, posting roughly 3 times a week — sound right for
where you're at?"*) is the model this file generalises to every other question that could be
something we already hold — this file is what makes that the DEFAULT for any question, not one
hand-built exception.

**A stale number is never read back as if it were current (the FRFRMU-1317 risk).** The "Stale
read-back" column above always says WHEN the number is from, or that it might have moved — never
a bare re-statement of an old figure as though it were fresh. And the reverse failure matters
just as much: never invent a number when the tool returns nothing — an absent field is the
normal ask, not a guess dressed as a fact (asking-rules.md §5).
