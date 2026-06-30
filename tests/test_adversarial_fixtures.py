from __future__ import annotations

from pathlib import Path

from gdoctor.scanner import scan_project


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "examples" / "adversarial"


def ids(path: Path) -> set[str]:
    return {issue.rule_id for issue in scan_project(path).issues}


def test_obvious_bad_case_triggers_interaction_rules():
    report = scan_project(FIXTURES / "obvious-bad")

    assert report.readiness == "NOT_READY"
    assert {"GD013", "GD014", "GD015", "GD016", "GD017", "GD018"}.issubset({issue.rule_id for issue in report.issues})


def test_simple_one_shot_fixture_does_not_trigger_stateful_rules():
    report = scan_project(FIXTURES / "simple-one-shot-pass")
    rule_ids = {issue.rule_id for issue in report.issues}

    assert report.readiness == "READY"
    assert "GD013" not in rule_ids
    assert "GD014" not in rule_ids


def test_structured_messages_are_not_brittle_history():
    rule_ids = ids(FIXTURES / "near-miss-structured-messages")

    assert "GD002" not in rule_ids
    assert "GD013" not in rule_ids
    assert "GD014" not in rule_ids


def test_read_only_tool_does_not_trigger_destructive_tool_rules():
    rule_ids = ids(FIXTURES / "read-only-tool")

    assert "GD003" not in rule_ids
    assert "GD018" not in rule_ids


def test_risky_prose_approval_triggers_machine_readable_rule():
    assert "GD018" in ids(FIXTURES / "risky-prose-approval")


def test_grounded_claim_with_evidence_object_passes():
    assert "GD017" not in ids(FIXTURES / "evidence-object-pass")


def test_structured_safe_pattern_passes_interaction_rules():
    report = scan_project(FIXTURES / "structured-safe-pattern")
    rule_ids = {issue.rule_id for issue in report.issues}

    assert report.readiness == "READY"
    assert not {"GD013", "GD014", "GD015", "GD017", "GD018"} & rule_ids


def test_unusual_layout_is_scanned():
    rule_ids = ids(FIXTURES / "unusual-layout")

    assert "GD013" in rule_ids
    assert "GD014" in rule_ids
