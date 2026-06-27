# Gemini Interactions Doctor

Gemini Interactions Doctor is a local readiness checker for Gemini apps moving from simple model calls to stateful, tool-using workflows. It scans a repo for fragile harness patterns - manual chat history, vague tool schemas, risky side effects, brittle structured-output parsing, missing trace events, unsupported grounding claims, and missing smoke tests - then produces a migration plan and safe starter patches.

## What Is Gemini Interactions Doctor?

Gemini Interactions Doctor helps Gemini apps graduate from one-shot calls to reliable stateful, tool-using workflows.

It is a focused local analyzer for Gemini application harnesses. It reads source files, finds evidence-backed interaction risks, and emits:

- an Interactions/API readiness report
- a prioritized migration plan
- safe patch suggestions
- optional starter files for logging, structured outputs, AI instructions, and smoke tests

This is not a generic linter, a benchmark, a multi-model framework, or official Google tooling.

## Why This Exists

Many Gemini prototypes start with one prompt and one `generateContent` or `generate_content` call. That is fine for early experiments. The friction appears when the app grows into a workflow with state, tools, structured outputs, grounding claims, side effects, logs, and tests.

Interactions Doctor focuses on the harness around the model call: the part that determines whether a prototype can support iteration without becoming brittle.

## 60-Second Demo

```bash
gdoctor demo
```

The demo scans `examples/fragile-gemini-app`, reports `NOT_READY`, writes safe patch starter files under `patches/fragile-gemini-app`, and then scans `examples/upgraded-gemini-app` to show a safer shape.

Expected terminal shape:

```text
Gemini Interactions Doctor

Target: examples/fragile-gemini-app
Readiness: NOT_READY
Migration blockers:
  - one-shot model call used for multi-turn workflow
  - destructive tool lacks approval boundary
  - freeform output parsed as JSON
  - no trace events for tool calls
  - no primary AI smoke test

Patch suggestions written:
  patches/fragile-gemini-app/
```

## Install

From a fresh clone:

```bash
python -m pip install -e .
```

For development:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

## Usage

```bash
gdoctor scan ./examples/fragile-gemini-app
gdoctor scan ./examples/fragile-gemini-app --out reports/fragile --html
gdoctor plan ./examples/fragile-gemini-app --out reports/fragile-plan.md
gdoctor patch ./examples/fragile-gemini-app --out patches/fragile
gdoctor scan ./examples/upgraded-gemini-app --out reports/upgraded --html
gdoctor demo
gdoctor doctor
```

## Example Report

```text
Gemini Interactions Doctor
Readiness report for fragile-gemini-app

Readiness: NOT_READY
Score: 0 / 100

Migration blockers:
1. one-shot model call used for multi-turn workflow
2. destructive tool lacks approval boundary
3. freeform output parsed as JSON
4. no trace events for tool calls
5. no primary AI smoke test
```

Markdown reports are designed to paste into a GitHub issue or PR description. HTML reports are self-contained and require no external assets.

## What It Checks

Interactions Doctor implements 12 Gemini interaction-readiness rules:

- `GD001` one-shot call used for multi-turn or agentic workflow
- `GD002` manual chat history is fragile
- `GD003` destructive tool lacks approval boundary
- `GD004` tool schema too vague
- `GD005` broad data access tool
- `GD006` freeform output parsed as JSON
- `GD007` missing structured output contract
- `GD008` no trace events for tool calls
- `GD009` no primary AI smoke test
- `GD010` grounding claim without grounding path
- `GD011` prompt injection boundary missing
- `GD012` missing `AGENTS.md` or project-specific AI instructions

## Patch Generation

`gdoctor patch` writes starter files into the output directory and does not mutate the scanned app by default.

Generated files can include:

- `.env.example`
- `AGENTS.md`
- `tests/test_ai_smoke.py`
- `observability/trace_schema.json`
- `prompts/structured_output_prompt.md`
- `prompts/external_content_boundary.md`
- `tools/approval_boundary_example.json`
- `MIGRATION_PLAN.md`

The generated files are intentionally conservative. They are meant to give a builder a safe starting point, not silently rewrite app logic.

## How This Relates To Gemini / AI Studio

Interactions Doctor is for builders using Gemini APIs or graduating AI Studio-style prototypes into local app code. It looks for harness patterns that commonly appear when a prototype starts handling turns, tools, structured responses, and evidence.

It is an external local tool. It does not claim to be endorsed by Google, and it does not replace Gemini API documentation or production review.

## How This Is Different From ShipCheck

ShipCheck asks: "Should I share or deploy this Gemini app yet?"

Interactions Doctor asks: "Is my Gemini app harness wired in a way that can support state, tools, tests, and iteration?"

That distinction matters. Interactions Doctor is about migration readiness and developer workflow, not broad launch approval.

## What It Does Not Do

- It does not call Gemini.
- It does not send source code to a remote service.
- It does not guarantee production readiness.
- It does not automatically rewrite application logic.
- It does not prove that tools are safe.
- It does not replace security, privacy, legal, or reliability review.

## Design Principles

- Migration over criticism.
- Evidence before advice.
- Safe patches only.
- Gemini-specific, not generic LLM lint.
- Local-first and offline-demoable.
- Helps builders graduate prototypes into maintainable apps.

## Roadmap

- More language-specific Gemini SDK detectors.
- Optional SARIF output.
- Framework-aware project profiles.
- Safer codemod previews for trivial harness upgrades.
- Report comparison across migration iterations.

## Disclaimer

Gemini Interactions Doctor is an independent developer-experience artifact. It is not official Google tooling and does not guarantee that an application is ready for production, sharing, or deployment.
