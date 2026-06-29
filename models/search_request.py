"""Search request model for the V1.0 AI Search workflow."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SearchRequest:
    """User search request passed into the backend retrieval service."""

    query: str
    mode: str = "hybrid"
    top_k: int = 5
    max_query_length: int = 300

    def normalized_mode(self) -> str:
        """Return the lower-case search mode."""
        return self.mode.strip().lower()
