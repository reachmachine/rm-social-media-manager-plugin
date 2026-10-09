#!/usr/bin/env python3
"""Uploads a session's new transcript lines to Reach Machine, in the
background, after every turn and at session end (RMP-27/RMP-45).

Spec: docs/plugin-v2/01c-session-transcript.md §2, §5, §9. Called by
`transcript-upload.sh` (Stop + SessionEnd), which starts this as a detached
`setsid nohup` child and returns immediately -- see that script's own
docstring for why (`"async": true` was measured to NOT survive `claude -p`
exiting; a detached child does).

ONE PASS, THEN EXIT. `upload_once` does exactly one read-redact-send cycle
against the transcript file's CURRENT contents, then returns a short status
string (see its own docstring) -- it never loops or blocks on the file
growing further; the next Stop/SessionEnd starts the next pass.

FAIL-SAFE: this runs unattended on the customer's machine with nothing
watching stderr. `upload_once` never raises -- every branch that can fail
(the lock, the network, a corrupt cursor file, a redaction bug) degrades to
a status string, never a crash. `main()` wraps everything again and always
exits 0.
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

import plugin_api
import state_file_io
import transcript_cursor as tc
import transcript_extract
import transcript_redaction

_BATCH_SIZE = 200
_RETRY_DELAY_S = 2.0
_TOOL_NAMES_CAP = 2_000
_LOG_FILENAME = "upload.log"
_LOG_MAX_LINES = 200


def _log(session_id: str, status: str, count: int) -> None:
    """One local debug line per pass -- time, session id, status, counts.
    NEVER the entry text or the upload key. Capped at `_LOG_MAX_LINES`
    (trim the oldest). Never raises."""
    ts = datetime.now(timezone.utc).isoformat()
    state_file_io.append_trimmed_line(tc.transcripts_dir() / _LOG_FILENAME, f"{ts} session={session_id} status={status} count={count}", _LOG_MAX_LINES)


def _cap_tool_names(tool_names_by_id: dict[str, str]) -> None:
    """Drop the oldest entries once the map exceeds `_TOOL_NAMES_CAP`.
    Mutates in place -- insertion order is Python dict order, and entries
    are added in transcript order, so "oldest" means "first inserted"."""
    overflow = len(tool_names_by_id) - _TOOL_NAMES_CAP
    if overflow <= 0:
        return
    for key in list(tool_names_by_id.keys())[:overflow]:
        del tool_names_by_id[key]


def _redact_entries(entries: list[dict[str, Any]], upload_key: str) -> None:
    """Hides private details in every entry's `text`, in place, before
    anything is sent -- including this session's own upload key, so it can
    never leak through the conversation it authorizes."""
    home = os.path.expanduser("~")
    for entry in entries:
        text = entry.get("text")
        if isinstance(text, str):
            entry["text"] = transcript_redaction.redact_text(text, home=home, extra_secrets=(upload_key,))


def _post_batch(
    api_url: str, upload_key: str, session_id: str, batch: list[dict[str, Any]], timeout_s: float,
) -> str:
    """One batch, up to one retry after `_RETRY_DELAY_S` on a network error
    or 5xx (spec §5). Returns "sent" | "deleted" | "failed". Never raises."""
    body = json.dumps({
        "client_session_id": session_id,
        "redaction_version": transcript_redaction.REDACTION_VERSION,
        "entries": batch,
    }).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-RM-Upload-Key": upload_key,
        # RMP-57: Cloudflare blocks urllib's default "Python-urllib/3.x"
        # with a 403 ("error code: 1010"), so every upload failed on dev.
        "User-Agent": plugin_api.user_agent(),
    }
    for attempt in range(2):
        request = urllib.request.Request(api_url, data=body, method="POST", headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout_s):
                return "sent"
        except urllib.error.HTTPError as exc:
            if exc.code == 410:
                return "deleted"
            if exc.code >= 500 and attempt == 0:
                time.sleep(_RETRY_DELAY_S)
                continue
            return "failed"
        except Exception:
            if attempt == 0:
                time.sleep(_RETRY_DELAY_S)
                continue
            return "failed"
    return "failed"


def _api_url() -> str:
    """The `reachmachine` server URL from `.claude-plugin/plugin.json`, path
    swapped for `/api/v1/plugin/session-transcript` -- the dev->prod switch
    at publish needs no second edit here. `RM_TRANSCRIPT_API_URL` overrides
    it (tests only -- never the real dev/prod API from a unit test).

    P1669: the "read plugin.json, swap the path" logic itself now lives in
    `plugin_api.api_url`, shared with `website_upload.py`'s own upload URL --
    this function's own behaviour and env var are unchanged."""
    return plugin_api.api_url("/api/v1/plugin/session-transcript", "RM_TRANSCRIPT_API_URL")


def upload_once(session_id: str, transcript_path: str, *, api_url: str, timeout_s: float = 10.0) -> str:
    """One pass. Returns a short status for tests: "no_key" | "deleted" |
    "nothing_new" | "sent" | "failed" | "locked". Never raises."""
    lock_fd: int | None = None
    try:
        lock_file = tc.lock_path(session_id)
        if lock_file is None:
            return "no_key"  # bad session_id -- nothing safe to do
        lock_file.parent.mkdir(parents=True, exist_ok=True)
        lock_fd = os.open(str(lock_file), os.O_CREAT | os.O_RDWR, 0o600)
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            return "locked"  # Stop and SessionEnd can fire a second apart

        cursor = tc.read_cursor(session_id)
        if cursor.get("deleted") is True:
            return "deleted"
        upload_key = cursor.get("upload_key")
        if not isinstance(upload_key, str) or not upload_key:
            return "no_key"  # step 1 not recorded yet -- nothing is lost

        tool_names_by_id = cursor.get("tool_names_by_id")
        if not isinstance(tool_names_by_id, dict):
            tool_names_by_id = {}
        byte_offset = cursor.get("byte_offset") or 0
        next_seq = cursor.get("next_seq") or 0

        lines, new_offset = transcript_extract.read_new_lines(transcript_path, byte_offset)
        entries, next_seq_after = transcript_extract.to_entries(
            lines, start_seq=next_seq, tool_names_by_id=tool_names_by_id,
        )
        if not entries:
            if new_offset != byte_offset:
                cursor["byte_offset"] = new_offset
                tc.write_cursor(session_id, cursor)
            _log(session_id, "nothing_new", 0)
            return "nothing_new"

        _redact_entries(entries, upload_key)

        for start in range(0, len(entries), _BATCH_SIZE):
            batch = entries[start:start + _BATCH_SIZE]
            status = _post_batch(api_url, upload_key, session_id, batch, timeout_s)
            if status == "deleted":
                cursor["deleted"] = True
                tc.write_cursor(session_id, cursor)
                _log(session_id, "deleted", start)
                return "deleted"
            if status != "sent":
                # A failure half-way re-sends only the rest next pass --
                # nothing here is persisted, and re-sending everything from
                # this pass is harmless (the server dedupes by entry_id).
                _log(session_id, "failed", start)
                return "failed"

        _cap_tool_names(tool_names_by_id)
        cursor.update({
            "byte_offset": new_offset, "next_seq": next_seq_after,
            "tool_names_by_id": tool_names_by_id,
        })
        tc.write_cursor(session_id, cursor)
        _log(session_id, "sent", len(entries))
        return "sent"
    except Exception:
        return "failed"
    finally:
        if lock_fd is not None:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            except Exception:
                pass
            try:
                os.close(lock_fd)
            except Exception:
                pass


def main(argv: list[str]) -> int:
    """`--session <id> --transcript <path>`, call `upload_once`, always
    exit 0 -- see module docstring."""
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--session")
        parser.add_argument("--transcript")
        args = parser.parse_args(argv[1:])
        if args.session and args.transcript:
            upload_once(args.session, args.transcript, api_url=_api_url())
    except SystemExit:
        pass
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
