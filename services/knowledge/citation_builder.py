"""Citation builder for full-text Knowledge handoff."""

from __future__ import annotations

from typing import Any
import json

from models.knowledge_citation_metadata import KnowledgeCitationMetadata
from repositories.knowledge_repository import KnowledgeRepository


class CitationBuilder:
    """Build citation metadata records without search logic."""

    def __init__(self, repository: KnowledgeRepository | None = None) -> None:
        self.repository = repository or KnowledgeRepository()

    @staticmethod
    def query_key(knowledge_document_id: int) -> str:
        return f"handoff:{knowledge_document_id}"

    def build(self, knowledge_document_id: int) -> list[int]:
        """Create citation records for every chunk of one knowledge document."""
        document = self.repository.get_document(knowledge_document_id)
        if not document:
            raise ValueError("knowledge document not found")
        citation_ids: list[int] = []
        query_text = self.query_key(knowledge_document_id)
        for chunk in self.repository.list_chunks(knowledge_document_id):
            payload: dict[str, Any] = {
                "document_id": knowledge_document_id,
                "chunk_id": chunk.get("id"),
                "chunk_order": chunk.get("chunk_order"),
                "section": chunk.get("section"),
                "checksum": document.get("checksum") or document.get("source_checksum"),
            }
            citation_ids.append(
                self.repository.add_citation_metadata(
                    KnowledgeCitationMetadata(
                        query_text=query_text,
                        source_knowledge_document_id=knowledge_document_id,
                        source_chunk_id=int(chunk["id"]),
                        title=document.get("title"),
                        document_number=document.get("document_number"),
                        document_type=document.get("document_type"),
                        page=chunk.get("page"),
                        section=chunk.get("section"),
                        file_path=document.get("source_path"),
                        checksum=document.get("checksum") or document.get("source_checksum"),
                        score=1.0,
                        citation_json=json.dumps(payload, ensure_ascii=False),
                    )
                )
            )
        return citation_ids
