"""Citation metadata model for Knowledge Metadata Engine."""

from __future__ import annotations

from dataclasses import dataclass

from models.base import BaseModel


@dataclass(slots=True)
class KnowledgeCitationMetadata(BaseModel):
    """Citation enrichment record built from semantic search results."""

    query_text: str = ""
    source_knowledge_document_id: int | None = None
    source_chunk_id: int | None = None
    title: str | None = None
    document_number: str | None = None
    document_type: str | None = None
    authority_level: str | None = None
    validity_status: str | None = None
    issued_date: str | None = None
    page: int | None = None
    section: str | None = None
    file_path: str | None = None
    checksum: str | None = None
    score: float = 0.0
    citation_json: str | None = None
    created_at: str | None = None

    def __post_init__(self) -> None:
        self.query_text = self.query_text.strip()
        if self.source_knowledge_document_id is not None and self.source_knowledge_document_id <= 0:
            raise ValueError("source_knowledge_document_id phai lon hon 0")
        if self.source_chunk_id is not None and self.source_chunk_id <= 0:
            raise ValueError("source_chunk_id phai lon hon 0")
        if self.score < 0:
            raise ValueError("score khong duoc am")
