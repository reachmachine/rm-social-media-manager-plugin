"""
test_version_check.py — standalone driver for `runner.py`'s version-check-
and-pull logic (prd.md Amendment 44 §44.8, P1162).

Why this exists (not pytest): `github-marketing` has no `backend/` and no
test framework at all. This is a plain script: run it with
`python .claude/skills/rm-content-planner/.dev/test_version_check.py` and
read the PASS/FAIL lines it prints. Exit code 0 = all pass, 1 = any failed.

It does NOT require `claude-agent-sdk` to be installed — `runner.py` imports
it at module top only to build the Agent SDK options for the live run, which
this driver never touches. A tiny stub module is registered in `sys.modules`
before `runner.py` is imported so the import succeeds without the real
package.

NOT one of the 14 whitelisted distributed files (prd.md §44.5) — this lives
under `.dev/` on purpose and is never uploaded/published as part of a skill
bundle.
"""
from __future__ import annotations

import importlib.util
import pathlib
import shutil
import sys
import tempfile
import types

# --- stub claude_agent_sdk so `import runner` succeeds without the package ---
if "claude_agent_sdk" not in sys.modules:
    _stub = types.ModuleType("claude_agent_sdk")
    _stub.query = lambda *a, **k: None  # never called by this driver
    _stub.ClaudeAgentOptions = object
    sys.modules["claude_agent_sdk"] = _stub

_RUNNER_PATH = pathlib.Path(__file__).resolve().parent.parent / "runner.py"
_spec = importlib.util.spec_from_file_location("rm_runner_under_test", _RUNNER_PATH)
runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runner)

FAILURES: list[str] = []


def _report(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


def _make_skill_dir(version: str = "v1.2.0") -> pathlib.Path:
    d = pathlib.Path(tempfile.mkdtemp(prefix="rm_skill_test_"))
    (d / "VERSION").write_text(f"{version}\n", encoding="utf-8")
    (d / "SKILL.md").write_text("SKILL v1.2.0 content\n", encoding="utf-8")
    (d / "README.md").write_text("README v1.2.0 content\n", encoding="utf-8")
    return d


def _snapshot(d: pathlib.Path) -> dict[str, str]:
    # .as_posix() so keys use "/" on every OS (Windows rglob gives "\\"),
    # matching the "/"-joined filenames the MCP bundle contract uses.
    return {
        p.relative_to(d).as_posix(): p.read_text(encoding="utf-8")
        for p in sorted(d.rglob("*"))
        if p.is_file()
    }


FAKE_BUNDLE_FILES = {
    "SKILL.md": "SKILL v1.3.0 content\n",
    "PLAYBOOK.md": "PLAYBOOK v1.3.0 content\n",
    "rules/authority.md": "authority v1.3.0 content\n",
    "README.md": "README v1.3.0 content\n",
    "VERSION": "v1.3.0\n",
}


# --- case (a): tool call raises/errors ---------------------------------------
def test_case_a_tool_call_raises() -> None:
    d = _make_skill_dir()
    try:
        before = _snapshot(d)

        def _raising_call_tool(name: str, arguments: dict):
            raise RuntimeError("simulated MCP transport failure")

        raised = False
        try:
            runner.check_and_update_skill(d, _raising_call_tool)
        except Exception:  # noqa: BLE001
            raised = True

        after = _snapshot(d)
        _report(
            "case (a) tool call raises -> fail-open, no crash",
            (not raised) and before == after,
            "did not raise" if not raised else "RAISED (fail-open broken)",
        )
    finally:
        shutil.rmtree(d, ignore_errors=True)


# --- case (b): current_version is None (nothing ever published) -----------
def test_case_b_remote_version_none() -> None:
    d = _make_skill_dir()
    try:
        before = _snapshot(d)

        def _empty_registry_call_tool(name: str, arguments: dict):
            assert name == "get_skill_version"
            return {"skill_id": "rm-content-planner", "current_version": None, "changelog": ""}

        raised = False
        try:
            runner.check_and_update_skill(d, _empty_registry_call_tool)
        except Exception:  # noqa: BLE001
            raised = True

        after = _snapshot(d)
        _report(
            "case (b) remote current_version=None -> no-op, no crash",
            (not raised) and before == after,
        )
    finally:
        shutil.rmtree(d, ignore_errors=True)


# --- case (c): remote version is newer -> full update happy path ----------
def test_case_c_newer_version_updates() -> None:
    d = _make_skill_dir(version="v1.2.0")
    try:
        def _newer_call_tool(name: str, arguments: dict):
            if name == "get_skill_version":
                return {
                    "skill_id": "rm-content-planner",
                    "current_version": "1.3.0",
                    "changelog": "Adds G107 rewatch_driven signal.",
                }
            if name == "get_skill_bundle":
                return {
                    "skill_id": "rm-content-planner",
                    "version": "1.3.0",
                    "changelog": "Adds G107 rewatch_driven signal.",
                    "files": dict(FAKE_BUNDLE_FILES),
                }
            raise AssertionError(f"unexpected tool call: {name}")

        runner.check_and_update_skill(d, _newer_call_tool)

        after = _snapshot(d)
        files_ok = all(after.get(fn) == content for fn, content in FAKE_BUNDLE_FILES.items())
        version_ok = (d / "VERSION").read_text(encoding="utf-8").strip() == "v1.3.0"
        _report(
            "case (c) newer remote version -> files + VERSION written",
            files_ok and version_ok,
            f"files_ok={files_ok} version_ok={version_ok} VERSION={after.get('VERSION')!r}",
        )
    finally:
        shutil.rmtree(d, ignore_errors=True)


# --- Rule 3 break #1: mid-write failure must leave VERSION untouched -------
def test_rule3_partial_write_leaves_version_old() -> None:
    """Inject an OSError on the 3rd of 5 fake-file writes (SKILL.md=1,
    PLAYBOOK.md=2, rules/authority.md=3 <- fails, README.md=4, VERSION=5 —
    never reached). Asserts VERSION is still the OLD local value afterward.

    This is the falsifiability break from prd.md §44.8 point 3 / the P1162
    prompt's Rule 3 item 1: prove 'write VERSION last' actually protects a
    partial write, not just that it looks that way in the happy path.
    """
    d = _make_skill_dir(version="v1.2.0")
    try:
        write_count = {"n": 0}
        original_write_text = pathlib.Path.write_text

        def _flaky_write_text(self, *args, **kwargs):
            write_count["n"] += 1
            if self.name == "authority.md" and write_count["n"] == 3:
                raise OSError("synthetic disk failure on write #3 of 5")
            return original_write_text(self, *args, **kwargs)

        def _newer_call_tool(name: str, arguments: dict):
            if name == "get_skill_version":
                return {"skill_id": "rm-content-planner", "current_version": "1.3.0", "changelog": "x"}
            if name == "get_skill_bundle":
                return {
                    "skill_id": "rm-content-planner",
                    "version": "1.3.0",
                    "changelog": "x",
                    "files": dict(FAKE_BUNDLE_FILES),
                }
            raise AssertionError(f"unexpected tool call: {name}")

        pathlib.Path.write_text = _flaky_write_text
        try:
            raised = False
            try:
                runner.check_and_update_skill(d, _newer_call_tool)
            except Exception:  # noqa: BLE001
                raised = True
        finally:
            pathlib.Path.write_text = original_write_text

        version_after = (d / "VERSION").read_text(encoding="utf-8").strip()
        _report(
            "Rule3-break#1: mid-write OSError -> VERSION NOT updated, no crash",
            (not raised) and version_after == "v1.2.0",
            f"raised={raised} VERSION={version_after!r} (expected v1.2.0, unchanged)",
        )
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main() -> int:
    test_case_a_tool_call_raises()
    test_case_b_remote_version_none()
    test_case_c_newer_version_updates()
    test_rule3_partial_write_leaves_version_old()

    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED: {', '.join(FAILURES)}")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
