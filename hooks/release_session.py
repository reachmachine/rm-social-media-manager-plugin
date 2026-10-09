#!/usr/bin/env python3
"""Releases this chat's workspace lease when the session ends cleanly
(RMP-79 part 3, docs/plugin-v2/08-one-chat-per-workspace.md "Design" step 4).

Called by `release-session.sh` (SessionEnd), alongside the existing
transcript-upload.sh SessionEnd hook. A clean close is the fast path for
freeing a workspace — without it, the customer would have to wait out the
15-minute lease TTL (`AGENT_WORKSPACE_LEASE_TTL_S`) before a second chat
could open the same workspace.

Reuses this session's own transcript-upload key (`transcript_cursor.
read_cursor`'s `upload_key` — the same one `record_session_start` issued and
`transcript_upload.py` already sends as `X-RM-Upload-Key`), so this needs no
new credential of its own. No key on file (step 1 never ran, or the
transcript was deleted) means nothing to release server-side either — quiet
no-op.

FAIL-SAFE: this runs unattended at session end with nothing watching
stderr, and MUST NEVER block or fail the session close (prompt: "timeout
<= 3 s, swallow failures"). `release_once` never raises; `main()` wraps it
again and always exits 0.
"""
from __future__ import annotations

import argparse
import sys
import urllib.error
import urllib.request

import plugin_api
import transcript_cursor as tc

_TIMEOUT_S = 3.0


def _api_url() -> str:
    """Same dev/prod-swap convention as `transcript_upload._api_url` /
    `website_upload`'s own URL builder — `RM_AGENT_SESSION_RELEASE_API_URL`
    overrides it (tests only)."""
    return plugin_api.api_url(
        "/api/v1/plugin/agent-session/release", "RM_AGENT_SESSION_RELEASE_API_URL",
    )


def release_once(session_id: str, *, api_url: str, timeout_s: float = _TIMEOUT_S) -> str:
    """One release attempt. Returns "no_key" | "released" | "failed" — for
    tests; the caller ignores the return value. Never raises."""
    try:
        cursor = tc.read_cursor(session_id)
        upload_key = cursor.get("upload_key")
        if not isinstance(upload_key, str) or not upload_key:
            return "no_key"  # step 1 never recorded a key -- nothing to release

        headers = {
            "X-RM-Upload-Key": upload_key,
            "Content-Length": "0",
            "User-Agent": plugin_api.user_agent(),
        }
        request = urllib.request.Request(api_url, data=b"", method="POST", headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout_s):
                return "released"
        except urllib.error.HTTPError:
            return "failed"
        except Exception:
            return "failed"
    except Exception:
        return "failed"


def main(argv: list[str]) -> int:
    """`--session <id>`, call `release_once`, always exit 0 (module
    docstring: must never block or fail SessionEnd)."""
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("--session")
        args = parser.parse_args(argv[1:])
        if args.session:
            release_once(args.session, api_url=_api_url())
    except SystemExit:
        pass
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
