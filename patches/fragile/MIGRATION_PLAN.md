# Gemini Interaction Migration Plan

Target: `/Users/rajkashikar/Documents/Codex/2026-06-26/you-are-codex-working-inside-a/gemini-interactions-doctor/examples/fragile-gemini-app`
Readiness: `NOT_READY`
Score: `0 / 100`

## Priority 1: Migration Blockers

1. one-shot model call used for multi-turn workflow (`GD001`)
2. destructive tool lacks approval boundary (`GD003`)
3. freeform output parsed as JSON (`GD006`)
4. no trace events for tool calls (`GD008`)
5. no primary AI smoke test (`GD009`)

## Priority 2: Warnings

- manual chat history is fragile (`GD002`)
- tool schema too vague (`GD004`)
- broad data access tool (`GD005`)
- missing structured output contract (`GD007`)
- grounding claim without grounding path (`GD010`)
- prompt injection boundary missing (`GD011`)
- missing AGENTS.md or project-specific AI instructions (`GD012`)

## Safe Starter Patches

- `tools/approval_boundary_example.json`
- `prompts/structured_output_prompt.md`
- `observability/trace_schema.json`
- `tests/test_ai_smoke.py`

## Recommended Sequence

- Resolve blocker findings before treating the app as interaction-ready.
- Add an explicit structured output contract and validate model responses against it.
- Place approval boundaries around destructive or irreversible tools.
- Emit trace events for model calls, tool calls, approvals, and output validation.
- Add a smoke test that exercises the primary Gemini path without requiring live credentials.
- Work through warnings after blockers so the harness is easier to iterate on.

## Reminder

This plan is a local migration aid. It does not guarantee production readiness, security, privacy, or compliance.
