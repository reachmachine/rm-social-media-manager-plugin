"""Falsifiable test for pre-filling the Reach Machine MCP connection.

Two things changed so a customer doesn't have to hand-type connection details:

1. `plugin.json` declares the public `reachmachine` MCP endpoint (URL only) so
   Claude Code's interactive CLI shows it automatically and offers OAuth login
   via `/mcp` — no `claude mcp add` needed.
2. `runner.py` (the headless path) now defaults `RM_MCP_URL` to that same
   public endpoint, so only the per-user `ANTHROPIC_API_KEY` / `RM_MCP_TOKEN`
   are required.

Both checks guard against the one thing that must never happen here: a static
access token committed anywhere in the plugin. The URL is public and safe to
bake in; the token is per-user and must never be.

Standalone-runnable, like `test_g249_defaults.py`: `python test_rm_mcp_prefill.py`.
"""
from __future__ import annotations

import ast
import json
import pathlib
import sys

_SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent
_RUNNER = _SKILL_DIR / "runner.py"
_PLUGIN_JSON = _SKILL_DIR.parent.parent / ".claude-plugin" / "plugin.json"

_EXPECTED_URL = "https://api.reachmachine.org/mcp"


def _runner_text() -> str:
    return _RUNNER.read_text(encoding="utf-8")


def _plugin_json() -> dict:
    return json.loads(_PLUGIN_JSON.read_text(encoding="utf-8"))


def test_plugin_json_declares_the_reachmachine_endpoint() -> None:
    """plugin.json pre-fills the MCP URL so Claude Code offers /mcp OAuth login."""
    data = _plugin_json()
    servers = data.get("mcpServers", {})
    assert "reachmachine" in servers, "plugin.json has no mcpServers.reachmachine entry"
    entry = servers["reachmachine"]
    assert entry.get("type") == "http", "reachmachine MCP entry is not type=http"
    assert entry.get("url") == _EXPECTED_URL, (
        f"reachmachine MCP url is {entry.get('url')!r}, expected {_EXPECTED_URL!r}"
    )


def test_plugin_json_never_carries_a_static_token() -> None:
    """Guard: the URL is safe to bake in; a token never is."""
    raw = _PLUGIN_JSON.read_text(encoding="utf-8")
    for banned in ("headers", "Authorization", "Bearer", "RM_MCP_TOKEN"):
        assert banned not in raw, (
            f"plugin.json contains {banned!r} — a static credential must never be "
            "committed; each user authenticates their own account via /mcp OAuth"
        )


def _run_function_env_check() -> tuple[str, ...]:
    """Return the tuple of env-var names `run()` requires before it will start."""
    tree = ast.parse(_runner_text())
    run_fn = next(
        n for n in ast.walk(tree)
        if isinstance(n, ast.AsyncFunctionDef) and n.name == "run"
    )
    for node in ast.walk(run_fn):
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Tuple):
            names = [elt.value for elt in node.iter.elts if isinstance(elt, ast.Constant)]
            if names and names[0] == "ANTHROPIC_API_KEY":
                return tuple(names)
    raise AssertionError("could not find the required-env-vars loop in run()")


def test_run_no_longer_requires_rm_mcp_url() -> None:
    """RM_MCP_URL must NOT be in the hard-required list — it now has a default."""
    required = _run_function_env_check()
    assert "RM_MCP_URL" not in required, (
        f"RM_MCP_URL is still hard-required: {required!r} — the default isn't wired up"
    )
    assert required == ("ANTHROPIC_API_KEY", "RM_MCP_TOKEN"), (
        f"required env vars changed unexpectedly: {required!r}"
    )


def test_run_sets_the_default_before_checking_env() -> None:
    """`run()` must call os.environ.setdefault(RM_MCP_URL, ...) before the env check,
    so a caller who never sets RM_MCP_URL still gets a working connection."""
    text = _runner_text()
    setdefault_pos = text.find('os.environ.setdefault("RM_MCP_URL"')
    check_pos = text.find('for var in ("ANTHROPIC_API_KEY", "RM_MCP_TOKEN")')
    assert setdefault_pos != -1, "run() never calls os.environ.setdefault for RM_MCP_URL"
    assert check_pos != -1, "the required-env-vars loop text moved; update this test"
    assert setdefault_pos < check_pos, (
        "os.environ.setdefault(RM_MCP_URL, ...) must run BEFORE the required-vars "
        "check, or an unset RM_MCP_URL still fails the run"
    )


def test_default_rm_mcp_url_matches_the_plugin_endpoint() -> None:
    """The headless default and the plugin's pre-filled URL must be the same
    endpoint, or the two paths silently point at different Reach Machine
    deployments."""
    assert f'_DEFAULT_RM_MCP_URL = "{_EXPECTED_URL}"' in _runner_text(), (
        f"runner.py's _DEFAULT_RM_MCP_URL does not equal {_EXPECTED_URL!r}, "
        "or does not match plugin.json's mcpServers.reachmachine.url"
    )


_CHECKS = [
    ("plugin.json pre-fills the reachmachine MCP endpoint",
     test_plugin_json_declares_the_reachmachine_endpoint),
    ("plugin.json never carries a static token/header",
     test_plugin_json_never_carries_a_static_token),
    ("run() no longer hard-requires RM_MCP_URL",
     test_run_no_longer_requires_rm_mcp_url),
    ("run() sets the RM_MCP_URL default before the env check",
     test_run_sets_the_default_before_checking_env),
    ("headless default matches the plugin's pre-filled URL",
     test_default_rm_mcp_url_matches_the_plugin_endpoint),
]


def main() -> int:
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
