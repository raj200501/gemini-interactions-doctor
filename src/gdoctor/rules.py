from __future__ import annotations

import re

from gdoctor.models import Issue, Severity
from gdoctor.scanner import ScanContext, SourceFile


def _snippet(text: str) -> str:
    compact = " ".join(text.strip().split())
    return compact[:180]


def _issue(
    *,
    rule_id: str,
    title: str,
    severity: Severity,
    category: str,
    match: tuple[SourceFile, int, str] | None,
    fallback_file: str,
    why_it_matters: str,
    gemini_relevance: str,
    migration_advice: str,
    safe_patch_available: bool,
    confidence: float,
) -> Issue:
    if match:
        source_file, line_number, line = match
        file_name = source_file.relative_path
        line_start = line_number
        line_end = line_number
        evidence = _snippet(line)
    else:
        file_name = fallback_file
        line_start = 1
        line_end = 1
        evidence = "Project-level evidence"

    return Issue(
        rule_id=rule_id,
        title=title,
        severity=severity,
        category=category,
        file=file_name,
        line_start=line_start,
        line_end=line_end,
        evidence_snippet=evidence,
        why_it_matters=why_it_matters,
        gemini_relevance=gemini_relevance,
        migration_advice=migration_advice,
        safe_patch_available=safe_patch_available,
        confidence=confidence,
    )


def gd001_one_shot_agentic_workflow(ctx: ScanContext) -> list[Issue]:
    if not ctx.uses_gemini:
        return []
    generate = ctx.first_match(r"generateContent|generate_content")
    if not generate:
        return []
    agentic_signals = ctx.any_match(r"\bhistory\b|\bconversation\b|\btools?\b|\bworkflow\b|\bmulti[-_ ]?turn\b|\bsteps?\b")
    state_abstraction = ctx.any_match(
        r"class\s+\w*(State|Session|Conversation|Interaction)|MessageEvent|InteractionEvent|start_chat|chats\.create|ChatSession|session_id"
    )
    if agentic_signals and not state_abstraction:
        return [
            _issue(
                rule_id="GD001",
                title="one-shot model call used for multi-turn workflow",
                severity="blocker",
                category="state",
                match=generate,
                fallback_file="(project root)",
                why_it_matters="This may work for simple prompts, but stateful or tool-using apps usually need explicit state handling.",
                gemini_relevance="Gemini workflows that use tools or multiple turns are easier to debug when turns, tool calls, and state transitions are explicit.",
                migration_advice="Introduce a session or event model before layering tools and multi-step behavior on top of ad hoc generateContent calls.",
                safe_patch_available=False,
                confidence=0.84,
            )
        ]
    return []


def gd002_manual_chat_history(ctx: ScanContext) -> list[Issue]:
    match = ctx.first_match(
        r"history\.join|messages\.map\(.*\.join|conversation\s*\+=|prompt\s*\+=.*(history|conversation)|['\"]\\n['\"]\.join\(history"
    )
    if not match:
        return []
    return [
        _issue(
            rule_id="GD002",
            title="manual chat history is fragile",
            severity="warning",
            category="state",
            match=match,
            fallback_file="(project root)",
            why_it_matters="Manual string accumulation makes it hard to preserve roles, tool events, approvals, and trace IDs.",
            gemini_relevance="Gemini apps that graduate from single prompts need structured turn and event records to keep context reliable.",
            migration_advice="Represent turns as structured messages or events and render prompts from those records only at the model boundary.",
            safe_patch_available=False,
            confidence=0.86,
        )
    ]


def gd003_destructive_tool_approval(ctx: ScanContext) -> list[Issue]:
    match = ctx.first_match(
        r"def\s+(refund|delete|charge|cancel|transfer|disable|update)_\w+|['\"]name['\"]\s*:\s*['\"](refund|delete|charge|cancel|transfer|disable|update)_\w+"
    )
    if not match:
        return []
    has_approval = ctx.any_match(r"approval|approve|approved_by|confirm|human_review|requires_approval|ApprovalBoundary")
    if has_approval:
        return []
    return [
        _issue(
            rule_id="GD003",
            title="destructive tool lacks approval boundary",
            severity="blocker",
            category="tools",
            match=match,
            fallback_file="(project root)",
            why_it_matters="A model-facing tool that changes money, accounts, records, or access needs an explicit approval boundary before execution.",
            gemini_relevance="Tool-using Gemini workflows should make side effects auditable and separable from model suggestion text.",
            migration_advice="Split destructive tools into propose and execute phases, require approval metadata, and trace both decisions.",
            safe_patch_available=True,
            confidence=0.9,
        )
    ]


def gd004_vague_tool_schema(ctx: ScanContext) -> list[Issue]:
    for source_file in ctx.files:
        for index, line in enumerate(source_file.lines, start=1):
            match = re.search(r"['\"]description['\"]\s*:\s*['\"]([^'\"]+)['\"]|description\s*=\s*['\"]([^'\"]+)['\"]", line, re.IGNORECASE)
            if not match:
                continue
            description = match.group(1) or match.group(2) or ""
            words = re.findall(r"[A-Za-z0-9_]+", description)
            vague = description.strip().lower() in {"does refund", "gets data", "updates user", "does stuff", "runs tool"}
            if vague or len(words) < 5:
                return [
                    _issue(
                        rule_id="GD004",
                        title="tool schema too vague",
                        severity="warning",
                        category="tools",
                        match=(source_file, index, line.strip()),
                        fallback_file="(project root)",
                        why_it_matters="Vague tool descriptions increase the chance that the model calls the tool at the wrong time or with incomplete parameters.",
                        gemini_relevance="Gemini tool declarations work best when names, descriptions, and parameter descriptions make the intended use precise.",
                        migration_advice="Rewrite tool descriptions with concrete preconditions, side effects, and parameter meanings.",
                        safe_patch_available=False,
                        confidence=0.78,
                    )
                ]
    return []


def gd005_broad_data_access(ctx: ScanContext) -> list[Issue]:
    match = ctx.first_match(r"get_all_(users|customers|accounts|records)|export_database|SELECT\s+\*|include_all\s*=\s*True|include_all=true")
    if not match:
        return []
    return [
        _issue(
            rule_id="GD005",
            title="broad data access tool",
            severity="warning",
            category="tools",
            match=match,
            fallback_file="(project root)",
            why_it_matters="Broad retrieval makes it harder to reason about least privilege, privacy, and what context the model actually needed.",
            gemini_relevance="Gemini tool calls should prefer scoped inputs and narrow results so the interaction remains explainable.",
            migration_advice="Replace broad tools with scoped lookup functions that require identifiers, filters, limits, and traceable purpose.",
            safe_patch_available=False,
            confidence=0.82,
        )
    ]


def gd006_freeform_json_parse(ctx: ScanContext) -> list[Issue]:
    match = ctx.first_match(r"JSON\.parse\(.*(text|response|model)|json\.loads\((response|.*\.text|model_text|raw_text|model_output)")
    if not match:
        return []
    has_validation = ctx.any_match(r"model_validate_json|TypeAdapter|response_schema|json_schema|BaseModel|pydantic|zod|schema\.parse")
    if has_validation:
        return []
    return [
        _issue(
            rule_id="GD006",
            title="freeform output parsed as JSON",
            severity="blocker",
            category="structured-output",
            match=match,
            fallback_file="(project root)",
            why_it_matters="Parsing freeform model text as JSON fails brittlely and can hide missing or malformed fields.",
            gemini_relevance="Gemini apps that need structured results should define a response contract and validate the returned object.",
            migration_advice="Add a structured output prompt or schema, then validate the response before downstream code uses it.",
            safe_patch_available=True,
            confidence=0.88,
        )
    ]


def gd007_missing_structured_contract(ctx: ScanContext) -> list[Issue]:
    expects_fields = ctx.first_match(r"\[['\"](action|answer|amount|confidence|next_step|summary|status)['\"]\]|\.get\(['\"](action|answer|amount|confidence|next_step|summary|status)['\"]")
    if not expects_fields:
        return []
    has_contract = ctx.any_match(r"response_schema|json_schema|structured output|BaseModel|TypedDict|OutputSchema|schema\.parse|model_validate")
    if has_contract:
        return []
    return [
        _issue(
            rule_id="GD007",
            title="missing structured output contract",
            severity="warning",
            category="structured-output",
            match=expects_fields,
            fallback_file="(project root)",
            why_it_matters="Code expects structured fields, but the prompt or schema does not make the contract explicit.",
            gemini_relevance="Gemini structured outputs are more maintainable when the fields, types, and failure behavior are defined up front.",
            migration_advice="Document the expected response fields and validate them with Pydantic, JSON Schema, or an equivalent typed contract.",
            safe_patch_available=True,
            confidence=0.76,
        )
    ]


def gd008_no_trace_events(ctx: ScanContext) -> list[Issue]:
    has_tools = ctx.any_match(r"\btools\s*=|function_declarations|@tool|Tool\(|def\s+(refund|delete|charge|get_customer|lookup|search|export)_\w+")
    if not has_tools:
        return []
    has_trace = ctx.any_match(r"trace_event|tool_call|run_event|span_id|observability|emit_trace|logger\.(info|debug)\(.*tool")
    if has_trace:
        return []
    match = ctx.first_match(r"\btools\s*=|function_declarations|@tool|Tool\(|def\s+(refund|delete|charge|get_customer|lookup|search|export)_\w+")
    return [
        _issue(
            rule_id="GD008",
            title="no trace events for tool calls",
            severity="blocker",
            category="observability",
            match=match,
            fallback_file="(project root)",
            why_it_matters="Without trace events, tool calls are difficult to debug, audit, or reproduce.",
            gemini_relevance="Gemini tool workflows need visibility into model calls, tool decisions, approvals, and validation outcomes.",
            migration_advice="Emit structured trace events for model requests, tool calls, approval decisions, and response validation.",
            safe_patch_available=True,
            confidence=0.83,
        )
    ]


def gd009_no_ai_smoke_test(ctx: ScanContext) -> list[Issue]:
    if not ctx.uses_gemini:
        return []
    for source_file in ctx.files:
        name = source_file.relative_path.lower()
        is_test_file = name.startswith("tests/") or "/tests/" in name or name.startswith("test_") or name.endswith(".test.ts") or name.endswith(".spec.ts")
        if is_test_file and re.search(r"smoke|gemini|ai path|generate_content|generateContent|model", source_file.text, re.IGNORECASE):
            return []
    return [
        _issue(
            rule_id="GD009",
            title="no primary AI smoke test",
            severity="blocker",
            category="tests",
            match=None,
            fallback_file="(project root)",
            why_it_matters="A smoke test catches broken prompts, missing environment setup, and harness regressions before a demo or deploy.",
            gemini_relevance="Gemini integration code should have a fast local test for the primary AI path, even when live API calls are mocked.",
            migration_advice="Add a smoke test that exercises the main Gemini workflow with a fake model or recorded response.",
            safe_patch_available=True,
            confidence=0.81,
        )
    ]


def gd010_grounding_claim(ctx: ScanContext) -> list[Issue]:
    match = ctx.first_match(r"\b(verified|current|cited|grounded)\b")
    if not match:
        return []
    has_grounding_path = ctx.any_match(r"source_urls|citations|grounding_metadata|retrieval|google_search|evidence|reference_url|sources\s*=")
    if has_grounding_path:
        return []
    return [
        _issue(
            rule_id="GD010",
            title="grounding claim without grounding path",
            severity="warning",
            category="grounding",
            match=match,
            fallback_file="(project root)",
            why_it_matters="UI or prompt language that says an answer is verified, current, cited, or grounded should point to the evidence path.",
            gemini_relevance="Gemini apps should distinguish model confidence from retrieval-backed evidence or explicit citations.",
            migration_advice="Tone down the claim or attach a source, URL, file, citation, or retrieval metadata object.",
            safe_patch_available=False,
            confidence=0.7,
        )
    ]


def gd011_prompt_injection_boundary(ctx: ScanContext) -> list[Issue]:
    match = ctx.first_match(r"prompt\s*=.*(email_body|external_content|ticket_text|webpage|html)|contents\s*=.*(email_body|external_content|ticket_text|webpage|html)")
    if not match:
        return []
    has_boundary = ctx.any_match(r"BEGIN_UNTRUSTED_CONTENT|END_UNTRUSTED_CONTENT|untrusted content|treat .*external .*as data|do not follow instructions in")
    if has_boundary:
        return []
    return [
        _issue(
            rule_id="GD011",
            title="prompt injection boundary missing",
            severity="warning",
            category="prompt-safety",
            match=match,
            fallback_file="(project root)",
            why_it_matters="External content can contain instructions that conflict with developer intent.",
            gemini_relevance="Gemini prompts that include email, web, ticket, or document text should clearly delimit untrusted content.",
            migration_advice="Wrap external content in explicit delimiters and instruct the model to treat it as data, not instructions.",
            safe_patch_available=True,
            confidence=0.77,
        )
    ]


def gd012_missing_agents_md(ctx: ScanContext) -> list[Issue]:
    if not ctx.uses_gemini:
        return []
    has_instructions = ctx.has_project_file({"AGENTS.md", "CLAUDE.md", ".cursorrules"}) or ctx.any_match(r"copilot-instructions\.md")
    if has_instructions:
        return []
    return [
        _issue(
            rule_id="GD012",
            title="missing AGENTS.md or project-specific AI instructions",
            severity="warning",
            category="project-instructions",
            match=None,
            fallback_file="(project root)",
            why_it_matters="AI-heavy repos benefit from explicit local instructions about model boundaries, tool safety, tests, and generated files.",
            gemini_relevance="Gemini app contributors need shared guidance for prompts, tools, structured outputs, and trace expectations.",
            migration_advice="Add an AGENTS.md that states the app's Gemini integration patterns and safety expectations.",
            safe_patch_available=True,
            confidence=0.74,
        )
    ]


ALL_RULES = [
    gd001_one_shot_agentic_workflow,
    gd002_manual_chat_history,
    gd003_destructive_tool_approval,
    gd004_vague_tool_schema,
    gd005_broad_data_access,
    gd006_freeform_json_parse,
    gd007_missing_structured_contract,
    gd008_no_trace_events,
    gd009_no_ai_smoke_test,
    gd010_grounding_claim,
    gd011_prompt_injection_boundary,
    gd012_missing_agents_md,
]
