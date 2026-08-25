"""Falsifiable test for G370 — "we build the customer a dashboard and never tell
them where it is."

The bug: the planner really does produce `dashboard.html` (SKILL.md names it as
the delivery format, and says to write it to
`content-plans/<subject-handle>/<YYYY-MM>/dashboard.html`). But nothing in the
whole plugin ever told the creator WHERE that file ended up. The closest wording
shipped was "write it to a file they can open" — which never says where. A
non-technical creator is left with a finished dashboard sitting in a folder they
cannot find, which is the same, to them, as not getting one.

The fix is three sentences of instruction, in the two files that drive delivery:

1. print the ABSOLUTE path, on its own line, nothing else on that line;
2. one short sentence saying what is inside it;
3. try to open it in their default browser — and if that cannot be done, say
   plainly "open this file in your browser" and carry on. Never fail, retry or
   hold up the delivery over the opening step.

Plus the two enablers that make (3) possible at all:

* `allowed-tools:` had NO shell tool, so the skill could not run `start` /
  `open` / `xdg-open` even if it wanted to. Scoped Bash entries are granted.
* headless / unattended runs (`runner.py`) must SKIP the auto-open — popping a
  browser open on a server is a bug, not a feature — while still printing the
  path.

CONTROL TESTS (the G175 lesson): every block this file scopes its assertions to
is proved to exist and to be the right block FIRST, using text that was already
in the file before the fix. Without that, a typo in a section marker would make
every real assertion "pass" against an empty string.

Standalone-runnable (the RAM guard blocks pytest on this box):
`python test_g370_dashboard_handoff.py`.
"""
from __future__ import annotations

import pathlib
import re
import sys

# Plugin root by marker-walk, never parent-counting (same reason as
# test_commands.py: fixed-depth path math broke on the last re-nesting).
_HERE = pathlib.Path(__file__).resolve()
_PLUGIN_ROOT = next(
    p for p in _HERE.parents if (p / ".claude-plugin" / "plugin.json").is_file()
)
_SKILL = _PLUGIN_ROOT / "skills" / "rm-content-planner"
_SKILL_MD = _SKILL / "SKILL.md"
_PLAYBOOK_MD = _SKILL / "PLAYBOOK.md"


def _squash(text: str) -> str:
    """Collapse newlines/indent so a sentence-scoped regex is not defeated by
    wherever the markdown source happens to wrap."""
    return " ".join(text.split())


def _dashboard_block() -> str:
    """SKILL.md's 'Present as a DASHBOARD' bullet, up to the next top-level
    bullet."""
    text = _SKILL_MD.read_text(encoding="utf-8")
    start = text.index("- **Present as a DASHBOARD")
    nxt = text.find("\n- **", start + 1)
    return _squash(text[start : nxt if nxt != -1 else len(text)])


def _outputs_block() -> str:
    """SKILL.md's 'Where the OUTPUTS go' section, up to the next `##` heading."""
    text = _SKILL_MD.read_text(encoding="utf-8")
    start = text.index("## Where the OUTPUTS go")
    nxt = text.find("\n## ", start + 1)
    return _squash(text[start : nxt if nxt != -1 else len(text)])


def _step_8() -> str:
    """PLAYBOOK.md Step 8 — the deliverable step SKILL.md's summary points at."""
    text = _PLAYBOOK_MD.read_text(encoding="utf-8")
    start = text.index("## Step 8 — What the deliverable MUST contain")
    end = text.index("## Step 9 — Guardrails", start)
    return _squash(text[start:end])


def _save_failure_fallback() -> str:
    """PLAYBOOK Step 12's 'the save didn't land' fallback — the other place the
    skill hands the creator a file and has to say where it is."""
    text = _PLAYBOOK_MD.read_text(encoding="utf-8")
    start = text.index("If it still hasn't saved after three tries")
    end = text.index("**Privacy:**", start)
    return _squash(text[start:end])


def _allowed_tools() -> list[str]:
    text = _SKILL_MD.read_text(encoding="utf-8")
    m = re.search(r"^allowed-tools:\s*(.+)$", text, re.MULTILINE)
    assert m, "allowed-tools: line not found in SKILL.md frontmatter"
    return [t.strip() for t in m.group(1).split(",")]


# --- the three ideas, as CLAIMS and not as loose keywords ---------------------

# "absolute path" is the whole point: "the filename" and "a file they can open"
# both shipped and both left the creator hunting.
_ABSOLUTE_PATH_RE = re.compile(r"absolute path", re.IGNORECASE)

# ...and it has to be alone on its line so it is copy-pasteable / clickable.
_OWN_LINE_RE = re.compile(r"on its own line", re.IGNORECASE)

# An instruction to actually open it, in ONE sentence (`[^.]` cannot cross a
# full stop) so "open" from an unrelated sentence plus "browser" from another
# cannot fake a match.
_OPEN_IN_BROWSER_RE = re.compile(r"open[^.]{0,120}browser", re.IGNORECASE)

# The graceful-degrade clause. Opening a browser fails on plenty of machines and
# is unavailable in every headless run; the delivery must not die with it.
_DEGRADE_RE = re.compile(
    r"never fail|do not fail|don'?t fail|carry on|carry straight on", re.IGNORECASE
)

# The plain words to fall back to, quoted so the wording cannot drift into
# jargon a non-technical creator won't act on.
_PLAIN_FALLBACK = "open this file in your browser"


# --- CONTROL TESTS -----------------------------------------------------------
# These pass BEFORE and AFTER the fix on purpose. They prove each block below
# is the real block, so a failing assertion means the instruction is missing —
# not that the marker string was mistyped and the block came back empty.

def test_control_dashboard_block_is_the_real_block() -> None:
    block = _dashboard_block()
    assert len(block) > 200, f"dashboard block looks empty/truncated: {block!r}"
    assert "dashboard.html" in block, "wrong block — no dashboard.html in it"
    assert '<script id="plan">' in block, "wrong block — no plan JSON instruction"


def test_control_outputs_block_is_the_real_block() -> None:
    block = _outputs_block()
    assert len(block) > 200, f"outputs block looks empty/truncated: {block!r}"
    assert "content-plans/" in block, "wrong block — no content-plans/ folder rule"


def test_control_step_8_is_the_real_step() -> None:
    step = _step_8()
    assert len(step) > 2000, f"Step 8 looks empty/truncated: {len(step)} chars"
    assert "Section 00 — Foundation" in step, "wrong block — Step 8 item 1 missing"


def test_control_save_failure_fallback_is_the_real_block() -> None:
    block = _save_failure_fallback()
    assert len(block) > 400, f"save-failure block looks empty/truncated: {block!r}"
    assert "idempotency_key" in block, "wrong block — not the Step 12 fallback"


# --- THE REAL TESTS ----------------------------------------------------------

def test_dashboard_step_prints_the_absolute_path() -> None:
    block = _dashboard_block()
    assert _ABSOLUTE_PATH_RE.search(block), (
        "SKILL.md's dashboard delivery step never tells the skill to print the "
        "ABSOLUTE path of dashboard.html. That is G370: the file is written and "
        "the creator is never told where it is."
    )
    assert _OWN_LINE_RE.search(block), (
        "the path must be printed on its own line (nothing else on that line) so "
        "a non-technical creator can copy or click it"
    )


def test_dashboard_step_says_what_is_inside_the_file() -> None:
    block = _dashboard_block()
    assert re.search(r"one (?:short )?sentence", block, re.IGNORECASE), (
        "SKILL.md's dashboard step doesn't ask for the one-sentence summary of "
        "what is in the file — a bare path tells the creator nothing"
    )


def test_dashboard_step_tries_to_open_it_in_the_browser() -> None:
    assert _OPEN_IN_BROWSER_RE.search(_dashboard_block()), (
        "SKILL.md's dashboard step never tries to open dashboard.html in the "
        "creator's browser"
    )


def test_dashboard_step_degrades_gracefully_when_it_cannot_open() -> None:
    block = _dashboard_block()
    assert _PLAIN_FALLBACK in block.lower(), (
        f"SKILL.md's dashboard step lacks the plain fallback words "
        f"{_PLAIN_FALLBACK!r} for when the file cannot be opened automatically"
    )
    assert _DEGRADE_RE.search(block), (
        "SKILL.md's dashboard step doesn't say the delivery must NOT fail or be "
        "retried because opening the file didn't work"
    )


def test_dashboard_step_skips_the_auto_open_when_headless() -> None:
    """`runner.py` runs this skill unattended. Launching a browser there is a
    bug; printing the path is still required."""
    assert re.search(r"headless", _dashboard_block(), re.IGNORECASE), (
        "SKILL.md's dashboard step has no headless carve-out — an unattended "
        "run would try to pop a browser open on a server"
    )


def test_outputs_section_mirrors_the_path_handoff() -> None:
    """The two places that describe the same delivery must not drift apart."""
    assert _ABSOLUTE_PATH_RE.search(_outputs_block()), (
        "SKILL.md's 'Where the OUTPUTS go' section says where files are WRITTEN "
        "but never that the absolute path is told to the creator"
    )


def test_playbook_step_8_mirrors_all_three_handoff_points() -> None:
    step = _step_8()
    missing = [
        label
        for label, rx in (
            ("print the absolute path", _ABSOLUTE_PATH_RE),
            ("open it in the browser", _OPEN_IN_BROWSER_RE),
            ("degrade gracefully", _DEGRADE_RE),
        )
        if not rx.search(step)
    ]
    assert not missing, (
        "PLAYBOOK Step 8 (the delivery step) is missing the dashboard handoff "
        "rule(s): " + ", ".join(missing) + ". SKILL.md is the short contract and "
        "the PLAYBOOK is the method — if only one carries the rule they drift."
    )


def test_save_failure_fallback_gives_the_full_path_not_just_the_filename() -> None:
    """Same defect class, second location: 'tell them the filename' leaves a
    creator hunting through folders exactly like the dashboard did."""
    assert _ABSOLUTE_PATH_RE.search(_save_failure_fallback()), (
        "PLAYBOOK Step 12's save-failure fallback still only names the FILENAME "
        "of the rescue file. Tell them the absolute path, same as the dashboard."
    )


def test_a_shell_tool_is_granted_so_the_file_can_be_opened() -> None:
    """Without this the open-in-browser instruction is impossible to obey: the
    frontmatter granted no shell tool at all."""
    tools = _allowed_tools()
    assert any(t.startswith("Bash") for t in tools), (
        "SKILL.md allowed-tools grants no Bash, so the skill cannot run "
        f"start / open / xdg-open to open the dashboard. Granted: {tools}"
    )


def test_existing_tool_grants_survive() -> None:
    """Regression guard — adding the shell grant must not drop the old ones."""
    tools = _allowed_tools()
    for tool in ("Read", "Write", "WebFetch", "WebSearch"):
        assert tool in tools, f"{tool} was dropped from allowed-tools"


_CHECKS = [
    ("CONTROL: dashboard block is the real block",
     test_control_dashboard_block_is_the_real_block),
    ("CONTROL: outputs block is the real block",
     test_control_outputs_block_is_the_real_block),
    ("CONTROL: Step 8 is the real step",
     test_control_step_8_is_the_real_step),
    ("CONTROL: save-failure fallback is the real block",
     test_control_save_failure_fallback_is_the_real_block),
    ("dashboard step prints the ABSOLUTE path",
     test_dashboard_step_prints_the_absolute_path),
    ("dashboard step says what is inside the file",
     test_dashboard_step_says_what_is_inside_the_file),
    ("dashboard step tries to open it in the browser",
     test_dashboard_step_tries_to_open_it_in_the_browser),
    ("dashboard step degrades gracefully",
     test_dashboard_step_degrades_gracefully_when_it_cannot_open),
    ("dashboard step skips auto-open when headless",
     test_dashboard_step_skips_the_auto_open_when_headless),
    ("outputs section mirrors the path handoff",
     test_outputs_section_mirrors_the_path_handoff),
    ("PLAYBOOK Step 8 mirrors all three handoff points",
     test_playbook_step_8_mirrors_all_three_handoff_points),
    ("save-failure fallback gives the full path",
     test_save_failure_fallback_gives_the_full_path_not_just_the_filename),
    ("a shell tool is granted so the file can be opened",
     test_a_shell_tool_is_granted_so_the_file_can_be_opened),
    ("existing tool grants survive",
     test_existing_tool_grants_survive),
]


def main() -> int:
    # These docs contain emoji (the 🔴 prohibition marker). A failure message
    # quoting one must not die in Windows' cp1252 console before it prints.
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
