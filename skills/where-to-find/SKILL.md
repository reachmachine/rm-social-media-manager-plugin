---
name: where-to-find
description: Step 10 of Reach Machine plugin v2. Finds where the customer's dream customers spend time online, in the background, and points them to the profile tab.
---

**Work silently.** Never announce or describe any action you take or are about to take -- only the server's own `say`/`question` lines and the customer's own words. Never name a tool, a field, a research service or a price.

Load tools with ONE call: `ToolSearch` with query `select:mcp__plugin_rm-plugin-v2_reachmachine__get_hangouts,mcp__plugin_rm-plugin-v2_reachmachine__answer_question`.

The server writes every word. Say its lines as given -- never invent an account, a place or a number.

## Loop

1. Call `get_hangouts` with `view: "summary"`.
2. `status: "not_started"` -- the research has not begun. Follow the plan's `next_actions` and stop. Never retry this turn.
3. Otherwise say `say` once if there is one.
4. If the plan's `next_actions` holds the budget question, ask it with `AskUserQuestion` exactly as given, then send the answer with the tool it names. It is the ONLY question this step asks. Never ask it twice.
5. The research runs in background jobs. Never run a scraper or a search for it in this chat. A finished job is no news: say nothing.
6. When the server says the map is ready, tell the customer the where-to-find-your-dream-customer tab is on their profile page, and that they add the accounts they like there. That is the last line of this step.

## Never

- Never ask "add these accounts?" in chat. Accounts are added from the profile tab only.
- Never list or describe any person or account the research found.
- Never say what a lookup cost. The server's budget line is the only money talk.
- No research service connected: say the server's line as given. Only the free parts run. Never ask the customer to connect one now.
- A small niche: the summary `say` carries the server's line. Say it as given. Never promise more accounts than the tab shows.
- Some places could not be read: the summary `say` carries one plain line about it. Say it as given. Never name a tool or an error.

Answer in the customer's own language.
