"""Model mẫu văn bản cho phân hệ Soạn thảo văn bản."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import logging

from models.base import BaseModel

logger = logging.getLogger(__name__)

ALLOWED_TEMPLATE_EXTENSIONS = {".doc", ".docx", ".pdf"}


@dataclass(slots=True)
class DocumentTemplate(BaseModel):
    """Mẫu văn bản được nạp để hệ thống học thể thức và văn phong."""

    name: str = ""
    document_type: str = "Công văn"
    source_path: str = ""
    file_ext: str = ""
    file_size: int = 0
    field: str | None = None
    status: str = "Mới nạp"
    summary: str | None = None
    keywords: str | None = None
    analysis_json: str | None = None
    created_by: str = "Nguyễn Trung Hiền"
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self) -> None:
        """Chuẩn hóa và kiểm tra dữ liệu tối thiểu của mẫu văn bản."""
        self.name = self.name.strip()
        self.document_type = self.document_type.strip() or "Công văn"
        self.source_path = self.source_path.strip()
        self.file_ext = (self.file_ext or Path(self.source_path).suffix).lower().strip()
        self.status = self.status.strip() or "Mới nạp"
        self.created_by = self.created_by.strip() or "Người dùng"
        if self.file_size < 0:
            logger.error("Kích thước mẫu văn bản không hợp lệ: %s", self.file_size)
            raise ValueError("file_size không được âm")
        if self.file_ext and self.file_ext not in ALLOWED_TEMPLATE_EXTENSIONS:
            logger.error("Định dạng mẫu văn bản không được hỗ trợ: %s", self.file_ext)
            raise ValueError("Chỉ hỗ trợ DOC, DOCX và PDF")

    @property
    def is_ready_for_analysis(self) -> bool:
        """Cho biết mẫu đã đủ thông tin để chuyển sang bước phân tích."""
        return bool(self.name and self.source_path and self.file_ext in ALLOWED_TEMPLATE_EXTENSIONS)
