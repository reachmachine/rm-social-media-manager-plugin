#!/usr/bin/env python3
"""Step 10 "search in the customer's window" hooks (RMP-257, P2041, design 17.2/17.3/17.12).

For the blogs / events / linkedin channels the server hands a job a list of SEARCHES
(`run.mode == "websearch"`) instead of an Apify actor. The job runs them with the built-in
`WebSearch` tool. Three small handlers keep that honest. The plugin only enforces and carries;
every decision about which links count is made by the server.

  `handle_work_item`  PostToolUse on `get_hangouts_work`: store the issued searches under
                      `hangouts_websearch:<safe agent_id>` (via `tool_result_dispatch`).
  `decide`            PreToolUse on `WebSearch`: no record for THIS job -> no-op. Otherwise allow
                      only an issued, unused search (query exact, `allowed_domains` equal as a
                      set, no `blocked_domains`); mark it used under the file lock.
  `handle_result` /   PostToolUse / PostToolUseFailure on `WebSearch`: POST the links to the server.
  `handle_failure`    Links come ONLY from dict items' `content[*].url` in the raw tool result.
                      The model's own prose summary (a plain string in `results`) is never read.

FAIL-SAFE like `hangouts_upload.py`: never raises, never blocks an unrelated tool call, never logs
a URL, a title or the upload key (status only).
"""
from __future__ import annotations

import json
import sys
from typing import Any

import apify_actor_allowlist as aal
import connection_state as cs
import deny_lines
import hangouts_upload as hu
import slim_scraper_output
import state_file_io
import transcript_cursor as tc
from payload_util import tool_args

_PREFIX = "hangouts_websearch"
_PATH = "/api/v1/plugin/hangouts/websearch"
_MAX_SEARCHES = 50
_MAX_URLS = 20
_MAX_TITLE = 300
_MAX_URL = 2000
_DENY_OTHER = "search_exact"
_DENY_DONE = "search_done"


def _key(agent_id: Any) -> str | None:
    return f"{_PREFIX}:{aal._safe(agent_id)}" if isinstance(agent_id, str) and agent_id else None


def _domains(value: Any) -> tuple[str, ...] | None:
    """Sorted unique domains; `()` when absent; None when the value is not a list of strings."""
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        return None
    return tuple(sorted(set(value)))


def _record(session_id: str, key: str) -> dict[str, Any]:
    value = cs.read_raw(session_id).get(key)
    return value if isinstance(value, dict) and isinstance(value.get("searches"), dict) else {}


def _matches(search: Any, query: Any, domains: tuple[str, ...]) -> bool:
    return (isinstance(search, dict) and search.get("query") == query
            and _domains(search.get("allowed_domains")) == domains)


def _issued(run: dict) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    searches = run.get("searches")
    for item in searches[:_MAX_SEARCHES] if isinstance(searches, list) else []:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]:
            continue
        domains = _domains(item.get("allowed_domains"))
        if not isinstance(item.get("query"), str) or not item["query"] or domains is None:
            continue
        out[item["id"]] = {"query": item["query"], "allowed_domains": list(domains), "used": False}
    return out


def handle_work_item(session_id: str, payload: dict) -> None:
    """`PostToolUse` on `get_hangouts_work`. Never raises."""
    try:
        key = _key(payload.get("agent_id"))
        data = hu._json_dict(payload.get("tool_response"))
        run = data.get("run") if data else None
        run_id = run.get("run_id") if isinstance(run, dict) else None
        if not key or not isinstance(run_id, str) or not run_id:
            return
        if run.get("mode") != "websearch":
            if key in cs.read_raw(session_id):
                cs.write_patch(session_id, {key: None})   # this job moved on to a normal (Apify) run
            return
        if _record(session_id, key).get("run_id") == run_id:
            return   # the same open run again: keep which searches are used / posted
        searches = _issued(run)
        if searches:
            cs.write_patch(session_id, {key: {"run_id": run_id, "searches": searches}})
    except Exception:
        pass


def _deny(reason_id: str, session_id: str) -> dict:
    return deny_lines.resolve(session_id, deny_lines.deny_id(reason_id))   # RMP-291 P2321: the server's words


def _modify(session_id: str, mutate: Any) -> None:
    state_file_io.modify_json(cs.state_path(session_id), lambda: cs.read_raw(session_id), mutate)


def decide(payload: dict) -> dict | None:
    """None = allow. Never raises."""
    try:
        session_id, key = payload.get("session_id"), _key(payload.get("agent_id"))
        if payload.get("tool_name") != "WebSearch" or not key or not isinstance(session_id, str) or not session_id:
            return None
        if not _record(session_id, key):
            return None   # not a websearch job: step 8/9 research keeps its own rules
        args = tool_args(payload)
        domains = _domains(args.get("allowed_domains"))
        if args.get("blocked_domains") or domains is None:
            return _deny(_DENY_OTHER, session_id)
        verdict: list[str] = []

        def mutate(current: dict) -> None:
            rec = current.get(key)
            searches = rec.get("searches") if isinstance(rec, dict) else None
            found = [(sid, s) for sid, s in searches.items() if _matches(s, args.get("query"), domains)] \
                if isinstance(searches, dict) else []
            free = [sid for sid, s in found if not s.get("used")]
            if free:
                searches[free[0]]["used"] = True   # under the file lock: parallel calls count separately
            verdict.append("allow" if free else ("done" if found else "other"))

        _modify(session_id, mutate)
        if not verdict:   # lock or file trouble: fail-safe means never block
            return None
        return None if verdict[0] == "allow" else _deny(_DENY_DONE if verdict[0] == "done" else _DENY_OTHER, session_id)
    except Exception:
        return None


def _links(tool_response: Any) -> list[dict[str, str]]:
    """https links from DICT items' `content[*]` only; the prose string is never looked at."""
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    results = tool_response.get("results") if isinstance(tool_response, dict) else None
    for item in results if isinstance(results, list) else []:
        content = item.get("content") if isinstance(item, dict) else None
        for link in content if isinstance(content, list) else []:
            url = link.get("url") if isinstance(link, dict) else None
            if not isinstance(url, str) or not url.startswith("https://") or len(url) > _MAX_URL or url in seen:
                continue
            seen.add(url)
            title = link.get("title")
            out.append({"title": title[:_MAX_TITLE] if isinstance(title, str) else "", "url": url})
            if len(out) >= _MAX_URLS:
                return out
    return out


def _claim(session_id: str, key: str, args: dict, domains: tuple[str, ...]) -> tuple[str, str] | None:
    """Mark the matching search `posted` (used ones first); return (run_id, search_id) or None."""
    got: list[tuple[str, str]] = []

    def mutate(current: dict) -> None:
        rec = current.get(key)
        searches = rec.get("searches") if isinstance(rec, dict) else None
        if not isinstance(searches, dict):
            return
        found = [(sid, s) for sid, s in searches.items()
                 if _matches(s, args.get("query"), domains) and not s.get("posted")]
        found.sort(key=lambda pair: not pair[1].get("used"))
        if found:
            found[0][1]["posted"] = True
            found[0][1]["used"] = True
            got.append((str(rec.get("run_id")), found[0][0]))

    _modify(session_id, mutate)
    return got[0] if got else None


def _release(session_id: str, key: str, search_id: str) -> None:
    def mutate(current: dict) -> None:
        rec = current.get(key)
        search = rec.get("searches", {}).get(search_id) if isinstance(rec, dict) else None
        if isinstance(search, dict):
            search.pop("posted", None)

    _modify(session_id, mutate)


def _send(session_id: str, payload: dict, failed: bool) -> None:
    key = _key(payload.get("agent_id"))
    if not key or not _record(session_id, key):
        return
    upload_key = tc.read_cursor(session_id).get("upload_key")
    if not isinstance(upload_key, str) or not upload_key:
        return
    args = tool_args(payload)
    domains = _domains(args.get("allowed_domains"))
    claimed = _claim(session_id, key, args, domains) if domains is not None else None
    if claimed is None:
        return
    run_id, search_id = claimed
    urls = [] if failed else _links(payload.get("tool_response"))
    body = {"run_id": run_id, "search_id": search_id, "urls": urls, "failed": failed}
    if not hu._post(session_id, upload_key, body, _PATH):
        _release(session_id, key, search_id)   # a replay may try again; the server de-duplicates


def handle_result(session_id: str, payload: dict) -> None:
    """`PostToolUse` on `WebSearch`. Never raises."""
    try:
        _send(session_id, payload, failed=False)
    except Exception:
        pass


def _print_slim(session_id: str, payload: dict) -> None:
    """RMP-280: the model's copy of a job's search result, printed as `updatedToolOutput` after the links went
    to the server. Only for a job with an open websearch run. Never raises."""
    try:
        key = _key(payload.get("agent_id"))
        if not key or not _record(session_id, key):
            return
        response = payload.get("tool_response")
        slim = slim_scraper_output.websearch_slim(response, len(_links(response)))
        if slim is not None:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "updatedToolOutput": slim}}))
    except Exception:
        pass


def handle_failure(session_id: str, payload: dict) -> None:
    """`PostToolUseFailure` on `WebSearch`. Never raises."""
    try:
        _send(session_id, payload, failed=True)
    except Exception:
        pass


def main(argv: list[str]) -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    if not isinstance(payload, dict):
        return 0
    mode = argv[1] if len(argv) > 1 else "gate"
    try:
        if mode == "gate":
            result = decide(payload)
            if result is not None:
                print(json.dumps(result))
        else:
            session_id = payload.get("session_id")
            if payload.get("tool_name") == "WebSearch" and isinstance(session_id, str) and session_id:
                failed = payload.get("hook_event_name") == "PostToolUseFailure"
                (handle_failure if failed else handle_result)(session_id, payload)
                if not failed:
                    _print_slim(session_id, payload)
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
