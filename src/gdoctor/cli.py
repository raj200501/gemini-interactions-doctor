from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from gdoctor.doctor import print_summary, run_demo, run_doctor
from gdoctor.patches import write_patch_files
from gdoctor.reports import render_html, render_markdown, render_plan
from gdoctor.rules import RULE_CATALOG
from gdoctor.scanner import scan_project

app = typer.Typer(
    add_completion=False,
    help="Gemini Interactions Doctor helps Gemini apps graduate from one-shot calls to reliable stateful, tool-using workflows.",
)
console = Console()


def _write_scan_outputs(report, out: Path, include_html: bool) -> list[Path]:
    written: list[Path] = []
    if out.suffix:
        markdown_path = out if out.suffix.lower() in {".md", ".markdown"} else out.with_suffix(".md")
    else:
        markdown_path = out.with_suffix(".md")
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    written.append(markdown_path)

    if include_html:
        html_path = out.with_suffix(".html") if out.suffix else out.with_suffix(".html")
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(render_html(report), encoding="utf-8")
        written.append(html_path)
    return written


@app.command()
def scan(
    target: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, readable=True),
    out: Path | None = typer.Option(None, "--out", "-o", help="Write a Markdown report, and HTML when --html is set."),
    html: bool = typer.Option(False, "--html/--no-html", help="Also write a self-contained HTML report."),
) -> None:
    """Scan a Gemini app for interaction-readiness issues."""
    report = scan_project(target)
    print_summary(report, console)
    if out:
        written = _write_scan_outputs(report, out, html)
        console.print()
        console.print("Reports written:")
        for path in written:
            console.print(f"  {path.as_posix()}")


@app.command()
def plan(
    target: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, readable=True),
    out: Path = typer.Option(..., "--out", "-o", help="Markdown file to write the migration plan to."),
) -> None:
    """Write a prioritized migration plan."""
    report = scan_project(target)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render_plan(report), encoding="utf-8")
    console.print(f"Migration plan written: {out.as_posix()}")


@app.command()
def patch(
    target: Path = typer.Argument(..., exists=True, file_okay=False, dir_okay=True, readable=True),
    out: Path = typer.Option(..., "--out", "-o", help="Directory where safe starter patch files should be written."),
) -> None:
    """Generate safe starter patch files without mutating the target app."""
    report = scan_project(target)
    written = write_patch_files(report, out)
    console.print("Patch suggestions written:")
    console.print(f"  {out.as_posix()}/")
    console.print()
    console.print("Generated files:")
    for path in written:
        console.print(f"  {path.as_posix()}")
    console.print()
    console.print("Review these files and copy the relevant parts into the target app when ready.")


@app.command()
def demo() -> None:
    """Run the offline 60-second demo."""
    run_demo(console)


@app.command()
def rules() -> None:
    """List all Gemini interaction-readiness rules."""
    table = Table(title="Gemini Interactions Doctor Rules")
    table.add_column("ID", no_wrap=True)
    table.add_column("Title")
    table.add_column("Severity", no_wrap=True)
    table.add_column("Category", no_wrap=True)
    table.add_column("Purpose")
    for rule in RULE_CATALOG:
        table.add_row(
            rule["rule_id"],
            rule["title"],
            rule["severity"],
            rule["category"],
            rule["purpose"],
        )
    console.print(table)


@app.command()
def doctor() -> None:
    """Check local gdoctor installation health."""
    raise typer.Exit(run_doctor(console))
