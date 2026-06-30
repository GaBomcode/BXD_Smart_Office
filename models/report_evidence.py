"""Evidence model for Advisory Report Engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ReportEvidence:
    """Traceable evidence item used by advisory report statements."""

    source_type: str
    source_id: int
    title: str
    excerpt: str
    citation: str
    metadata: dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Serialize evidence to a plain dictionary."""
        return {
            "source_type": self.source_type,
            "source_id": self.source_id,
            "title": self.title,
            "excerpt": self.excerpt,
            "citation": self.citation,
            "metadata": self.metadata,
            "confidence": self.confidence,
        }
