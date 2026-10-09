#!/usr/bin/env python3
"""Keep hook-only bytes out of the model's chat history (RMP-76).

`open_workspace` and `get_resume_checklist` reply with the server's step
`rules` (about 5 KB) so THIS plugin's hooks can cache them. The model never
reads them, but everything in a tool reply is re-read on every later model
call (token audit 2026-09-28: `open_workspace` was 9.4 KB, 5.4 KB of it
rules). The reply also carries dozens of `null` fields.

After `step_rules_cache` has stored the rules, this module builds the reply
the model should see instead: the same JSON, without `rules` and without
`null` values, in the SAME shape the harness gave the hook (text blocks
stay text blocks). The hook prints it as `hookSpecificOutput.
updatedToolOutput` ("Replaces the tool output before it is sent to the
model" -- read from the installed Claude Code 2.1.284 hook schema).

Fail-safe: any doubt returns None and the model just sees the full reply,
exactly as before. Nothing here can lose data the hooks need, because the
hooks read the ORIGINAL payload, not this output.
"""
from __future__ import annotations

import json
from typing import Any

import connection_state as cs
import plan_cache
import slim_scraper_output
import step_rules_cache

_SLIMMED_TOOLS = ("open_workspace", "get_resume_checklist", "next_actions")


def _drop_nulls(node: Any) -> Any:
    if isinstance(node, dict):
        return {k: _drop_nulls(v) for k, v in node.items() if v is not None}
    if isinstance(node, list):
        return [_drop_nulls(x) for x in node]
    return node


def _sent_deny_reasons(data: dict) -> dict:
    """The `deny_reasons` map a reply carries (top level or inside its `next_actions`); {} when none."""
    found: dict = {}
    for holder in (data.get("next_actions"), data):
        if isinstance(holder, dict) and isinstance(holder.get("deny_reasons"), dict):
            found.update(holder["deny_reasons"])
    return found


def _deny_reasons_are_kept(session_id: str, data: dict) -> bool:
    """True when the hooks hold every line of the map this reply carries (P2314: the model never reads them, so they ride only once)."""
    sent = _sent_deny_reasons(data)
    kept = plan_cache.read_state(session_id).get("deny_reasons") or {}
    return bool(sent) and all(kept.get(k) == v for k, v in sent.items())


def _slim_text(text: str, drop_deny: bool = False) -> str | None:
    try:
        data = json.loads(text)
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    data.pop("rules", None)
    if drop_deny:
        data.pop("deny_reasons", None)
        if isinstance(data.get("next_actions"), dict):
            data["next_actions"].pop("deny_reasons", None)
    return json.dumps(_drop_nulls(data), separators=(",", ":"), ensure_ascii=False)


def _replace_text(tool_response: Any, slim: str) -> Any | None:
    """Same shape in, same shape out. None when the shape is unknown."""
    if isinstance(tool_response, str):
        return slim
    if isinstance(tool_response, list):
        out: list[Any] = []
        done = False
        for item in tool_response:
            if not done and isinstance(item, dict) and isinstance(item.get("text"), str):
                out.append({**item, "text": slim})
                done = True
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                continue  # a second text block would repeat the full reply
            else:
                out.append(item)
        return out if done else None
    if isinstance(tool_response, dict):
        content = tool_response.get("content")
        if isinstance(content, (list, str)):
            inner = _replace_text(content, slim)
            return None if inner is None else {**tool_response, "content": inner}
        if isinstance(tool_response.get("text"), str):
            return {**tool_response, "text": slim}
    return None


def slimmed_output(session_id: str, payload: dict) -> Any | None:
    """The replacement tool output, or None to leave the reply untouched."""
    try:
        tool_name = payload.get("tool_name")
        if not isinstance(tool_name, str):
            return None
        if cs.server_of(tool_name) == "apify":   # RMP-280: a background job's big scraper results
            slim = slim_scraper_output.apify_slim_text(session_id, payload, tool_name.rsplit("__", 1)[-1])
            return None if slim is None else _replace_text(payload.get("tool_response"), slim)
        if cs.server_of(tool_name) != "reachmachine":
            return None
        if tool_name.rsplit("__", 1)[-1] not in _SLIMMED_TOOLS:
            return None
        tool_response = payload.get("tool_response")
        text = cs.flatten_response_text(tool_response)
        try:
            original = json.loads(text)
        except Exception:
            return None
        if isinstance(original, dict) and original.get("rules") is not None:
            if step_rules_cache.cached_rules(session_id) is None:
                return None  # the hooks did not keep the rules: leave it whole
        slim = _slim_text(text, isinstance(original, dict) and _deny_reasons_are_kept(session_id, original))
        if slim is None or len(slim) >= len(text):
            return None
        return _replace_text(tool_response, slim)
    except Exception:
        return None
