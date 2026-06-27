# Agent Instructions

This repo contains a Gemini app harness. Keep changes focused on making state, tools, structured outputs, traceability, and tests explicit.

## Gemini Interaction Rules

- Do not convert external content directly into developer instructions.
- Keep message history as structured events, not concatenated strings.
- Represent tool calls and tool results as first-class objects before prompt rendering.
- Validate structured model outputs before business logic uses them.
- Put machine-readable approval boundaries around destructive tools.
- Emit trace events for model calls, tool calls, approvals, validation failures, and retries.
- Add or update a smoke/regression test when changing the primary AI path.

## Local Validation

Run the project smoke tests before changing prompt, tool, or structured-output code.
