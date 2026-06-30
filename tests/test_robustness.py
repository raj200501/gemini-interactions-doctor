from __future__ import annotations

import json
from pathlib import Path

import pytest

from gdoctor.scanner import scan_project


ROOT = Path(__file__).resolve().parents[1]


def write_file(root: Path, relative: str, content: str) -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def test_random_text_files_do_not_crash(tmp_path):
    write_file(tmp_path, "notes.txt", "random words without Gemini SDK calls\n" * 10)

    report = scan_project(tmp_path)

    assert report.readiness == "READY"


def test_weird_unicode_does_not_crash(tmp_path):
    write_file(tmp_path, "prompt.md", "Gemini prompt draft with snowman ☃ and CJK 入口 text")

    report = scan_project(tmp_path)

    assert report.score >= 0


def test_empty_repo_has_clear_ready_result(tmp_path):
    report = scan_project(tmp_path)

    assert report.readiness == "READY"
    assert report.score == 100
    assert report.issues == []


def test_nested_folders_are_scanned(tmp_path):
    write_file(
        tmp_path,
        "services/support/app.py",
        "history=[]\ndef run(model):\n return model.generate_content(model='gemini-2.5-flash', contents='support workflow')\n",
    )

    rule_ids = {issue.rule_id for issue in scan_project(tmp_path).issues}

    assert "GD013" in rule_ids


def test_malformed_json_artifact_does_not_crash(tmp_path):
    write_file(tmp_path, "config/bad.json", "{ this is not valid json")
    write_file(tmp_path, "app.py", "def run(model):\n return model.generate_content(model='gemini-2.5-flash', contents='hi')\n")

    report = scan_project(tmp_path)

    assert report.score >= 0


def test_missing_target_has_clear_error(tmp_path):
    with pytest.raises(FileNotFoundError, match="Target path does not exist"):
        scan_project(tmp_path / "missing")


def test_schema_files_are_valid_json():
    for schema_path in (ROOT / "schemas").glob("*.json"):
        json.loads(schema_path.read_text(encoding="utf-8"))
