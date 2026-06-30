"""Report section model for Advisory Report Engine."""

from __future__ import annotations

from dataclasses import dataclass, field

from models.report_evidence import ReportEvidence


@dataclass(slots=True)
class ReportSection:
    """A report section containing only evidence-backed statements."""

    title: str
    statements: list[str] = field(default_factory=list)
    evidence: list[ReportEvidence] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        """Serialize section to a plain dictionary."""
        return {
            "title": self.title,
            "statements": self.statements,
            "evidence": [item.to_dict() for item in self.evidence],
        }
