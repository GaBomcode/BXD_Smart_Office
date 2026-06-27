"""Model mẫu văn bản cho Sprint 3."""

from __future__ import annotations

from dataclasses import dataclass
from models.base import BaseModel


@dataclass(slots=True)
class DocumentTemplate(BaseModel):
    """Mẫu văn bản được nạp để hệ thống học thể thức và văn phong."""

    name: str = ""
    document_type: str = "Công văn"
    source_path: str = ""
    file_ext: str = ""
    file_size: int = 0
    status: str = "Mới nạp"
    summary: str | None = None
    keywords: str | None = None
    created_by: str = "Nguyễn Trung Hiền"
    created_at: str | None = None
    updated_at: str | None = None
