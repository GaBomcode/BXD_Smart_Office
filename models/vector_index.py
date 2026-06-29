"""Vector index model for Knowledge embeddings."""

from __future__ import annotations

from dataclasses import dataclass

from models.base import BaseModel


@dataclass(slots=True)
class VectorIndex(BaseModel):
    """Index metadata for one stored embedding vector."""

    embedding_id: int | None = None
    chunk_id: int | None = None
    document_id: int | None = None
    dimension: int = 0
    checksum: str = ""
    norm: float = 0.0
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self) -> None:
        self.checksum = self.checksum.strip()
        if self.embedding_id is not None and self.embedding_id <= 0:
            raise ValueError("embedding_id must be greater than 0")
        if self.chunk_id is not None and self.chunk_id <= 0:
            raise ValueError("chunk_id must be greater than 0")
        if self.document_id is not None and self.document_id <= 0:
            raise ValueError("document_id must be greater than 0")
        if self.dimension < 0:
            raise ValueError("dimension cannot be negative")
        if not self.checksum:
            raise ValueError("checksum is required")
        if self.norm < 0:
            raise ValueError("norm cannot be negative")
