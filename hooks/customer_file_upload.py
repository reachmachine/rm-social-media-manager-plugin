#!/usr/bin/env python3
"""Uploads a customer-named file/folder to the server (RMP-194 part 4).

Spec: RMP-194-DESIGN.md, "Part 2: Customer documents". Wired as a
`PostToolUse` hook on `send_customer_files`, driven by `customer_upload_
dispatch.py` (own dispatcher, NOT `connection_state_cli.py`, which is
already at the 300-line limit).

PATH SAFETY runs first (`customer_upload_path_guard.screen_path`) -- see
that module's own docstring for the full rule list. A refusal returns the
matching SERVER-WRITTEN line (RMP-76: the plugin only executes, never
invents its own wording) as this hook's return value; the caller
(`customer_upload_dispatch.py`) delivers it as `additionalContext`.

FAIL-SAFE, same convention as `website_upload.py`: never crashes the tool
call, never surfaces raw errors to the customer. Every failure -- no open
upload, no upload key, a network error, a non-2xx response -- degrades to a
one-line log entry (status/exception class only, NEVER the path, key, or
file content) in `customer_file_upload.log`, next to the other uploaders'
own log files.

THE FILE NEVER ENTERS THE CHAT: only its name and byte count travel through
this process's own local log; the model only ever sees the refusal line (if
any) and later, get_customer_upload's own name+status summary.
"""
from __future__ import annotations

import gzip
import io
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import customer_upload_kinds as kinds
import customer_upload_path_guard as guard
import customer_upload_state as cus
import plugin_api
import state_file_io
import transcript_cursor as tc
from payload_util import tool_args

_LOG_FILENAME = "customer_file_upload.log"
_LOG_MAX_LINES = 200
_TIMEOUT_S = 30.0
_UPLOAD_PATH = "/api/v1/plugin/customer-file"
_FALLBACK_REFUSAL = "I couldn't send that file -- please try a different one."


def _log(session_id: str, status: str) -> None:
    """One local debug line per file -- time, session id, status. NEVER the
    path, the upload key, or file content. Same convention as
    `website_upload._log`. Never raises."""
    ts = datetime.now(timezone.utc).isoformat()
    state_file_io.append_trimmed_line(tc.transcripts_dir() / _LOG_FILENAME, f"{ts} session={session_id} status={status}", _LOG_MAX_LINES)


def _maybe_gzip(data: bytes, kind: str) -> tuple[bytes, bool]:
    """Gzips text/csv content (design doc, Part 3 -- only these compress
    meaningfully); everything else travels uncompressed. Break: always
    return `(data, False)` -> a text file is never gzip-ed, still correct
    but no longer the falsifiable behaviour this pairs with (Rule 3 test)."""
    if not kinds.gzip_worth_it(kind):
        return data, False
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
        gz.write(data)
    return buf.getvalue(), True


def _post_file(
    session_id: str, upload_id: str, upload_key: str, path: Path, batch_total: int
) -> None:
    """One POST, one file. Never raises -- every failure is logged and
    swallowed (module docstring)."""
    try:
        data = path.read_bytes()
    except Exception as exc:
        _log(session_id, f"read_error_{type(exc).__name__}")
        return

    kind = kinds.kind_for_name(path.name) or ""
    body, gzipped = _maybe_gzip(data, kind)

    api_url = plugin_api.api_url(_UPLOAD_PATH, "RM_WEBSITE_API_URL")
    headers = {
        "Content-Type": "application/octet-stream",
        "X-RM-Upload-Key": upload_key,
        "X-RM-Upload-Id": upload_id,
        "X-RM-File-Name": path.name,
        "X-RM-Batch-Total": str(batch_total),
        # RMP-57: Cloudflare blocks urllib's default "Python-urllib/3.x".
        "User-Agent": plugin_api.user_agent(),
    }
    if gzipped:
        headers["Content-Encoding"] = "gzip"

    request = urllib.request.Request(api_url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT_S) as resp:
            _log(session_id, f"sent_{resp.status}")
    except urllib.error.HTTPError as exc:
        _log(session_id, f"http_{exc.code}")
    except Exception as exc:
        _log(session_id, f"error_{type(exc).__name__}")


def base_dir(payload: dict) -> Path | None:
    """The folder Claude runs in (the hook payload's own `cwd`), or None to use this process's folder."""
    cwd = payload.get("cwd")
    return Path(cwd) if isinstance(cwd, str) and cwd else None


def handle(session_id: str, payload: dict) -> str | None:
    """`PostToolUse` on `send_customer_files`. Returns a line to relay to the
    customer (a refusal) or `None` (nothing to say -- either no open upload,
    a malformed call, or a successful dispatch, which stays silent; the
    model learns the outcome from `get_customer_upload` instead)."""
    upload = cus.open_upload(session_id)
    if upload is None:
        return None

    args = tool_args(payload)
    raw_path = args.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        return None

    last_prompt = cus.last_prompt(session_id)
    files, refusal_key = guard.screen_path(raw_path, last_prompt, base_dir(payload))
    if refusal_key is not None:
        _log(session_id, f"refused_{refusal_key}")
        refusals = upload.get("refusals")
        refusals = refusals if isinstance(refusals, dict) else {}
        return refusals.get(refusal_key, _FALLBACK_REFUSAL)

    cursor = tc.read_cursor(session_id)
    upload_key = cursor.get("upload_key") if isinstance(cursor, dict) else None
    if not isinstance(upload_key, str) or not upload_key:
        _log(session_id, "no_upload_key")
        return None

    upload_id = upload.get("upload_id")
    if not isinstance(upload_id, str) or not upload_id:
        return None

    # RMP-194's Read/Bash/Glob gate needs to know WHICH path is now "sent for
    # you, don't open it" -- only set once the guard has actually passed and
    # a real send is starting, never for a refused call.
    cus.record_active_path(session_id, raw_path)

    total = len(files)
    for one_path in files:
        _post_file(session_id, upload_id, upload_key, one_path, total)
    return None
