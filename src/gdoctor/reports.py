from __future__ import annotations

from html import escape
from pathlib import Path

from jinja2 import Template

from gdoctor.models import Issue, ScanReport

GENERATED_STARTER_FILES = [
    ".env.example",
    "AGENTS.md",
    "tests/test_ai_smoke.py",
    "observability/interaction_event_schema.json",
    "observability/trace_schema.json",
    "evals/sample_interaction_regression.jsonl",
    "prompts/structured_output_prompt.md",
    "prompts/external_content_boundary.md",
    "tools/approval_boundary_example.json",
    "MIGRATION_PLAN.md",
]

RECOMMENDED_MIGRATION_ORDER = [
    "Move from brittle string prompts to structured messages/events.",
    "Make tool calls and tool results first-class objects.",
    "Add machine-readable approval boundaries for side-effecting tools.",
    "Add structured output validation.",
    "Add trace events and run IDs.",
    "Add one replayable smoke/regression test.",
    "Tighten grounding/evidence claims.",
]

TOP_BLOCKER_LABELS = {
    "GD013": "Stateful workflow is wired through one-shot model calls.",
    "GD014": "Tool calls/results are not represented as structured events.",
    "GD015": "Tool calls/results are not represented as structured events.",
    "GD003": "Destructive tool approval is not machine-readable.",
    "GD018": "Destructive tool approval is not machine-readable.",
    "GD006": "Model output is parsed as JSON without validation.",
    "GD017": "Grounded answer claims lack an evidence object.",
    "GD008": "Tool calls are missing trace events.",
    "GD009": "Primary Gemini workflow is missing a smoke test.",
}

TOP_BLOCKER_ORDER = ["GD013", "GD014", "GD015", "GD003", "GD018", "GD006", "GD017", "GD008", "GD009"]


def _target_name(report: ScanReport) -> str:
    return Path(report.target_path).name


def top_migration_blockers(report: ScanReport, limit: int = 5) -> list[str]:
    labels: list[str] = []
    issues_by_rule = {issue.rule_id: issue for issue in report.issues}
    for rule_id in TOP_BLOCKER_ORDER:
        issue = issues_by_rule.get(rule_id)
        if not issue:
            continue
        label = TOP_BLOCKER_LABELS.get(rule_id, issue.title)
        if label not in labels:
            labels.append(label)
        if len(labels) == limit:
            return labels
    for issue in report.blockers:
        label = TOP_BLOCKER_LABELS.get(issue.rule_id, issue.title)
        if label not in labels:
            labels.append(label)
        if len(labels) == limit:
            return labels
    return labels


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
    top_blocker_lines = "\n".join(f"{index}. {title}" for index, title in enumerate(top_migration_blockers(report), start=1)) or "None."
    patch_lines = "\n".join(f"- `{path}`" for path in report.suggested_patch_files) or "- No starter patch files recommended."
    generated_files = "\n".join(f"- `{path}`" for path in GENERATED_STARTER_FILES)
    migration_order = "\n".join(f"{index}. {step}" for index, step in enumerate(RECOMMENDED_MIGRATION_ORDER, start=1))
    next_steps = "\n".join(f"- {step}" for step in report.next_steps)
    guarantees = "\n".join(f"- {item}" for item in report.what_the_tool_does_not_guarantee)

    return f"""# Gemini Interactions Doctor Readiness Report

Readiness report for `{_target_name(report)}`

- Target: `{report.target_path}`
- Scan time: `{report.scan_time}`
- Readiness: `{report.readiness}`
- Score: `{report.score} / 100`

## Summary

Gemini Interactions Doctor checks whether this Gemini app harness appears ready to support stateful interactions, function/tool calling, structured outputs, traceability, evidence, and iteration.

## Readiness Scoring

Score starts at `100`.

- Blocker: `-20`
- Warning: `-8`
- Note: `-3`

Readiness is `NOT_READY` when any blocker exists or score is below `70`, `READY_WITH_CAUTION` from `70-89` with no blockers, and `READY` at `90+` with no blockers.

## Migration Blockers

{blocker_lines}

## Top Migration Blockers

{top_blocker_lines}

## Patch Suggestions

{patch_lines}

## Generated Starter Files

`gdoctor patch` writes these safe starters into the output directory without mutating the scanned app:

{generated_files}

## Recommended Migration Order

{migration_order}

{_issue_section("Warnings", warnings)}

{_issue_section("Evidence Snippets", blockers + notes)}

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
      <div class="panel">
        <h2>Top Migration Blockers</h2>
        {% if report.blockers %}
        <ol>
          {% for blocker in top_blockers %}
          <li>{{ blocker }}</li>
          {% endfor %}
        </ol>
        {% else %}
        <p>No blocker findings.</p>
        {% endif %}
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
      <h2>Readiness Scoring</h2>
      <div class="panel">
        <p>Score starts at <code>100</code>. Blockers subtract <code>20</code>, warnings subtract <code>8</code>, and notes subtract <code>3</code>.</p>
        <p><code>NOT_READY</code> means a blocker exists or score is below <code>70</code>. <code>READY_WITH_CAUTION</code> means no blockers and score from <code>70-89</code>. <code>READY</code> means no blockers and score is <code>90+</code>.</p>
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
      <h2>Evidence Snippets</h2>
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
        <ul>
          {% for file in generated_files %}
          <li><code>{{ file }}</code></li>
          {% endfor %}
        </ul>
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
        <h2>Recommended Migration Order</h2>
        <ol>
          {% for step in migration_order %}
          <li>{{ step }}</li>
          {% endfor %}
        </ol>
      </div>
    </section>

    <section>
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
        generated_files=GENERATED_STARTER_FILES,
        migration_order=RECOMMENDED_MIGRATION_ORDER,
        top_blockers=top_migration_blockers(report),
    )


def render_plan(report: ScanReport) -> str:
    blocker_lines = "\n".join(f"{index}. {issue.title} (`{issue.rule_id}`)" for index, issue in enumerate(report.blockers, start=1)) or "None."
    warning_lines = "\n".join(f"- {issue.title} (`{issue.rule_id}`)" for issue in report.warnings) or "- None."
    patch_lines = "\n".join(f"- `{path}`" for path in report.suggested_patch_files) or "- No starter patch files recommended."
    generated_files = "\n".join(f"- `{path}`" for path in GENERATED_STARTER_FILES)
    migration_order = "\n".join(f"{index}. {step}" for index, step in enumerate(RECOMMENDED_MIGRATION_ORDER, start=1))
    manual_work = "\n".join(f"- {step}" for step in report.next_steps)

    return f"""# Gemini Interaction Migration Plan

Target: `{report.target_path}`
Readiness: `{report.readiness}`
Score: `{report.score} / 100`

## Current Readiness

This app is `{report.readiness}` with a score of `{report.score} / 100`.

## Top Blockers

{blocker_lines}

## Warnings

{warning_lines}

## Generated Starter Files

`gdoctor patch` can generate these files without mutating the source app:

{generated_files}

## Recommended Migration Order

{migration_order}

## Suggested Patch Files For This Scan

{patch_lines}

## What To Do Manually

{manual_work}

## What Not To Overbuild

- Do not build a full eval platform before you have one replayable scenario.
- Do not rewrite the app before making state, tool calls, and tool results visible.
- Do not add production observability before defining the local trace event shape.
- Do not claim grounding unless evidence is represented as data.

## Reminder

This plan is a local migration aid. It does not guarantee production readiness, security, privacy, or compliance.
"""
