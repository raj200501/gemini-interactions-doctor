from __future__ import annotations

import json
from pathlib import Path

from gdoctor.scanner import scan_project


ROOT = Path(__file__).resolve().parents[1]

TARGETS = {
    "fragile": ROOT / "examples" / "fragile-gemini-app",
    "upgraded": ROOT / "examples" / "upgraded-gemini-app",
    "simple-one-shot": ROOT / "examples" / "adversarial" / "simple-one-shot-pass",
}

GOLDENS = {
    "fragile": ROOT / "tests" / "golden" / "fragile-normalized.json",
    "upgraded": ROOT / "tests" / "golden" / "upgraded-normalized.json",
    "simple-one-shot": ROOT / "tests" / "golden" / "simple-one-shot-normalized.json",
}


def normalize(name: str) -> dict:
    report = scan_project(TARGETS[name])
    rule_ids = sorted({issue.rule_id for issue in report.issues})
    return {
        "name": name,
        "readiness": report.readiness,
        "score": report.score,
        "rule_ids": rule_ids,
        "severity_counts": {
            "blocker": sum(1 for issue in report.issues if issue.severity == "blocker"),
            "warning": sum(1 for issue in report.issues if issue.severity == "warning"),
            "note": sum(1 for issue in report.issues if issue.severity == "note"),
        },
    }


def test_golden_reports_match_stable_fields():
    for name, golden_path in GOLDENS.items():
        expected = json.loads(golden_path.read_text(encoding="utf-8"))
        actual = normalize(name)

        assert actual == {key: expected[key] for key in actual}
        for rule_id in expected["absent_rule_ids"]:
            assert rule_id not in actual["rule_ids"]
