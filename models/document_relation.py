"""Model quan hệ giữa các văn bản trong kho."""

from __future__ import annotations

from dataclasses import dataclass

from models.base import BaseModel


@dataclass(slots=True)
class DocumentRelation(BaseModel):
    """Quan hệ nghiệp vụ giữa hai văn bản."""

    source_document_id: int | None = None
    target_document_id: int | None = None
    relation_type: str = ""
    note: str | None = None
    created_at: str | None = None

    def __post_init__(self) -> None:
        self.relation_type = self.relation_type.strip()
        if self.source_document_id is not None and self.source_document_id <= 0:
            raise ValueError("source_document_id phải lớn hơn 0")
        if self.target_document_id is not None and self.target_document_id <= 0:
            raise ValueError("target_document_id phải lớn hơn 0")
        if self.source_document_id and self.target_document_id and self.source_document_id == self.target_document_id:
            raise ValueError("Không tạo quan hệ văn bản với chính nó")
        if not self.relation_type:
            raise ValueError("relation_type là bắt buộc")
