#!/usr/bin/env python3
"""Hide private details in a session-transcript entry, on the customer's own
machine, before anything leaves it (RMP-27/RMP-44,
docs/plugin-v2/01c-session-transcript.md §4).

PLUGIN's own copy of `backend/app/services/transcript_redaction.py` (and the
secret patterns it reuses from `backend/app/services/canon_shared/redaction.py`)
-- the plugin ships alone with stdlib-only Python, so it cannot import the
backend; the rules and order are ported here by hand. Both sides run the SAME
test cases (`plugins/rm-plugin-v2/redaction/vectors.json`) -- a case that
passes one and fails the other is a red build, see
`tests/test_transcript_redaction.py` here and
`backend/tests/unit/test_transcript_redaction.py`.

FAIL-SAFE: runs inside a hook on the customer's machine. `redact_text` never
raises -- every step is a plain `re.sub`/`str.replace`, which cannot throw on
any `str`, but the whole body is still wrapped so an unforeseen input
degrades to "nothing" (empty string) rather than a crash, or worse, the raw
unredacted text leaking through.
"""
from __future__ import annotations

import re

REDACTION_VERSION: int = 1

# The words the redactor writes in place of a private detail (the same on the server, see vectors.json). A refusal that
# SHOWS hidden text names the kind by these keys and lets `deny_lines.localize_markers` word it in the owner's language.
MARKERS: dict[str, str] = {
    "phone": "[phone number hidden]", "card": "[card number hidden]", "email": "[email hidden]",
    "bank": "[bank number hidden]", "id_number": "[ID number hidden]", "secret": "[secret hidden]",
}

_UPLOAD_KEY_RE = re.compile(r'"upload_key"\s*:\s*"[^"]*"')

# Ported from backend/app/services/canon_shared/redaction.py (`_SECRET_PATTERNS`).
_SECRET_PATTERNS = (
    (re.compile(r"://[^/\s:@]+:[^/\s:@]+@"), "://[REDACTED]@"),
    (re.compile(r"(?i)\bBearer\s+\S+"), "Bearer [REDACTED]"),
    (
        re.compile(
            r"(?i)\b(api[_-]?key|access[_-]?token|auth[_-]?token|token|secret|"
            r"password|authorization)\b\s*[:=]\s*[\"']?[^\s\"',;]+",
        ),
        r"\1=[REDACTED]",
    ),
    (re.compile(r"\b(?:sk|pk|rk)-[A-Za-z0-9_-]{8,}"), "[REDACTED]"),
)

# Linear-time form of the old pattern `LOCAL+@DOMAIN\.TLD`. The old one restarted
# at every letter of a long run (time grew with the square of the length).
# Branch 2 swallows a whole local-part run that is not an e-mail in one step, so
# the search never restarts inside it. A match without "@" is left unchanged.
# The frozen-copy differential test (RPH-234) proves the output is identical.
_EMAIL_RE = re.compile(
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}|[A-Za-z0-9._%+-]+"
)


def _redact_email(m: "re.Match[str]") -> str:
    return MARKERS["email"] if "@" in m.group(0) else m.group(0)


# 13-19 digits total, single space/dash allowed between any two digits,
# boundary-checked so it never matches inside a longer digit/letter run.
_CARD_CANDIDATE_RE = re.compile(r"(?<![\w])\d(?:[ -]?\d){12,18}(?![\w])")

_IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")

_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_PAN_RE = re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")

# Optional leading +, then 9-20 characters of digits/space/dash/dot/parens,
# boundary-checked the same way as the card pattern. Digit count (10-15) is
# checked in the callback, not the regex, because separators make a fixed
# character-length window meaningless on its own.
_PHONE_CANDIDATE_RE = re.compile(r"(?<![\w])\+?[\d .\-()]{9,20}(?![\w])")

_MIN_PHONE_DIGITS = 10
_MAX_PHONE_DIGITS = 15
_MIN_CARD_DIGITS = 13
_MAX_CARD_DIGITS = 19

# A candidate that CONTAINS a full ISO date (2026-09-24) is a timestamp, not
# a phone number (see backend's transcript_redaction.py for why they collide).
_ISO_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")

# Plugin-only: the backend never sees the customer's machine, so it cannot
# know their home folder. These generic shapes catch it even when `home` is
# not passed (or catch a DIFFERENT user's home folder mentioned in the text).
_HOME_PATTERNS = (
    re.compile(r"/home/[^/\s]+"),
    re.compile(r"/Users/[^/\s]+"),
    re.compile(r"C:\\Users\\[^\\\s]+"),
)


def _luhn_ok(digits: str) -> bool:
    total = 0
    for i, ch in enumerate(reversed(digits)):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    return total % 10 == 0


def _redact_card(match: re.Match[str]) -> str:
    raw = match.group(0)
    digits = re.sub(r"\D", "", raw)
    if _MIN_CARD_DIGITS <= len(digits) <= _MAX_CARD_DIGITS and _luhn_ok(digits):
        return MARKERS["card"]
    return raw


def _split_phone_trailing_punctuation(raw: str) -> tuple[str, str]:
    """Split a phone candidate into (number, trailing).

    The candidate's character class allows `.`, `,`-adjacent space, and `()`,
    so a candidate like "(+44 7700 900123)" or "555-010-4477." grabs a
    trailing ")" or "." that actually belongs to the surrounding sentence,
    not the number (RMP-80). Move it to `trailing` so it survives the
    replacement. A ")" only counts as sentence punctuation when the
    candidate has more ")" than "(" -- an internal area-code group like
    "(555)" stays part of the number. Ported from
    backend/app/services/transcript_redaction.py -- keep both in sync.
    """
    trailing = ""
    while raw:
        last = raw[-1]
        if last in ".," or last.isspace():
            trailing = last + trailing
            raw = raw[:-1]
            continue
        if last == ")" and raw.count(")") > raw.count("("):
            trailing = last + trailing
            raw = raw[:-1]
            continue
        break
    return raw, trailing


def _redact_phone(match: re.Match[str]) -> str:
    raw = match.group(0)
    if _ISO_DATE_RE.search(raw):
        return raw
    number, trailing = _split_phone_trailing_punctuation(raw)
    digits = re.sub(r"\D", "", number)
    if _MIN_PHONE_DIGITS <= len(digits) <= _MAX_PHONE_DIGITS:
        return MARKERS["phone"] + trailing
    return raw


def _redact_secrets(text: str) -> str:
    for pattern, replacement in _SECRET_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def _redact_home(text: str, home: str | None) -> str:
    if home:
        text = text.replace(home, "~")
    for pattern in _HOME_PATTERNS:
        text = pattern.sub("~", text)
    return text


def redact_text(text: str, *, home: str | None = None, extra_secrets: tuple[str, ...] = ()) -> str:
    """Hide private details in *text* (spec §4), same rules and order as the
    backend copy (`app.services.transcript_redaction.redact_text`), plus two
    steps only the plugin can do: hiding this session's own `extra_secrets`
    (its upload key, P1636) and the customer's `home` folder (also caught
    generically even when `home` is not passed).

    Never raises. On any unexpected failure this degrades to an empty
    string -- returning the raw, unredacted text would defeat the entire
    point, and raising would crash the caller's hook.
    """
    try:
        out = _UPLOAD_KEY_RE.sub('"upload_key": "' + MARKERS["secret"] + '"', text)
        out = _redact_secrets(out).replace("[REDACTED]", MARKERS["secret"])
        out = _EMAIL_RE.sub(_redact_email, out)
        out = _CARD_CANDIDATE_RE.sub(_redact_card, out)
        out = _IBAN_RE.sub(MARKERS["bank"], out)
        out = _SSN_RE.sub(MARKERS["id_number"], out)
        out = _PAN_RE.sub(MARKERS["id_number"], out)
        out = _PHONE_CANDIDATE_RE.sub(_redact_phone, out)
        for secret in extra_secrets:
            if isinstance(secret, str) and secret:
                out = out.replace(secret, MARKERS["secret"])
        out = _redact_home(out, home)
        return out
    except Exception:
        return ""
