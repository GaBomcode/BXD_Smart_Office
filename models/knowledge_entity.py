"""Model entity tri thức."""

from __future__ import annotations

from dataclasses import dataclass

from models.base import BaseModel


@dataclass(slots=True)
class KnowledgeEntity(BaseModel):
    """Entity rule-based sinh từ văn bản/chunk."""

    document_id: int | None = None
    chunk_id: int | None = None
    entity_type: str = ""
    entity_value: str = ""
    weight: float = 1
    source: str = "rule"
    created_at: str | None = None

    def __post_init__(self) -> None:
        self.entity_type = self.entity_type.strip()
        self.entity_value = self.entity_value.strip()
        self.source = self.source.strip() or "rule"
        if not self.entity_type:
            raise ValueError("entity_type là bắt buộc")
        if not self.entity_value:
            raise ValueError("entity_value là bắt buộc")
        if self.weight <= 0:
            raise ValueError("weight phải lớn hơn 0")
