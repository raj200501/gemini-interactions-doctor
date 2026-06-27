# Gemini Interaction Migration Plan

Target: `/Users/rajkashikar/Documents/Codex/2026-06-26/you-are-codex-working-inside-a/gemini-interactions-doctor/examples/fragile-gemini-app`
Readiness: `NOT_READY`
Score: `0 / 100`

## Current Readiness

This app is `NOT_READY` with a score of `0 / 100`.

## Top Blockers

1. one-shot model call used for multi-turn workflow (`GD001`)
2. destructive tool lacks approval boundary (`GD003`)
3. freeform output parsed as JSON (`GD006`)
4. no trace events for tool calls (`GD008`)
5. no primary AI smoke test (`GD009`)
6. simple model call used where structured interaction state is needed (`GD013`)
7. no structured interaction/event model (`GD014`)
8. tool result is not represented separately from model text (`GD015`)
9. grounded answer path not represented as evidence object (`GD017`)

## Warnings

- manual chat history is fragile (`GD002`)
- tool schema too vague (`GD004`)
- broad data access tool (`GD005`)
- grounding claim without grounding path (`GD010`)
- prompt injection boundary missing (`GD011`)
- missing AGENTS.md or project-specific AI instructions (`GD012`)
- no replayable test case format (`GD016`)
- approval boundary not machine-readable (`GD018`)

## Generated Starter Files

`gdoctor patch` can generate these files without mutating the source app:

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

## Recommended Migration Order

1. Move from brittle string prompts to structured messages/events.
2. Make tool calls and tool results first-class objects.
3. Add machine-readable approval boundaries for side-effecting tools.
4. Add structured output validation.
5. Add trace events and run IDs.
6. Add one replayable smoke/regression test.
7. Tighten grounding/evidence claims.

## Suggested Patch Files For This Scan

- `tools/approval_boundary_example.json`
- `prompts/structured_output_prompt.md`
- `observability/trace_schema.json`
- `tests/test_ai_smoke.py`
- `observability/interaction_event_schema.json`
- `evals/sample_interaction_regression.jsonl`

## What To Do Manually

- Resolve blocker findings before treating the app as interaction-ready.
- Move from brittle string prompts to structured messages and interaction events.
- Represent tool calls and tool results as first-class objects before rendering prompts.
- Add an explicit structured output contract and validate model responses against it.
- Place machine-readable approval boundaries around destructive or irreversible tools.
- Emit trace events for model calls, tool calls, approvals, and output validation.
- Add one replayable smoke or regression test for the primary Gemini workflow.
- Tighten grounded or source-backed claims so evidence is represented as data.
- Work through warnings after blockers so the harness is easier to iterate on.

## What Not To Overbuild

- Do not build a full eval platform before you have one replayable scenario.
- Do not rewrite the app before making state, tool calls, and tool results visible.
- Do not add production observability before defining the local trace event shape.
- Do not claim grounding unless evidence is represented as data.

## Reminder

This plan is a local migration aid. It does not guarantee production readiness, security, privacy, or compliance.
