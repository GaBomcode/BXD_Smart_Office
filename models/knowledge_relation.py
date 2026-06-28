"""Model relation tri thức."""

from __future__ import annotations

from dataclasses import dataclass

from models.base import BaseModel


KNOWLEDGE_RELATION_TYPES = {"replaces", "references", "follows", "implements", "reports", "related"}


@dataclass(slots=True)
class KnowledgeRelation(BaseModel):
    """Quan hệ giữa tài liệu/entity trong Knowledge Engine."""

    source_document_id: int | None = None
    target_document_id: int | None = None
    source_entity_id: int | None = None
    target_entity_id: int | None = None
    relation_type: str = "related"
    weight: float = 1
    confidence: float = 1
    is_bidirectional: int = 0
    evidence: str | None = None
    source: str = "rule"
    created_at: str | None = None

    def __post_init__(self) -> None:
        self.relation_type = self.relation_type.strip() or "related"
        self.source = self.source.strip() or "rule"
        if self.relation_type not in KNOWLEDGE_RELATION_TYPES:
            raise ValueError(f"relation_type không hợp lệ: {self.relation_type}")
        if self.weight <= 0:
            raise ValueError("weight phải lớn hơn 0")
        if self.confidence <= 0:
            raise ValueError("confidence phải lớn hơn 0")
        self.is_bidirectional = 1 if self.is_bidirectional else 0
