from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["blocker", "warning", "note"]
Readiness = Literal["READY", "READY_WITH_CAUTION", "NOT_READY"]


class Issue(BaseModel):
    rule_id: str
    title: str
    severity: Severity
    category: str
    file: str
    line_start: int
    line_end: int
    evidence_snippet: str
    why_it_matters: str
    gemini_relevance: str
    migration_advice: str
    safe_patch_available: bool
    confidence: float = Field(ge=0, le=1)


class ScanReport(BaseModel):
    target_path: str
    scan_time: str
    readiness: Readiness
    score: int = Field(ge=0, le=100)
    issues: list[Issue]
    migration_blockers: list[str]
    suggested_patch_files: list[str]
    next_steps: list[str]
    what_the_tool_does_not_guarantee: list[str]

    @property
    def blockers(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "blocker"]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "warning"]

    @property
    def notes(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "note"]
