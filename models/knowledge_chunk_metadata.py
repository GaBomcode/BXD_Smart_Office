"""Metadata model for rule-based knowledge chunks."""

from __future__ import annotations

from dataclasses import dataclass

from models.base import BaseModel


@dataclass(slots=True)
class KnowledgeChunkMetadata(BaseModel):
    """Persistent lineage and token metadata for one knowledge chunk."""

    chunk_id: int | None = None
    document_id: int | None = None
    chunk_uid: str = ""
    text_hash: str = ""
    start_token: int = 0
    end_token: int = 0
    overlap_tokens: int = 0
    overlap_with_previous: int = 0
    source_engine: str = "rule_chunk_v1"
    metadata_json: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self) -> None:
        self.chunk_uid = self.chunk_uid.strip()
        self.text_hash = self.text_hash.strip()
        self.source_engine = self.source_engine.strip() or "rule_chunk_v1"
        if self.chunk_id is not None and self.chunk_id <= 0:
            raise ValueError("chunk_id must be greater than 0")
        if self.document_id is not None and self.document_id <= 0:
            raise ValueError("document_id must be greater than 0")
        if not self.chunk_uid:
            raise ValueError("chunk_uid is required")
        if not self.text_hash:
            raise ValueError("text_hash is required")
        if self.start_token < 0 or self.end_token < 0:
            raise ValueError("token offsets cannot be negative")
        if self.end_token < self.start_token:
            raise ValueError("end_token must be greater than or equal to start_token")
        if self.overlap_tokens < 0:
            raise ValueError("overlap_tokens cannot be negative")
        if self.overlap_with_previous not in (0, 1):
            raise ValueError("overlap_with_previous must be 0 or 1")
