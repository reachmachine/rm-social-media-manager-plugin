#!/usr/bin/env python3
"""RMP-159/RMP-198: catch the SHAPE of process narration, not a phrase list.

Why: five rounds of adding exact phrases to jargon.json lost to paraphrase
each time ("closing the browser and recording the session" became "close
the browser and log this session", then "Closing browser and recording
session now"). Real leaked lines from the local live logs
(chat-dev/events-live-*.jsonl) all share one shape: the agent announces its
OWN next action ("Let me check the connections first", "I need to fill
them from the site", "I'll keep polling directly", "so move on to step 3").

A customer-safe line is a question, a result, or a plain status
("Reading your website now."). So this looks for a first-person announcement
sentence ("let me" / "I'll" / "I need to" ...) followed by a process verb.

Deliberately NOT flagged (real, working customer text):
- any line with a "?" (a consent line: "I'll check Reddit ... about $0.10. OK?")
- bullet / numbered / table lines (option labels: "No, let me fix it")
- "I'll keep you posted", "I'll let you know", "I'll check back/again"
- "let me show you" (not a process verb)
Log-only (block=false): the caller marks every hit as narration, never a leak.
"""
from __future__ import annotations

import re

NARRATION_SAY = "say nothing about it, just do it"

_VERBS = (
    r"check(?!\s+(?:back|again))|run|call|pull|restart|retry|keep\s+(?:polling|it\s+going)|close|log|record|save|"
    r"fill\s+(?:them|those|the\s+facts)|start|consult|proceed|verify|poll|tick|pass|fetch|look\s+up|do\s+one|"
    r"wait\s+for\s+the|hand\s+off|move\s+on|re-?run|re-?check|first\s+check"
)
_LEAD = r"(?:now\s+|first\s*,?\s+|quickly\s+|just\s+|then\s+|also\s+)*"
_SENTENCE_START = r"(?:^|[.!?;:—–]\s+|,\s+so\s+)"
_ANNOUNCE = re.compile(
    _SENTENCE_START
    + r"(?:(?:hi|hello|ok|okay|good|great|got it)[!.,]?\s+)?"
    + _LEAD
    + r"(?:let(?:'s| me)|i(?:'ll|'m going to| will| am going to| need to| have to| should| must)|we need to)\s+"
    + r"(?:(?:first|now|quickly|just|also|start by)\s+)*"
    + r"(?:" + _VERBS + r")\b",
    re.IGNORECASE,
)
# "so move on to step 3", "so proceed to preview", "so we need to fill".
_SO_ACTION = re.compile(r"\bso\s+(?:move\s+on|proceed|we\s+need\s+to|i\s+need\s+to)\b", re.IGNORECASE)
# RMP-201 live 2026-09-29: "Running the three probes now." -- the same
# announcement in the "-ing" shape, with no "I'll"/"let me" to catch. Only
# when the thing run is a process noun, so "Reading your website now." (a
# real customer status) and "Running the numbers" are never flagged.
_GERUND_ANNOUNCE = re.compile(
    _SENTENCE_START
    + r"(?:now\s+)?(?:running|calling|firing|executing|polling|kicking\s+off)\s+"
    + r"(?:the|these|those|all|each|my)\s+(?:\w+\s+){0,2}(?:probes?|checks?|tools?|calls?|tests?|commands?|scripts?|hooks?)\b",
    re.IGNORECASE,
)
# RMP-159 live 2026-09-29: "Now the three probe calls, exactly as specified."
# -- a noun-phrase announcement (no verb) that also parrots the skill's own
# "exactly" wording. Two shapes: "Now the <..> calls/probes/checks/steps" and
# "exactly as specified/instructed/..." or "per the skill/hook/instructions".
_NOUN_ANNOUNCE = re.compile(
    _SENTENCE_START
    + r"now\s+(?:the|these|those|all)\s+(?:\w+\s+){0,3}(?:probes?|calls?|checks?|tools?|steps?)\b",
    re.IGNORECASE,
)
_PARROT = re.compile(
    r"\bexactly\s+as\s+(?:specified|instructed|directed|required|written|described)\b"
    r"|\b(?:as|per)\s+(?:the\s+)?(?:skill|hook|instructions?)\b",
    re.IGNORECASE,
)
# RMP-198 live 2026-09-30: "Website step is done. Next, the business check.
# Loading that step." -- a handover that names the agent's own mechanics.
_LOADING_STEP = re.compile(
    r"\bloading\s+(?:that|this|the\s+next|the)\s+(?:step|skill)\b"
    r"|\b(?:website|connection|workspace)?\s*step\s+is\s+done\.\s+next\b",
    re.IGNORECASE,
)
_LIST_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)]|\|)\s")


def narration_hits_in_line(line: str) -> list[tuple[str, str]]:
    """`(matched_text, say)` pairs for one line; `[]` for a safe line."""
    if "?" in line or _LIST_ITEM.match(line):
        return []
    hits: list[tuple[str, str]] = []
    for pattern in (_ANNOUNCE, _SO_ACTION, _GERUND_ANNOUNCE, _NOUN_ANNOUNCE, _PARROT, _LOADING_STEP):
        match = pattern.search(line)
        if match:
            hits.append((match.group(0).strip(" .!?;:—–,"), NARRATION_SAY))
    return hits
