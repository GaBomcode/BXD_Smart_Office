"""Model văn bản trong kho văn bản."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from models.base import BaseModel

logger = logging.getLogger(__name__)

DOCUMENT_LIBRARY_STATUSES = {
    "new",
    "indexed",
    "failed",
    "need_ocr",
    "need_review",
    "duplicate",
    "unsupported",
    "deleted",
}


@dataclass(slots=True)
class LibraryDocument(BaseModel):
    """Thông tin chỉ mục của một văn bản/tệp trong kho văn bản."""

    title: str = ""
    file_name: str = ""
    file_path: str = ""
    file_ext: str = ""
    file_size: int = 0
    checksum: str = ""
    document_type: str | None = None
    document_number: str | None = None
    issued_date: str | None = None
    issuing_agency: str | None = None
    signer: str | None = None
    summary: str | None = None
    keywords: str | None = None
    field: str | None = None
    status: str = "new"
    indexed_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self) -> None:
        """Chuẩn hóa dữ liệu tối thiểu trước khi ghi repository."""
        self.title = self.title.strip() or self.file_name.strip()
        self.file_name = self.file_name.strip()
        self.file_path = self.file_path.strip()
        self.file_ext = self.file_ext.lower().strip()
        self.checksum = self.checksum.strip()
        self.status = self.status.strip() or "new"
        if not self.file_name:
            raise ValueError("file_name là bắt buộc")
        if not self.file_path:
            raise ValueError("file_path là bắt buộc")
        if self.file_size < 0:
            logger.error("file_size không hợp lệ: %s", self.file_size)
            raise ValueError("file_size không được âm")
        if not self.checksum:
            raise ValueError("checksum là bắt buộc")
        if self.status not in DOCUMENT_LIBRARY_STATUSES:
            raise ValueError(f"Trạng thái văn bản không hợp lệ: {self.status}")
