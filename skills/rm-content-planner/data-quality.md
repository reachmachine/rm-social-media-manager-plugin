# When the data looks wrong — read this before you explain it

Sometimes a Reach Machine answer looks off: a topic list full of one-off
headlines, a reel whose details are nearly empty, a reel with more engagement
than views. **Never narrate around it, and never present it as clean.** Say the
likely reason in plain words, say what the person CAN still trust, and — only for
something not on this page — file it as a bug so it gets fixed.

Load this file whenever a read comes back looking wrong, or a tool call is rejected twice.
It is short on purpose.

## The three rules

1. **Say the likely reason, honestly and softly.** Always "this looks odd
   because… — likely", never a definite claim. You are reading a symptom, not a
   diagnosis, and a confident wrong reason is worse than an honest uncertain one.
   Then say what still holds: "the counts are fine, it is the grouping that is
   off."
2. **A signature already on this page is ALREADY REPORTED — do not file it
   again.** The team knows. Filing it again buries the new problems underneath
   the old ones. Tell the person, and move on.
3. **Anything NOT on this page → file it once** with `report_gap`:
   `type="bug"`, a short plain title, the symptom in `description`, the ACTUAL
   tool output in `evidence` (paste it, do not describe it), `where_it_hit` (the
   command or tool that surfaced it), `severity` by how much it hurts the person
   in front of you, and an `idempotency_key` built from the workspace, the
   signature and today's date — so a repeat sighting in the same session does not
   file a second copy. Then carry on answering; the report is fire-and-forget and
   never blocks the reply.

## The failure signatures

The Status column is for whoever maintains this page. **Never read a ticket key
out to the person you are talking to** — say "known issue, being fixed" or
"already handled", in their words, not ours.

| What you see | The likely reason, in plain words | Status |
| --- | --- | --- |
| A topic list of one-off headlines, each seen once | Topics used to be grouped by exact wording, so two ways of saying the same thing counted separately | FIXED — topic dictionary (FRFRMU-944, FRFRMU-945). If it comes back, that is a regression: report it |
| One reel's details are almost empty | Our analysis of that ONE reel broke part-way. The reel is fine; our reading of it is not | HANDLED — the read says `degraded: true` and names the step in `degraded_stages`. See the box below |
| A reel shows more engagement than views | The scrape brought back impossible numbers, and they used to be averaged in anyway | FIXED — flagged rows are now left out of averages and counted in `excluded_data_quality` (FRFRMU-947) |
| Older reels have no value for a field newer ones do | Those reels were analysed by an older version of our analysis, which did not record that field yet — so "nobody does this" and "we were not recording it yet" looked identical | HANDLED — the answer's metadata carries `schema_version_mix`; quote it instead of reading absence as a finding (FRFRMU-949) |
| A quoted spoken hook reads wrong or garbled | The transcript for that reel went out without passing our trust check | KNOWN — being fixed. Do not quote that hook; use a different reel |
| `get_topic_heat` says the topic dictionary is not built, while `get_content_strategy` shows a full `topic_distribution` from the same reels | Not a bug — and not the same thing. `topic_distribution` is the content-FAMILY (niche) mix ("AI automation tools"); `get_topic_heat` counts real grouped TOPICS, which need a separate dictionary this environment may not have built or switched on yet. Check `get_topic_heat`'s `state` field for which case you are in | HANDLED — read `state`, use the niche mix as weaker interim evidence, and say so in the receipt (FRFRMU-1109) |
| Anything else that looks wrong | You do not know yet — say so | NEW → file it with `report_gap`, rule 3 above |

## What already happens for a broken reel — so you do NOT report it

A reel whose analysis failed is handled end to end without you:

* **It is marked.** A per-reel read comes back with `degraded: true`,
  `degraded_stages` naming the step that failed, and a `degraded_note` you can
  pass on in plain words. Lists behave differently: `get_content_breakdown` and
  `get_posts_detailed` leave broken reels OUT and tell you how many in
  `excluded_broken_reels` — say that number when you cite the list.
* **The team is told once a day.** One bug report per workspace, per kind of
  failure, per day — not one per read. So a reel read fifty times files one
  report, and tomorrow's sighting files a fresh one because the problem is still
  there. **You do not need to report it, and you must not tell the person to
  report it either.**
* **When the team has switched it on, it is retried once a day.** One re-analysis
  per broken reel, per workspace, per day, and only for reels our own pipeline
  marked as worth retrying — a reel that was only ever pictures and music is not
  retried, because it would fail the same way and still be charged for. The retry
  runs in the background: nothing waits for it, and it never costs the person a
  reply.

So for a broken reel your whole job is: do not invent the missing content, say
plainly that our analysis of that reel failed and the team already knows, and
pick a different reel.

## Before you say "broken" — when a tool call is REJECTED

This section is about a call that came back with an error — not data that just
looks odd (that is the table above). Four rules, for ANY tool, not only Apify:

1. **Two strikes, then change the SHAPE.** The same validator message twice
   means the values are not the problem. The third try must change the shape
   — wrapper on/off, string vs object, key names copied from the schema — and
   you count the tries out loud in your notes ("try 3 of 3, shape changed").
2. **The verbatim bar.** You may not call a tool defective, to the customer or
   in `report_gap`, until you have sent the schema's own example values in the
   schema's own shape, copied not retyped, and you paste that exact call and
   its reply as `evidence`.
3. **The ruled-out ledger.** Every `report_gap` with `type: "bug"` names what
   you ruled out and how: my own input shape · my own earlier write · the
   workspace changing under me · connection/permission. If you tested none,
   `description` says **"cause unknown — not tested"**. "I don't know why"
   beats an untested story. (One real example: a team once blamed a null
   field on "a read-after-write delay" that turned out to be the agent's own
   earlier write silently overwriting it moments before — testing the shape
   first would have caught that.)
4. **What the customer hears.** Never "the tooling is broken". Before the bar
   is met: "I'm still working out why the Instagram search isn't running."
   After: "I couldn't get the Instagram search to run; I've logged it for the
   team." (Audience rule above still applies — the technical detail stays in
   `report_gap`, never in what the customer reads.)

## Keeping this page true

When a fix ships, its row moves to FIXED and gains the sentence "if it comes
back, that is a regression: report it". A row that says KNOWN after the fix
landed is worse than no row — it tells the agent to stay quiet about a bug that
is now new again.
