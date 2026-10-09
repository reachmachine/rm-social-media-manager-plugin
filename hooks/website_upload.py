#!/usr/bin/env python3
"""Uploads each page the `website-reader` agent pulls in, one POST per
`browser_evaluate` call (RMP-66).

Spec: docs/plugin-v2/06-website-and-business-knowledge.md, "Wave 2 design",
"Reading the site (plugin)", "Upload hook". Wired from
`connection_state_cli.py`'s `PostToolUse` record entry for playwright
`browser_evaluate`, only while a website read is open
(`website_read_state.open_read`).

PARSING THE RESULT: `agents/website-reader.md`'s one fixed `browser_evaluate`
snippet returns a JS object; Claude Code wraps that as MCP text content
shaped `"### Result\\n<pretty JSON>\\n### Ran Playwright code\\n..."`
(captured live 2026-09-25, `tests/fixtures/capture_browser_evaluate_2026-09-
25.json`). `connection_state.flatten_response_text` reads the text out of
`tool_response` the same way every other hook here does; `_parse_evaluate_
result` then pulls the JSON between the `"### Result\\n"` marker and the
next `"\\n### "` line.

ONLY A REAL PAGE RESULT IS UPLOADED: a robots.txt/sitemap/link-list
`browser_evaluate` call (the agent's own reconnaissance, not this fixed
snippet) returns some other shape entirely -- no `url`/`text` at all, or the
wrong types -- and is silently skipped, never uploaded, never logged as an
error. An off-site `url` (the read's own site check, `website_read_state.
same_site`) is skipped the same way.

RMP-172: the snippet's `shop_evidence` is RAW, unclassified facts (a
generator meta value, ld+json blocks, cart-hint element texts, price-like
text snippets) -- the browser no longer decides platform/shop itself, the
server does, over these same fields, exactly as it does for a page it
fetched directly. Before this, the browser ran its own cruder copy of that
classification and disagreed with the server's (a Wix generator tag came out
"wix.com" in the browser, "wix" on the server), so a Wix/Squarespace site
read through this fallback silently never counted as a shop.

FAIL-SAFE, ON PURPOSE (spec: "Never blocks, never raises"): this must never
crash the tool call that triggered it, and it must never surface an error to
the customer. Every failure -- no open read, malformed result, off-site
page, no upload key, a network error, a non-2xx response -- degrades to
"upload this page" silently or ONE line in `website_upload.log` (next to the
transcript uploader's own `upload.log`, same directory) holding only the
status code or the exception's class name -- NEVER the upload key, and NEVER
the page text.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

import connection_state as cs
import plugin_api
import state_file_io
import transcript_cursor as tc
import website_read_state as wrs

_LOG_FILENAME = "website_upload.log"
_LOG_MAX_LINES = 200
_TIMEOUT_S = 8.0
_UPLOAD_PATH = "/api/v1/plugin/website-pages"
_RESULT_MARKER = "### Result\n"
_NEXT_SECTION_MARKER = "\n### "

# RMP-172: mirror the server's own limits (app.api.routes.website_pages_
# upload.RawShopEvidence / PageUpload.social_links) so a shape the server
# would reject only drops the offending piece -- never the whole page's
# url/title/text, since RawShopEvidence is extra="forbid".
_SHOP_EVIDENCE_GENERATOR_MAX_LEN = 200
_SHOP_EVIDENCE_LD_JSON_MAX = 5
_SHOP_EVIDENCE_LD_JSON_CHARS_MAX = 4000
_SHOP_EVIDENCE_CART_HINTS_MAX = 20
_SHOP_EVIDENCE_CART_HINT_CHARS_MAX = 120
_SHOP_EVIDENCE_PRICE_SNIPPETS_MAX = 30
_SHOP_EVIDENCE_PRICE_SNIPPET_CHARS_MAX = 40
_SOCIAL_LINKS_MAX = 10
_SOCIAL_LINK_MAX_LEN = 2000


def _log(session_id: str, status: str) -> None:
    """One local debug line per attempt -- time, session id, status. NEVER
    the upload key or the page text. Capped at `_LOG_MAX_LINES` (trim the
    oldest), same convention as `transcript_upload._log`. Never raises."""
    ts = datetime.now(timezone.utc).isoformat()
    state_file_io.append_trimmed_line(tc.transcripts_dir() / _LOG_FILENAME, f"{ts} session={session_id} status={status}", _LOG_MAX_LINES)


def _parse_evaluate_result(tool_response: Any) -> dict[str, Any] | None:
    """The JSON object between `"### Result\\n"` and the next `"\\n### "`
    line, or `None` for anything that does not have that shape at all
    (robots.txt/sitemap/link-list calls, or a page that failed to
    evaluate)."""
    text = cs.flatten_response_text(tool_response)
    start = text.find(_RESULT_MARKER)
    if start == -1:
        return None
    start += len(_RESULT_MARKER)
    end = text.find(_NEXT_SECTION_MARKER, start)
    json_text = text[start:end] if end != -1 else text[start:]
    try:
        data = json.loads(json_text)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _clean_str_list(value: Any, *, max_items: int, max_len: int) -> list[str]:
    """Only non-empty strings, each cut to `max_len`, list capped at
    `max_items`. Not a list at all -> `[]`. Shared bound-and-clean step for
    every `RawShopEvidence` list field (RMP-172) -- same convention as
    `_clean_social_links` below."""
    if not isinstance(value, list):
        return []
    cleaned: list[str] = []
    for item in value:
        if len(cleaned) >= max_items:
            break
        if isinstance(item, str) and item:
            cleaned.append(item[:max_len])
    return cleaned


def _clean_shop_evidence(evidence: Any) -> dict[str, Any] | None:
    """The browser's raw `shop_evidence` bundle (RMP-172), cleaned to only
    the fields/bounds the server's `RawShopEvidence` schema accepts -- or
    `None` when `evidence` itself is not a dict, or nothing about it
    survives cleaning. Because `RawShopEvidence` is `extra="forbid"`,
    forwarding it unfiltered risks a 422 that would reject the WHOLE page
    (url/title/text too); this keeps that from ever happening.
    Break: return `evidence` unchanged -> RED (Rule 3 test)."""
    if not isinstance(evidence, dict):
        return None
    cleaned: dict[str, Any] = {}
    generator = evidence.get("generator")
    if isinstance(generator, str) and generator:
        cleaned["generator"] = generator[:_SHOP_EVIDENCE_GENERATOR_MAX_LEN]
    ld_json = _clean_str_list(
        evidence.get("ld_json"),
        max_items=_SHOP_EVIDENCE_LD_JSON_MAX,
        max_len=_SHOP_EVIDENCE_LD_JSON_CHARS_MAX,
    )
    if ld_json:
        cleaned["ld_json"] = ld_json
    cart_hints = _clean_str_list(
        evidence.get("cart_hints"),
        max_items=_SHOP_EVIDENCE_CART_HINTS_MAX,
        max_len=_SHOP_EVIDENCE_CART_HINT_CHARS_MAX,
    )
    if cart_hints:
        cleaned["cart_hints"] = cart_hints
    price_snippets = _clean_str_list(
        evidence.get("price_snippets"),
        max_items=_SHOP_EVIDENCE_PRICE_SNIPPETS_MAX,
        max_len=_SHOP_EVIDENCE_PRICE_SNIPPET_CHARS_MAX,
    )
    if price_snippets:
        cleaned["price_snippets"] = price_snippets
    return cleaned or None


def _clean_social_links(value: Any) -> list[str]:
    """Only non-empty strings, each capped at `_SOCIAL_LINK_MAX_LEN`, list
    capped at `_SOCIAL_LINKS_MAX` -- matches the server's `PageUpload.
    social_links` field/list length caps so an over-generous browser result
    never 422s the page. Not a string list at all -> `[]`."""
    if not isinstance(value, list):
        return []
    cleaned: list[str] = []
    for item in value:
        if len(cleaned) >= _SOCIAL_LINKS_MAX:
            break
        if isinstance(item, str) and item and len(item) <= _SOCIAL_LINK_MAX_LEN:
            cleaned.append(item)
    return cleaned


def _outcome_status(body_bytes: bytes) -> str:
    """"sent" normally, "sent_unmatched" (RMP-179) when the server's own JSON
    body says `"matched": false` -- this upload did not resolve any planned
    `browser_pages` entry, so the reader is about to be handed the SAME url
    again. Visibility (a log line) only: the reader's own loop is driven
    purely by the server's `browser_pages` list on the NEXT `wait_for_
    website_read` call, never by this hook, so a body we cannot parse (or
    that omits `matched` entirely -- an older server) simply falls back to
    "sent", same as before this existed.
    Break: always return "sent" -> RED (Rule 3 test)."""
    try:
        data = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        return "sent"
    if isinstance(data, dict) and data.get("matched") is False:
        return "sent_unmatched"
    return "sent"


def _post_page(session_id: str, read_id: str, upload_key: str, page: dict[str, Any]) -> None:
    """One POST, one page. Never raises -- every failure is logged and
    swallowed (module docstring). Break: remove this try/except and let the
    exception escape -> RED (Rule 3 test 5)."""
    api_url = plugin_api.api_url(_UPLOAD_PATH, "RM_WEBSITE_API_URL")
    body = json.dumps({"read_id": read_id, "pages": [page]}).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-RM-Upload-Key": upload_key,
        # RMP-57: Cloudflare blocks urllib's default "Python-urllib/3.x"
        # with a 403 ("error code: 1010"), so every upload failed on dev.
        "User-Agent": plugin_api.user_agent(),
    }
    request = urllib.request.Request(api_url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT_S) as resp:
            _log(session_id, _outcome_status(resp.read()))
    except urllib.error.HTTPError as exc:
        _log(session_id, f"http_{exc.code}")
    except Exception as exc:
        _log(session_id, f"error_{type(exc).__name__}")


def handle(session_id: str, payload: dict) -> None:
    """`PostToolUse` on playwright `browser_evaluate`. No-op unless: a read
    is open, the result parses to a dict with a non-empty str `url` and a
    non-empty str `text`, and that `url` is on the read's own site.

    RMP-172: `shop_evidence` (raw, unclassified facts -- see the module
    docstring) and `social_links` (footer/header Instagram hrefs, RMP-166)
    travel on the same evaluate result and are cleaned + forwarded too,
    whenever the browser snippet sent them -- see `_clean_shop_evidence`/
    `_clean_social_links`. Before RMP-167 both were parsed out of `data` and
    silently thrown away; RMP-172 replaced the browser's own ALREADY-
    CLASSIFIED `shop` object with these raw facts, which the server now
    classifies itself (`page_shop_raw_evidence.classify_raw_shop_evidence`)."""
    read = wrs.open_read(session_id)
    if read is None:
        return
    data = _parse_evaluate_result(payload.get("tool_response"))
    if data is None:
        return
    url = data.get("url")
    text = data.get("text")
    if not isinstance(url, str) or not url or not isinstance(text, str) or not text:
        return
    if not wrs.same_site(url, read["host"], read["allowed_hosts"]):
        return
    upload_key = tc.read_cursor(session_id).get("upload_key")
    if not isinstance(upload_key, str) or not upload_key:
        return
    title = data.get("title")
    title = title if isinstance(title, str) else ""
    page: dict[str, Any] = {"url": url, "title": title, "text": text}
    # RMP-179: the url THIS navigate was actually sent to, recorded by
    # website_gate.py before any redirect -- lets the server match this
    # upload to its planned page even when `url` (post-redirect) cannot.
    # Absent for a plugin/session with no matching navigate record yet.
    requested_url = wrs.last_navigate(session_id, read["read_id"])
    if requested_url:
        page["requested_url"] = requested_url
    shop_evidence = _clean_shop_evidence(data.get("shop_evidence"))
    if shop_evidence is not None:
        page["shop_evidence"] = shop_evidence
    social_links = _clean_social_links(data.get("social_links"))
    if social_links:
        page["social_links"] = social_links
    _post_page(session_id, read["read_id"], upload_key, page)
