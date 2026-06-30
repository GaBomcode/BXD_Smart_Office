"""Report result models for Advisory Report Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from models.report_evidence import ReportEvidence
from models.report_recommendation import ReportRecommendation
from models.report_request import ReportRequest
from models.report_section import ReportSection


@dataclass(slots=True)
class ReportValidationResult:
    """Validation result for advisory reports."""

    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize validation result."""
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
        }


@dataclass(slots=True)
class ReportResult:
    """Generated advisory report object awaiting human review."""

    request: ReportRequest
    sections: list[ReportSection]
    recommendations: list[ReportRecommendation]
    evidence: list[ReportEvidence]
    validation: ReportValidationResult
    report_id: int | None = None
    status: str = "pending_human_review"
    export_ready: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Serialize report result."""
        return {
            "report_id": self.report_id,
            "request": {
                "report_type": self.request.report_type,
                "title": self.request.title,
                "workspace_id": self.request.workspace_id,
                "topic": self.request.topic,
                "period_start": self.request.period_start,
                "period_end": self.request.period_end,
                "requested_by": self.request.requested_by,
            },
            "sections": [section.to_dict() for section in self.sections],
            "recommendations": [item.to_dict() for item in self.recommendations],
            "evidence": [item.to_dict() for item in self.evidence],
            "validation": self.validation.to_dict(),
            "status": self.status,
            "export_ready": self.export_ready,
        }


@dataclass(slots=True)
class ExportReadyReport:
    """Human-approved report object for the existing export layer."""

    report_id: int
    title: str
    payload: dict[str, Any]
    approved_by: str

    def to_dict(self) -> dict[str, Any]:
        """Serialize export-ready report."""
        return {
            "report_id": self.report_id,
            "title": self.title,
            "payload": self.payload,
            "approved_by": self.approved_by,
            "export_ready": True,
        }
