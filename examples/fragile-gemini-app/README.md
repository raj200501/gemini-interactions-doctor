# Fragile Gemini App

This intentionally brittle sample is used by `gdoctor demo`.

It models an AI Studio-style support/research helper that grew from a one-shot Gemini call into a multi-step workflow with chat history, tool schemas, broad data access, a refund side effect, pasted tool results, brittle JSON parsing, and a "verified source-backed answer" banner.

It intentionally omits the harness pieces a maintainable Gemini workflow needs:

- structured interaction events
- tool call and tool result objects
- machine-readable approval metadata
- structured output validation
- trace events
- replayable regression cases
- smoke tests
- `AGENTS.md`
