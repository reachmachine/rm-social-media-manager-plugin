"""Falsifiable test for G366 — nothing tells the customer HOW to connect Apify.

The bug in plain words: benchmark discovery (`/find-competitors`, PLAYBOOK
Step 2) cannot search Instagram unless the customer is signed in to Apify.
`.claude-plugin/plugin.json` pre-fills the `apify` MCP server for them, but
before this fix **no file in the plugin told a human what to do about it**:

  * `commands/find-competitors.md` told the model to STOP when Apify is not
    connected (G332) and never said how to connect it,
  * `skills/rm-content-planner/README.md` explained the `/mcp` browser sign-in
    for the `reachmachine` server ONLY, even though plugin.json ships two
    servers,
  * `PLAYBOOK.md` Step 2 mentioned the Apify sign-in as an aside to the MODEL,
    never as something to say to the user.

So a paying customer hit "I cannot search Instagram right now" as a dead end.

What this test guards, one check per edited file:

(a) `find-competitors.md` carries the sign-in path: run `/mcp`, sign in to the
    `apify` server in the browser, and the Apify account itself is free to make.
(b) README's SETUP section (not just the money table further down) names the
    `apify` server and its own `/mcp` sign-in.
(c) plugin.json still declares BOTH servers, and the apify block still ships no
    token or secret. This one PASSES before the fix on purpose — it is a
    CONTROL. If the marker-walk below ever found the wrong folder, or the
    `apify` server were dropped, the sign-in text this test demands would be
    telling customers to sign in to something that no longer exists.
(d) PLAYBOOK Step 2 tells the model to say the sign-in path OUT LOUD to the
    user the first time discovery runs.

Plus `test_control_the_files_under_test_are_the_real_ones`, which proves the
paths resolved to the live shipped files and not to empty or missing ones — a
check that reads a file which isn't there would otherwise "fail" (or later
"pass") for a reason that has nothing to do with G366.

Standalone-runnable (the RAM guard blocks pytest on this box):
`python test_g366_apify_onboarding.py`.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

# Plugin root by marker-walk, never parent-counting (same reason as
# test_commands.py / test_g339: fixed-depth path math broke on a re-nesting).
_HERE = pathlib.Path(__file__).resolve()
_PLUGIN_ROOT = next(
    p for p in _HERE.parents if (p / ".claude-plugin" / "plugin.json").is_file()
)
_SKILL = _PLUGIN_ROOT / "skills" / "rm-content-planner"

_FIND = _PLUGIN_ROOT / "commands" / "find-competitors.md"
_README = _SKILL / "README.md"
_PLAYBOOK = _SKILL / "PLAYBOOK.md"
_PLUGIN_JSON = _PLUGIN_ROOT / ".claude-plugin" / "plugin.json"


# Markdown hard-wraps at ~90 chars, so every multi-word phrase below is matched
# against whitespace-collapsed text. Matching per line would let the position of
# a line break decide whether a sentence is "there".
def _flat(text: str) -> str:
    return " ".join(text.split())


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _slice(text: str, start_marker: str, end_marker: str) -> str:
    """Text between two headings. Heading-scoped, never line-number-scoped."""
    start = text.index(start_marker)
    end = text.index(end_marker, start + len(start_marker))
    return text[start:end]


# "sign in" in all the shapes a doc writer actually uses.
_SIGN_IN = r"sign[- ]?in|signs? in|log ?in|logs? in|authenticate"

# The sign-in instruction, as ONE sentence: Apify and the act of signing in have
# to be in the same breath. `[^.]` cannot cross a full stop, so "apify" in one
# sentence and "sign in" two sentences later does not count.
_APIFY_SIGNIN_RE = re.compile(
    rf"apify[^.]{{0,220}}?(?:{_SIGN_IN})|(?:{_SIGN_IN})[^.]{{0,220}}?apify",
    re.IGNORECASE,
)

# "the Apify account costs nothing to create".
_FREE_ACCOUNT_RE = re.compile(
    r"free[^.]{0,120}?apify[^.]{0,120}?account"
    r"|apify[^.]{0,120}?account[^.]{0,120}?free"
    r"|apify\.com[^.]{0,120}?free",
    re.IGNORECASE,
)


# --------------------------------------------------------------------------
# CONTROL — prove we are reading the real, shipped files.
# --------------------------------------------------------------------------
def test_control_the_files_under_test_are_the_real_ones() -> None:
    """If the marker-walk landed somewhere wrong, every other check in this file
    would fail (or pass) for a reason that has nothing to do with G366. Anchor on
    text that was in these files LONG before this fix."""
    for path in (_FIND, _README, _PLAYBOOK, _PLUGIN_JSON):
        assert path.is_file(), f"{path} does not exist — wrong plugin root?"
        assert path.stat().st_size > 200, f"{path} is suspiciously empty"

    assert "G332" in _read(_FIND), (
        "find-competitors.md has no G332 stop rule — this is not the file this "
        "test thinks it is"
    )
    assert "## Step 2 — Find benchmark accounts" in _read(_PLAYBOOK), (
        "PLAYBOOK.md has no Step 2 heading — wrong file"
    )
    assert "## Using this plugin" in _read(_README), (
        "README.md has no setup section — wrong file"
    )


# --------------------------------------------------------------------------
# (a) the command a customer actually runs
# --------------------------------------------------------------------------
def test_find_competitors_tells_the_user_how_to_connect_apify() -> None:
    flat = _flat(_read(_FIND))

    assert "/mcp" in flat, (
        "find-competitors.md never mentions `/mcp` — it tells the model to STOP "
        "when Apify is not connected but gives the customer no way to connect it "
        "(G366)"
    )
    assert _APIFY_SIGNIN_RE.search(flat), (
        "find-competitors.md never says, in one sentence, that Apify needs its "
        "own browser sign-in — the customer is left at a dead end (G366)"
    )
    assert _FREE_ACCOUNT_RE.search(flat), (
        "find-competitors.md never says an Apify account is free to create. "
        "Customers assume a paid signup and stop there (G366)"
    )


def test_find_competitors_keeps_the_g332_stop_rule() -> None:
    """The sign-in path must be an ADDITION. If someone 'helpfully' replaces the
    stop rule with 'go sign in', the model is free to web-search again."""
    flat = _flat(_read(_FIND))
    assert "G332" in flat, "the G332 stop rule was removed"
    assert re.search(r"not\W{0,4}\*{0,2}\s*a substitute", flat, re.IGNORECASE), (
        "find-competitors.md lost the 'a web search is not a substitute' rule"
    )


def test_find_competitors_does_not_ask_for_an_api_key() -> None:
    """Apify signs in by OAuth here. Telling a customer to paste a key or fill in
    a .env would be a NEW bug, not a fix."""
    flat = _flat(_read(_FIND))
    offenders = [
        m.group(0).strip()
        for m in re.finditer(
            r"[^.]*apify[^.]{0,160}?"
            r"(?:api[- ]?key|API_TOKEN|\.env|paste[^.]{0,30}token)[^.]*",
            flat,
            re.IGNORECASE,
        )
        if not re.search(r"\bno\b|\bnever\b|\bwithout\b", m.group(0), re.IGNORECASE)
    ]
    assert not offenders, (
        "find-competitors.md asks the customer for an Apify API key or .env "
        "entry. The plugin uses browser sign-in — there is no key to paste:\n  "
        + "\n  ".join(offenders)
    )


# --------------------------------------------------------------------------
# (b) the README setup section
# --------------------------------------------------------------------------
def test_readme_setup_section_covers_both_mcp_servers() -> None:
    setup = _flat(_slice(_read(_README), "## Using this plugin", "### Slash commands"))

    assert "reachmachine" in setup.lower(), (
        "README setup section no longer names the reachmachine server"
    )
    assert "apify" in setup.lower(), (
        "README's setup section explains the `/mcp` sign-in for the reachmachine "
        "server only. plugin.json ships TWO servers, and the apify one also needs "
        "a one-time browser sign-in before discovery works (G366). Mentioning "
        "Apify only in the money table further down is not setup instructions."
    )
    assert "/mcp" in setup, "README setup section lost the `/mcp` instruction"
    assert _APIFY_SIGNIN_RE.search(setup), (
        "README setup section names Apify but never says it needs its own "
        "sign-in (G366)"
    )
    assert _FREE_ACCOUNT_RE.search(setup), (
        "README setup section never says an Apify account is free to create (G366)"
    )


# --------------------------------------------------------------------------
# (c) CONTROL + guard — the thing the docs point at must still exist
# --------------------------------------------------------------------------
def test_plugin_json_still_declares_the_apify_server_with_no_secret() -> None:
    manifest = json.loads(_read(_PLUGIN_JSON))
    servers = manifest.get("mcpServers", {})

    assert "reachmachine" in servers, "plugin.json dropped the reachmachine server"
    assert "apify" in servers, (
        "plugin.json no longer pre-fills the `apify` MCP server, so the sign-in "
        "steps this test demands would point customers at nothing"
    )

    blob = json.dumps(servers["apify"])
    for banned in ("token", "secret", "password", "apiKey", "api_key"):
        assert banned.lower() not in blob.lower(), (
            f"the apify server block carries a `{banned}` — this plugin ships to "
            "customers and must never contain a credential"
        )
    assert "mcp.apify.com" in blob, "the apify server no longer points at Apify"


# --------------------------------------------------------------------------
# (d) PLAYBOOK Step 2 — say it out loud, don't just know it
# --------------------------------------------------------------------------
def test_playbook_step_2_tells_the_model_to_say_the_sign_in_out_loud() -> None:
    step2 = _flat(
        _slice(_read(_PLAYBOOK), "## Step 2 — Find benchmark accounts", "## Step 3")
    )

    assert "/mcp" in step2, (
        "PLAYBOOK Step 2 mentions the Apify sign-in only as an aside to the "
        "MODEL. It must carry the actual `/mcp` instruction the model repeats to "
        "the user (G366)"
    )
    assert re.search(
        rf"(?:tell|say|spell out|walk)[^.]{{0,240}}?(?:/mcp|{_SIGN_IN})",
        step2,
        re.IGNORECASE,
    ), (
        "PLAYBOOK Step 2 never instructs the model to SAY the sign-in path to "
        "the user — knowing it privately is what G366 already was"
    )


_CHECKS = [
    ("CONTROL: the files under test are the real shipped ones",
     test_control_the_files_under_test_are_the_real_ones),
    ("find-competitors tells the user how to connect Apify",
     test_find_competitors_tells_the_user_how_to_connect_apify),
    ("find-competitors keeps the G332 stop rule",
     test_find_competitors_keeps_the_g332_stop_rule),
    ("find-competitors does not ask for an API key",
     test_find_competitors_does_not_ask_for_an_api_key),
    ("README setup section covers BOTH mcp servers",
     test_readme_setup_section_covers_both_mcp_servers),
    ("plugin.json still declares apify, with no secret",
     test_plugin_json_still_declares_the_apify_server_with_no_secret),
    ("PLAYBOOK Step 2 says the sign-in out loud",
     test_playbook_step_2_tells_the_model_to_say_the_sign_in_out_loud),
]


def main() -> int:
    # These docs contain emoji (the red-circle marker). A failure message quoting
    # one must not die in Windows' cp1252 console before it prints.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    failed = 0
    for label, check in _CHECKS:
        try:
            check()
        except AssertionError as exc:
            failed += 1
            print(f"[FAIL] {label}: {exc}")
        else:
            print(f"[PASS] {label}")
    print(f"{len(_CHECKS) - failed}/{len(_CHECKS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
