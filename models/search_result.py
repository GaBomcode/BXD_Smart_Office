"""Search result model for the V1.0 AI Search workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class SearchResult:
    """Document retrieval result returned by keyword, semantic and hybrid search."""

    document_id: int
    title: str
    summary: str | None
    score: float
    matched_chunks: list[dict[str, Any]] = field(default_factory=list)
    citations: list[dict[str, Any]] = field(default_factory=list)
    status: str = "READY"

    def to_dict(self) -> dict[str, Any]:
        """Serialize the result for callers that expect plain dictionaries."""
        return {
            "document_id": self.document_id,
            "title": self.title,
            "summary": self.summary,
            "score": self.score,
            "matched_chunks": self.matched_chunks,
            "citations": self.citations,
            "status": self.status,
        }
