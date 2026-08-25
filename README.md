# Reach Machine Social Media Manager — Claude Code Plugin

Content planning agent + skill for Reach Machine, packaged as a Claude Code plugin.

## Install

Inside Claude Code, run:

```
/plugin marketplace add AI-DOC-Tools/rm-social-media-manager-plugin
/plugin install rm-social-media-manager@rm-social-media-manager-marketplace
```

## Update

When a new version is published here, run:

```
/plugin marketplace update rm-social-media-manager-marketplace
/reload-plugins
```

You can also turn on background auto-checking for this marketplace in Claude Code's
plugin settings — Claude Code will still ask you to run `/reload-plugins` once it
finds a newer version, it won't switch versions on you silently.

## What this plugin does

Adds Reach Machine competitor research, content planning, and analytics commands
to Claude Code, backed by the Reach Machine and Apify MCP servers. See `commands/`
for the full list, and `agents/social-media-manager.md` for the agent definition.
