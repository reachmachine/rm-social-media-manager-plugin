# Reach Machine Social Media Manager — Claude Code Plugin

Content planning agent + skill for Reach Machine, packaged as a Claude Code plugin.

This folder is the source of truth. It is mirrored out to its own public repo
(`github.com/reachmachine/rm-social-media-manager-plugin`) by `scripts/publish-plugin.sh`
so customers can install and update it without access to the main Reachmachine codebase.

## Install

Inside Claude Code, run:

```
/plugin marketplace add reachmachine/rm-social-media-manager-plugin
/plugin install rm-social-media-manager@rm-social-media-manager-marketplace
```

## Update

When a new version is published, run:

```
/plugin marketplace update rm-social-media-manager-marketplace
/reload-plugins
```

Background auto-checking can be turned on for this marketplace in Claude Code's plugin
settings — it will still ask for `/reload-plugins` once it finds a newer version, it
never switches versions silently.

## Publishing a new version (for maintainers)

1. Bump `"version"` in `.claude-plugin/plugin.json`.
2. From the repo root, run `scripts/publish-plugin.sh`.
3. It mirrors every git-tracked file under this folder into the plugin repo, commits,
   tags `vX.Y.Z`, and pushes.

## What this plugin does

Adds Reach Machine competitor research, content planning, and analytics commands
to Claude Code, backed by the Reach Machine and Apify MCP servers. See `commands/`
for the full list, and `agents/social-media-manager.md` for the agent definition.
