# Trial closes — micro-yes lines + the 16, in our voice (FRFRMU-1072, p34)

Small yeses build momentum toward the one that matters. **Gate 5 and CT.1/
CT.2 stay in charge — this file only supplies wording; it never widens
where a close is allowed.** A cold/young account still gets reply-bait, not
closes (unchanged).

## Micro-yes lines

Nurture/activation reels may carry **at most ONE** micro-yes beat ("sound
familiar?", "does this make sense?") placed by the planner's beat order.
Long-form scripts (a live, FRFRMU-1071) seed **~1 per minute**. **The first
yes is always about the problem or the dream — never money.** A reach reel
on a cold account carries none (Gate 5's reply-bait default stands).

## 🔴 Open legal item — read before using classes 6, 9, 16

India's consumer-protection dark-pattern guidelines reportedly name
"confirm shaming" and "nagging" as categories that shame-edged,
repeated-push closes structurally match when delivered to ONE person in a
DM (a crowd isn't individually cornered; a DM recipient is). **Until
counsel clears the mapping, classes 6, 9 and 16 are `dm_allowed: false` —
webinar/page-only, never a 1:1 channel.** This file does not invent a
resolution to that open question; it only enforces the restrictive default
until counsel says otherwise.

## The 16, in our voice

Each carries `{class, name, our_voice, surface[], dm_allowed, maps_to}`.
`surface` values: `reel`, `caption`, `dm`, `live`, `offer_page`.

| class | name | our voice (compliance-safe, shame removed) | surface | dm_allowed |
|---|---|---|---|---|
| 1 | Money is Good | "Money is just a tool — the question is what you trade it for." | reel, caption, offer_page | true |
| 2 | Disposable Income | "You're already spending this somewhere. This is just choosing where." | offer_page, dm | true |
| 3 | Money Replenishes | "You can make more money. You can't make more of this month." | offer_page, live | true |
| 4 | Break Old Habits | "The old way is still there tomorrow if you want it back — most people don't." | offer_page, live | true |
| 5 | Information Alone | "A plan without a system to run it is just a list. The system is what carries you through." | offer_page, dm | true |
| 6 | Money or Excuses | **"Two things can be true: this costs money, and staying where you are costs more. Which one do you want to be paying for in a year?"** (rewritten — shame removed) | offer_page, live | **false** |
| 7 | Your Two Choices | "One path costs less and gives less. This one costs more and gives more. Both are valid — pick on purpose." | offer_page | true |
| 8 | Their Two Choices | "Doing nothing has a cost too — it's just spread out so it's harder to see." | offer_page, dm | true |
| 9 | Us vs. Them | **"There are people who try things and people who watch. Which one have you been lately?"** (rewritten — no in/out-group framing, a question not a label) | reel, caption | **false** |
| 10 | The Hand Hold | "Here's exactly what happens after you say yes — no guessing." | offer_page, dm | true |
| 11 | Say Goodbye | maps to the avatar's own escape phrases (FRFRMU-1031) — "Say goodbye to [their own words for the pain]." | reel, caption, offer_page | true |
| 12 | Now & Later | "Picture this time next year, still here. Now picture it done. Which one are you closer to today?" | live, offer_page | true |
| 13 | Only Excuses | Pre-answers the three real hesitations — don't know how, scared, price — each named plainly, not dismissed. | offer_page, live | true |
| 14 | Reluctant Hero | maps to the persona chair (FRFRMU-1043) — "This isn't about being special. It's the system — anyone who runs it gets the result." | reel, caption, live | true |
| 15 | If You Only Got | maps to the stack's If/All statements (FRFRMU-1049) — "Even if you only got [one stack element], would that alone be worth it?" | offer_page, dm | true |
| 16 | Close Close | **"Whatever's still on your mind — ask it. That's what this is for."** (rewritten — an open invitation, not a repeated push) | live | **false** |

## Placement rule

One close before each stack element in the running-stack reel (FRFRMU-1049)
and the live script (FRFRMU-1071); several in a live's final Q&A sequence.
Stage gate (Gate 5) decides WHETHER a close runs on this slot at all — this
file only supplies which close and its wording once the gate says yes.

## The comfort screen (ask-user, once)

*"Here are the closing lines I'd use, in your voice — cross out any that
don't sound like you."* Cut ones are recorded `closes_disabled_by_user[]`
on the Creator Brief and **never re-proposed** on a later run.

## Validator (advisory → hard for the DM rule)

- `check_closes` — a close appearing in a `reach` slot, or on a cold/young
  account, fails (Gate 5's job, restated here so a copy pack can be
  checked standalone). A close matching the ORIGINAL shaming wording of
  class 6/9/16 (not the rewritten `our_voice` text) fails outright. A
  close the creator disabled reappearing fails.
- `check_closes_dm_restricted` — **hard.** A DM script containing a close
  whose `dm_allowed` is `false` (classes 6, 9, 16) fails, no exceptions
  until the legal item above is cleared.
- `check_first_yes_not_money` — the first micro-yes in a script is about
  the problem or the dream, never a money question.

## Guardrails

- No income promises in any close — the structure forces a decision, it
  never guarantees an outcome.
- The creator's comfort screen wins over the library, always.
- Reply-bait before closes — Gate 5 unchanged, in charge.
