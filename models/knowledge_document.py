"""Knowledge document model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json
import logging

from models.base import BaseModel

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class KnowledgeDocument(BaseModel):
    """Knowledge representation of one document library record."""

    document_id: int | None = None
    library_document_id: int | None = None
    title: str = ""
    full_text: str | None = None
    checksum: str | None = None
    chunk_count: int = 0
    embedding_version: str | None = None
    indexed_time: str | None = None
    source_path: str | None = None
    document_type: str | None = None
    document_number: str | None = None
    field: str | None = None
    status: str = "ready"
    source_checksum: str | None = None
    indexed_checksum: str | None = None
    last_indexed_at: str | None = None
    metadata_json: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        self.full_text = self.full_text.strip() if self.full_text else None
        self.status = self.status.strip() or "ready"
        if self.document_id is not None and self.document_id <= 0:
            raise ValueError("document_id must be greater than 0")
        if self.library_document_id is not None and self.library_document_id <= 0:
            raise ValueError("library_document_id must be greater than 0")
        if not self.title:
            raise ValueError("title is required")
        if self.full_text is not None and not self.full_text:
            raise ValueError("full_text cannot be empty")
        if self.chunk_count < 0:
            raise ValueError("chunk_count cannot be negative")
        logger.debug("Validated knowledge document title=%s status=%s", self.title, self.status)

    @classmethod
    def from_library_document(
        cls,
        document: dict[str, Any],
        *,
        full_text: str | None = None,
        chunk_count: int = 0,
        status: str = "ready",
    ) -> "KnowledgeDocument":
        """Build a knowledge document from one document library row."""
        metadata = {
            key: document.get(key)
            for key in ("summary", "keywords", "issued_date", "issuing_agency", "signer", "file_ext", "checksum")
        }
        source_id = int(document["id"])
        checksum = document.get("checksum")
        return cls(
            document_id=source_id,
            library_document_id=source_id,
            title=str(document.get("title") or document.get("file_name") or "Van ban"),
            full_text=full_text,
            checksum=checksum,
            chunk_count=chunk_count,
            source_path=document.get("file_path"),
            document_type=document.get("document_type"),
            document_number=document.get("document_number"),
            field=document.get("field"),
            status=status,
            source_checksum=checksum,
            indexed_checksum=checksum,
            metadata_json=json.dumps(metadata, ensure_ascii=False),
        )
