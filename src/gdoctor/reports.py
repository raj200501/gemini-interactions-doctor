from __future__ import annotations

from html import escape
from pathlib import Path

from jinja2 import Template

from gdoctor.models import Issue, ScanReport


def _target_name(report: ScanReport) -> str:
    return Path(report.target_path).name


def _issue_section(title: str, issues: list[Issue]) -> str:
    if not issues:
        return f"## {title}\n\nNone.\n"
    lines = [f"## {title}", ""]
    for issue in issues:
        lines.extend(
            [
                f"### {issue.rule_id}: {issue.title}",
                "",
                f"- Severity: `{issue.severity}`",
                f"- Category: `{issue.category}`",
                f"- Location: `{issue.file}:{issue.line_start}`",
                f"- Evidence: `{issue.evidence_snippet}`",
                f"- Why it matters: {issue.why_it_matters}",
                f"- Gemini relevance: {issue.gemini_relevance}",
                f"- Migration advice: {issue.migration_advice}",
                f"- Safe patch available: `{str(issue.safe_patch_available).lower()}`",
                f"- Confidence: `{issue.confidence:.2f}`",
                "",
            ]
        )
    return "\n".join(lines)


def render_markdown(report: ScanReport) -> str:
    blockers = report.blockers
    warnings = report.warnings
    notes = report.notes
    blocker_lines = "\n".join(f"{index}. {title}" for index, title in enumerate(report.migration_blockers, start=1)) or "None."
    patch_lines = "\n".join(f"- `{path}`" for path in report.suggested_patch_files) or "- No starter patch files recommended."
    next_steps = "\n".join(f"- {step}" for step in report.next_steps)
    guarantees = "\n".join(f"- {item}" for item in report.what_the_tool_does_not_guarantee)

    return f"""# Gemini Interactions Doctor Readiness Report

Readiness report for `{_target_name(report)}`

- Target: `{report.target_path}`
- Scan time: `{report.scan_time}`
- Readiness: `{report.readiness}`
- Score: `{report.score} / 100`

## Summary

Gemini Interactions Doctor checks whether this Gemini app harness appears ready to support state, tools, structured outputs, traceability, and iteration.

## Migration Blockers

{blocker_lines}

## Patch Suggestions

{patch_lines}

{_issue_section("Warnings", warnings)}

{_issue_section("Evidence", blockers + notes)}

## Generated Files

Run:

```bash
gdoctor patch {report.target_path} --out patches/{_target_name(report)}
```

## Next Steps

{next_steps}

## What This Does Not Guarantee

{guarantees}
"""


HTML_TEMPLATE = Template(
    """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Gemini Interactions Doctor - {{ target }}</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #182026;
      --muted: #5a6570;
      --line: #d9dee3;
      --panel: #ffffff;
      --soft: #f5f7f8;
      --accent: #0f766e;
      --danger: #b42318;
      --warn: #b7791f;
      --ok: #166534;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--ink);
      background: #f7f8fa;
      line-height: 1.5;
    }
    header {
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }
    .wrap {
      width: min(1120px, calc(100vw - 40px));
      margin: 0 auto;
    }
    .hero {
      min-height: 420px;
      display: grid;
      align-content: center;
      gap: 24px;
      padding: 48px 0 38px;
    }
    .eyebrow {
      margin: 0;
      color: var(--accent);
      font-weight: 700;
      letter-spacing: 0;
      text-transform: uppercase;
      font-size: 13px;
    }
    h1 {
      margin: 0;
      font-size: clamp(34px, 5vw, 64px);
      line-height: 1.02;
      letter-spacing: 0;
    }
    .subtitle {
      margin: 0;
      max-width: 780px;
      color: var(--muted);
      font-size: 18px;
    }
    .summary-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
    }
    .metric {
      background: var(--soft);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }
    .metric-label {
      margin: 0 0 6px;
      color: var(--muted);
      font-size: 13px;
    }
    .metric-value {
      margin: 0;
      font-weight: 800;
      font-size: 22px;
      overflow-wrap: anywhere;
    }
    main {
      padding: 34px 0 64px;
    }
    section {
      margin: 0 0 34px;
    }
    h2 {
      margin: 0 0 14px;
      font-size: 24px;
      letter-spacing: 0;
    }
    .issue-list {
      display: grid;
      gap: 12px;
    }
    .issue {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }
    .issue-head {
      display: flex;
      justify-content: space-between;
      gap: 14px;
      align-items: flex-start;
    }
    .issue h3 {
      margin: 0 0 8px;
      font-size: 18px;
    }
    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 28px;
      border-radius: 999px;
      padding: 4px 10px;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      white-space: nowrap;
      border: 1px solid var(--line);
    }
    .blocker { color: var(--danger); background: #fff1f0; border-color: #ffd1cd; }
    .warning { color: var(--warn); background: #fff8e8; border-color: #f5dfad; }
    .note { color: var(--accent); background: #e9fbf8; border-color: #bfe9e2; }
    code {
      background: var(--soft);
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 2px 5px;
      overflow-wrap: anywhere;
    }
    .evidence {
      margin: 12px 0;
      padding: 12px;
      background: #111827;
      color: #f9fafb;
      border-radius: 8px;
      overflow-wrap: anywhere;
    }
    ul, ol { padding-left: 22px; }
    .cols {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 18px;
    }
    .panel {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }
    footer {
      color: var(--muted);
      border-top: 1px solid var(--line);
      padding: 24px 0;
      background: var(--panel);
    }
    @media (max-width: 820px) {
      .summary-grid, .cols { grid-template-columns: 1fr; }
      .wrap { width: min(100vw - 28px, 1120px); }
      .issue-head { display: block; }
      .badge { margin-top: 8px; }
    }
  </style>
</head>
<body>
  <header>
    <div class="wrap hero">
      <div>
        <p class="eyebrow">Gemini Interactions Doctor</p>
        <h1>Readiness report for {{ target }}</h1>
      </div>
      <p class="subtitle">A local scan of Gemini harness patterns for state, tools, structured outputs, traceability, grounding, and tests.</p>
      <div class="summary-grid">
        <div class="metric">
          <p class="metric-label">Readiness</p>
          <p class="metric-value">{{ report.readiness }}</p>
        </div>
        <div class="metric">
          <p class="metric-label">Score</p>
          <p class="metric-value">{{ report.score }} / 100</p>
        </div>
        <div class="metric">
          <p class="metric-label">Migration blockers</p>
          <p class="metric-value">{{ report.blockers|length }}</p>
        </div>
        <div class="metric">
          <p class="metric-label">Warnings</p>
          <p class="metric-value">{{ report.warnings|length }}</p>
        </div>
      </div>
    </div>
  </header>
  <main class="wrap">
    <section>
      <h2>Summary</h2>
      <div class="panel">
        <p><strong>Target:</strong> <code>{{ report.target_path }}</code></p>
        <p><strong>Scan time:</strong> <code>{{ report.scan_time }}</code></p>
      </div>
    </section>

    <section>
      <h2>Migration Blockers</h2>
      {% if report.migration_blockers %}
      <ol>
        {% for blocker in report.migration_blockers %}
        <li>{{ blocker }}</li>
        {% endfor %}
      </ol>
      {% else %}
      <p>No blocker findings.</p>
      {% endif %}
    </section>

    <section>
      <h2>Warnings</h2>
      <div class="issue-list">
        {% for issue in report.warnings %}
        {{ render_issue(issue) }}
        {% else %}
        <div class="panel">No warning findings.</div>
        {% endfor %}
      </div>
    </section>

    <section>
      <h2>Evidence</h2>
      <div class="issue-list">
        {% for issue in report.blockers + report.notes %}
        {{ render_issue(issue) }}
        {% else %}
        <div class="panel">No blocker or note evidence.</div>
        {% endfor %}
      </div>
    </section>

    <section class="cols">
      <div class="panel">
        <h2>Patch Suggestions</h2>
        {% if report.suggested_patch_files %}
        <ul>
          {% for patch in report.suggested_patch_files %}
          <li><code>{{ patch }}</code></li>
          {% endfor %}
        </ul>
        {% else %}
        <p>No starter patch files recommended.</p>
        {% endif %}
      </div>
      <div class="panel">
        <h2>Generated Files</h2>
        <p>Run <code>gdoctor patch {{ report.target_path }} --out patches/{{ target }}</code> to write safe starter files.</p>
      </div>
    </section>

    <section class="cols">
      <div class="panel">
        <h2>Next Steps</h2>
        <ul>
          {% for step in report.next_steps %}
          <li>{{ step }}</li>
          {% endfor %}
        </ul>
      </div>
      <div class="panel">
        <h2>What This Does Not Guarantee</h2>
        <ul>
          {% for item in report.what_the_tool_does_not_guarantee %}
          <li>{{ item }}</li>
          {% endfor %}
        </ul>
      </div>
    </section>
  </main>
  <footer>
    <div class="wrap">Gemini Interactions Doctor is an external local tool and is not official Google tooling.</div>
  </footer>
</body>
</html>"""
)


def _render_issue_html(issue: Issue) -> str:
    return f"""<article class="issue">
  <div class="issue-head">
    <div>
      <h3>{escape(issue.rule_id)}: {escape(issue.title)}</h3>
      <p><code>{escape(issue.file)}:{issue.line_start}</code> · {escape(issue.category)}</p>
    </div>
    <span class="badge {escape(issue.severity)}">{escape(issue.severity)}</span>
  </div>
  <div class="evidence">{escape(issue.evidence_snippet)}</div>
  <p><strong>Why it matters:</strong> {escape(issue.why_it_matters)}</p>
  <p><strong>Gemini relevance:</strong> {escape(issue.gemini_relevance)}</p>
  <p><strong>Migration advice:</strong> {escape(issue.migration_advice)}</p>
  <p><strong>Safe patch available:</strong> <code>{str(issue.safe_patch_available).lower()}</code> · <strong>Confidence:</strong> <code>{issue.confidence:.2f}</code></p>
</article>"""


def render_html(report: ScanReport) -> str:
    return HTML_TEMPLATE.render(
        report=report,
        target=_target_name(report),
        render_issue=_render_issue_html,
    )


def render_plan(report: ScanReport) -> str:
    blocker_lines = "\n".join(f"{index}. {issue.title} (`{issue.rule_id}`)" for index, issue in enumerate(report.blockers, start=1)) or "None."
    warning_lines = "\n".join(f"- {issue.title} (`{issue.rule_id}`)" for issue in report.warnings) or "- None."
    patch_lines = "\n".join(f"- `{path}`" for path in report.suggested_patch_files) or "- No starter patch files recommended."
    next_steps = "\n".join(f"- {step}" for step in report.next_steps)

    return f"""# Gemini Interaction Migration Plan

Target: `{report.target_path}`
Readiness: `{report.readiness}`
Score: `{report.score} / 100`

## Priority 1: Migration Blockers

{blocker_lines}

## Priority 2: Warnings

{warning_lines}

## Safe Starter Patches

{patch_lines}

## Recommended Sequence

{next_steps}

## Reminder

This plan is a local migration aid. It does not guarantee production readiness, security, privacy, or compliance.
"""
