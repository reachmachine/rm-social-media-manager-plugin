"""Falsifiable test for the G369 SessionStart hook.

The hook (`hooks/hooks.json` + `hooks/session-resume-check.sh`) fires when a
customer resumes a previous session. `SessionStart` runs before MCP servers
finish connecting, so the script cannot call `get_creator_brief` itself — its
only job is to make sure the resume-check instruction (the one P1414 put at
the top of `PLAYBOOK.md` Step 1) reaches Claude automatically, instead of
waiting for the customer to re-invoke a command.

This guards four things:
1. `hooks/hooks.json` is valid JSON with a `SessionStart` entry matched on
   `"resume"` (not every session start — a brand-new session has nothing to
   resume), pointing at the script via the literal `${CLAUDE_PLUGIN_ROOT}`
   path Claude Code expands at runtime.
2. The script the manifest names actually exists at that path and is
   executable — a `hooks.json` that names a dead or non-executable file would
   fire and do nothing, the same "dead automation" failure class
   `test_no_inert_retry_queues.py` guards on the backend side.
3. Running the script exits 0 and its stdout mentions both
   `get_creator_brief` and `planning_progress` — the two things P1414's
   resume check actually needs to be told to look for. The hook could have
   valid JSON and an executable script and still fail to trigger the right
   behaviour if the wording drifts.
4. CONTROL: `plugin.json` parses as valid JSON and its `name` is
   `rm-social-media-manager` — proves the plugin root resolved is the right
   one before trusting anything else above.

Standalone-runnable (the RAM guard blocks pytest on this box):
`python test_g369_sessionstart_hook.py`.
"""
from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

# Plugin root by marker-walk, never parent-counting (plugin-creator memory:
# fixed-depth path math is exactly what broke on the last re-nesting).
_HERE = pathlib.Path(__file__).resolve()
_PLUGIN_ROOT = next(
    p for p in _HERE.parents if (p / ".claude-plugin" / "plugin.json").is_file()
)
_HOOKS_JSON = _PLUGIN_ROOT / "hooks" / "hooks.json"
_HOOK_SCRIPT = _PLUGIN_ROOT / "hooks" / "session-resume-check.sh"


def test_plugin_root_is_correct() -> None:
    """CONTROL: prove we resolved the right plugin before trusting anything else."""
    manifest = json.loads(
        (_PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    assert manifest["name"] == "rm-social-media-manager", (
        f"resolved plugin root {_PLUGIN_ROOT} has name {manifest.get('name')!r}, "
        "not rm-social-media-manager — every other check below is meaningless"
    )


def test_hooks_json_declares_a_resume_matched_sessionstart_hook() -> None:
    data = json.loads(_HOOKS_JSON.read_text(encoding="utf-8"))
    entries = data["hooks"]["SessionStart"]
    assert any(e.get("matcher") == "resume" for e in entries), (
        "hooks.json has no SessionStart entry matched on 'resume' — without "
        "this, the hook fires on every session (noise) or never (dead)"
    )
    resume_entry = next(e for e in entries if e.get("matcher") == "resume")
    commands = [h.get("command") for h in resume_entry.get("hooks", [])]
    assert "${CLAUDE_PLUGIN_ROOT}/hooks/session-resume-check.sh" in commands, (
        f"resume entry points at {commands!r}, not the expected script path — "
        "a wrong path here would fire silently and do nothing"
    )


def test_referenced_script_exists_and_is_executable() -> None:
    assert _HOOK_SCRIPT.is_file(), (
        f"hooks.json names {_HOOK_SCRIPT}, which does not exist — this is the "
        "'dead automation' failure class test_no_inert_retry_queues.py guards "
        "against on the backend: nothing would ever say so"
    )
    assert os.access(_HOOK_SCRIPT, os.X_OK), (
        f"{_HOOK_SCRIPT} exists but is not executable — Claude Code cannot run it"
    )


def test_script_runs_and_names_both_resume_check_terms() -> None:
    result = subprocess.run(
        [str(_HOOK_SCRIPT)], capture_output=True, text=True, timeout=10
    )
    assert result.returncode == 0, (
        f"script exited {result.returncode}, must be 0 — a SessionStart hook "
        f"must never block a session. stderr: {result.stderr}"
    )
    assert "get_creator_brief" in result.stdout, (
        "script stdout never mentions get_creator_brief — the hook could fire "
        "perfectly and still fail to tell Claude which tool to call"
    )
    assert "planning_progress" in result.stdout, (
        "script stdout never mentions planning_progress — the hook could fire "
        "perfectly and still fail to tell Claude which field to check"
    )


_CHECKS = [
    ("plugin root resolves to rm-social-media-manager", test_plugin_root_is_correct),
    ("hooks.json declares a resume-matched SessionStart hook",
     test_hooks_json_declares_a_resume_matched_sessionstart_hook),
    ("referenced script exists and is executable",
     test_referenced_script_exists_and_is_executable),
    ("script runs, exits 0, and names both resume-check terms",
     test_script_runs_and_names_both_resume_check_terms),
]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    failed = 0
    for label, check in _CHECKS:
        try:
            check()
        except Exception as exc:  # noqa: BLE001 - a crash IS a failed check here
            failed += 1
            print(f"[FAIL] {label}: {exc}")
        else:
            print(f"[PASS] {label}")
    print(f"{len(_CHECKS) - failed}/{len(_CHECKS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
