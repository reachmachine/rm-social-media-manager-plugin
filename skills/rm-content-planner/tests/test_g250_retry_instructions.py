"""Falsifiable test for G250 - the skill must retry a failed save instead of giving up
after one attempt.

Everything is checked by reading the real `PLAYBOOK.md` (no mocks). Five content checks:

1. The old give-up-immediately instruction is gone. That sentence was bolded
   (`**say so plainly and move on**`) and fired on the FIRST failure. This check matches
   the old BOLDED construction, and separately asserts the terminal step is gated behind
   three tries, so deleting the ceiling cannot pass quietly. (P1344 replaced the terminal
   paragraph outright, so "say so plainly and move on" no longer appears in any form.)
2. `idempotency_key` is named in the save section.
3. A retry ceiling is stated - the word "three" appears in the save section.
4. `already_saved` is named, so the skill knows the success signal for a duplicate.
5. `submit_analysis` is documented as NOT needing a key.

Five more checks cover what happens after the LAST failed attempt (P1344/FRFRMU-125).
"Say so plainly and move on" preserved nothing: the plan only existed in chat scrollback,
which is the customer's problem to find. So the save section must now write the plan to a
file, say plainly it is NOT in the Reach Machine library, hand the `idempotency_key` back,
and name concrete retry waits. The old "already delivered in-chat" sentence is asserted
ABSENT so the previous behaviour cannot creep back in a later edit.

There is also a check that is deliberately NOT a content assertion:
`test_backend_halves_are_present_when_merged`. It encodes one rule - if the PLAYBOOK tells
the skill to SEND `idempotency_key`, every MCP schema file it names must ACCEPT it. It used
to `pytest.skip` when the field was in none of the three files, which is EXACTLY the
dangerous state (PLAYBOOK merged, neither backend half merged), so the one state it existed
to catch passed green. It now returns early only when the PLAYBOOK is not asking for the
field at all - the genuinely safe state - and asserts otherwise.

The other test files in this directory are pytest-style, so these are plain `test_*`
functions too. Unlike them, this file also runs standalone
(`python test_g250_retry_instructions.py`) and prints one [PASS]/[FAIL] line per check,
exiting non-zero if any check failed. Prefer `python -m pytest` regardless: the sibling
files in this directory have no `__main__` block and exit 0 silently under plain `python`.
"""
from __future__ import annotations

import pathlib
import re
import sys

_SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent
_PLAYBOOK = _SKILL_DIR / "PLAYBOOK.md"
# Robust to how deep this skill folder sits (standalone vs. inside a plugin's
# skills/ dir) — walk up to the nearest ".claude" ancestor and take its parent,
# same technique runner.py's own REPO_ROOT already uses. A fixed `.parent.parent.parent`
# broke the moment this skill moved one level deeper into
# .claude/skills/rm-social-media-manager/skills/rm-content-planner/ (plugin packaging,
# 2026-08-15) — it resolved to `.claude/skills` instead of the repo root, and this
# check's read of the backend schema files raised FileNotFoundError.
_REPO_ROOT = next(p.parent for p in _SKILL_DIR.parents if p.name == ".claude")

# The three MCP schema files P1291/P1292 add `idempotency_key` to.
_SCHEMA_FILES = (
    "backend/app/mcp/tool_schemas_content_plan.py",
    "backend/app/mcp/tool_schemas_agent_gap.py",
    "backend/app/mcp/tool_schemas_content_plan_run.py",
)

# U+2014 EM DASH, named once so the sentence below stays readable. Never printed: the
# Windows console here is cp1252 and would raise on it.
_EM = "—"

# The pre-G250 sentence, exactly as it read, with its bold markers. The new text keeps the
# bare words but drops the bold and moves them behind a three-try ceiling, so this string
# is absent after the fix and present again the moment anyone restores the original.
_OLD_GIVE_UP = (
    "**say so plainly and move on** " + _EM
    + " never fail the delivered plan over the save."
)


def _playbook_text() -> str:
    return _PLAYBOOK.read_text(encoding="utf-8")


def _flat() -> str:
    """PLAYBOOK text with every run of whitespace collapsed to one space.

    The PLAYBOOK is hard-wrapped, so the sentences under test are split across lines with
    leading indentation. Flattening lets a check match the sentence, not the wrapping.
    """
    return re.sub(r"\s+", " ", _playbook_text())


def _save_section() -> str:
    """The step-12 save block: from `3. **Confirm**` up to the `**Privacy:**` note."""
    text = _playbook_text()
    start = re.search(r"^3\. \*\*Confirm\*\*", text, re.MULTILINE)
    assert start, "the '3. **Confirm**' save step was not found in PLAYBOOK.md"
    rest = text[start.start():]
    end = re.search(r"^\*\*Privacy:\*\*", rest, re.MULTILINE)
    assert end, "the '**Privacy:**' note after the save step was not found"
    return rest[: end.start()]


def test_old_give_up_immediately_sentence_is_gone() -> None:
    """G250 - the first failure must no longer end the attempt.

    Checks the OLD bolded construction is absent AND the new text puts the same words
    behind a three-try ceiling, so removing the ceiling cannot pass this quietly.
    """
    flat = _flat()
    assert _OLD_GIVE_UP not in flat, (
        "PLAYBOOK.md still carries the pre-G250 give-up-on-first-failure sentence"
    )
    assert "If it still hasn't saved after three tries, do not just move on" in flat, (
        "PLAYBOOK.md does not gate the terminal hand-back behind three tries"
    )


def test_save_section_names_the_idempotency_key() -> None:
    """G250 - the retry is only safe because the same key is resent."""
    block = _save_section()
    assert "idempotency_key" in block, (
        "the save step does not tell the skill to send an idempotency_key"
    )
    assert "same key on the first attempt and on every retry" in re.sub(
        r"\s+", " ", block
    ), "the save step does not say to reuse the SAME key on every retry"


def test_save_section_states_a_retry_ceiling() -> None:
    """G250 - retries must stop. An unbounded retry loop is its own outage."""
    block = re.sub(r"\s+", " ", _save_section())
    assert "three" in block, "the save step states no retry ceiling"
    assert "up to **three times in total**" in block, (
        "the save step does not cap retries at three attempts in total"
    )


def test_save_section_names_the_duplicate_success_signal() -> None:
    """G250 - a resend that the server recognises must be read as success, not failure."""
    block = _save_section()
    assert "already_saved" in block, (
        "the save step does not name `already_saved`, so the skill cannot recognise a "
        "successful resend and would keep retrying a save that already landed"
    )


def test_submit_analysis_is_documented_as_needing_no_key() -> None:
    """G250 - `submit_analysis` already upserts on {post_url, org_id}.

    Sending it a key would add a second gate on a write that is already safe, so the
    PLAYBOOK must call out the exception rather than leave the skill to guess.
    """
    block = re.sub(r"\s+", " ", _save_section())
    assert "`submit_analysis` is different and needs no key" in block, (
        "the save step does not document submit_analysis as the no-key exception"
    )


def test_backend_halves_are_present_when_merged() -> None:
    """Merge-order guard, NOT a content assertion (see this file's docstring + COMMS).

    The rule: if the PLAYBOOK asks the skill to SEND a field, every server schema it
    names must ACCEPT that field. The old version skipped when the field was in none of
    the three files - which is exactly the dangerous state (PLAYBOOK merged, neither
    backend half merged), so the one state it was written to catch was waved through
    green. It now returns early only when the PLAYBOOK is not asking for the field at
    all, which is the genuinely safe state.
    """
    missing = [
        name
        for name in _SCHEMA_FILES
        if "idempotency_key" not in (_REPO_ROOT / name).read_text(encoding="utf-8")
    ]
    playbook_sends_the_key = "idempotency_key" in _PLAYBOOK.read_text(encoding="utf-8")
    if not playbook_sends_the_key:
        return  # the PLAYBOOK does not ask for the field, so the server need not accept it
    assert not missing, (
        "The PLAYBOOK tells the skill to send idempotency_key, but these MCP schema files "
        "do not accept it: " + ", ".join(missing) + ". Shipping in this state makes every "
        "save fail three times and give up, which is worse than no retry at all. The two "
        "backend halves must be on the same branch as the PLAYBOOK change."
    )


def test_final_failure_writes_the_plan_to_a_file() -> None:
    """G250 terminal step - the customer's work must survive the conversation.

    Chat scrollback is not preservation. After the last failed attempt the skill has to
    write the full plan out as a file the customer can open and name that file to them.
    """
    block = re.sub(r"\s+", " ", _save_section())
    assert "Write the complete plan to a file they can open" in block, (
        "the save step does not tell the skill to write the plan out to a file after the "
        "last failed attempt - the customer's work would only exist in chat scrollback"
    )
    assert "tell them the filename" in block, (
        "the save step writes a file but never tells the customer what it is called"
    )


def test_final_failure_tells_them_it_is_not_in_the_library() -> None:
    """G250 terminal step - never let the customer find out on their own.

    'Content Calendar' alone would be unfalsifiable here: the success confirmation line
    in the same block already contains it. This checks the explicit NOT-saved sentence.
    """
    block = re.sub(r"\s+", " ", _save_section())
    assert "it is NOT in their Reach Machine library" in block, (
        "the save step does not tell the customer plainly that the plan did NOT reach "
        "their Reach Machine library"
    )


def test_final_failure_hands_over_the_idempotency_key() -> None:
    """G250 terminal step - the key is what makes a later manual retry safe."""
    block = re.sub(r"\s+", " ", _save_section())
    assert "Give them the `idempotency_key` you used" in block, (
        "the save step does not hand the idempotency_key back to the customer, so a "
        "later retry could store a second copy"
    )
    assert "tell them to keep it" in block, (
        "the save step names the key but does not tell the customer to keep it"
    )


def test_the_old_move_on_sentence_is_gone() -> None:
    """G250 terminal step - stop the old 'it's in the chat, that'll do' behaviour.

    This is the check that prevents the old wording creeping back in a later edit.
    """
    flat = _flat()
    assert (
        "The plan is already delivered in-chat; the save is a convenience, "
        "not the deliverable." not in flat
    ), (
        "PLAYBOOK.md still carries the old terminal sentence that treats chat scrollback "
        "as good enough. Nothing in that behaviour preserves the customer's work."
    )


def test_retry_backoff_names_real_waits() -> None:
    """G250 - 'waiting a moment longer' names no interval, so it cannot be followed."""
    block = re.sub(r"\s+", " ", _save_section())
    assert "wait about 2 seconds before the second attempt" in block, (
        "the save step does not name a concrete wait before the second attempt"
    )
    assert "about 5 seconds before the third" in block, (
        "the save step does not name a concrete wait before the third attempt"
    )


_CHECKS = [
    ("old give-up-on-first-failure sentence is gone",
     test_old_give_up_immediately_sentence_is_gone),
    ("save step names the idempotency_key and says to reuse it",
     test_save_section_names_the_idempotency_key),
    ("save step caps retries at three", test_save_section_states_a_retry_ceiling),
    ("save step names already_saved as the duplicate success signal",
     test_save_section_names_the_duplicate_success_signal),
    ("submit_analysis documented as the no-key exception",
     test_submit_analysis_is_documented_as_needing_no_key),
    ("merge-order guard: backend halves present",
     test_backend_halves_are_present_when_merged),
    ("final failure writes the plan out to a file",
     test_final_failure_writes_the_plan_to_a_file),
    ("final failure says the plan is NOT in the library",
     test_final_failure_tells_them_it_is_not_in_the_library),
    ("final failure hands the idempotency_key back",
     test_final_failure_hands_over_the_idempotency_key),
    ("old 'already in the chat' sentence is gone",
     test_the_old_move_on_sentence_is_gone),
    ("retry backoff names real waits", test_retry_backoff_names_real_waits),
]


def main() -> int:
    """No check in this file skips any more, so there is no [SKIP] branch to report.

    The merge-order guard used to skip in the one state it existed to catch; it now
    either returns quietly (the PLAYBOOK is not asking for the field) or asserts.
    """
    failed = 0
    for label, check in _CHECKS:
        try:
            check()
        except AssertionError as exc:
            failed += 1
            print(f"[FAIL] {label}: {exc}")
        else:
            print(f"[PASS] {label}")
    passed = len(_CHECKS) - failed
    print(f"{passed}/{len(_CHECKS)} checks passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
