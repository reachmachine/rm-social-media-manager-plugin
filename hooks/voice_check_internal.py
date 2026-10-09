#!/usr/bin/env python3
"""RMP-76 split: internal-term matching, kept out of `voice_check.py` so that
file stays under the 300-line limit.

The founder's rule (RMP-76): "user should not know the backend on whats
happening." A customer must never see an internal tool name or a backend
word, EVEN IF the model tries to "hide" it inside backticks -- the opposite
of the old jargon-list rule, which ignores backtick spans on purpose (so the
model can still quote a handle like `@janesbikes`).

ONE exception: the term "mcp" is never flagged right after a "/" (e.g.
`/mcp`). That is a real Claude Code command the customer is told to type,
in connection-check/SKILL.md, to sign in -- not a backend detail leaking
out. Every other internal term has no such exception.

"HTTP 4"/"HTTP 5" are deliberately PREFIX matches (no trailing word
boundary) so they catch any status code -- "HTTP 404", "HTTP 503" -- not
just those two bare characters.

P1722 (RMP-77 follow-up): a hand-maintained list can never keep up with
every new backend field/tool name, so `_generic_snake_case_hits` flags ANY
lowercase word joined by underscores (e.g. "revenue_model",
"own_instagram_account") on its own, with no entry needed in jargon.json.
Two things must never be caught by that generic rule, because both are
real, working customer content: a link (the customer must be able to open
it) and an Instagram handle (which can itself contain an underscore, e.g.
"@janes_bikes" -- see prompts/COMMS.md, P1722 HEADS-UP). Both are masked
out before the generic pattern runs.

RMP-159 part 5 (founder, 2026-09-26, "Block and rewrite"): each hit now
also reports whether it is a genuine internal name/field/tool (blockable
-- `voice_check_block.py` forces a same-turn rewrite) or one of the
RMP-159 parts 2-4 narration-style markers ("now checking", "so I need to
ask", ...), which stay log-only. A `jargon.json` row is blockable unless it
sets `"block": false`; every generic snake_case hit is always blockable --
it can only ever be a real field/variable name.
"""
from __future__ import annotations

import re
from typing import Any

from voice_check_narration import narration_hits_in_line

_URL_RE = re.compile(r"https?://\S+")
_HANDLE_RE = re.compile(r"@\S+")
_SNAKE_CASE_RE = re.compile(r"(?<![\w-])[a-z]+(?:_[a-z]+)+(?![\w-])")
_GENERIC_SAY = "describe what you did in plain words"
# RMP-198 (live 2026-09-30): a finished sentence followed by " · summary" -- an
# internal field/stage label glued to the end of the customer's line. Only a
# sentence end then a lowercase word at the END of the line, so a real
# "Services: ... · 4.9 stars" (digits, more words) is never caught.
_TRAILING_LABEL_RE = re.compile(r"[.!?)]\s*·\s*([a-z][a-z_]{2,24})\s*$")
_TRAILING_LABEL_SAY = "never show an internal label after a sentence"


def _internal_phrase_pattern(term: str) -> re.Pattern[str]:
    tokens = term.split()
    body = r"[\s-]+".join(re.escape(t) for t in tokens)
    is_mcp = term.strip().lower() == "mcp"
    # RMP-200: "th retry" catches the narrated "Nth retry" shape ("4th
    # retry", "5th retry", ...) -- "th" is always glued to a preceding
    # digit ("4th"), so the ordinary left boundary (no preceding \w) would
    # never match it at all. Same shape as the "mcp" exception above: this
    # ONE term relaxes the left boundary to allow a digit right before it.
    is_ordinal_retry = term.strip().lower() == "th retry"
    if is_mcp:
        left = r"(?<![\w/-])"
    elif is_ordinal_retry:
        left = r"(?<![A-Za-z_-])"
    else:
        left = r"(?<![\w-])"
    is_http_code_prefix = bool(tokens) and tokens[-1].isdigit()
    right = "" if is_http_code_prefix else r"(?![\w-])"
    return re.compile(left + body + right, re.IGNORECASE)


def _generic_snake_case_hits(line: str) -> list[tuple[str, str]]:
    """Any lowercase_word_like_this is an internal term on its own, unless
    it appears inside a URL or an @handle (both masked out first)."""
    masked = _URL_RE.sub(lambda m: " " * len(m.group(0)), line)
    masked = _HANDLE_RE.sub(lambda m: " " * len(m.group(0)), masked)
    return [(m.group(0), _GENERIC_SAY) for m in _SNAKE_CASE_RE.finditer(masked)]


def internal_term_hits_in_line(
    line: str, internal_terms: list[dict[str, Any]]
) -> list[tuple[str, str, bool]]:
    """Returns `(term, say, blockable)` triples, at most one per row/word.
    Scans the RAW line -- no backtick masking, no allow-list masking (the
    old jargon allow-list, e.g. "Reach Machine", never overlaps an internal
    term). The list is checked first, then the generic snake_case rule -- a
    word already caught by name (e.g. "search_business_knowledge") is not
    reported a second time."""
    hits: list[tuple[str, str, bool]] = []
    seen: set[str] = set()
    for entry in internal_terms:
        if not isinstance(entry, dict):
            continue
        term = entry.get("term")
        say = entry.get("say")
        if not isinstance(term, str) or not term or not isinstance(say, str):
            continue
        if _internal_phrase_pattern(term).search(line):
            hits.append((term, say, entry.get("block") is not False))
            seen.add(term.lower())
    for term, say in _generic_snake_case_hits(line):
        if term.lower() in seen:
            continue
        hits.append((term, say, True))
        seen.add(term.lower())
    label = _TRAILING_LABEL_RE.search(line)
    if label and label.group(1).lower() not in seen:
        hits.append((label.group(0).strip(), _TRAILING_LABEL_SAY, True))
        seen.add(label.group(1).lower())
    # RMP-159/198: process narration by SHAPE (never a leak, log-only).
    for term, say in narration_hits_in_line(line):
        if term.lower() not in seen:
            hits.append((term, say, False))
            seen.add(term.lower())
    return hits
