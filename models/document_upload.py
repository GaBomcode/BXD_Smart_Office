"""Model kết quả upload mẫu văn bản."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import logging

from models.document_template import ALLOWED_TEMPLATE_EXTENSIONS

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class DocumentUploadResult:
    """Thông tin file mẫu sau khi đã được lưu vào kho templates."""

    original_name: str
    stored_name: str
    stored_path: str
    file_ext: str
    file_size: int
    checksum_sha256: str

    def __post_init__(self) -> None:
        """Chuẩn hóa và kiểm tra dữ liệu upload."""
        self.original_name = self.original_name.strip()
        self.stored_name = self.stored_name.strip()
        self.stored_path = self.stored_path.strip()
        self.file_ext = self.file_ext.lower().strip()
        if not self.original_name:
            raise ValueError("Tên file gốc là bắt buộc")
        if not self.stored_name:
            raise ValueError("Tên file lưu là bắt buộc")
        if not self.stored_path:
            raise ValueError("Đường dẫn file lưu là bắt buộc")
        if self.file_ext not in ALLOWED_TEMPLATE_EXTENSIONS:
            logger.error("Định dạng upload không hỗ trợ: %s", self.file_ext)
            raise ValueError("Chỉ hỗ trợ DOC, DOCX và PDF")
        if self.file_size <= 0:
            raise ValueError("File upload phải có dung lượng lớn hơn 0")
        if len(self.checksum_sha256) != 64:
            raise ValueError("checksum_sha256 không hợp lệ")

    @property
    def path(self) -> Path:
        """Đường dẫn file đã lưu dưới dạng Path."""
        return Path(self.stored_path)
