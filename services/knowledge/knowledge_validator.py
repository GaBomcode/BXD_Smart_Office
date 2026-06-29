"""Integrity validation for full-text Knowledge handoff."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from repositories.embedding_repository import EmbeddingRepository
from repositories.knowledge_repository import KnowledgeRepository
from services.knowledge.citation_builder import CitationBuilder

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Knowledge handoff validation result."""

    valid: bool
    missing: tuple[str, ...]


class KnowledgeValidator:
    """Validate that one knowledge document is search-ready."""

    def __init__(
        self,
        repository: KnowledgeRepository | None = None,
        embedding_repository: EmbeddingRepository | None = None,
    ) -> None:
        self.repository = repository or KnowledgeRepository()
        self.embedding_repository = embedding_repository or EmbeddingRepository()

    def validate(self, knowledge_document_id: int) -> ValidationResult:
        """Validate metadata, full text, chunks, embeddings and citations."""
        missing: list[str] = []
        document = self.repository.get_document(knowledge_document_id)
        if not document:
            return ValidationResult(valid=False, missing=("metadata", "full_text", "chunk", "embedding", "citation"))
        if not document.get("title") or not document.get("checksum"):
            missing.append("metadata")
        if not str(document.get("full_text") or "").strip():
            missing.append("full_text")
        chunks = self.repository.list_chunks(knowledge_document_id)
        if not chunks:
            missing.append("chunk")
        completed_embeddings = [self.embedding_repository.get_by_chunk_id(int(chunk["id"])) for chunk in chunks]
        if not chunks or any(not row or row.get("status") != "completed" for row in completed_embeddings):
            missing.append("embedding")
        citations = self.repository.list_citation_metadata(
            query_text=CitationBuilder.query_key(knowledge_document_id),
            limit=None,
        )
        if not citations:
            missing.append("citation")
        valid = not missing
        if not valid:
            logger.warning("Knowledge validation failed id=%s missing=%s", knowledge_document_id, missing)
        return ValidationResult(valid=valid, missing=tuple(missing))
