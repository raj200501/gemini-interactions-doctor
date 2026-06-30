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


def test_cli_version():
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "gdoctor 0.2.0" in result.output
    assert "schema 0.2.0" in result.output


def test_scan_strict_exit_codes(monkeypatch):
    monkeypatch.chdir(ROOT)
    fragile = ROOT / "examples" / "fragile-gemini-app"
    upgraded = ROOT / "examples" / "upgraded-gemini-app"

    fragile_result = runner.invoke(app, ["scan", fragile.as_posix(), "--strict", "--quiet"])
    upgraded_result = runner.invoke(app, ["scan", upgraded.as_posix(), "--strict", "--quiet"])

    assert fragile_result.exit_code == 1
    assert upgraded_result.exit_code == 0
    assert upgraded_result.output == ""


def test_scan_verbose_prints_findings(monkeypatch):
    monkeypatch.chdir(ROOT)
    target = ROOT / "examples" / "fragile-gemini-app"
    result = runner.invoke(app, ["scan", target.as_posix(), "--verbose"])

    assert result.exit_code == 0
    assert "Findings" in result.output
    assert "GD013" in result.output


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
