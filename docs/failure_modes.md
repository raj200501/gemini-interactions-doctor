# Failure Modes

Gemini Interactions Doctor is useful because it looks for common harness-readiness patterns, but it is still a static heuristic tool.

## Known False Positives

- A repo stores structured messages under names other than `Message`, `InteractionEvent`, `ToolCall`, or `ToolResult`.
- Approval metadata is enforced by a framework or service configuration outside scanned files.
- JSON validation happens through a helper that does not expose obvious `schema`, `BaseModel`, `zod`, or `jsonschema` names.
- Prompt injection boundaries are wrapped in a shared template outside the scanned directory.
- A simple read-only helper uses a name that resembles a side-effecting tool.

## Known False Negatives

- Tools are created dynamically at runtime.
- Prompts are fetched from a database, remote CMS, or AI Studio export not committed to the repo.
- A wrapper hides `generateContent` calls and tool execution.
- Destructive behavior uses domain-specific names that do not match mutation terms.
- Evidence is stored in freeform fields that happen to be named `sources` but are not actually structured.

## Examples

- A safe workflow with `steps = [...]` and no tools may be flagged as needing a harness if it also stuffs prior turns into a prompt.
- A risky `resolve_claim()` function that issues a refund but lacks mutation words may be missed.
- A generated SDK client with schemas in build output may be skipped if it lives under ignored directories.

## Mitigation Ideas

- Add project-specific allow/deny hints.
- Add language-aware AST passes for Python and TypeScript.
- Add framework profiles for common Gemini SDK wrappers.
- Accept runtime traces from companion tooling.
- Compare scans before and after migration so teams focus on deltas.

## Why This Scope Is Still Useful

The scanner is meant to catch the migration moment where a working Gemini prototype starts growing state, tools, structured outputs, evidence, and tests without a harness shape. Even imperfect static findings can help builders notice fragile integration patterns early.
