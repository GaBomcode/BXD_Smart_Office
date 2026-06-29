"""Metadata models for Knowledge Metadata Engine."""

from __future__ import annotations

from dataclasses import dataclass

from models.base import BaseModel


@dataclass(slots=True)
class KnowledgeMetadata(BaseModel):
    """Normalized metadata derived from an indexed knowledge document."""

    knowledge_document_id: int | None = None
    library_document_id: int | None = None
    title: str = ""
    document_number: str | None = None
    document_type: str | None = None
    normalized_type: str | None = None
    field: str | None = None
    issuing_agency: str | None = None
    signer: str | None = None
    issued_date: str | None = None
    effective_date: str | None = None
    expiry_date: str | None = None
    authority_level: str = "unknown"
    authority_score: float = 0.0
    validity_status: str = "unknown"
    validity_reason: str | None = None
    source_checksum: str | None = None
    metadata_hash: str | None = None
    metadata_json: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        self.authority_level = self.authority_level.strip() or "unknown"
        self.validity_status = self.validity_status.strip() or "unknown"
        if self.knowledge_document_id is not None and self.knowledge_document_id <= 0:
            raise ValueError("knowledge_document_id phai lon hon 0")
        if self.library_document_id is not None and self.library_document_id <= 0:
            raise ValueError("library_document_id phai lon hon 0")
        if not 0 <= self.authority_score <= 1:
            raise ValueError("authority_score phai nam trong khoang 0..1")
