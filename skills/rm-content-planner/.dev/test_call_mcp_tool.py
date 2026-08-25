"""
test_call_mcp_tool.py — standalone driver for runner.py's `_call_mcp_tool`
wire format (prd.md Amendment 44 §44.8, P1165).

Why this exists: P1160/P1161 flagged this function's JSON-RPC wire format as
an educated guess, never verified against the real MCP server.
`.dev/test_version_check.py` only exercises `check_and_update_skill` against
a FAKE `call_tool` — it never calls the real `_call_mcp_tool`, so this bug
had zero coverage. P1165 verified the real shape directly (in-process probe
against the real FastMCP server code + the real MCPAuthMiddleware) and found
it broken two ways — see runner.py's own docstring on `_call_mcp_tool` for
the fix. GOLDEN_SSE_RESPONSE is the REAL response bytes from that probe.

Run: python .claude/skills/rm-content-planner/.dev/test_call_mcp_tool.py
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import types
import urllib.request
from unittest.mock import MagicMock, patch

if "claude_agent_sdk" not in sys.modules:
    _stub = types.ModuleType("claude_agent_sdk")
    _stub.query = lambda *a, **k: None
    _stub.ClaudeAgentOptions = object
    sys.modules["claude_agent_sdk"] = _stub

_RUNNER_PATH = pathlib.Path(__file__).resolve().parent.parent / "runner.py"
_spec = importlib.util.spec_from_file_location("rm_runner_under_test_wire", _RUNNER_PATH)
runner = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(runner)

FAILURES: list[str] = []


def _report(name: str, ok: bool, detail: str = "") -> None:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}" + (f" — {detail}" if detail else ""))
    if not ok:
        FAILURES.append(name)


# Real byte-for-byte response captured from a live probe against the actual
# FastMCP server (P1165) — Mongo unreachable, tool fails open to
# current_version=None, exactly what get_skill_version returns in that case.
GOLDEN_SSE_RESPONSE = (
    b': ping - 2026-08-11 06:44:40.494997+00:00\r\n\r\n'
    b'event: message\r\n'
    b'data: {"jsonrpc":"2.0","id":2,"result":{"content":[{"type":"text","text":'
    b'"{\\n  \\"skill_id\\": \\"rm-content-planner\\",\\n  \\"current_version\\": null,'
    b'\\n  \\"changelog\\": \\"\\"\\n}"}],"structuredContent":{"skill_id":"rm-content-planner",'
    b'"current_version":null,"changelog":""},"isError":false}}\r\n\r\n'
)


def _fake_urlopen(captured_requests):
    def _opener(req, timeout=15):
        captured_requests.append(req)
        cm = MagicMock()
        cm.__enter__.return_value.read.return_value = GOLDEN_SSE_RESPONSE
        cm.__exit__.return_value = False
        return cm
    return _opener


def test_call_mcp_tool_wraps_args_and_parses_real_sse_response() -> None:
    captured: list = []
    with patch.object(urllib.request, "urlopen", _fake_urlopen(captured)):
        result = runner._call_mcp_tool(
            "https://devapi.reachmachine.org/mcp/", "fake-token",
            "get_skill_version", {"skill_id": "rm-content-planner"},
        )
    sent_body = json.loads(captured[0].data.decode("utf-8"))
    args_wrapped = sent_body["params"]["arguments"] == {"args": {"skill_id": "rm-content-planner"}}
    parsed_ok = result == {
        "skill_id": "rm-content-planner", "current_version": None, "changelog": "",
    }
    _report(
        "_call_mcp_tool wraps arguments under 'args' and parses real SSE response",
        args_wrapped and parsed_ok,
        f"args_wrapped={args_wrapped} parsed_ok={parsed_ok} result={result!r}",
    )


def test_call_mcp_tool_raises_on_error_result() -> None:
    error_sse = (
        b'event: message\r\n'
        b'data: {"jsonrpc":"2.0","id":2,"result":{"content":[{"type":"text",'
        b'"text":"boom"}],"isError":true}}\r\n\r\n'
    )
    def _opener(req, timeout=15):
        cm = MagicMock()
        cm.__enter__.return_value.read.return_value = error_sse
        cm.__exit__.return_value = False
        return cm
    raised = False
    with patch.object(urllib.request, "urlopen", _opener):
        try:
            runner._call_mcp_tool("https://x/mcp/", "t", "get_skill_version", {})
        except RuntimeError:
            raised = True
    _report("_call_mcp_tool raises RuntimeError on isError result", raised)


def main() -> int:
    test_call_mcp_tool_wraps_args_and_parses_real_sse_response()
    test_call_mcp_tool_raises_on_error_result()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} FAILED: {', '.join(FAILURES)}")
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
