# Agent Instructions

This sample app keeps Gemini interaction state, tool calls, tool results, structured outputs, evidence, trace events, and tests explicit.

- Keep turns as `InteractionEvent` records with `run_id` correlation.
- Keep tool calls as `ToolCall` records.
- Keep tool results as `ToolResult` records.
- Keep side-effecting tools behind an `ApprovalDecision`.
- Validate model outputs through `StructuredAnswer`.
- Preserve evidence objects for source-backed claims.
- Preserve the external content boundary wrapper.
- Update `tests/test_ai_smoke.py` and `evals/sample_interaction_regression.jsonl` when changing the primary AI path.
