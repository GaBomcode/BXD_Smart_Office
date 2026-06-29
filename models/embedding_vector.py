"""Embedding vector model for Knowledge chunks."""

from __future__ import annotations

from dataclasses import dataclass

from models.base import BaseModel


@dataclass(slots=True)
class EmbeddingVector(BaseModel):
    """Stored embedding result for one knowledge chunk."""

    chunk_id: int | None = None
    document_id: int | None = None
    embedding_model: str = ""
    embedding_provider: str = ""
    vector_json: str | None = None
    vector_dimension: int = 0
    chunk_checksum: str = ""
    status: str = "completed"
    error_message: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self) -> None:
        self.embedding_model = self.embedding_model.strip()
        self.embedding_provider = self.embedding_provider.strip()
        self.chunk_checksum = self.chunk_checksum.strip()
        self.status = self.status.strip() or "pending"
        if self.chunk_id is not None and self.chunk_id <= 0:
            raise ValueError("chunk_id must be greater than 0")
        if self.document_id is not None and self.document_id <= 0:
            raise ValueError("document_id must be greater than 0")
        if not self.embedding_model:
            raise ValueError("embedding_model is required")
        if not self.embedding_provider:
            raise ValueError("embedding_provider is required")
        if self.vector_dimension < 0:
            raise ValueError("vector_dimension cannot be negative")
        if not self.chunk_checksum:
            raise ValueError("chunk_checksum is required")
        if self.status not in {"pending", "completed", "failed", "skipped"}:
            raise ValueError("status is invalid")
