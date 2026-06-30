"""Recommendation model for Advisory Report Engine."""

from __future__ import annotations

from dataclasses import dataclass, field

from models.report_evidence import ReportEvidence


@dataclass(slots=True)
class ReportRecommendation:
    """Evidence-backed advisory recommendation."""

    title: str
    reason: str
    supporting_evidence: list[ReportEvidence]
    confidence_score: float
    affected_documents: list[int] = field(default_factory=list)
    affected_tasks: list[int] = field(default_factory=list)
    priority: str = "medium"

    def to_dict(self) -> dict[str, object]:
        """Serialize recommendation to a plain dictionary."""
        return {
            "title": self.title,
            "reason": self.reason,
            "supporting_evidence": [item.to_dict() for item in self.supporting_evidence],
            "confidence_score": self.confidence_score,
            "affected_documents": self.affected_documents,
            "affected_tasks": self.affected_tasks,
            "priority": self.priority,
        }
