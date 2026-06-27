# Gemini Interactions Doctor Readiness Report

Readiness report for `fragile-gemini-app`

- Target: `/Users/rajkashikar/Documents/Codex/2026-06-26/you-are-codex-working-inside-a/gemini-interactions-doctor/examples/fragile-gemini-app`
- Scan time: `2026-06-27T04:02:37+00:00`
- Readiness: `NOT_READY`
- Score: `0 / 100`

## Summary

Gemini Interactions Doctor checks whether this Gemini app harness appears ready to support state, tools, structured outputs, traceability, and iteration.

## Migration Blockers

1. one-shot model call used for multi-turn workflow
2. destructive tool lacks approval boundary
3. freeform output parsed as JSON
4. no trace events for tool calls
5. no primary AI smoke test

## Patch Suggestions

- `tools/approval_boundary_example.json`
- `prompts/structured_output_prompt.md`
- `observability/trace_schema.json`
- `tests/test_ai_smoke.py`

## Warnings

### GD002: manual chat history is fragile

- Severity: `warning`
- Category: `state`
- Location: `app.py:48`
- Evidence: `conversation += f"\nUser: {user_message}\nSupport email: {email_body}"`
- Why it matters: Manual string accumulation makes it hard to preserve roles, tool events, approvals, and trace IDs.
- Gemini relevance: Gemini apps that graduate from single prompts need structured turn and event records to keep context reliable.
- Migration advice: Represent turns as structured messages or events and render prompts from those records only at the model boundary.
- Safe patch available: `false`
- Confidence: `0.86`

### GD004: tool schema too vague

- Severity: `warning`
- Category: `tools`
- Location: `app.py:20`
- Evidence: `"description": "does refund",`
- Why it matters: Vague tool descriptions increase the chance that the model calls the tool at the wrong time or with incomplete parameters.
- Gemini relevance: Gemini tool declarations work best when names, descriptions, and parameter descriptions make the intended use precise.
- Migration advice: Rewrite tool descriptions with concrete preconditions, side effects, and parameter meanings.
- Safe patch available: `false`
- Confidence: `0.78`

### GD005: broad data access tool

- Severity: `warning`
- Category: `tools`
- Location: `app.py:30`
- Evidence: `"name": "get_all_customers",`
- Why it matters: Broad retrieval makes it harder to reason about least privilege, privacy, and what context the model actually needed.
- Gemini relevance: Gemini tool calls should prefer scoped inputs and narrow results so the interaction remains explainable.
- Migration advice: Replace broad tools with scoped lookup functions that require identifiers, filters, limits, and traceable purpose.
- Safe patch available: `false`
- Confidence: `0.82`

### GD007: missing structured output contract

- Severity: `warning`
- Category: `structured-output`
- Location: `app.py:63`
- Evidence: `if parsed["action"] == "refund":`
- Why it matters: Code expects structured fields, but the prompt or schema does not make the contract explicit.
- Gemini relevance: Gemini structured outputs are more maintainable when the fields, types, and failure behavior are defined up front.
- Migration advice: Document the expected response fields and validate them with Pydantic, JSON Schema, or an equivalent typed contract.
- Safe patch available: `true`
- Confidence: `0.76`

### GD010: grounding claim without grounding path

- Severity: `warning`
- Category: `grounding`
- Location: `README.md:5`
- Evidence: `It models a support helper that grew from a one-shot Gemini call into a workflow with chat history, tools, JSON parsing, and a "verified answer" banner, but without the harness pie`
- Why it matters: UI or prompt language that says an answer is verified, current, cited, or grounded should point to the evidence path.
- Gemini relevance: Gemini apps should distinguish model confidence from retrieval-backed evidence or explicit citations.
- Migration advice: Tone down the claim or attach a source, URL, file, citation, or retrieval metadata object.
- Safe patch available: `false`
- Confidence: `0.70`

### GD011: prompt injection boundary missing

- Severity: `warning`
- Category: `prompt-safety`
- Location: `app.py:49`
- Evidence: `prompt = f"Use the support email directly: {email_body}\nConversation so far:\n{conversation}\nReturn JSON with action, answer, and amount."`
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


## Evidence

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
- Location: `app.py:19`
- Evidence: `"name": "refund_customer",`
- Why it matters: A model-facing tool that changes money, accounts, records, or access needs an explicit approval boundary before execution.
- Gemini relevance: Tool-using Gemini workflows should make side effects auditable and separable from model suggestion text.
- Migration advice: Split destructive tools into propose and execute phases, require approval metadata, and trace both decisions.
- Safe patch available: `true`
- Confidence: `0.90`

### GD006: freeform output parsed as JSON

- Severity: `blocker`
- Category: `structured-output`
- Location: `app.py:60`
- Evidence: `parsed = json.loads(response.text)`
- Why it matters: Parsing freeform model text as JSON fails brittlely and can hide missing or malformed fields.
- Gemini relevance: Gemini apps that need structured results should define a response contract and validate the returned object.
- Migration advice: Add a structured output prompt or schema, then validate the response before downstream code uses it.
- Safe patch available: `true`
- Confidence: `0.88`

### GD008: no trace events for tool calls

- Severity: `blocker`
- Category: `observability`
- Location: `app.py:17`
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


## Generated Files

Run:

```bash
gdoctor patch /Users/rajkashikar/Documents/Codex/2026-06-26/you-are-codex-working-inside-a/gemini-interactions-doctor/examples/fragile-gemini-app --out patches/fragile-gemini-app
```

## Next Steps

- Resolve blocker findings before treating the app as interaction-ready.
- Add an explicit structured output contract and validate model responses against it.
- Place approval boundaries around destructive or irreversible tools.
- Emit trace events for model calls, tool calls, approvals, and output validation.
- Add a smoke test that exercises the primary Gemini path without requiring live credentials.
- Work through warnings after blockers so the harness is easier to iterate on.

## What This Does Not Guarantee

- It does not prove production readiness.
- It does not execute or call Gemini APIs.
- It does not verify security, privacy, legal, or compliance posture.
- It does not guarantee that suggested patches are sufficient for your app architecture.
