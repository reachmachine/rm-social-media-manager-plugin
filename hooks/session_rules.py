#!/usr/bin/env python3
"""SessionStart: load the shared voice and business-fact rules once (RMP-76).

Before: the same ten voice rules (and the business-fact rule) were copied into
six skill files, so a customer who walked steps 1-6 paid for six copies in
every later model call (measured on the 2026-09-30 salon run: about 3k tokens
of repeats, re-read on about 60 later requests).

Now: the one source is `voice/session_rules.md`. This hook prints it as
`additionalContext` on startup, resume, clear and compact. Each skill keeps a
one-line reminder between its `rmp-voice-rules` markers.

FAIL-SAFE: a SessionStart hook must never block a session. Any doubt prints
nothing.
"""
from __future__ import annotations

import json
import pathlib

RULES_FILE = pathlib.Path(__file__).resolve().parent.parent / "voice" / "session_rules.md"


def rules_text() -> str | None:
    try:
        text = RULES_FILE.read_text(encoding="utf-8").strip()
    except Exception:
        return None
    return text or None


def main() -> int:
    text = rules_text()
    if text is None:
        return 0
    try:
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "SessionStart", "additionalContext": text,
        }}))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
