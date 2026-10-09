#!/usr/bin/env python3
"""Reads a step 10 dataset page that Claude Code moved to a file (RMP-218, P1860).

WHY: one Instagram profile row can be 70-90k characters. Over Claude Code's tool-result limit, the model and the
hook get only a note ("... exceeds maximum allowed tokens. Output has been saved to <path>"). The saved file holds
the normal `get-dataset-items` JSON, and the hook runs on the same machine, so it can read it.

SAFETY: the path comes from tool-result text, so it is never trusted. It is used only when, after `realpath`
(symlinks and `..` resolved), it is a regular file of at most `max_bytes`, inside a `tool-results` folder under
`<Claude home>/projects/`, and named like a `get-dataset-items` result of this plugin. Anything else gives None.
Never raises, never logs the path or any content.
"""
from __future__ import annotations

import os
import re
import stat
from pathlib import Path

_PATH_RE = re.compile(r"saved to (/\S+?\.txt)")
_FILE_PREFIX = "mcp-plugin_rm-plugin-v2_apify-get-dataset-items"
_FOLDER = "tool-results"


def _projects_root() -> str:
    home = os.environ.get("CLAUDE_CONFIG_DIR") or str(Path.home() / ".claude")
    return os.path.realpath(os.path.join(home, "projects"))


def _safe_path(note: str) -> str | None:
    match = _PATH_RE.search(note)
    if not match:
        return None
    resolved = os.path.realpath(match.group(1))
    root = _projects_root()
    parent = os.path.dirname(resolved)
    if os.path.basename(parent) != _FOLDER or not parent.startswith(root + os.sep):
        return None
    if not os.path.basename(resolved).startswith(_FILE_PREFIX):
        return None
    return resolved


def read_diverted_page(note: str, max_bytes: int) -> str | None:
    """The saved page's text for a diverted-result `note`, or None for any refusal or failure."""
    try:
        path = _safe_path(note)
        if path is None or not stat.S_ISREG(os.stat(path).st_mode):
            return None
        with open(path, "rb") as fh:
            raw = fh.read(max_bytes + 1)   # bounded read: a file that grows after the stat check is still capped
        if len(raw) > max_bytes:
            return None
        return raw.decode("utf-8")
    except Exception:
        return None
