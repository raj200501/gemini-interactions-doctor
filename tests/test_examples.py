from __future__ import annotations

from pathlib import Path

from gdoctor.scanner import scan_project


ROOT = Path(__file__).resolve().parents[1]


def test_fragile_example_is_not_ready_with_five_blockers():
    report = scan_project(ROOT / "examples" / "fragile-gemini-app")
    blocker_ids = {issue.rule_id for issue in report.blockers}

    assert report.readiness == "NOT_READY"
    assert len(report.blockers) == 5
    assert blocker_ids == {"GD001", "GD003", "GD006", "GD008", "GD009"}


def test_upgraded_example_is_ready_or_ready_with_caution():
    report = scan_project(ROOT / "examples" / "upgraded-gemini-app")

    assert report.readiness in {"READY", "READY_WITH_CAUTION"}
    assert not report.blockers
    assert report.score >= 90
