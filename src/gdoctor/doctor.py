from __future__ import annotations

from importlib import metadata
import os
from pathlib import Path
import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from gdoctor import __schema_version__, __version__
from gdoctor.patches import PATCH_TEMPLATE_NAMES, write_patch_files
from gdoctor.reports import GENERATED_STARTER_FILES
from gdoctor.scanner import scan_project


def repo_root() -> Path:
    cwd = Path.cwd()
    if (cwd / "examples").exists() and (cwd / "src" / "gdoctor").exists():
        return cwd
    package_root = Path(__file__).resolve().parents[2]
    return package_root


def display_path(path: str | Path) -> str:
    resolved = Path(path)
    for base in (Path.cwd(), repo_root()):
        try:
            return resolved.relative_to(base.resolve()).as_posix()
        except ValueError:
            continue
    return resolved.as_posix()


def print_summary(report, console: Console) -> None:
    console.print("[bold]Gemini Interactions Doctor[/bold]")
    console.print()
    console.print(f"Target: {display_path(report.target_path)}")
    console.print(f"Readiness: [bold]{report.readiness}[/bold]")
    console.print(f"Score: {report.score} / 100")
    console.print("Migration blockers:")
    if report.migration_blockers:
        for blocker in report.migration_blockers:
            console.print(f"  - {blocker}")
    else:
        console.print("  - none")
    if report.suggested_patch_files:
        console.print()
        console.print("Recommended patches:")
        for patch in report.suggested_patch_files:
            console.print(f"  - {patch}")


def run_demo(console: Console) -> None:
    root = repo_root()
    fragile_relative = Path("examples") / "fragile-gemini-app"
    upgraded_relative = Path("examples") / "upgraded-gemini-app"
    fragile = root / fragile_relative
    upgraded = root / upgraded_relative
    scan_fragile = fragile_relative if Path.cwd().resolve() == root.resolve() else fragile
    scan_upgraded = upgraded_relative if Path.cwd().resolve() == root.resolve() else upgraded

    fragile_report = scan_project(scan_fragile)
    print_summary(fragile_report, console)
    patch_dir = root / "patches" / "fragile-gemini-app"
    write_patch_files(fragile_report, patch_dir)
    console.print()
    console.print("Patch suggestions written:")
    console.print(f"  {patch_dir.relative_to(root).as_posix()}/")

    upgraded_report = scan_project(scan_upgraded)
    console.print()
    console.print("[bold]Fixed example[/bold]")
    console.print(f"Target: {upgraded.relative_to(root).as_posix()}")
    console.print(f"Readiness: [bold]{upgraded_report.readiness}[/bold]")
    console.print(f"Score: {upgraded_report.score} / 100")


def run_doctor(console: Console) -> int:
    root = repo_root()
    table = Table(title="gdoctor doctor")
    table.add_column("Check")
    table.add_column("Result")

    table.add_row("gdoctor version", __version__)
    table.add_row("schema version", __schema_version__)
    table.add_row("Python", sys.version.split()[0])
    for dependency in ["typer", "rich", "pydantic", "jinja2", "pytest"]:
        try:
            version = metadata.version(dependency)
        except metadata.PackageNotFoundError:
            version = "missing"
        table.add_row(dependency, version)

    fragile = root / "examples" / "fragile-gemini-app"
    upgraded = root / "examples" / "upgraded-gemini-app"
    table.add_row("fragile example", "present" if fragile.exists() else "missing")
    table.add_row("upgraded example", "present" if upgraded.exists() else "missing")
    table.add_row("report templates", "present" if GENERATED_STARTER_FILES else "missing")
    table.add_row("patch templates", f"{len(PATCH_TEMPLATE_NAMES)} available")
    table.add_row("Gemini API key", "present" if os.getenv("GEMINI_API_KEY") else "not present")

    console.print(table)
    if fragile.exists() and upgraded.exists():
        fragile_report = scan_project(fragile)
        upgraded_report = scan_project(upgraded)
        console.print(
            Panel(
                f"fragile: {fragile_report.readiness} ({fragile_report.score}/100)\n"
                f"upgraded: {upgraded_report.readiness} ({upgraded_report.score}/100)",
                title="Example scan health",
            )
        )
        return 0

    console.print("[red]Doctor status: missing example projects.[/red]")
    return 1
