# Gemini Interactions Doctor Spec

Schema version: `0.2.0`

Gemini Interactions Doctor is a static local readiness checker for Gemini app harnesses. Its core question is:

> Is this Gemini app harness wired for state, tools, tests, traces, and iteration?

## Input Assumptions

- The input is a local directory.
- The scanner reads text-like source, prompt, config, doc, JSON, JSONL, YAML, and HTML files.
- The scanner skips common dependency/build/cache directories.
- The scanner does not execute project code or call Gemini.
- The scanner treats findings as readiness signals, not final judgments.

## Report Schema

A report contains:

- `target_path`: absolute scanned path.
- `scan_time`: ISO-8601 UTC timestamp.
- `readiness`: `READY`, `READY_WITH_CAUTION`, or `NOT_READY`.
- `score`: integer from `0` to `100`.
- `issues`: list of findings.
- `migration_blockers`: blocker titles.
- `suggested_patch_files`: starter patch paths.
- `next_steps`: ordered remediation guidance.
- `what_the_tool_does_not_guarantee`: explicit scope limits.

Machine-readable schema: `schemas/report.schema.json`.

## Finding Schema

Each finding contains:

- `rule_id`
- `title`
- `severity`
- `category`
- `file`
- `line_start`
- `line_end`
- `evidence_snippet`
- `why_it_matters`
- `gemini_relevance`
- `migration_advice`
- `safe_patch_available`
- `confidence`

Machine-readable schema: `schemas/finding.schema.json`.

## Scoring

Score starts at `100`.

- `blocker`: minus `20`
- `warning`: minus `8`
- `note`: minus `3`

Readiness:

- `NOT_READY`: any blocker or score below `70`
- `READY_WITH_CAUTION`: no blockers and score from `70` to `89`
- `READY`: no blockers and score at least `90`

## Example JSON

```json
{
  "target_path": "/repo/examples/fragile-gemini-app",
  "scan_time": "2026-06-30T18:00:00+00:00",
  "readiness": "NOT_READY",
  "score": 0,
  "issues": [
    {
      "rule_id": "GD014",
      "title": "no structured interaction/event model",
      "severity": "blocker",
      "category": "state",
      "file": "app.py",
      "line_start": 12,
      "line_end": 12,
      "evidence_snippet": "history = []",
      "why_it_matters": "Stateful Gemini apps are hard to debug when events are not first-class objects.",
      "gemini_relevance": "A structured event model supports replay, traces, smoke tests, and AI Studio prototype migration.",
      "migration_advice": "Add an InteractionEvent schema with run_id, event_id, role/type, content, and tool metadata.",
      "safe_patch_available": true,
      "confidence": 0.84
    }
  ],
  "migration_blockers": ["no structured interaction/event model"],
  "suggested_patch_files": ["observability/interaction_event_schema.json"],
  "next_steps": ["Move from brittle string prompts to structured messages and interaction events."],
  "what_the_tool_does_not_guarantee": ["It does not execute or call Gemini APIs."]
}
```

## Interaction Event Shape

The generated interaction event starter gives builders a local shape for:

- `message`
- `model_request`
- `model_response`
- `tool_call`
- `tool_result`
- `approval`
- `validation`
- `error`

Machine-readable schema: `schemas/interaction_event.schema.json`.

## Versioning Strategy

- The package version and schema version are reported by `gdoctor version`.
- Schema changes that add optional fields can remain within a minor release.
- Required-field changes should bump the schema version.
- Golden tests compare stable fields and intentionally ignore timestamps and absolute paths.

## Compatibility Notes

- Python support target: 3.10, 3.11, and 3.12.
- Reports preserve relative CLI target paths when the scan is invoked with a relative path.
- `GDOCTOR_SCAN_TIME` can pin the timestamp for committed sample reports and CI fixtures.
- The scanner uses static heuristics and does not require a Gemini API key.

## Limitations

This tool can miss dynamically generated prompts, tool schemas loaded from services, framework-level validation hidden behind wrappers, and runtime-only approval logic. It can also flag patterns that are mitigated elsewhere in the app. Production-grade use would need runtime traces, language-aware parsing, organization-specific review, and real regression suites.
