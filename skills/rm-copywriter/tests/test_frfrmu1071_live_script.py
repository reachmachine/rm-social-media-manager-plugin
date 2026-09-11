"""Falsifiable guards for p33's copywriter half -- the `live_script` block
skeleton (FRFRMU-1071).

Only exists when the creator has a live/webinar/workshop already on the
calendar as an `anchors` entry -- this skill never suggests running one.
The planner half (the 5-question readiness check) lives in
rm-content-planner/tests/test_frfrmu1071_sales_readiness_check.py.

Standalone-runnable: `python test_frfrmu1071_live_script.py`.
"""
from __future__ import annotations

import re
import sys

from _copywriter import block_skeletons_text, closes_text


def _flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def test_live_script_section_exists() -> None:
    text = block_skeletons_text()
    assert "live_script" in text
    assert "FRFRMU-1071" in text


def test_anchor_guard_is_hard() -> None:
    text = block_skeletons_text()
    idx = text.rindex("check_live_script")
    nearby = _flat(text[idx: idx + 400])
    assert "hard" in nearby.lower()
    assert "anchor" in nearby.lower()
    assert "fails outright" in nearby.lower() or "no exceptions" in nearby.lower()


def test_nine_opening_beats_present() -> None:
    flat = _flat(block_skeletons_text())
    for beat in (
        "title", "rapport", "the ruler", "brief qualify", "origin story",
        "liken it", "one case study", "transition naming the 3 secrets",
    ):
        assert beat.lower() in flat.lower(), f"live_script opening missing beat: {beat!r}"


def test_body_maps_to_core_three() -> None:
    flat = _flat(block_skeletons_text())
    assert "core_three" in flat
    assert "state it" in flat.lower()
    assert "bridge story" in flat.lower()
    assert "break old belief" in flat.lower()
    assert "restate as truth" in flat.lower()


def test_close_uses_the_running_stack_and_closes_md() -> None:
    text = block_skeletons_text()
    idx = text.index("## 6. Live / webinar script")
    section = text[idx: text.index("## Draft-pass rules")]
    assert "FRFRMU-1049" in section  # running stack
    assert "closes.md" in section
    assert "FRFRMU-1053" in section  # guarantee
    assert "FRFRMU-1050" in section  # real limits


def test_teaches_method_self_check() -> None:
    flat = _flat(block_skeletons_text())
    assert "teaches_method" in flat
    assert "teaches_method: false" in flat or "teaches_method` is `false`" in flat.replace(
        "`", ""
    ).replace("`", "") or "teaches_method is false" in flat.lower()


def test_trial_close_density_and_first_yes() -> None:
    flat = _flat(block_skeletons_text()).lower()
    assert "~1 per minute" in flat or "1 per minute" in flat


def test_never_a_fake_deadline_for_a_live() -> None:
    flat = _flat(block_skeletons_text()).lower()
    idx = flat.index("real limits only")
    nearby = flat[idx: idx + 150]
    assert "never fake one" in nearby


def test_dm_restricted_closes_still_apply() -> None:
    """Sanity: closes.md's own DM restriction wording is unaffected by adding
    the live_script consumer."""
    text = closes_text()
    assert "dm_allowed: false" in text.lower() or "**false**" in text


_CHECKS = [
    ("live_script section exists", test_live_script_section_exists),
    ("anchor guard is hard", test_anchor_guard_is_hard),
    ("nine opening beats present", test_nine_opening_beats_present),
    ("body maps to core_three", test_body_maps_to_core_three),
    ("close uses the running stack + closes.md", test_close_uses_the_running_stack_and_closes_md),
    ("teaches_method self-check", test_teaches_method_self_check),
    ("trial-close density ~1/min", test_trial_close_density_and_first_yes),
    ("never a fake deadline for a live", test_never_a_fake_deadline_for_a_live),
    ("DM-restricted closes still apply", test_dm_restricted_closes_still_apply),
]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    failed = 0
    for label, check in _CHECKS:
        try:
            check()
        except (AssertionError, FileNotFoundError, ValueError) as exc:
            failed += 1
            print(f"[FAIL] {label}: {exc}")
        else:
            print(f"[PASS] {label}")
    print(f"{len(_CHECKS) - failed}/{len(_CHECKS)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
