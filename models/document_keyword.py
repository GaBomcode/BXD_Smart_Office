"""Model từ khóa gắn với văn bản trong kho."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from models.base import BaseModel

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DocumentKeyword(BaseModel):
    """Một từ khóa được trích hoặc người dùng duyệt cho văn bản."""

    document_id: int | None = None
    keyword: str = ""
    weight: float = 1
    created_at: str | None = None

    def __post_init__(self) -> None:
        self.keyword = self.keyword.strip()
        if self.document_id is not None and self.document_id <= 0:
            raise ValueError("document_id phải lớn hơn 0")
        if not self.keyword:
            raise ValueError("keyword là bắt buộc")
        if self.weight <= 0:
            logger.error("weight không hợp lệ: %s", self.weight)
            raise ValueError("weight phải lớn hơn 0")
