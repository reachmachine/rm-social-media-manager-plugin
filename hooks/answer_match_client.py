#!/usr/bin/env python3
"""Thin HTTP client for `POST /api/v1/plugin/match-answer` (RMP-76 part 1).

`answer_matcher.py`'s `match_label`/`match_typed_reply` used to decide,
locally, which of a question step's options the customer's reply matched.
That decision now lives on the server (`app/services/plugin_answer_match.py`)
-- this module is the ONLY place that talks to it, one POST per call, same
upload-key auth as `website_upload.py`'s `_post_page`.

LATENCY BUDGET: this call sits in the middle of a live customer turn (a
`PostToolUse`/`UserPromptSubmit` hook, not a background upload), so there is
no retry here, unlike `transcript_upload._post_batch`'s one-retry-on-5xx --
a retry would double the worst case and blow the "under 2s" budget the
resilience test (`test_answer_match_client_resilience.py`) checks against a
deliberately slow fake server.

FAIL-SAFE, ask-again-not-guess: `call` returns the parsed response dict on a
clean 200, or `None` for EVERY other outcome -- no upload key yet, a
timeout, a connection error, a non-200 status, a body that is not valid
JSON, or a JSON body that is not an object. `None` here means "the server
could not be reached," and is NEVER confused with the server's own honest
`{"matched": false}` answer -- callers in `answer_matcher.py` keep those two
outcomes apart via the `UNREACHABLE` sentinel it defines. Never raises.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

import plugin_api
import state_file_io
import transcript_cursor as tc

_TIMEOUT_S = 1.5
_MATCH_PATH = "/api/v1/plugin/match-answer"
_LOG_FILENAME = "answer_match.log"
_LOG_MAX_LINES = 200


def _log(session_id: str, status: str) -> None:
    """One local debug line per call -- time, session id, status. NEVER the
    reply text or the upload key. Capped at `_LOG_MAX_LINES` (trim the
    oldest). Never raises. Same shape as `transcript_upload._log`/
    `website_upload._log`, next to their own log files."""
    ts = datetime.now(timezone.utc).isoformat()
    state_file_io.append_trimmed_line(tc.transcripts_dir() / _LOG_FILENAME, f"{ts} session={session_id} status={status}", _LOG_MAX_LINES)


def call(session_id: str, body: dict[str, Any]) -> dict[str, Any] | None:
    """One request, no retry. `body` is already the exact JSON shape
    `app/api/routes/plugin_answer_match.py` expects (built by
    `answer_matcher.py`). Returns the parsed response, or `None` if the
    server could not be reached or answered anything but a valid JSON
    object."""
    upload_key = tc.read_cursor(session_id).get("upload_key")
    if not isinstance(upload_key, str) or not upload_key:
        _log(session_id, "no_key")
        return None

    api_url = plugin_api.api_url(_MATCH_PATH, "RM_MATCH_API_URL")
    data = json.dumps(body).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-RM-Upload-Key": upload_key,
        # RMP-57: Cloudflare blocks urllib's default "Python-urllib/3.x".
        "User-Agent": plugin_api.user_agent(),
    }
    request = urllib.request.Request(api_url, data=data, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT_S) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        _log(session_id, f"http_{exc.code}")
        return None
    except Exception as exc:
        _log(session_id, f"error_{type(exc).__name__}")
        return None

    try:
        result = json.loads(raw)
    except Exception:
        _log(session_id, "bad_json")
        return None
    if not isinstance(result, dict):
        _log(session_id, "bad_shape")
        return None
    _log(session_id, "ok")
    return result
