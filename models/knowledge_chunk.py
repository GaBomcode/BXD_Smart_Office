"""Model chunk tri thức."""

from __future__ import annotations

from dataclasses import dataclass

from models.base import BaseModel


@dataclass(slots=True)
class KnowledgeChunk(BaseModel):
    """Một đoạn văn bản nhỏ dùng cho keyword, relation và semantic search."""

    document_id: int | None = None
    page: int = 0
    section: str = "Nội dung"
    chunk_order: int = 0
    text: str = ""
    token_count: int = 0
    embedding_json: str | None = None
    embedding_model: str | None = None
    embedding_backend: str | None = None
    embedding_version: str | None = None
    embedding_hash: str | None = None
    source_checksum: str | None = None
    embedding_updated_at: str | None = None
    created_at: str | None = None

    def __post_init__(self) -> None:
        self.section = self.section.strip() or "Nội dung"
        self.text = self.text.strip()
        if self.document_id is not None and self.document_id <= 0:
            raise ValueError("document_id phải lớn hơn 0")
        if not self.text:
            raise ValueError("text là bắt buộc")
        if self.token_count < 0:
            raise ValueError("token_count không được âm")
