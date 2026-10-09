#!/usr/bin/env python3
"""Typed (headless) answers to the step 4 skip question and the later
re-offer (RMP-281 P2187). Split from step_skip.py for the 300-line limit.

A headless session has no widget, so the plugin prints the question as plain
text and the customer types "1", "skip" or "not now". The old code accepted
only the exact option label. Here a typed number or a short word also counts,
but ONLY while that question is the one the customer is answering: the last
assistant message must contain the question's exact text. A bare "1" is
also a valid answer to other questions (step 3, step 5), so without that check
it would hijack them. If the transcript cannot be read, nothing loose is
accepted (fail safe: never skip by accident). A bare "yes" never matches."""
from __future__ import annotations

import re

import voice_check_transcript as vct

# option value -> extra typed words (the exact label is matched separately).
SKIP_WORDS = {
    "skip": ("skip", "skip it", "skip for now", "yes skip"),  # an older server's question (before RMP-281)
    "no_instagram": ("no", "skip", "skip it", "skip for now", "yes skip", "no instagram", "we dont use instagram"),
    "add": ("add", "add it", "add my account"),
}
REOFFER_WORDS = {
    "add": ("add it now", "add"),
    "later": ("not now", "later", "no"),
}

_TRAILING = " \t\r\n.!?,;:"


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().casefold()).strip(_TRAILING)


def question_pending(transcript_path: object, question_text: str) -> bool:
    """True when the last assistant message contains `question_text`. False on
    any read problem or when there is no transcript."""
    if not isinstance(transcript_path, str) or not transcript_path or not question_text:
        return False
    try:
        found = vct.last_assistant_message_blocks(transcript_path)
    except Exception:
        return False
    if found is None:
        return False
    return _norm(question_text) in _norm(" ".join(found[1]))


def match_loose(typed: str, options: list[dict[str, str]], words: dict[str, tuple[str, ...]]) -> str | None:
    """Option value for a typed number (1 = first option) or one of the short
    words, else None. Call only when the question is pending."""
    t = _norm(typed)
    if t.isdigit():
        index = int(t) - 1
        return options[index]["value"] if 0 <= index < len(options) else None
    for opt in options:
        if t in words.get(opt["value"], ()) or t == _norm(opt.get("label", "")):
            return opt["value"]
    return None
