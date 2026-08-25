---
description: "Remove specific competitors from this workspace. DESTRUCTIVE — can permanently erase an account's analysed library. Needs an explicit yes"
argument-hint: "[the @handle(s) to remove]"
---

Remove competitors from this workspace's watchlist. **This is destructive and some of it cannot
be undone.** Follow the skill's PLAYBOOK Step 3 rules; treat this with more care than any spend.

Who to remove: $ARGUMENTS

## 🔴 Read this before removing anything: removal can DESTROY data

Removing a competitor is not always just "untrack it". **If this workspace is the last one
tracking that account, its collected reels and completed analyses can be erased for good.** The
credits already spent analysing them do not come back, and re-adding the account later means
paying to analyse it all over again.

So removal has two very different outcomes, and **you must say which one applies** before asking
for a yes:

- **Another workspace still tracks it** → this workspace stops seeing it; the data survives.
- **This is the last workspace tracking it** → the analysed library goes with it. Permanent.

If you cannot tell which case you are in from `get_profile_details` / `search_watchlist`, **say
that you cannot tell** and treat it as the destructive case. Never guess in the direction that
makes the action look safer.

## The steps

1. **Never remove from a filter or a guess.** `search_watchlist` first and resolve the exact
   handle. If `$ARGUMENTS` is vague or matches more than one account, ask — do not pick.
2. **Show what will be lost**, per account: handle, reels held, reels **analysed**, and which of
   the two outcomes above applies. Numbers, not adjectives.
3. **Ask for an explicit yes, naming the accounts.** One yes covers one named list. A yes for
   three accounts is not a yes for a fourth. If the user says "remove the junk ones", that is
   not consent — list them and ask again.
4. `remove_competitor`, one at a time, confirming each result as you go.
5. **Report what actually happened**, including anything that failed. A removal that errored has
   not happened — say so rather than reporting the intended outcome.

## Suggest the cheaper option first

Most requests to "delete" a competitor are really "stop it polluting my insights". That does not
need deletion: `set_data_selection` scopes reads to the accounts they care about, and costs
nothing to undo. **Offer that first.** Deletion should be the choice they make after hearing the
alternative, not the default.

**Hard limit:** never call Apify or a spend tool here.
