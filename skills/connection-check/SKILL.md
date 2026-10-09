---
name: connection-check
description: Step 1 of Reach Machine plugin v2. Checks the three connections this plugin needs (Reach Machine, Apify, the browser) before anything else runs. Always run this first in a new or resumed session, and whenever the customer says "check again".
---

**Work silently.** Never speak before or between tool calls. Show only the
question or result -- nothing about what you are doing.

<!-- rmp-voice-rules:start -->
Voice rules: the ten rules loaded when this session started still apply. Plain words, short bullets, answer first, never name a tool, never narrate.
<!-- rmp-voice-rules:end -->

Load this step's new tools in ONE `ToolSearch` call, query
`select:mcp__plugin_rm-plugin-v2_reachmachine__get_billing_status,mcp__plugin_rm-plugin-v2_reachmachine__record_session_start,mcp__plugin_rm-plugin-v2_apify__get-actor-run,mcp__plugin_rm-plugin-v2_playwright__browser_navigate,mcp__plugin_rm-plugin-v2_playwright__browser_close`.
Earlier steps' tools stay loaded: never load one twice.

# Connection check

This is the first thing this plugin does, every session, including a resumed one. Until
it passes, no other part of the plugin runs — a hook enforces that, not this file. This
file only tells you what to call and what to say.

## 1. Make these three calls

Say nothing while making these three calls or right after -- not a running commentary,
not "all three passed", nothing about what you are about to do next. The only thing you
say for this whole step is in section 3. Your first words are the section 3 report.

Call these three tools with these inputs. The hook that records the result only
recognises this shape — a different input does not count.

```
get_billing_status   {}
get-actor-run        {"runId": "rmp-connection-probe-000", "waitSecs": 0}
browser_navigate     {"url": "https://example.com/"}
```

These two tools take their fields directly. **Do NOT wrap them in `args`** — only Reach
Machine tools use `args`.

**`get-actor-run`: an error saying the run was not found is the PASS signal for this
one.** Only Apify's real API, once you are signed in, can say a run with that made-up
id does not exist. Do not report this to the customer as a failure — it means the
connection works.

**`browser_navigate`**: once this and the other two calls have run, the plugin
itself tells you the exact next actions in the same turn -- do not decide this
yourself, and do not write anything before it arrives. Follow that instruction
exactly: it names every call still needed (closing the browser, recording the
session) and exactly what to say afterward. Add nothing before, between, or
after what it tells you to do and say.

None of these three calls spends RM credits, starts a scraper, or spends the customer's
own Apify money.

## 2. If a tool is missing

If a server's check tool does not exist in this session at all (you only see an
`authenticate` tool from that server, or nothing), that connection is ⚠️ needs sign-in.
Do not call anything else to "check" it — a missing tool means the customer has never
signed in to that server yet.

## 3. Record, then report -- call before you say anything

Decide each connection's state silently (next table), then call `record_session_start`
right away, BEFORE you say a word to the customer -- **exactly** the JSON payload the
connection-reminder line gave you for this session. Do not compute the values yourself,
and do not guess `client_session_id`, `results`, or `earlier_checks`. The hook checks
what you send against what it actually found, and a different value is refused. Say
nothing about this call.

- **`say` is present in the result (all three connected):** say it exactly, word for
  word, as your WHOLE report for this step -- no sentence before it, no sentence after
  it, nothing about what you just did or are about to do. It already carries the saved-chat line; add nothing.
- **`say` is not present:** say one line per connection from the table below, in order,
  with the meaning given, in the customer's language. No sentence before or after the list, and no summary
  of your own about the check as a whole.

| Status | Meaning | What to say |
|---|---|---|
| ✅ connected | the check passed | nothing more |
| ⚠️ needs sign-in | only `authenticate`, or nothing, from that server | `lines.needs_signin`, `{server}` = `reachmachine` or `apify` |
| ❌ broken | the check ran and failed | Reach Machine: account disabled `lines.reachmachine_off`, anything else `lines.reachmachine_down`. Apify: auth-style error `lines.apify_expired`, anything else `lines.apify_down`. Browser: not installed `lines.browser_missing`, can't start (no Node.js) `lines.no_node`. |

The `lines` are in `offers.connection_check.lines` of `record_session_start`'s result. Say each exactly as given, with its `{holes}` filled. A line that is not there: say nothing for it.

**An error that starts "Invalid arguments" means YOUR input was wrong, not the
connection.** Call the tool again with the exact input above. Never report it as ❌
broken and never tell the customer to sign in again because of it.

If the customer asks to carry on without Apify: do not skip the check; say `lines.apify_needed`, `{server}` = `apify`.

If Reach Machine is not ✅, add `lines.saved_later` after the list. Nothing else
changes in what you say to the customer.

## 4. Installing the browser

If the browser check fails because the browser program is not installed, offer to
install it. **Only after the customer says yes**, run the exact command the error text
gave you — `npx -y @playwright/mcp@0.0.79 install-browser <name>`, taking `<name>` from
that error text. Then re-run only the browser check (step 1, item 3).

## 5. "check again"

When the customer says "check again", make all three calls again from the top.

When all three connections show ✅, the report in section 3 already says so. Then
continue straight to step 2 (choose the workspace) — the `choose-workspace` skill.
