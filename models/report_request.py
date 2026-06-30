"""Report request model for Advisory Report Engine."""

from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_REPORT_TYPES = {
    "weekly",
    "monthly",
    "quarterly",
    "topic",
    "work_dossier",
}


@dataclass(slots=True)
class ReportRequest:
    """Operator request for an advisory report."""

    report_type: str
    title: str
    workspace_id: int | None = None
    topic: str | None = None
    period_start: str | None = None
    period_end: str | None = None
    requested_by: str = "Nguoi dung"

    def normalized_type(self) -> str:
        """Return normalized report type."""
        return self.report_type.strip().lower()

    def validate(self) -> list[str]:
        """Return request validation errors."""
        errors: list[str] = []
        if self.normalized_type() not in SUPPORTED_REPORT_TYPES:
            errors.append("Unsupported report type")
        if not self.title.strip():
            errors.append("Report title is required")
        if self.normalized_type() in {"topic", "work_dossier"} and not (self.topic or "").strip():
            errors.append("Topic is required for this report type")
        if self.workspace_id is not None and self.workspace_id <= 0:
            errors.append("workspace_id must be greater than 0")
        return errors
