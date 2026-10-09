#!/usr/bin/env python3
"""The `voice/` miss log's file I/O (RMP-106, RMP-198): append-and-trim to
`~/.claude/rm-plugin-v2/voice-misses.jsonl`.

Split out of `voice_check.py` (already at the 300-line cap) when RMP-198
added a second caller (`voice_check_midturn.py`, the mid-turn `PostToolUse`
scan) -- one file, one writer, so the `Stop` hook and the mid-turn scan can
never disagree on the path, the trim size, or the JSON shape.

Never raises -- a logging failure must never affect a hook's own decision,
same fail-safe direction as every write in this plugin's hooks.
"""
from __future__ import annotations

import json
import os
import pathlib

import state_file_io

MISSES_FILENAME = "voice-misses.jsonl"
MISSES_MAX_LINES = 200


def _plugin_home() -> pathlib.Path:
    override = os.environ.get("RM_PLUGIN_V2_HOME")
    if override:
        return pathlib.Path(override)
    return pathlib.Path.home() / ".claude" / "rm-plugin-v2"


def _misses_path() -> pathlib.Path:
    return _plugin_home() / MISSES_FILENAME


def append_entry(entry: dict) -> None:
    """Appends one JSON line, trimmed to the last `MISSES_MAX_LINES`. Never
    raises."""
    try:
        state_file_io.append_trimmed_line(_misses_path(), json.dumps(entry), MISSES_MAX_LINES)
    except Exception:
        pass
