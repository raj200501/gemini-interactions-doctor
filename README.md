# Gemini Interactions Doctor

Gemini Interactions Doctor is a local readiness checker for Gemini apps moving from quick prototypes to stateful, tool-using workflows. It scans a repo for fragile harness patterns - one-shot calls used for multi-step flows, manual state strings, vague tool schemas, side-effecting tools without machine-readable approval, brittle structured-output parsing, missing trace events, unsupported grounding claims, and missing smoke tests - then produces a migration plan and safe starter patches.

One-line positioning:

> Gemini Interactions Doctor helps Gemini apps graduate from one-shot calls to reliable stateful, tool-using workflows.

## What Is Gemini Interactions Doctor?

Gemini Interactions Doctor is an external local developer tool for Gemini and AI Studio builders moving from prototype to maintainable Gemini workflow.

It looks at the harness around the Gemini call:

- how state is represented
- how function/tool calls are described
- how side effects are approved
- how structured outputs are validated
- how tool calls and results are traced
- how grounding or sources are represented
- how primary AI paths are smoke-tested or replayed

It is not a generic linter, benchmark, multi-model framework, or official Google tool.

## Why This Exists

Many Gemini prototypes start as a single prompt and one `generateContent` or `generate_content` call. That is useful for learning and fast demos. The trouble starts when the same harness begins handling previous turns, tools, support tickets, research steps, structured JSON, citations, approval flows, and tests.

Interactions Doctor focuses on that migration point:

```text
quick Gemini prototype -> maintainable stateful Gemini workflow
```

It gives builders evidence-backed findings, a migration order, and starter files they can adapt locally.

## 60-Second Demo

```bash
python -m pip install -e .
gdoctor demo
```

The demo scans `examples/fragile-gemini-app`, writes starter patches, then scans `examples/upgraded-gemini-app`.

Expected shape:

```text
Gemini Interactions Doctor

Target: examples/fragile-gemini-app
Readiness: NOT_READY
Score: 0 / 100
Migration blockers:
  - one-shot model call used for multi-turn workflow
  - destructive tool lacks approval boundary
  - freeform output parsed as JSON
  - no trace events for tool calls
  - no primary AI smoke test
  - simple model call used where structured interaction state is needed
  - no structured interaction/event model
  - tool result is not represented separately from model text
  - grounded answer path not represented as evidence object

Patch suggestions written:
  patches/fragile-gemini-app/

Fixed example
Target: examples/upgraded-gemini-app
Readiness: READY
Score: 100 / 100
```

## Install

From a fresh clone:

```bash
git clone https://github.com/raj200501/gemini-interactions-doctor.git
cd gemini-interactions-doctor
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
make verify
```

For development:

```bash
python -m pip install -e ".[dev]"
python -m pytest
make verify
```

## Usage

```bash
gdoctor scan ./examples/fragile-gemini-app
gdoctor scan ./examples/fragile-gemini-app --out reports/fragile --html
gdoctor scan ./examples/fragile-gemini-app --verbose
gdoctor scan ./examples/upgraded-gemini-app --strict --quiet
gdoctor plan ./examples/fragile-gemini-app --out reports/fragile-plan.md
gdoctor patch ./examples/fragile-gemini-app --out patches/fragile
gdoctor scan ./examples/upgraded-gemini-app --out reports/upgraded --html
gdoctor rules
gdoctor version
gdoctor doctor
gdoctor demo
```

## Example Report

The HTML report opens with:

```text
Gemini Interactions Doctor
Readiness report for fragile-gemini-app

Readiness: NOT_READY
Score: 0 / 100

Top migration blockers:
1. one-shot model call used for multi-turn workflow
2. destructive tool lacks approval boundary
3. freeform output parsed as JSON
4. no trace events for tool calls
5. no primary AI smoke test
```

Markdown reports are designed to paste into a GitHub issue or PR description.

## What It Checks

`gdoctor rules` lists every rule with id, title, severity, category, and purpose.

Current checks:

- `GD001` one-shot model call used for multi-turn workflow
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
- `GD013` simple model call used where structured interaction state is needed
- `GD014` no structured interaction/event model
- `GD015` tool result is not represented separately from model text
- `GD016` no replayable test case format
- `GD017` grounded answer path not represented as evidence object
- `GD018` approval boundary not machine-readable

## Why This Is Not Just A Linter

Linters usually catch local code style or static errors. Interactions Doctor looks for harness-readiness patterns: whether state, tools, outputs, evidence, and traces are represented in a way that a Gemini app can be debugged, replayed, and improved.

The core question is not "Is this line valid Python or TypeScript?" It is "Can this Gemini workflow survive tools, state, retries, evidence, and tests?"

## Credibility And Limitations

Interactions Doctor checks local source files and docs for common Gemini harness-readiness signals: ad hoc one-shot calls in stateful workflows, brittle manual state strings, vague or risky tool declarations, freeform JSON parsing, missing trace events, unsupported grounding claims, absent replay/smoke fixtures, and missing project-specific AI instructions.

It does not execute the app, call Gemini, inspect private services, evaluate answer quality, verify business logic, or review security/privacy/legal posture. The generated patch files are starter artifacts for review, not automatic rewrites.

False positives can happen when a repo uses names the scanner does not recognize, stores structured state in generated code, documents approval boundaries outside scanned files, or validates responses through framework conventions that are not visible statically.

False negatives can happen when risky behavior is hidden behind wrappers, dynamic imports, metaprogramming, remote configuration, prompts stored outside the repo, or runtime-only tool definitions.

Most findings are static heuristics. Replayable JSONL fixtures and smoke tests are generated as local starting points, but this tool does not run a live interaction replay by default.

Production-grade use would need language-aware parsers, framework profiles, runtime traces, human review of side effects and data access, real regression suites, and organization-specific policy checks.

This is not official Google tooling, is not affiliated with Google, uses only public/local artifacts, and does not guarantee safety, security, correctness, compliance, or production readiness.

## Patch Generation

`gdoctor patch` writes starter files into the output directory and does not mutate the scanned app by default.

Generated files:

- `.env.example`
- `AGENTS.md`
- `tests/test_ai_smoke.py`
- `observability/interaction_event_schema.json`
- `observability/trace_schema.json`
- `evals/sample_interaction_regression.jsonl`
- `prompts/structured_output_prompt.md`
- `prompts/external_content_boundary.md`
- `tools/approval_boundary_example.json`
- `MIGRATION_PLAN.md`
- `README.patch-notes.md`

These are safe starting points, not automatic rewrites.

## Recommended Migration Order

1. Move from brittle string prompts to structured messages/events.
2. Make tool calls and tool results first-class objects.
3. Add machine-readable approval boundaries for side-effecting tools.
4. Add structured output validation.
5. Add trace events and run IDs.
6. Add one replayable smoke/regression test.
7. Tighten grounding/evidence claims.

## How This Relates To Gemini / AI Studio

Interactions Doctor is for builders using Gemini APIs or graduating AI Studio-style prototypes into local app code. It looks for harness patterns that commonly appear when a prototype starts handling turns, tools, structured responses, side effects, and evidence.

It does not require internal APIs. It does not know private AI Studio roadmap details. It is an external local tool that uses static heuristics and templates.

## How This Differs From ShipCheck And Flight Recorder

- **ShipCheck** asks: "Should I share or deploy this Gemini app yet?"
- **Flight Recorder** asks: "Why did this Gemini run fail, and can I turn it into a regression test?"
- **Interactions Doctor** asks: "Is this Gemini app harness wired for state, tools, tests, and iteration?"

In a three-tool suite:

- `ai-studio-shipcheck` is about share/deploy readiness.
- `gemini-flight-recorder` is about debugging a run and turning failure into regression coverage.
- `gemini-interactions-doctor` is about harness readiness before the workflow grows brittle.

## What This Does Not Do

- Not official Google tooling.
- Not affiliated with Google.
- Does not guarantee production readiness.
- Does not replace security review.
- Does not require internal APIs.
- Does not know private AI Studio roadmap details.
- Uses static heuristics and safe patch templates.
- Does not automatically rewrite application logic.

## Design Principles

- Migration over criticism.
- Evidence before advice.
- Safe patches only.
- Gemini-specific, not generic LLM lint.
- Local-first and offline-demoable.
- Helps builders graduate prototypes into maintainable apps.

## Development

```bash
make test
make demo
make reports
make verify
```

The verification flow runs schema loading, tests, demo, report generation, patch generation, rules, version, and local installation health checks.

## Roadmap

- More language-specific Gemini SDK detectors.
- Optional SARIF output.
- Framework-aware project profiles.
- Safer codemod previews for trivial harness upgrades.
- Report comparison across migration iterations.
- Import/export from failed run traces produced by companion tooling.

## Disclaimer

Gemini Interactions Doctor is an independent developer-experience artifact. It is not official Google tooling, is not affiliated with Google, and does not guarantee that an application is ready for production, sharing, or deployment.
