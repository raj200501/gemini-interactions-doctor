from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from gdoctor.cli import app


ROOT = Path(__file__).resolve().parents[1]
runner = CliRunner()


def test_cli_demo(monkeypatch):
    monkeypatch.chdir(ROOT)
    result = runner.invoke(app, ["demo"])

    assert result.exit_code == 0
    assert "Gemini Interactions Doctor" in result.output
    assert "Readiness: NOT_READY" in result.output
    assert "Fixed example" in result.output


def test_cli_doctor(monkeypatch):
    monkeypatch.chdir(ROOT)
    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "gdoctor doctor" in result.output
    assert "Example scan health" in result.output
    assert "Gemini API key" in result.output


def test_cli_rules():
    result = runner.invoke(app, ["rules"])

    assert result.exit_code == 0
    assert "Gemini Interactions Doctor Rules" in result.output
    assert "GD018" in result.output


def test_cli_scan_writes_markdown_and_html(tmp_path):
    target = ROOT / "examples" / "fragile-gemini-app"
    out = tmp_path / "fragile"
    result = runner.invoke(app, ["scan", target.as_posix(), "--out", out.as_posix(), "--html"])

    assert result.exit_code == 0
    assert (tmp_path / "fragile.md").exists()
    assert (tmp_path / "fragile.html").exists()


def test_cli_plan_and_patch(tmp_path):
    target = ROOT / "examples" / "fragile-gemini-app"
    plan_out = tmp_path / "plan.md"
    patch_out = tmp_path / "patches"

    plan_result = runner.invoke(app, ["plan", target.as_posix(), "--out", plan_out.as_posix()])
    patch_result = runner.invoke(app, ["patch", target.as_posix(), "--out", patch_out.as_posix()])

    assert plan_result.exit_code == 0
    assert patch_result.exit_code == 0
    assert plan_out.exists()
    assert (patch_out / "AGENTS.md").exists()
    assert (patch_out / "observability" / "interaction_event_schema.json").exists()
    assert (patch_out / "evals" / "sample_interaction_regression.jsonl").exists()
