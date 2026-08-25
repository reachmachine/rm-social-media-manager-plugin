---
description: "Switch the active workspace (one per client) and re-confirm whose account you are planning for. Free, never spends credits"
argument-hint: "[workspace name, or leave empty to list them]"
---

Switch which workspace is active. **Reads and one setting change — never spends credits.**
Workspace scoping is the skill's PLAYBOOK Step 3 rule 1 — one workspace per client, confirmed
deliberately, never assumed.

Target: $ARGUMENTS

1. `list_workspaces` — show them with the active one marked. If `$ARGUMENTS` is empty, ask
   which one; never guess.
2. `set_active_workspace` for the chosen one, then **confirm the switch back by name**.
3. **Show what is actually in the new workspace** — `get_workspace_stats` +
   `get_analysis_coverage`. A workspace switch changes the whole data picture; the user needs
   to see the new one, not assume it matches the old.

## 🔴 Re-confirm the Instagram handle after EVERY switch (G223)

The Instagram handle is saved **per account, not per workspace.** So after switching to a new
client's workspace, the saved handle may still be the **previous** client's, and nothing warns
you. A plan built on it would silently describe the wrong business.

So: call `get_business_profile` and `get_creator_brief` right after the switch, show the handle
you found, and **ask in one line whether it belongs to this workspace's client.** If it does
not, fix it with `update_business_profile` before doing anything else. Never carry a handle
across a switch on assumption. This is a known open product bug, not a normal step — say
plainly that you are double-checking because the handle is shared account-wide.

Also re-check positioning: **positioning IS per-workspace**, so a new workspace may simply have
none yet. Missing positioning means any plan can only clone competitors — route to
`/rm-social-media-manager:know-business` to set it.

**Hard limit:** never call a spend or destructive tool here, and never call Apify.
