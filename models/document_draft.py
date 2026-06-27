"""Model dự thảo văn bản cho Sprint 3."""

from __future__ import annotations

from dataclasses import dataclass
from models.base import BaseModel


@dataclass(slots=True)
class DocumentDraft(BaseModel):
    """Dự thảo văn bản do người dùng hoặc AI tham mưu tạo ra."""

    title: str = ""
    document_type: str = "Công văn"
    template_id: int | None = None
    workspace_id: int | None = None
    request_text: str | None = None
    draft_content: str | None = None
    status: str = "Nháp"
    created_by: str = "Nguyễn Trung Hiền"
    created_at: str | None = None
    updated_at: str | None = None
