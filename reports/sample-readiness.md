# Gemini Interactions Doctor Readiness Report

Readiness report for `fragile-gemini-app`

- Target: `examples/fragile-gemini-app`
- Scan time: `2026-06-30T00:00:00+00:00`
- Readiness: `NOT_READY`
- Score: `0 / 100`

## Summary

Gemini Interactions Doctor checks whether this Gemini app harness appears ready to support stateful interactions, function/tool calling, structured outputs, traceability, evidence, and iteration.

## Readiness Scoring

Score starts at `100`.

- Blocker: `-20`
- Warning: `-8`
- Note: `-3`

Readiness is `NOT_READY` when any blocker exists or score is below `70`, `READY_WITH_CAUTION` from `70-89` with no blockers, and `READY` at `90+` with no blockers.

## Migration Blockers

1. one-shot model call used for multi-turn workflow
2. destructive tool lacks approval boundary
3. freeform output parsed as JSON
4. no trace events for tool calls
5. no primary AI smoke test
6. simple model call used where structured interaction state is needed
7. no structured interaction/event model
8. tool result is not represented separately from model text
9. grounded answer path not represented as evidence object

## Top Migration Blockers

1. Stateful workflow is wired through one-shot model calls.
2. Tool calls/results are not represented as structured events.
3. Destructive tool approval is not machine-readable.
4. Model output is parsed as JSON without validation.
5. Grounded answer claims lack an evidence object.

## Patch Suggestions

- `tools/approval_boundary_example.json`
- `prompts/structured_output_prompt.md`
- `observability/trace_schema.json`
- `tests/test_ai_smoke.py`
- `observability/interaction_event_schema.json`
- `evals/sample_interaction_regression.jsonl`

## Generated Starter Files

`gdoctor patch` writes these safe starters into the output directory without mutating the scanned app:

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

## Recommended Migration Order

1. Move from brittle string prompts to structured messages/events.
2. Make tool calls and tool results first-class objects.
3. Add machine-readable approval boundaries for side-effecting tools.
4. Add structured output validation.
5. Add trace events and run IDs.
6. Add one replayable smoke/regression test.
7. Tighten grounding/evidence claims.

## Warnings

### GD002: manual chat history is fragile

- Severity: `warning`
- Category: `state`
- Location: `app.py:62`
- Evidence: `conversation += f"\nUser: {user_message}\nSupport email: {email_body}"`
- Why it matters: Manual string accumulation makes it hard to preserve roles, tool events, approvals, and trace IDs.
- Gemini relevance: Gemini apps that graduate from single prompts need structured turn and event records to keep context reliable.
- Migration advice: Represent turns as structured messages or events and render prompts from those records only at the model boundary.
- Safe patch available: `false`
- Confidence: `0.86`

### GD004: tool schema too vague

- Severity: `warning`
- Category: `tools`
- Location: `app.py:25`
- Evidence: `"description": "does refund",`
- Why it matters: Vague tool descriptions increase the chance that the model calls the tool at the wrong time or with incomplete parameters.
- Gemini relevance: Gemini tool declarations work best when names, descriptions, and parameter descriptions make the intended use precise.
- Migration advice: Rewrite tool descriptions with concrete preconditions, side effects, and parameter meanings.
- Safe patch available: `false`
- Confidence: `0.78`

### GD005: broad data access tool

- Severity: `warning`
- Category: `tools`
- Location: `app.py:35`
- Evidence: `"name": "get_all_customers",`
- Why it matters: Broad retrieval makes it harder to reason about least privilege, privacy, and what context the model actually needed.
- Gemini relevance: Gemini tool calls should prefer scoped inputs and narrow results so the interaction remains explainable.
- Migration advice: Replace broad tools with scoped lookup functions that require identifiers, filters, limits, and traceable purpose.
- Safe patch available: `false`
- Confidence: `0.82`

### GD010: grounding claim without grounding path

- Severity: `warning`
- Category: `grounding`
- Location: `README.md:5`
- Evidence: `It models an AI Studio-style support/research helper that grew from a one-shot Gemini call into a multi-step workflow with chat history, tool schemas, broad data access, a refund s`
- Why it matters: UI or prompt language that says an answer is verified, current, cited, or grounded should point to the evidence path.
- Gemini relevance: Gemini apps should distinguish model confidence from retrieval-backed evidence or explicit citations.
- Migration advice: Tone down the claim or attach a source, URL, file, citation, or retrieval metadata object.
- Safe patch available: `false`
- Confidence: `0.70`

### GD011: prompt injection boundary missing

- Severity: `warning`
- Category: `prompt-safety`
- Location: `app.py:74`
- Evidence: `prompt = build_prompt(user_message, email_body, tool_result)`
- Why it matters: External content can contain instructions that conflict with developer intent.
- Gemini relevance: Gemini prompts that include email, web, ticket, or document text should clearly delimit untrusted content.
- Migration advice: Wrap external content in explicit delimiters and instruct the model to treat it as data, not instructions.
- Safe patch available: `true`
- Confidence: `0.77`

### GD012: missing AGENTS.md or project-specific AI instructions

- Severity: `warning`
- Category: `project-instructions`
- Location: `(project root):1`
- Evidence: `Project-level evidence`
- Why it matters: AI-heavy repos benefit from explicit local instructions about model boundaries, tool safety, tests, and generated files.
- Gemini relevance: Gemini app contributors need shared guidance for prompts, tools, structured outputs, and trace expectations.
- Migration advice: Add an AGENTS.md that states the app's Gemini integration patterns and safety expectations.
- Safe patch available: `true`
- Confidence: `0.74`

### GD016: no replayable test case format

- Severity: `warning`
- Category: `tests`
- Location: `README.md:5`
- Evidence: `It models an AI Studio-style support/research helper that grew from a one-shot Gemini call into a multi-step workflow with chat history, tool schemas, broad data access, a refund s`
- Why it matters: Not every app needs a full eval suite, but stateful Gemini workflows benefit from at least one replayable scenario.
- Gemini relevance: Replayable JSONL scenarios help builders turn AI Studio-style examples and failed Gemini runs into local regression coverage.
- Migration advice: Add a JSONL scenario with user input, expected tool calls, expected structured output fields, and evidence expectations.
- Safe patch available: `true`
- Confidence: `0.78`

### GD018: approval boundary not machine-readable

- Severity: `warning`
- Category: `tools`
- Location: `app.py:24`
- Evidence: `"name": "refund_customer",`
- Why it matters: Agent/tool harnesses need boundaries the code can inspect, not just README or prompt wording.
- Gemini relevance: Gemini tool schemas should expose side-effect risk and approval requirements in fields that orchestration code can enforce.
- Migration advice: Add requiresApproval, approval_required, requires_confirmation, dry_run, side_effect, or risk_level metadata to destructive tool schemas.
- Safe patch available: `true`
- Confidence: `0.79`


## Evidence Snippets

### GD001: one-shot model call used for multi-turn workflow

- Severity: `blocker`
- Category: `state`
- Location: `app.py:5`
- Evidence: `def generate_content(self, **kwargs):`
- Why it matters: This may work for simple prompts, but stateful or tool-using apps usually need explicit state handling.
- Gemini relevance: Gemini workflows that use tools or multiple turns are easier to debug when turns, tool calls, and state transitions are explicit.
- Migration advice: Introduce a session or event model before layering tools and multi-step behavior on top of ad hoc generateContent calls.
- Safe patch available: `false`
- Confidence: `0.84`

### GD003: destructive tool lacks approval boundary

- Severity: `blocker`
- Category: `tools`
- Location: `app.py:24`
- Evidence: `"name": "refund_customer",`
- Why it matters: A model-facing tool that changes money, accounts, records, or access needs an explicit approval boundary before execution.
- Gemini relevance: Tool-using Gemini workflows should make side effects auditable and separable from model suggestion text.
- Migration advice: Split destructive tools into propose and execute phases, require approval metadata, and trace both decisions.
- Safe patch available: `true`
- Confidence: `0.90`

### GD006: freeform output parsed as JSON

- Severity: `blocker`
- Category: `structured-output`
- Location: `app.py:80`
- Evidence: `parsed = json.loads(response.text)`
- Why it matters: Parsing freeform model text as JSON fails brittlely and can hide missing or malformed fields.
- Gemini relevance: Gemini apps that need structured results should define a response contract and validate the returned object.
- Migration advice: Add a structured output prompt or schema, then validate the response before downstream code uses it.
- Safe patch available: `true`
- Confidence: `0.88`

### GD008: no trace events for tool calls

- Severity: `blocker`
- Category: `observability`
- Location: `app.py:22`
- Evidence: `TOOLS = [`
- Why it matters: Without trace events, tool calls are difficult to debug, audit, or reproduce.
- Gemini relevance: Gemini tool workflows need visibility into model calls, tool decisions, approvals, and validation outcomes.
- Migration advice: Emit structured trace events for model requests, tool calls, approval decisions, and response validation.
- Safe patch available: `true`
- Confidence: `0.83`

### GD009: no primary AI smoke test

- Severity: `blocker`
- Category: `tests`
- Location: `(project root):1`
- Evidence: `Project-level evidence`
- Why it matters: A smoke test catches broken prompts, missing environment setup, and harness regressions before a demo or deploy.
- Gemini relevance: Gemini integration code should have a fast local test for the primary AI path, even when live API calls are mocked.
- Migration advice: Add a smoke test that exercises the main Gemini workflow with a fake model or recorded response.
- Safe patch available: `true`
- Confidence: `0.81`

### GD013: simple model call used where structured interaction state is needed

- Severity: `blocker`
- Category: `state`
- Location: `app.py:5`
- Evidence: `def generate_content(self, **kwargs):`
- Why it matters: This may be fine for a one-shot prompt, but this app appears to manage state/tools/workflow steps. A structured interaction/event layer will be easier to debug, replay, and test.
- Gemini relevance: Gemini app harnesses become more reliable when turns, tool calls, tool results, and model responses are represented before prompt rendering.
- Migration advice: Introduce InteractionEvent, Message, ToolCall, and ToolResult records, then render Gemini prompts from those records.
- Safe patch available: `true`
- Confidence: `0.86`

### GD014: no structured interaction/event model

- Severity: `blocker`
- Category: `state`
- Location: `README.md:5`
- Evidence: `It models an AI Studio-style support/research helper that grew from a one-shot Gemini call into a multi-step workflow with chat history, tool schemas, broad data access, a refund s`
- Why it matters: Stateful Gemini apps are hard to debug when messages, tool calls, tool results, approvals, and run IDs are not first-class objects.
- Gemini relevance: A structured event model gives Gemini API builders a local shape for replay, trace logs, smoke tests, and migration from AI Studio prototypes.
- Migration advice: Add an InteractionEvent schema with run_id, event_id, role/type, content, tool call metadata, tool result metadata, and timestamps.
- Safe patch available: `true`
- Confidence: `0.84`

### GD015: tool result is not represented separately from model text

- Severity: `blocker`
- Category: `tools`
- Location: `app.py:66`
- Evidence: `prompt += f"Tool result: {tool_result}\n"`
- Why it matters: Tool-using Gemini apps are easier to debug and replay when tool calls and tool results are first-class events.
- Gemini relevance: Gemini function-calling workflows need a durable boundary between the model message, the tool execution, and the tool result.
- Migration advice: Create a ToolResult object with tool name, arguments, result payload, status, and trace IDs before using it in prompt rendering.
- Safe patch available: `true`
- Confidence: `0.82`

### GD017: grounded answer path not represented as evidence object

- Severity: `blocker`
- Category: `grounding`
- Location: `README.md:5`
- Evidence: `It models an AI Studio-style support/research helper that grew from a one-shot Gemini call into a multi-step workflow with chat history, tool schemas, broad data access, a refund s`
- Why it matters: Grounded or source-backed answer claims should be represented as evidence data, not only as words in the final answer.
- Gemini relevance: Gemini apps that show sources need a durable evidence object so grounding can be tested, rendered, and audited.
- Migration advice: Add evidence, sources, citations, or grounding_metadata objects to the structured output and UI boundary.
- Safe patch available: `true`
- Confidence: `0.80`


## Generated Files

Run:

```bash
gdoctor patch examples/fragile-gemini-app --out patches/fragile-gemini-app
```

## Next Steps

- Resolve blocker findings before treating the app as interaction-ready.
- Move from brittle string prompts to structured messages and interaction events.
- Represent tool calls and tool results as first-class objects before rendering prompts.
- Add an explicit structured output contract and validate model responses against it.
- Place machine-readable approval boundaries around destructive or irreversible tools.
- Emit trace events for model calls, tool calls, approvals, and output validation.
- Add one replayable smoke or regression test for the primary Gemini workflow.
- Tighten grounded or source-backed claims so evidence is represented as data.
- Work through warnings after blockers so the harness is easier to iterate on.

## What This Does Not Guarantee

- It is not official Google tooling and is not affiliated with Google.
- It does not know private AI Studio or Gemini roadmap details.
- It is not a production readiness assessment.
- It does not execute or call Gemini APIs.
- It does not replace security, privacy, legal, or compliance review.
- It uses static heuristics and safe patch templates.
- Suggested patches still need project-specific review.
