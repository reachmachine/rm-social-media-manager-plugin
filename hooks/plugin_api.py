#!/usr/bin/env python3
"""Shared "which server does this plugin call" URL builder, plus the shared
`plugin.json` reader, User-Agent string, own-name lookup, and MCP tool-name
matcher (RMP-66, RMP-177).

Split out of `transcript_upload._api_url` so the new website-page uploader
(`website_upload.py`) can build the exact same kind of URL -- the
`reachmachine` server's own URL from `.claude-plugin/plugin.json`, with its
path swapped for whichever endpoint the caller needs -- without a second
copy of "read plugin.json, find the reachmachine URL, swap the path".
`transcript_upload._api_url` now calls this too (P1669); its own tests must
stay green, because this function's behaviour is unchanged from what that
file used to do inline.

`plugin_json`/`user_agent` moved here from `transcript_upload` (P1675) so
`website_upload._post_page` can send the same `User-Agent` header --
Cloudflare in front of the API answers a 403 ("error code: 1010") to
urllib's default `Python-urllib/3.x`, so any upload without it fails on dev
(RMP-57). `api_url` now reads `plugin.json` through `plugin_json` too, so
there is only one place that reads the file.

FAIL-SAFE: none of this ever raises. Any read failure (missing file, bad
JSON, no `mcpServers.reachmachine.url`) falls through to a hardcoded dev URL
or an "unknown" version -- the same fallback shape the transcript uploader
always had.

`plugin_name`/`server_of` (RMP-177): a plugin's MCP tools are named
`mcp__plugin_<plugin-name>_<server>__<tool>`. Before RMP-177, `server_of`
matched ANY plugin name (`[^_]+`), so a foreign plugin's same-named server
(e.g. v1's `apify`, still installed at user level) was counted as OUR
connection or gated by OUR steps. `server_of` now requires THIS plugin's own
name, read fresh from `plugin_json()` on every call so a rename (or a
test's `CLAUDE_PLUGIN_ROOT` override) takes effect immediately -- see that
docstring for why "fresh, not cached" also matters for tests.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import urllib.parse
from typing import Any

_DEV_HOST = "https://devapi.reachmachine.org"
_PROD_HOST = "https://api.reachmachine.org"
_DEFAULT_HOST = _DEV_HOST  # kept for older callers; use `fallback_host()`
_BUILD_TARGET_FILE = "build_target.json"
_DEFAULT_PLUGIN_NAME = "rm-plugin-v2"
_MCP_SERVERS = ("reachmachine", "apify", "playwright")


def _plugin_files(name: str) -> list[pathlib.Path]:
    candidates: list[pathlib.Path] = []
    root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if root:
        candidates.append(pathlib.Path(root) / ".claude-plugin" / name)
    candidates.append(pathlib.Path(__file__).resolve().parent.parent / ".claude-plugin" / name)
    return candidates


def plugin_json() -> dict[str, Any]:
    """The first readable `.claude-plugin/plugin.json` (CLAUDE_PLUGIN_ROOT
    first, then the copy beside this module). `{}` when none can be read.
    Never raises."""
    for path in _plugin_files("plugin.json"):
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
    return {}


def is_release_build() -> bool:
    """True only in a published copy. `build_release.py` writes
    `.claude-plugin/build_target.json` = {"target": "release"}; the source
    tree has no such file, so it is a dev build. Never raises (RMP-303)."""
    for path in _plugin_files(_BUILD_TARGET_FILE):
        try:
            return json.loads(path.read_text(encoding="utf-8")).get("target") == "release"
        except Exception:
            continue
    return False


def fallback_host() -> str:
    """The host used when `plugin.json` cannot be read. A release build falls
    back to PRODUCTION, never to dev (RMP-303)."""
    return _PROD_HOST if is_release_build() else _DEV_HOST


def user_agent() -> str:
    """`rm-plugin-v2/<version from plugin.json>`, or `rm-plugin-v2/unknown`
    when the version cannot be read. Never raises."""
    try:
        version = plugin_json().get("version")
        if isinstance(version, str) and version:
            return f"rm-plugin-v2/{version}"
    except Exception:
        pass
    return "rm-plugin-v2/unknown"


def plugin_name(default: str = _DEFAULT_PLUGIN_NAME) -> str:
    """This plugin's own name, from `plugin.json`'s `"name"` field. Falls
    back to `default` (the working name, `rm-plugin-v2`) when the file is
    missing, unreadable, or has no non-empty string `"name"` -- so
    tool-name matching (`server_of`, below) keeps working even if
    `plugin.json` is briefly unreadable, instead of silently matching every
    plugin's tools (the RMP-177 bug) or none at all. Never raises."""
    name = plugin_json().get("name")
    return name if isinstance(name, str) and name else default


def server_of(tool_name: Any) -> str | None:
    """This plugin's own server name ("reachmachine"/"apify"/"playwright")
    if `tool_name` is one of OUR MCP tools, else `None` -- including for a
    different plugin's server of the same name (RMP-177). Recomputes the
    pattern from `plugin_name()` on every call (cheap: one small file read)
    rather than caching it at import time, so a session that runs under one
    plugin name never keeps matching a stale one, and so tests can change
    `CLAUDE_PLUGIN_ROOT` between calls without a stale cache lying to them."""
    if not isinstance(tool_name, str):
        return None
    pattern = re.compile(
        rf"^mcp__plugin_{re.escape(plugin_name())}_({'|'.join(_MCP_SERVERS)})__"
    )
    match = pattern.match(tool_name)
    return match.group(1) if match else None


def api_url(path: str, env_override: str) -> str:
    """The `reachmachine` server's own scheme+host, with `path` swapped in.

    `env_override` is an ENV VAR NAME (not a value) -- when that variable is
    set, its value is returned as-is. Tests only; never used to reach the
    real dev/prod API from a unit test. Otherwise reads `plugin.json` via
    `plugin_json` and swaps its `reachmachine` server's path for `path`.
    Falls back to `path` on the dev host (source tree) or the PRODUCTION host
    (release build) if nothing resolves."""
    override = os.environ.get(env_override)
    if override:
        return override
    try:
        base = plugin_json()["mcpServers"]["reachmachine"]["url"]
        parsed = urllib.parse.urlsplit(base)
        if parsed.scheme and parsed.netloc:
            if is_release_build() and f"{parsed.scheme}://{parsed.netloc}" == _DEV_HOST:
                return f"{_PROD_HOST}{path}"  # a release never talks to dev
            return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, path, "", ""))
    except Exception:
        pass
    return f"{fallback_host()}{path}"
