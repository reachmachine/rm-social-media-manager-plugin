> **Playbook step file — load only this one.** The full step list, and which file holds each
> step, is in `PLAYBOOK.md` (small, always loaded). A "Step N" reference below means that
> step's file in this same `playbook/` folder.

## Step 12 (transcript consent) — a SECOND, separate ask: save the conversation too? (FRFRMU-1596)

**Load this the moment `submit_content_plan` comes back `stored: true` — right after step 3's
confirmation in `playbook/step-12-capture.md`, before step 4 there loads the write-backs.**
`save_planning_transcript` was built (FRFRMU-1021), flag-enabled in production, and never once
called — nothing in the skill instructed the agent to call it, so no transcript was ever saved.
This file closes that gap, with the founder-approved consent (Jira FRFRMU-1596, comment 16491).

**🔴 Headless runs never reach this ask.** Same reasoning as `step-12-capture.md`'s own
headless note (G208): `consent: true` means "a human just said yes," and a headless run has no
human to ask. `runner.py`'s allow-list deliberately excludes `save_planning_transcript`, for the
identical reason it excludes `submit_content_plan`.

**🔴 Ask, SEPARATELY, whether to save the planning CONVERSATION too — call
`save_planning_transcript`.** This is a second, independent consent. It is **never the same yes
as step 1's plan-save consent** in `step-12-capture.md`, and it **defaults to NO** — a creator
who agreed to save the PLAN has agreed to nothing about the CONVERSATION that built it. Ask it
only now, after the plan is already confirmed saved, because this is the point where the creator
can see what was actually discussed — never up front, before anything exists.

Ask using this exact wording (founder-approved, do not reword it, and never add any claim about
virality or guaranteed results — this product has a compliance rule against results-guarantee
language, FRFRMU-1525):

> **Save this planning conversation?**
> Saving it lets us see how this plan was built and keep improving the method, so future plans
> are more likely to perform well. It may include the business details you shared in this
> session.
> Your content plan is saved either way — this is only about the conversation. You can say no.

- **On an explicit yes**, call `save_planning_transcript` with:
  - **`plan_id`** — the same `plan_id` `submit_content_plan` just returned.
  - **`skill_version`** — read `${CLAUDE_SKILL_DIR}/VERSION` fresh, exactly as the plan save does.
  - **`consent: true`** — ONLY because the creator just said yes to THIS ask. Never carry step
    1's plan-save consent over, and never set this true without the ask.
  - **`turns`** — the ordered conversation for this planning session: `role`
    (`user`/`agent`/`tool`), `text` (or a plain summary for a tool turn), `tool_name` +
    `tool_args_summary` + `cost_credits` when the turn IS a tool call, `decision` + `confidence`
    when you stated one. Never write a raw token or a full URL with its query string into
    `text`/`tool_args_summary` — the server strips shapes that look like a bearer token or a URL
    query as a backstop, but do not rely on that; write it clean yourself.
  - **`idempotency_key`** — a fresh unique string for this save, same rule as the plan save's.
- **On a "no", or on no answer at all** — say nothing more about it and move straight on to
  `playbook/step-12-after-the-save.md`. The plan already saved is complete and normal either
  way: no degraded output, no repeat asking, no nagging. **Silence is never a yes.**
- **Retry the same way as the plan save** if the call errors or times out (up to three tries,
  ~2 seconds then ~5, reusing the same `idempotency_key`). A repeat comes back
  `already_stored: true` — treat that as success and stop. If write tools are not enabled on
  this connection, say so once and move on — **never fail the delivered plan over this.**
- **This is never in place of, and never bundled with, `step-12-capture.md`'s plan-save
  consent.** A creator who says yes to saving the PLAN has said nothing about the CONVERSATION —
  always ask this one on its own, in its own turn.

**Once this is settled (yes, no, or silence), continue to
`playbook/step-12-after-the-save.md`** — the two write-backs there do not depend on this ask
either way.
