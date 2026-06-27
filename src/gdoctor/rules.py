from __future__ import annotations

import re

from gdoctor.models import Issue, Severity
from gdoctor.scanner import ScanContext, SourceFile

RULE_CATALOG = [
    {
        "rule_id": "GD001",
        "title": "one-shot model call used for multi-turn workflow",
        "severity": "blocker",
        "category": "state",
        "purpose": "Find Gemini workflows that appear to manage state or tools through ad hoc generateContent calls.",
    },
    {
        "rule_id": "GD002",
        "title": "manual chat history is fragile",
        "severity": "warning",
        "category": "state",
        "purpose": "Find brittle history strings instead of structured messages or events.",
    },
    {
        "rule_id": "GD003",
        "title": "destructive tool lacks approval boundary",
        "severity": "blocker",
        "category": "tools",
        "purpose": "Find side-effecting tools without an approval boundary.",
    },
    {
        "rule_id": "GD004",
        "title": "tool schema too vague",
        "severity": "warning",
        "category": "tools",
        "purpose": "Find Gemini tool declarations that do not give the model enough calling context.",
    },
    {
        "rule_id": "GD005",
        "title": "broad data access tool",
        "severity": "warning",
        "category": "tools",
        "purpose": "Find broad retrieval tools that should be scoped before model use.",
    },
    {
        "rule_id": "GD006",
        "title": "freeform output parsed as JSON",
        "severity": "blocker",
        "category": "structured-output",
        "purpose": "Find brittle parsing of model text without validation.",
    },
    {
        "rule_id": "GD007",
        "title": "missing structured output contract",
        "severity": "warning",
        "category": "structured-output",
        "purpose": "Find code that expects fields without an explicit response contract.",
    },
    {
        "rule_id": "GD008",
        "title": "no trace events for tool calls",
        "severity": "blocker",
        "category": "observability",
        "purpose": "Find tool workflows without trace events for debugging and replay.",
    },
    {
        "rule_id": "GD009",
        "title": "no primary AI smoke test",
        "severity": "blocker",
        "category": "tests",
        "purpose": "Find stateful or tool-using Gemini workflows without a fast smoke test.",
    },
    {
        "rule_id": "GD010",
        "title": "grounding claim without grounding path",
        "severity": "warning",
        "category": "grounding",
        "purpose": "Find verified/current/cited UI claims without a visible evidence path.",
    },
    {
        "rule_id": "GD011",
        "title": "prompt injection boundary missing",
        "severity": "warning",
        "category": "prompt-safety",
        "purpose": "Find external content inserted into prompts without untrusted-content boundaries.",
    },
    {
        "rule_id": "GD012",
        "title": "missing AGENTS.md or project-specific AI instructions",
        "severity": "warning",
        "category": "project-instructions",
        "purpose": "Find Gemini app repos without local AI coding and harness instructions.",
    },
    {
        "rule_id": "GD013",
        "title": "simple model call used where structured interaction state is needed",
        "severity": "blocker",
        "category": "state",
        "purpose": "Find prototype-style model calls in apps that now show state, tools, or workflow steps.",
    },
    {
        "rule_id": "GD014",
        "title": "no structured interaction/event model",
        "severity": "blocker",
        "category": "state",
        "purpose": "Find stateful or tool-using apps without Message, ToolCall, ToolResult, run, or event objects.",
    },
    {
        "rule_id": "GD015",
        "title": "tool result is not represented separately from model text",
        "severity": "blocker",
        "category": "tools",
        "purpose": "Find tool outputs pasted into prompts instead of represented as replayable result objects.",
    },
    {
        "rule_id": "GD016",
        "title": "no replayable test case format",
        "severity": "warning",
        "category": "tests",
        "purpose": "Find stateful Gemini workflows without a saved JSON/JSONL scenario for regression replay.",
    },
    {
        "rule_id": "GD017",
        "title": "grounded answer path not represented as evidence object",
        "severity": "blocker",
        "category": "grounding",
        "purpose": "Find source-backed claims that live only in final answer text instead of evidence data.",
    },
    {
        "rule_id": "GD018",
        "title": "approval boundary not machine-readable",
        "severity": "warning",
        "category": "tools",
        "purpose": "Find destructive tools where approval exists only in prose, not schema fields code can inspect.",
    },
]


DESTRUCTIVE_TOOL_PATTERN = (
    r"def\s+(refund|delete|charge|cancel|transfer|disable|update)_\w+|"
    r"['\"]name['\"]\s*:\s*['\"](refund|delete|charge|cancel|transfer|disable|update)_\w+"
)

STRUCTURED_EVENT_PATTERN = (
    r"TraceEvent|InteractionEvent|MessageEvent|Message\b|ToolCall|ToolResult|run_id|conversation_id|event_id|InteractionState"
)


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
    if ctx.needs_interaction_harness and not ctx.has_structured_event_model:
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
    match = ctx.first_match(DESTRUCTIVE_TOOL_PATTERN)
    if not match:
        return []
    has_approval = ctx.has_machine_readable_approval or ctx.any_match(
        r"ApprovalDecision|ApprovalBoundary|approved_by\s*[:=]|approved_at\s*[:=]|approval\s*:\s*ApprovalDecision"
    )
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
    has_validation = ctx.any_match(
        r"model_validate_json|model_validate\(|TypeAdapter|response_schema|json_schema|BaseModel|pydantic|zod|schema\.parse|jsonschema\.validate|validate\(.*schema"
    )
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
    if not ctx.has_tool_definitions:
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
    if not ctx.uses_gemini or not ctx.needs_interaction_harness:
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


def gd013_simple_call_needs_interaction_state(ctx: ScanContext) -> list[Issue]:
    if not ctx.uses_gemini or not ctx.needs_interaction_harness:
        return []
    generate = ctx.first_match(r"generateContent|generate_content")
    raw_prompt_state = ctx.any_match(r"prompt\s*=.*(history|conversation|tool_result|toolResult|previous_turns|email_body|ticket_text)")
    if not generate or ctx.has_structured_event_model:
        return []
    if not (ctx.has_tool_definitions or raw_prompt_state or ctx.has_multiturn_or_workflow_signals):
        return []
    return [
        _issue(
            rule_id="GD013",
            title="simple model call used where structured interaction state is needed",
            severity="blocker",
            category="state",
            match=generate,
            fallback_file="(project root)",
            why_it_matters="This may be fine for a one-shot prompt, but this app appears to manage state/tools/workflow steps. A structured interaction/event layer will be easier to debug, replay, and test.",
            gemini_relevance="Gemini app harnesses become more reliable when turns, tool calls, tool results, and model responses are represented before prompt rendering.",
            migration_advice="Introduce InteractionEvent, Message, ToolCall, and ToolResult records, then render Gemini prompts from those records.",
            safe_patch_available=True,
            confidence=0.86,
        )
    ]


def gd014_no_structured_interaction_event_model(ctx: ScanContext) -> list[Issue]:
    if not ctx.uses_gemini or not ctx.needs_interaction_harness or ctx.has_structured_event_model:
        return []
    match = ctx.first_match(r"\bhistory\b|\bconversation\b|\btools\s*=|function_declarations|workflow|support ticket|research assistant")
    return [
        _issue(
            rule_id="GD014",
            title="no structured interaction/event model",
            severity="blocker",
            category="state",
            match=match,
            fallback_file="(project root)",
            why_it_matters="Stateful Gemini apps are hard to debug when messages, tool calls, tool results, approvals, and run IDs are not first-class objects.",
            gemini_relevance="A structured event model gives Gemini API builders a local shape for replay, trace logs, smoke tests, and migration from AI Studio prototypes.",
            migration_advice="Add an InteractionEvent schema with run_id, event_id, role/type, content, tool call metadata, tool result metadata, and timestamps.",
            safe_patch_available=True,
            confidence=0.84,
        )
    ]


def gd015_tool_result_not_represented_separately(ctx: ScanContext) -> list[Issue]:
    if not ctx.has_tool_definitions:
        return []
    match = ctx.first_match(
        r"prompt\s*(\+=|=).*tool[_]?result|tool[_]?result.*prompt|f['\"].*\{tool[_]?result\}|contents\s*=.*tool[_]?result|answer\s*=.*tool[_]?result"
    )
    if not match:
        return []
    if ctx.any_match(r"ToolResult|tool_result\s*=\s*\{|tool_result\s*=\s*Tool|tool_results\s*:\s*list|tool_results\s*=\s*\["):
        return []
    return [
        _issue(
            rule_id="GD015",
            title="tool result is not represented separately from model text",
            severity="blocker",
            category="tools",
            match=match,
            fallback_file="(project root)",
            why_it_matters="Tool-using Gemini apps are easier to debug and replay when tool calls and tool results are first-class events.",
            gemini_relevance="Gemini function-calling workflows need a durable boundary between the model message, the tool execution, and the tool result.",
            migration_advice="Create a ToolResult object with tool name, arguments, result payload, status, and trace IDs before using it in prompt rendering.",
            safe_patch_available=True,
            confidence=0.82,
        )
    ]


def gd016_no_replayable_test_case_format(ctx: ScanContext) -> list[Issue]:
    if not ctx.uses_gemini or not ctx.needs_interaction_harness or ctx.has_replayable_case_format:
        return []
    match = ctx.first_match(r"\btools\s*=|workflow|support ticket|research assistant|generateContent|generate_content")
    return [
        _issue(
            rule_id="GD016",
            title="no replayable test case format",
            severity="warning",
            category="tests",
            match=match,
            fallback_file="(project root)",
            why_it_matters="Not every app needs a full eval suite, but stateful Gemini workflows benefit from at least one replayable scenario.",
            gemini_relevance="Replayable JSONL scenarios help builders turn AI Studio-style examples and failed Gemini runs into local regression coverage.",
            migration_advice="Add a JSONL scenario with user input, expected tool calls, expected structured output fields, and evidence expectations.",
            safe_patch_available=True,
            confidence=0.78,
        )
    ]


def gd017_grounded_path_not_evidence_object(ctx: ScanContext) -> list[Issue]:
    match = ctx.first_match(r"\b(source-backed|source backed|verified|cited|grounded|sources?:)\b")
    if not match:
        return []
    has_evidence_object = ctx.any_match(
        r"\bevidence\b\s*[:=]|\bsources\b\s*[:=]|\bcitations\b\s*[:=]|grounding_metadata|class\s+\w*(Evidence|Citation|Source)"
    )
    if has_evidence_object:
        return []
    freeform_claim = ctx.any_match(r"answer\s*=.*(source|verified|cited|grounded)|banner\s*=.*(source|verified|cited|grounded)|return\s+\{[^}]*['\"]answer['\"][^}]*")
    if not freeform_claim:
        return []
    return [
        _issue(
            rule_id="GD017",
            title="grounded answer path not represented as evidence object",
            severity="blocker",
            category="grounding",
            match=match,
            fallback_file="(project root)",
            why_it_matters="Grounded or source-backed answer claims should be represented as evidence data, not only as words in the final answer.",
            gemini_relevance="Gemini apps that show sources need a durable evidence object so grounding can be tested, rendered, and audited.",
            migration_advice="Add evidence, sources, citations, or grounding_metadata objects to the structured output and UI boundary.",
            safe_patch_available=True,
            confidence=0.8,
        )
    ]


def gd018_approval_boundary_not_machine_readable(ctx: ScanContext) -> list[Issue]:
    match = ctx.first_match(DESTRUCTIVE_TOOL_PATTERN)
    if not match:
        return []
    has_prose_approval = ctx.any_match(r"approval|approve|approved_by|confirm|human_review|human approval|reviewed")
    if not has_prose_approval or ctx.has_machine_readable_approval:
        return []
    return [
        _issue(
            rule_id="GD018",
            title="approval boundary not machine-readable",
            severity="warning",
            category="tools",
            match=match,
            fallback_file="(project root)",
            why_it_matters="Agent/tool harnesses need boundaries the code can inspect, not just README or prompt wording.",
            gemini_relevance="Gemini tool schemas should expose side-effect risk and approval requirements in fields that orchestration code can enforce.",
            migration_advice="Add requiresApproval, approval_required, requires_confirmation, dry_run, side_effect, or risk_level metadata to destructive tool schemas.",
            safe_patch_available=True,
            confidence=0.79,
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
    gd013_simple_call_needs_interaction_state,
    gd014_no_structured_interaction_event_model,
    gd015_tool_result_not_represented_separately,
    gd016_no_replayable_test_case_format,
    gd017_grounded_path_not_evidence_object,
    gd018_approval_boundary_not_machine_readable,
]
