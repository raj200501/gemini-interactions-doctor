# Evaluation

This evaluation is a development fixture suite, not a population benchmark. It is designed to catch regressions and demonstrate behavior on representative cases.

## Suite Size

- Core examples: 2
- Adversarial fixtures: 8
- Golden reports: 3
- Rule coverage: 18 rules

## Fixture Summary

| Fixture | Expected Shape | What It Tests |
| --- | --- | --- |
| `examples/fragile-gemini-app` | `NOT_READY` | Prototype harness with state, tools, brittle JSON, missing traces/tests/evidence. |
| `examples/upgraded-gemini-app` | `READY` or `READY_WITH_CAUTION` | Structured event model, scoped tools, validation, evidence, traces, tests. |
| `adversarial/obvious-bad` | `NOT_READY` | Compact bad case that should trigger state/tool/output findings. |
| `adversarial/simple-one-shot-pass` | `READY` | One prompt to one response should not be punished as workflow state. |
| `adversarial/near-miss-structured-messages` | No GD002/GD013/GD014 | Structured message arrays should not look like brittle history strings. |
| `adversarial/read-only-tool` | No GD003/GD018 | Safe read-only tools should not trigger destructive-tool rules. |
| `adversarial/risky-prose-approval` | GD018 | Prose approval without machine-readable approval fields. |
| `adversarial/evidence-object-pass` | No GD017 | Grounded claims backed by evidence/sources objects. |
| `adversarial/structured-safe-pattern` | `READY` or caution | Full safe structured interaction fixture. |
| `adversarial/unusual-layout` | Scanned | Nested app layout still produces findings. |

## Current Pass Criteria

- Fragile app is `NOT_READY`.
- Upgraded app is `READY` or `READY_WITH_CAUTION`.
- Simple one-shot app does not trigger GD013 or GD014.
- Safe read-only tool does not trigger destructive-tool warnings.
- Machine-readable approval suppresses GD018.
- Evidence objects suppress GD017.
- Validated JSON parsing suppresses GD006.
- Delimited untrusted content suppresses GD011.

## Known Limits

This suite is small and curated. It does not measure general scanner accuracy across the Gemini ecosystem, does not execute apps, and does not evaluate answer quality.
