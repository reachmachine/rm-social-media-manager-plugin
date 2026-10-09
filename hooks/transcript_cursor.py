#!/usr/bin/env python3
"""Shared cursor-file I/O for the session-transcript uploader (RMP-27/RMP-45).

Spec: docs/plugin-v2/01c-session-transcript.md §2, §5. One file per session,
`<plugin home>/transcripts/<session_id>.json` (plugin home = `RM_PLUGIN_V2_
HOME` or `~/.claude/rm-plugin-v2`, same convention as `session_record.
_plugin_home`), mode 0600, written atomically (temp file + `os.replace`):
    {"upload_key": str|None, "byte_offset": int, "next_seq": int,
     "tool_names_by_id": {...}, "deleted": bool}

TWO WRITERS, ONE SHAPE. `session_record.handle_record_session_start`
(PostToolUse of `record_session_start`) calls `save_upload_key` -- the ONLY
field it ever touches (a resumed session keeps its offset). `transcript_
upload.upload_once` (the Stop/SessionEnd background uploader) reads and
writes every field. Both live in this one module, not two independent
copies, so the file's shape can never drift between the two writers -- P1636
split this out of `session_record.py` (already at 249 lines) rather than
duplicating cursor I/O there, see prompts/COMMS.md.

SESSION ID = FILENAME. `session_id` must match `_SESSION_ID_RE` (letters,
digits, hyphens only -- the same pattern as the backend's own
`agent_session_check_store._CLIENT_SESSION_ID_RE`, ported here because the
plugin ships stdlib-only and cannot import the backend) before it becomes a
path component. `cursor_path`/`lock_path` return `None` for anything else,
so a `../` (or any other shape) never escapes the `transcripts/` directory.

FAIL-SAFE: every function here catches its own exceptions and degrades to
the safe default (an empty cursor, or doing nothing) -- this runs inside
hooks that must never crash a tool call.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
from typing import Any

_SESSION_ID_RE = re.compile(r"^[A-Za-z0-9-]+$")
_TRANSCRIPTS_DIRNAME = "transcripts"


def _plugin_home() -> pathlib.Path:
    override = os.environ.get("RM_PLUGIN_V2_HOME")
    if override:
        return pathlib.Path(override)
    return pathlib.Path.home() / ".claude" / "rm-plugin-v2"


def transcripts_dir() -> pathlib.Path:
    return _plugin_home() / _TRANSCRIPTS_DIRNAME


def _valid_session_id(session_id: Any) -> bool:
    return isinstance(session_id, str) and bool(_SESSION_ID_RE.match(session_id))


def cursor_path(session_id: str) -> pathlib.Path | None:
    """`None` for anything that is not a safe filename -- see module
    docstring ("no path tricks"). Never raises."""
    if not _valid_session_id(session_id):
        return None
    return transcripts_dir() / f"{session_id}.json"


def lock_path(session_id: str) -> pathlib.Path | None:
    if not _valid_session_id(session_id):
        return None
    return transcripts_dir() / f"{session_id}.json.lock"


def empty_cursor() -> dict[str, Any]:
    return {
        "upload_key": None, "byte_offset": 0, "next_seq": 0,
        "tool_names_by_id": {}, "deleted": False,
    }


def read_cursor(session_id: str) -> dict[str, Any]:
    """Missing, corrupt, wrong-shape file, or a bad session_id all read as
    `empty_cursor()`. Never raises."""
    cursor = empty_cursor()
    path = cursor_path(session_id)
    if path is None:
        return cursor
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return cursor
    if not isinstance(data, dict):
        return cursor
    for key in cursor:
        if key in data:
            cursor[key] = data[key]
    return cursor


def write_cursor(session_id: str, cursor: dict[str, Any]) -> None:
    """Atomic (temp file + `os.replace`), mode 0600. Never raises -- a write
    failure here must degrade to "progress not saved", not a crash."""
    path = cursor_path(session_id)
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(path.name + ".tmp")
        tmp.write_text(json.dumps(cursor), encoding="utf-8")
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    except Exception:
        pass


def save_upload_key(session_id: str, upload_key: str) -> None:
    """Called by `session_record.handle_record_session_start`. Creates the
    cursor file if missing, keeps every other field (a resumed session
    continues where it stopped) -- only `upload_key` is replaced."""
    try:
        cursor = read_cursor(session_id)
        cursor["upload_key"] = upload_key
        write_cursor(session_id, cursor)
    except Exception:
        pass
