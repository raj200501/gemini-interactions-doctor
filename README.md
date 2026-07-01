# Gemini Interactions Doctor

Readiness checker for Gemini app harnesses moving from prototype to stateful, tool-using workflows.

Interactions Doctor scans for fragile harness patterns: state handling, tool schemas, approval boundaries, structured outputs, traces, grounding evidence, and smoke tests. It then writes a migration plan and safe starter patches.

```bash
gdoctor demo
```

```text
Target: examples/fragile-gemini-app
Readiness: NOT_READY
Score: 0 / 100
Migration blockers: 9
Patch suggestions: patches/fragile-gemini-app/

Fixed example
Target: examples/upgraded-gemini-app
Readiness: READY
Score: 100 / 100
```

## Proof Of Concept

| Signal | Checked-in evidence |
| --- | --- |
| Readiness rules | 18 deterministic rules across state, tools, structured output, observability, tests, grounding, and project instructions. |
| Fixtures | Fragile/upgraded Gemini app examples plus 8 adversarial harness fixtures. |
| Patch artifacts | Migration plans and starter files under `patches/`; scan and patch output do not mutate the target app by default. |
| Report artifacts | HTML and Markdown reports under `reports/`, with JSON schemas under `schemas/`. |
| Test surface | 54 collected pytest cases, plus CI on Python 3.10, 3.11, and 3.12. |
| Offline run | `gdoctor demo` scans the fragile fixture, writes patch suggestions, and compares against the upgraded fixture without a Gemini API key. |

## What It Checks

Interactions Doctor looks at the harness around the Gemini call, not just syntax. It checks whether state, tools, outputs, evidence, traces, and tests are represented in a way that a growing workflow can be debugged and improved.

Primary categories:

- state and history handling;
- tool schemas and side-effect approval boundaries;
- structured output contracts and parsing;
- trace events for model calls, tool calls, and tool results;
- grounding evidence objects rather than unsupported claims;
- smoke tests and replayable regression fixtures;
- project-specific AI instructions such as `AGENTS.md`.

Run `gdoctor rules` for the full rule list with ids, titles, severities, categories, and purpose.

## Why This Exists

Many Gemini prototypes begin as a single prompt and one model call. That is useful for learning and demos. The brittle point comes when the same harness starts carrying turns, tools, support tickets, structured JSON, citations, approval flows, and tests.

Interactions Doctor focuses on that migration point: quick Gemini prototype to maintainable stateful Gemini workflow.

## Why This Is Not Just A Linter

Linters catch local code style or static errors. Interactions Doctor looks for harness-readiness patterns: whether a Gemini workflow can survive state, tools, retries, evidence, and tests.

The core question is not "Is this line valid Python or TypeScript?" It is "Can this Gemini workflow be debugged, replayed, and improved when the interaction gets more complex?"

## Part Of A Small Gemini Builder Trust Loop

- **ShipCheck** asks: "Should I share or deploy this Gemini app yet?"
- **Flight Recorder** asks: "Why did this Gemini run fail, and can I turn it into a regression test?"
- **Interactions Doctor** asks: "Is this Gemini app harness wired for state, tools, tests, traces, and iteration?"

The tools are separate local utilities with related questions. This is not a company, platform, or claim of official Google affiliation.

## Credibility And Limitations

Interactions Doctor checks local source files and docs for common Gemini harness-readiness signals. It does not execute the app, call Gemini, inspect private services, evaluate answer quality, verify business logic, or review security/privacy/legal posture.

False positives can happen when a repo uses names the scanner does not recognize, stores structured state in generated code, documents approval boundaries outside scanned files, or validates responses through framework conventions that are not visible statically.

False negatives can happen when risky behavior is hidden behind wrappers, dynamic imports, metaprogramming, remote configuration, prompts stored outside the repo, or runtime-only tool definitions.

Generated patch files are starter artifacts for review. They are not automatic rewrites of application logic.

## Install

```bash
git clone https://github.com/raj200501/gemini-interactions-doctor.git
cd gemini-interactions-doctor
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Usage

```bash
gdoctor scan ./examples/fragile-gemini-app
gdoctor scan ./examples/fragile-gemini-app --out reports/fragile --html
gdoctor plan ./examples/fragile-gemini-app --out reports/fragile-plan.md
gdoctor patch ./examples/fragile-gemini-app --out patches/fragile
gdoctor scan ./examples/upgraded-gemini-app --strict --quiet
gdoctor rules
gdoctor doctor
gdoctor version
```

`gdoctor scan` writes readiness findings. `gdoctor plan` writes a migration plan. `gdoctor patch` writes starter files into the output directory and does not mutate the scanned app by default.

Generated starter files can include trace schemas, an interaction event schema, smoke tests, regression JSONL, structured-output prompt guidance, approval-boundary examples, `AGENTS.md`, and patch notes.

## Development

```bash
make verify
make test
make demo
make reports
```

The verification flow runs schema loading, tests, demo, report generation, patch generation, rules, version, and local installation health checks.

## Docs

- [Readiness report schema](docs/spec.md)
- [Failure modes](docs/failure_modes.md)
- [Evaluation notes](docs/evaluation.md)
- [Suite positioning](docs/suite.md)
- Machine-readable schemas in [schemas/](schemas/)

## Disclaimer

Gemini Interactions Doctor is an independent local developer tool. It is not affiliated with, endorsed by, or sponsored by Google. It does not guarantee security, correctness, factuality, compliance, policy alignment, or production readiness.
