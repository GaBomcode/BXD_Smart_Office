"""Model đoạn/bố cục trong mẫu văn bản."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from models.base import BaseModel

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DocumentSection(BaseModel):
    """Một phần cấu trúc được trích ra từ mẫu văn bản."""

    template_id: int | None = None
    section_order: int = 0
    section_type: str = "Nội dung"
    title: str | None = None
    content: str | None = None
    style_name: str | None = None
    metadata_json: str | None = None
    created_at: str | None = None

    def __post_init__(self) -> None:
        """Kiểm tra thứ tự và loại section."""
        self.section_type = self.section_type.strip() or "Nội dung"
        if self.section_order < 0:
            logger.error("section_order không hợp lệ: %s", self.section_order)
            raise ValueError("section_order không được âm")
        if self.template_id is not None and self.template_id <= 0:
            logger.error("template_id không hợp lệ: %s", self.template_id)
            raise ValueError("template_id phải lớn hơn 0")
