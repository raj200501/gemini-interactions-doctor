from __future__ import annotations

import json
from pathlib import Path

from gdoctor.patches import write_patch_files
from gdoctor.reports import render_html, render_markdown, render_plan
from gdoctor.scanner import scan_project


ROOT = Path(__file__).resolve().parents[1]


def test_markdown_and_html_report_rendering():
    report = scan_project(ROOT / "examples" / "fragile-gemini-app")
    markdown = render_markdown(report)
    html = render_html(report)
    plan = render_plan(report)

    assert "Gemini Interactions Doctor Readiness Report" in markdown
    assert "Migration Blockers" in markdown
    assert "Recommended Migration Order" in markdown
    assert "<!doctype html>" in html
    assert "Readiness report for fragile-gemini-app" in html
    assert "Top Migration Blockers" in html
    assert "Gemini Interaction Migration Plan" in plan
    assert "What Not To Overbuild" in plan


def test_patch_generation_writes_safe_starter_files(tmp_path):
    report = scan_project(ROOT / "examples" / "fragile-gemini-app")
    written = write_patch_files(report, tmp_path / "patches")
    relative = {path.relative_to(tmp_path / "patches").as_posix() for path in written}

    assert ".env.example" in relative
    assert "AGENTS.md" in relative
    assert "tests/test_ai_smoke.py" in relative
    assert "observability/interaction_event_schema.json" in relative
    assert "observability/trace_schema.json" in relative
    assert "evals/sample_interaction_regression.jsonl" in relative
    assert "prompts/structured_output_prompt.md" in relative
    assert "prompts/external_content_boundary.md" in relative
    assert "tools/approval_boundary_example.json" in relative
    assert "MIGRATION_PLAN.md" in relative

    trace_schema = json.loads((tmp_path / "patches" / "observability" / "trace_schema.json").read_text())
    assert trace_schema["title"] == "Gemini interaction trace event"
