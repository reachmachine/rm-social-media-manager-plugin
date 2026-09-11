"""Shared fixture for the rm-copywriter skill tests (FRFRMU-1061).

Mirrors `rm-content-planner/tests/_playbook.py`'s shape on purpose — same
"one place that knows how the method is laid out on disk" idea, scaled down
to this skill's much smaller file set.

Not a test module (leading underscore keeps pytest from collecting it).
"""
from __future__ import annotations

import pathlib
import re

SKILL_DIR = pathlib.Path(__file__).resolve().parent.parent
AGENT_FILE = SKILL_DIR.parent.parent / "agents" / "copywriter.md"
PLUGIN_ROOT = next(
    p for p in SKILL_DIR.parents if (p / ".claude-plugin" / "plugin.json").is_file()
)
PLUGIN_MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"


def skill_text() -> str:
    return (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")


def correlation_table_text() -> str:
    return (SKILL_DIR / "correlation-table.md").read_text(encoding="utf-8")


def block_skeletons_text() -> str:
    return (SKILL_DIR / "block-skeletons.md").read_text(encoding="utf-8")


def qa_checklist_text() -> str:
    return (SKILL_DIR / "qa-checklist.md").read_text(encoding="utf-8")


def hook_variants_text() -> str:
    return (SKILL_DIR / "hook-variants.md").read_text(encoding="utf-8")


def proof_and_claims_text() -> str:
    return (SKILL_DIR / "proof-and-claims.md").read_text(encoding="utf-8")


def bullet_recipe_text() -> str:
    return (SKILL_DIR / "bullet-recipe.md").read_text(encoding="utf-8")


def belief_breaker_text() -> str:
    return (SKILL_DIR / "belief-breaker.md").read_text(encoding="utf-8")


def pattern_interrupt_text() -> str:
    return (SKILL_DIR / "pattern-interrupt.md").read_text(encoding="utf-8")


def swipe_file_text() -> str:
    return (SKILL_DIR / "swipe-file.md").read_text(encoding="utf-8")


def closes_text() -> str:
    return (SKILL_DIR / "closes.md").read_text(encoding="utf-8")


def writer_brief_text() -> str:
    return (SKILL_DIR / "writer-brief.md").read_text(encoding="utf-8")


def flop_diagnosis_text() -> str:
    return (SKILL_DIR / "flop-diagnosis.md").read_text(encoding="utf-8")


def agent_text() -> str:
    return AGENT_FILE.read_text(encoding="utf-8")


def frontmatter(text: str) -> str:
    """The `---\\n...\\n---` YAML-ish frontmatter block at the top of a file."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "no frontmatter block found"
    return m.group(1)


def allowed_tools(skill_md_text: str) -> list[str]:
    m = re.search(r"^allowed-tools:\s*(.+)$", skill_md_text, re.MULTILINE)
    assert m, "allowed-tools: line not found"
    return [t.strip() for t in m.group(1).split(",")]


_TABLE_ROW_RE = re.compile(
    r"^\|\s*([a-z_]+)\s*\|\s*([a-z_, ]+)\s*\|\s*(.+?)\s*\|\s*$",
    re.MULTILINE,
)


def parse_correlation_table(text: str | None = None) -> dict[str, set[str]]:
    """Parse the correlation table's rows into
    ``{framework_family: {hook_subcategory, ...}}``.

    Only rows under the real header (skips the header/separator rows and any
    other pipe-tables in the file, e.g. a stray example) by requiring the
    first column to be a lowercase/underscore token that is not the literal
    header words.
    """
    text = text if text is not None else correlation_table_text()
    result: dict[str, set[str]] = {}
    for match in _TABLE_ROW_RE.finditer(text):
        family, applies_to, _rest = match.groups()
        if family in ("framework_family", "---", "--- "):
            continue
        if set(family) <= {"-"}:
            continue
        subs = {s.strip() for s in applies_to.split(",") if s.strip()}
        if not subs:
            continue
        result[family] = subs
    return result


def allowed_families_for(subcategory: str, table: dict[str, set[str]] | None = None) -> set[str]:
    table = table if table is not None else parse_correlation_table()
    return {family for family, subs in table.items() if subcategory in subs}


def plugin_version() -> tuple[int, int, int]:
    import json

    manifest = json.loads(PLUGIN_MANIFEST.read_text(encoding="utf-8"))
    m = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", manifest["version"].strip())
    assert m, f"{manifest['version']!r} is not a three-part version number"
    return tuple(int(g) for g in m.groups())  # type: ignore[return-value]
