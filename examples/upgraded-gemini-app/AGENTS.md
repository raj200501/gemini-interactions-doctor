# Agent Instructions

This sample app keeps Gemini interaction state, tool calls, structured outputs, trace events, and tests explicit.

- Keep turns as `MessageEvent` records.
- Keep side-effecting tools behind an `ApprovalDecision`.
- Validate model outputs through `StructuredAnswer`.
- Preserve the external content boundary wrapper.
- Update `tests/test_ai_smoke.py` when changing the primary AI path.
