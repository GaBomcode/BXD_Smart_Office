"""Service chuyên xử lý kho mẫu văn bản.

Hiện tại lớp này bọc DocumentService để giữ ranh giới nghiệp vụ. Các patch sau
sẽ bổ sung đọc DOCX/PDF, phân tích thể thức và học văn phong tại đây.
"""

from __future__ import annotations

from pathlib import Path
import logging

from services.document_service import DocumentService

logger = logging.getLogger(__name__)


class TemplateService:
    """API nghiệp vụ cấp cao cho thao tác mẫu văn bản."""

    def __init__(self, document_service: DocumentService | None = None) -> None:
        self.document_service = document_service or DocumentService()

    def upload_template_file(
        self,
        file_path: str | Path,
        *,
        document_type: str = "Công văn",
        field: str | None = None,
        created_by: str = "Nguyễn Trung Hiền",
    ) -> int:
        """Upload file vào kho mẫu và đăng ký mẫu văn bản."""
        path = Path(file_path)
        logger.info("Upload template file: %s", path)
        return self.document_service.upload_template_file(
            path,
            document_type=document_type,
            field=field,
            created_by=created_by,
        )

    def register_existing_file(
        self,
        file_path: str | Path,
        *,
        document_type: str = "Công văn",
        field: str | None = None,
        created_by: str = "Nguyễn Trung Hiền",
    ) -> int:
        """Đăng ký một file mẫu đã tồn tại trên ổ đĩa."""
        path = Path(file_path)
        logger.info("Register template file: %s", path)
        return self.document_service.register_template(
            name=path.stem,
            source_path=str(path),
            document_type=document_type,
            field=field,
            created_by=created_by,
        )

    def list_all(self) -> list[dict]:
        """Liệt kê toàn bộ mẫu văn bản."""
        return self.document_service.list_templates()
