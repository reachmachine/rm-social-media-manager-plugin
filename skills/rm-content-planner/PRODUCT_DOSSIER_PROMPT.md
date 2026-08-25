# Product Dossier prompt — for SaaS / software subjects (G408)

**Who reads this file:** the social-media-manager agent running the rm-content-planner
skill. **Who the fenced prompt below is FOR:** the creator's OWN AI coding agent
(Claude Code or similar), running inside the creator's product codebase — a machine
this skill cannot see and must never try to reach.

## Why this exists

Two sources routinely undersell a software product:

1. **The creator's own words.** Founders forget features, undersell benefits, or
   struggle to explain their product on the spot. That is normal, not a flaw.
2. **The public website.** Marketing sites lag the product — features ship months
   before the site mentions them.

But the creator's codebase knows everything. If the creator (or their developer)
already uses an AI coding agent in that codebase, that agent can write us a
marketing dossier — the full feature list, who it's for, what each feature lets the
user do — without any code or secrets leaving their machine except the dossier text
the creator chooses to paste back.

## How to use it (SMM agent instructions)

- **Offer it ONCE during Step 1 intake** when the subject is a software product
  (SaaS, app, tool) — see PLAYBOOK Step 1, "Software or SaaS product? Offer the
  codebase dossier (G408)". Never require it; a creator without a dev agent just
  continues the normal conversation.
- **Hand the creator the fenced prompt below VERBATIM** in a copy-paste block. Do
  not shorten it — the safety rules inside it are the point.
- **Tell them it's re-runnable:** "Whenever your product grows, run this same
  prompt again and paste me the fresh dossier — your strategy stays current."
- **When the dossier comes back:** cross-check it against the website and the
  conversation (Step 1 rule 4), flag mismatches, and persist it via
  `update_creator_brief` under key `product_dossier` with
  `{value, source: "creator's dev agent via PRODUCT_DOSSIER_PROMPT", date, confidence}`.
- **Label:** the dossier is creator-supplied first-party info — never DATA-DRIVEN
  (§I reserves that for analysed-reel medians). It feeds positioning and topic
  selection, not performance claims.
- **NOT YET PUBLIC items stay private:** anything the dossier marks unreleased
  never becomes calendar content without the creator's explicit ok.

## The prompt (hand this to the creator verbatim)

```
You are helping prepare a MARKETING DOSSIER for a social media manager who
cannot see this code and has never used this product. Read this codebase and
write a file called product-dossier.md.

RULES:
- Write plain English a non-technical reader can follow. No jargon — if a
  technical term is unavoidable, explain it in one short phrase.
- NEVER include: source code, file paths, internal code names, API keys,
  secrets, environment variable values, or any customer data.
- Mark anything unreleased (feature flags that are off, work in progress,
  roadmap items) clearly as "NOT YET PUBLIC".
- If you cannot tell something from the codebase, write "unknown" — never
  guess.

Use these exact section headings:

1. What the product is — one short paragraph.
2. Who it is for — the target users, as the code, docs, and onboarding
   flow reveal them. Be specific about the audience.
3. The problem it solves — described in the user's own words, not ours.
4. Features and benefits — EVERY user-facing feature: its name in plain
   words, what the user can DO with it, and why that matters to them.
   Include features that are built but not yet marketed anywhere.
5. What makes it different — real differentiators visible in the product,
   not marketing claims.
6. Pricing and plans — if plans/limits exist in the code or config;
   otherwise "unknown".
7. Onboarding and first win — what a new user does first, and the moment
   they first get real value.
8. Integrations — third-party services a user sees or connects.
9. Coming soon (NOT YET PUBLIC) — unreleased items, clearly marked.
10. Dossier date and completeness — today's date, plus one line on what
    you could not determine from the code.

Save the file as product-dossier.md, then show it to me so I can review it
before sharing it with my social media manager.
```

## After the first run

Re-running the SAME prompt is the update mechanism: the creator runs it again
whenever the product grows, pastes back the fresh dossier, and the SMM agent
replaces the `product_dossier` brief entry with the new one (the brief keeps full
history). On any later strategy update for a software subject, check the brief's
`product_dossier` first — if its `stale` flag is set (30 days, G229) or the
creator mentions new features, remind them to re-run the prompt before planning.
