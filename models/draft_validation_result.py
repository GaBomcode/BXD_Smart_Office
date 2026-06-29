"""Result model for AI Draft final validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class DraftValidationResult:
    """Validation outcome returned before AI Draft export."""

    passed: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    score: float = 1.0
    missing_sections: list[str] = field(default_factory=list)
    invalid_citations: list[str] = field(default_factory=list)
    empty_fields: list[str] = field(default_factory=list)
    report: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize validation result for service callers."""
        return {
            "passed": self.passed,
            "errors": self.errors,
            "warnings": self.warnings,
            "score": self.score,
            "missing_sections": self.missing_sections,
            "invalid_citations": self.invalid_citations,
            "empty_fields": self.empty_fields,
            "report": self.report,
        }
