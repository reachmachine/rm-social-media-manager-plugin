#!/usr/bin/env python3
"""The two lines a hook builds for the customer's own Instagram account (RMP-53; words from the SERVER, RMP-281 P2361).

    "We'll plan for @h: 12,400 followers, 180 posts (as of Sep 24)."      `known_line`
    "Added @h: 2 followers, 1 post (as of today)."                        `added_line`

The plugin holds NO words. Every piece is a line the server wrote in the owner's language, in `offers.own_instagram_account.lines`
(`plan_for`, `added`, `numbers`, `as_of`, `today`, `date`, `months`, `follower_one`, `follower_many`, `post_one`, `post_many`),
and this module only fills the `{holes}` and joins the pieces. A missing piece makes the whole line None: the caller then
leaves `say` out (the hook says nothing rather than invent English). The date in `as_of_label` is the neutral ISO form; the
server's `months` + `date` lines turn it into the owner's month name, and with no usable `months` the ISO date is shown as is.

FAIL-SAFE: nothing here may raise.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import offer_lines

OFFER_ID = "own_instagram_account"
AS_OF_TODAY = "@today"   # an `as_of` value meaning "the numbers were just refreshed" (never shown as is)


def as_of_label(profile_fetched_at: str | None) -> str | None:
    """ISO timestamp -> '2026-09-24' (UTC date). Unparsable/None -> None. Never raises."""
    if not isinstance(profile_fetched_at, str) or not profile_fetched_at:
        return None
    try:
        fetched = datetime.fromisoformat(profile_fetched_at.replace("Z", "+00:00"))
        if fetched.tzinfo is None:
            fetched = fetched.replace(tzinfo=timezone.utc)
        return fetched.date().isoformat()
    except Exception:
        return None


def _count(session_id: str, num: Any, one: str, many: str) -> str | None:
    """'12,400 followers' from the server's line, '' when there is no number, None when the line is missing."""
    if not isinstance(num, (int, float)) or isinstance(num, bool):
        return ""
    return offer_lines.line(session_id, OFFER_ID, one if int(num) == 1 else many, n=f"{int(num):,}")


def _numbers(session_id: str, follower_count: Any, media_count: Any) -> str | None:
    """': 12,400 followers, 180 posts', '' when both are missing, None when a server line is missing."""
    parts = [_count(session_id, follower_count, "follower_one", "follower_many"), _count(session_id, media_count, "post_one", "post_many")]
    if None in parts:
        return None
    counts = ", ".join(p for p in parts if p)
    return offer_lines.line(session_id, OFFER_ID, "numbers", counts=counts) if counts else ""


def _date(session_id: str, iso: str) -> str:
    """The owner's 'Sep 24' form when the server sent usable month names, else the ISO date itself."""
    try:
        names = [m.strip() for m in (offer_lines.line(session_id, OFFER_ID, "months") or "").split(",")]
        _, month, day = (int(x) for x in iso.split("-"))
        if len(names) == 12 and all(names):
            return offer_lines.line(session_id, OFFER_ID, "date", month=names[month - 1], day=str(day)) or iso
    except Exception:
        pass
    return iso


def _as_of(session_id: str, as_of: str | None) -> str | None:
    """' (as of Sep 24)', '' when there is no date, None when a server line is missing."""
    if not as_of:
        return ""
    date = offer_lines.line(session_id, OFFER_ID, "today") if as_of == AS_OF_TODAY else _date(session_id, as_of)
    return None if date is None else offer_lines.line(session_id, OFFER_ID, "as_of", date=date)


def known_line(session_id: str, handle: str, follower_count: int | None, media_count: int | None, as_of: str | None) -> str | None:
    """"We'll plan for **@h**: 12,400 followers, 180 posts (as of Sep 24)." A missing number is left out, never written as 0; both
    missing -> "We'll plan for **@h**." `as_of` is `as_of_label(...)`, `AS_OF_TODAY` or None (no ' (as of ...)' part).
    None when the server did not send a line this needs. Never raises."""
    numbers, when = _numbers(session_id, follower_count, media_count), _as_of(session_id, as_of)
    if numbers is None or when is None:
        return None
    return offer_lines.line(session_id, OFFER_ID, "plan_for", handle=handle, numbers=numbers, as_of=when)


def added_line(session_id: str, handle: str, follower_count: int | None, media_count: int | None) -> str | None:
    """'Added **@h**: 2 followers, 1 post (as of today).' Both numbers missing -> 'Added **@h**.' (no date). Never raises."""
    numbers = _numbers(session_id, follower_count, media_count)
    when = _as_of(session_id, AS_OF_TODAY) if numbers else ""
    if numbers is None or when is None:
        return None
    return offer_lines.line(session_id, OFFER_ID, "added", handle=handle, numbers=numbers, as_of=when)
