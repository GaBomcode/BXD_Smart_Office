"""Model dự thảo văn bản cho phân hệ Soạn thảo văn bản."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from models.base import BaseModel

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DocumentDraft(BaseModel):
    """Dự thảo văn bản do người dùng hoặc AI tham mưu tạo ra."""

    title: str = ""
    document_type: str = "Công văn"
    template_id: int | None = None
    workspace_id: int | None = None
    request_text: str | None = None
    draft_content: str | None = None
    output_path: str | None = None
    status: str = "Nháp"
    review_note: str | None = None
    created_by: str = "Nguyễn Trung Hiền"
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self) -> None:
        """Chuẩn hóa và kiểm tra dữ liệu dự thảo."""
        self.title = self.title.strip()
        self.document_type = self.document_type.strip() or "Công văn"
        self.status = self.status.strip() or "Nháp"
        self.created_by = self.created_by.strip() or "Người dùng"
        if self.template_id is not None and self.template_id <= 0:
            logger.error("template_id không hợp lệ: %s", self.template_id)
            raise ValueError("template_id phải lớn hơn 0")
        if self.workspace_id is not None and self.workspace_id <= 0:
            logger.error("workspace_id không hợp lệ: %s", self.workspace_id)
            raise ValueError("workspace_id phải lớn hơn 0")

    @property
    def is_reviewable(self) -> bool:
        """Cho biết dự thảo đã có nội dung để người dùng xem/duyệt."""
        return bool(self.title and self.draft_content)
