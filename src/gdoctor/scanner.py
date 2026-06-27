from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re

from gdoctor.models import Issue, Readiness, ScanReport

SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".mjs",
    ".cjs",
    ".md",
    ".txt",
    ".json",
    ".yaml",
    ".yml",
    ".html",
}

SKIP_DIRS = {
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
}

PATCH_PRIORITY = {
    "GD003": "tools/approval_boundary_example.json",
    "GD006": "prompts/structured_output_prompt.md",
    "GD007": "prompts/structured_output_prompt.md",
    "GD008": "observability/trace_schema.json",
    "GD009": "tests/test_ai_smoke.py",
}


@dataclass(frozen=True)
class SourceFile:
    path: Path
    relative_path: str
    text: str

    @property
    def lines(self) -> list[str]:
        return self.text.splitlines()


class ScanContext:
    def __init__(self, target: Path, files: list[SourceFile]) -> None:
        self.target = target
        self.files = files
        self.all_text = "\n".join(file.text for file in files)

    @property
    def uses_gemini(self) -> bool:
        return bool(
            re.search(
                r"\bgemini\b|generateContent|generate_content|google\.generativeai|@google/generative-ai|from google import genai",
                self.all_text,
                re.IGNORECASE,
            )
        )

    def has_project_file(self, names: set[str]) -> bool:
        normalized = {name.lower() for name in names}
        return any(file.path.name.lower() in normalized for file in self.files)

    def first_match(self, pattern: str, flags: int = re.IGNORECASE) -> tuple[SourceFile, int, str] | None:
        regex = re.compile(pattern, flags)
        for source_file in self.files:
            for index, line in enumerate(source_file.lines, start=1):
                if regex.search(line):
                    return source_file, index, line.strip()
        return None

    def any_match(self, pattern: str, flags: int = re.IGNORECASE) -> bool:
        return bool(re.search(pattern, self.all_text, flags))


def collect_source_files(target: Path) -> list[SourceFile]:
    files: list[SourceFile] = []
    for path in sorted(target.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        files.append(
            SourceFile(
                path=path,
                relative_path=path.relative_to(target).as_posix(),
                text=text,
            )
        )
    return files


def score_issues(issues: list[Issue]) -> int:
    score = 100
    for issue in issues:
        if issue.severity == "blocker":
            score -= 20
        elif issue.severity == "warning":
            score -= 8
        else:
            score -= 3
    return max(0, min(100, score))


def readiness_for(issues: list[Issue], score: int) -> Readiness:
    if any(issue.severity == "blocker" for issue in issues) or score < 70:
        return "NOT_READY"
    if score < 90:
        return "READY_WITH_CAUTION"
    return "READY"


def suggested_patch_files(issues: list[Issue]) -> list[str]:
    patches: list[str] = []
    for issue in issues:
        patch = PATCH_PRIORITY.get(issue.rule_id)
        if patch and patch not in patches:
            patches.append(patch)
    return patches


def build_next_steps(issues: list[Issue]) -> list[str]:
    if not issues:
        return [
            "Keep the smoke test close to the primary Gemini path.",
            "Review tool approvals whenever you add side-effecting capabilities.",
            "Keep structured output contracts and trace events versioned with the app.",
        ]

    steps: list[str] = []
    blockers = [issue for issue in issues if issue.severity == "blocker"]
    warnings = [issue for issue in issues if issue.severity == "warning"]
    if blockers:
        steps.append("Resolve blocker findings before treating the app as interaction-ready.")
    if any(issue.rule_id in {"GD006", "GD007"} for issue in issues):
        steps.append("Add an explicit structured output contract and validate model responses against it.")
    if any(issue.rule_id == "GD003" for issue in issues):
        steps.append("Place approval boundaries around destructive or irreversible tools.")
    if any(issue.rule_id == "GD008" for issue in issues):
        steps.append("Emit trace events for model calls, tool calls, approvals, and output validation.")
    if any(issue.rule_id == "GD009" for issue in issues):
        steps.append("Add a smoke test that exercises the primary Gemini path without requiring live credentials.")
    if warnings:
        steps.append("Work through warnings after blockers so the harness is easier to iterate on.")
    return steps


def scan_project(target: str | Path) -> ScanReport:
    from gdoctor.rules import ALL_RULES

    target_path = Path(target).resolve()
    if not target_path.exists():
        raise FileNotFoundError(f"Target path does not exist: {target_path}")
    if not target_path.is_dir():
        raise NotADirectoryError(f"Target path must be a directory: {target_path}")

    context = ScanContext(target_path, collect_source_files(target_path))
    issues: list[Issue] = []
    for rule in ALL_RULES:
        rule_issues = rule(context)
        issues.extend(rule_issues)

    issues.sort(key=lambda issue: ({"blocker": 0, "warning": 1, "note": 2}[issue.severity], issue.rule_id))
    score = score_issues(issues)
    readiness = readiness_for(issues, score)
    blockers = [issue.title for issue in issues if issue.severity == "blocker"]

    return ScanReport(
        target_path=target_path.as_posix(),
        scan_time=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        readiness=readiness,
        score=score,
        issues=issues,
        migration_blockers=blockers,
        suggested_patch_files=suggested_patch_files(issues),
        next_steps=build_next_steps(issues),
        what_the_tool_does_not_guarantee=[
            "It does not prove production readiness.",
            "It does not execute or call Gemini APIs.",
            "It does not verify security, privacy, legal, or compliance posture.",
            "It does not guarantee that suggested patches are sufficient for your app architecture.",
        ],
    )
