---
description: "Switch the active workspace (one per client) and re-confirm whose account you are planning for. Free, never spends credits"
argument-hint: "[workspace name, or leave empty to list them]"
---

Switch which workspace is active. **Reads and one setting change — never spends credits.**
Workspace scoping is the skill's PLAYBOOK Step 3 rule 1 (`playbook/step-03-mcp.md`) — one
workspace per client, confirmed
deliberately, never assumed.

Target: $ARGUMENTS

1. `list_workspaces` — show them with the active one marked. **A workspace with `locked=true`
   (FRFRMU-1145) is still listed, never hidden — nothing is deleted — but mark it with a lock
   and say it is locked, not just "unavailable."** If `$ARGUMENTS` is empty, ask which one;
   never guess.
2. `set_active_workspace` for the chosen one, **on its own**, then **confirm the switch back
   by name**. Nothing from point 3 may travel in the same message as this call: it changes
   which workspace a read answers for, so a read sent alongside it can still describe the OLD
   workspace — and the user would never know.
   - **If the response comes back `locked=true`:** the switch did NOT happen — do not treat
     `confirmed=false` as success and do not retry. Relay `message` word for word (it names
     both the limit and the current count). If `can_swap=true`, offer the swap: naming this
     workspace open means one other workspace will lock to make room — say which one, and
     name any team members who would lose access, before asking them to confirm via
     `keep_workspace_open`. Never call a spend tool while a workspace is locked.
3. **Then send these four reads in ONE message — they do not depend on each other:**
   `get_workspace_stats`, `get_analysis_coverage`, `get_business_profile` and
   `get_creator_brief`. One round-trip, not four. The first two show what is actually in the
   new workspace — a switch changes the whole data picture, and the user needs to see the new
   one rather than assume it matches the old. The other two feed the handle re-check below.

## 🔴 Re-confirm the Instagram handle after EVERY switch (G223)

The Instagram handle is saved **per account, not per workspace.** So after switching to a new
client's workspace, the saved handle may still be the **previous** client's, and nothing warns
you. A plan built on it would silently describe the wrong business.

So: use the profile and brief you pulled in point 3, show the handle
you found, and **ask in one line whether it belongs to this workspace's client.** If it does
not, fix it with `update_business_profile` before doing anything else. Never carry a handle
across a switch on assumption. This is a known open product bug, not a normal step — say
plainly that you are double-checking because the handle is shared account-wide.

**If the handle they give is a DIFFERENT business, not a new handle for the same one (FRFRMU-1146)
— ask this, never skip it:** *"is this the same business under a new handle, or a different
business entirely?"* Same business → update the handle here, as above. A different business
→ this workspace still holds the OLD business's saved brief and detected niche; route to
`/rm-social-media-manager:repurpose-workspace` instead of silently patching the handle — that
command is the one deliberate reset, and swaps in a swap-first offer before it resets anything.

Also re-check positioning: **positioning IS per-workspace**, so a new workspace may simply have
none yet. Missing positioning means any plan can only clone competitors — route to
`/rm-social-media-manager:know-business` to set it.

**Hard limit:** never call a spend or destructive tool here, and never call Apify.
