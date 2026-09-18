> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

> **Load this during Step 3**, right after `step-03-5-prospect-research.md`, while the
> pull/analysis is still running. **Hard gate: refuses to run unless BOTH `avatar` (p02,
> FRFRMU-1031) and `prospect_research` (p04, FRFRMU-1035) exist** — a thin load-in produces
> generic answers, which is the card's #1 named risk. Missing either → say so plainly and
> point at the missing step; do not attempt a thin version. This is p05 "Run the Magic Desk
> Interview" (`marketing/rules/process-cards/p05-run-magic-desk-interview.md`, FRFRMU-1037):
> step inside the prospect's head, in their own voice.

## Step 3.6 — The magic desk interview (p05)

**Ask per `asking-rules.md`.**

**1. Intention line (agent drafts, user confirms).** One sentence for this session, e.g. "get
in touch with my prospect's major problems and fears about [topic]."

**2. Answer all 17 questions IN CHARACTER, first person, in the avatar's vocabulary
(agent-fills).** In order: what scares you most right now · if it happened what would it mean
· say that fear plainly · deepest want for your life · your business goals · what would build
burning desire · your words for this product & how it should be described · how badly you want
it · what would make you want it more · your objections & what overcomes them · what could get
in the way · what would sweeten the deal · what you like about competitors · what proof
converts you · a fair price · what else appeals · concerns not yet raised. **Third-person
summaries fail.**

**3. Audit pass (agent-fills).** Every answer tagged `grounded` (cites a `prospect_research`
quote or `avatar` phrase) or `inferred` (pure inference). **An untagged answer fails.** Any
answer that flatters the offer must cite a source or be tagged `inferred` — this is the guard
against role-play drifting into what the SELLER wishes the prospect felt.

**4. Human option, offered ONCE, never pushed.** The creator may run this themselves and paste
their transcript — a human can surface subconscious material an agent cannot.

**5. Extract at least 5 usable lines** for headline/hook/story seeds; name the "emotional
greed" (the want they're afraid to admit) explicitly, or acknowledge its absence honestly.

### The audience-ask variant — translate, never lead (founder decision, 2026-09-06)

A creator with a real audience can ASK instead of imagining. **Two tiers, never one:**

* **Tier 1 — OPEN, context-anchored (question stickers, reply-bait captions).** Anchor the
  CONTEXT from `avatar` + `prospect_research`; leave the ANSWER open. Second person, ≤15 words.
  ❌ "What terrifies you?" (generic) ❌ "Does hiring incompetent people scare you?" (leading) ✅
  "What's the scariest part of hiring your next person?" Tag replies `audience-grounded`.
* **Tier 2 — CLOSED polls, options cited from `prospect_research`.** 2-3 options, each citing a
  research item_id, plus an "other" escape. Ranks known fears; tag results `audience-validated`
  — **never quote a poll count as customer language.**
* **Self-check before posting any question:** names the product/offer, or presupposes the
  answer? → reject / move to Tier 2. Open first (discover), poll second (rank). **One question
  per post, spread across days — never a survey dump.**
* The plugin **cannot post to Instagram and cannot read replies** — it drafts the questions +
  posting plan; the creator posts and pastes answers back. Say this plainly, every time. A
  brand-new account (few followers) is told the variant's value grows with the audience.
* **Standing gate:** the creator approves the question batch before anything posts.
* Pasted answers upgrade tags (`audience-grounded`/`audience-validated`), land in the intake's
  audience-questions field, and seed future reels.

### What this step refuses to do

Run without both `avatar` and `prospect_research` · leave an answer untagged · flatter the
offer with no citation and no `inferred` tag · claim the pipeline posted or read replies ·
write a Tier-1 question that names the product or presupposes the answer · invent a Tier-2
option with no research citation · quote a poll result as customer language.

### Save it

Write the result to the Creator Brief as the Foundation card key `magic_desk`, Foundation-card
shape (FRFRMU-1042) — the same envelope `avatar`/`prospect_research`/`big_domino` use. **Every
item still needs `who` (`you`/`agent`) and `provenance` (one of `DATA-DRIVEN`, `DATA-INFERRED`,
`JUDGMENT`, `FROM-EXPERT`) — the audit pass's own `grounded`/`inferred` tags (step 3 above) are
NOT the same vocabulary and do not replace them.** Map audit tags onto provenance like this: a
`grounded` answer (cites a real `prospect_research`/`avatar` source) is `DATA-INFERRED` — a
judgment extrapolated from real data — with that citation kept in `source`; an `inferred`
(uncited) answer is plain `JUDGMENT`:

```
{
  "card": "magic_desk", "title": "The magic desk interview",
  "status": "confirmed",
  "summary": "<the intention line + the emotional greed line, or its honest absence>",
  "items": [
    {"item_id": "q01_scares_you", "label": "Q1 — what scares you most right now",
     "text": "<in-character, first person>", "who": "agent", "provenance": "DATA-INFERRED",
     "tag": "grounded", "source": "prospect_research:fear_01"},
    {"item_id": "q02_what_it_would_mean", "label": "Q2 — if it happened, what would it mean",
     "text": "<in-character, first person>", "who": "agent", "provenance": "JUDGMENT",
     "tag": "inferred"},
    "... one item per question, q03 through q17, same shape as q01/q02 above ...",
    {"item_id": "extracted_line_01", "label": "Extracted headline/hook/story seed",
     "text": "<usable line, cites the source item_id>", "who": "agent", "provenance": "JUDGMENT"},
    {"item_id": "emotional_greed", "label": "The emotional greed",
     "text": "<the want they're afraid to admit, or an honest 'not surfaced this pass'>",
     "who": "agent", "provenance": "JUDGMENT"},
    {"item_id": "question_batch", "label": "Drafted audience-ask batch (Tier 1/Tier 2)",
     "text": "<the drafted questions/polls, or 'not applicable — no audience yet'>",
     "who": "agent", "provenance": "JUDGMENT"}
  ],
  "updated_at": "<ISO date>"
}
```

An untagged answer (step 3's own rule) is also an incomplete item here — `tag` is required on
every `q0N_*` item, same as `who`/`provenance`.

## Wire into

* **Outline recipe (`step-08-outline-recipe.md`):** `story_setup` may draw from
  `magic_desk.extracted_lines`, cited by line id, when the card exists. No `magic_desk` key →
  unchanged (still a label with no content source).
* **Hook recipe (`step-08-hook-recipe.md` §H.4b):** Q1-4 lines (the fear chain + deepest want)
  are additional candidates in the SAME avatar-phrase conditional p02 wired in — shares one
  block, not a second one.
* **CTA recipe (`step-08-cta-recipe.md` reply-bait stage):** the audience-ask posts use the
  EXISTING reply-bait step-down; no new CTA type.
