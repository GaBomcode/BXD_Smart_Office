"""Service nghiệp vụ cho phân hệ Soạn thảo văn bản."""

from __future__ import annotations

from pathlib import Path
import logging

from core.config import DOCUMENT_TEMPLATE_DIR
from models.document_draft import DocumentDraft
from models.document_section import DocumentSection
from models.document_template import ALLOWED_TEMPLATE_EXTENSIONS, DocumentTemplate
from services.document_upload_service import DocumentUploadService
from repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)


class DocumentService:
    """Điều phối nghiệp vụ mẫu văn bản và dự thảo."""

    def __init__(self, repository: DocumentRepository | None = None) -> None:
        self.repository = repository or DocumentRepository()

    def upload_template_file(
        self,
        source_path: str | Path,
        *,
        document_type: str = "Công văn",
        field: str | None = None,
        created_by: str = "Nguyễn Trung Hiền",
    ) -> int:
        """Upload file mẫu vào kho templates rồi ghi nhận vào database."""
        upload_result = DocumentUploadService().save_local_file(source_path)
        return self.register_template(
            name=Path(upload_result.original_name).stem,
            source_path=upload_result.stored_path,
            document_type=document_type,
            field=field,
            created_by=created_by,
        )

    def register_template(
        self,
        *,
        name: str,
        source_path: str,
        document_type: str = "Công văn",
        field: str | None = None,
        created_by: str = "Nguyễn Trung Hiền",
    ) -> int:
        """Ghi nhận một mẫu văn bản đã có trong thư mục tài liệu."""
        path = Path(source_path)
        ext = path.suffix.lower()
        if ext not in ALLOWED_TEMPLATE_EXTENSIONS:
            logger.error("Không thể đăng ký mẫu do định dạng không hỗ trợ: %s", source_path)
            raise ValueError("Chỉ hỗ trợ DOC, DOCX và PDF")
        file_size = path.stat().st_size if path.exists() else 0
        template = DocumentTemplate(
            name=name or path.stem,
            document_type=document_type,
            field=field,
            source_path=str(path),
            file_ext=ext,
            file_size=file_size,
            created_by=created_by,
        )
        if not template.is_ready_for_analysis:
            raise ValueError("Mẫu văn bản chưa đủ thông tin để phân tích")
        return self.repository.create_template(template)

    def create_template_record(self, template: DocumentTemplate) -> int:
        """Tạo mẫu văn bản từ model đã được chuẩn hóa."""
        if not template.is_ready_for_analysis:
            raise ValueError("Mẫu văn bản chưa đủ thông tin")
        return self.repository.create_template(template)

    def list_templates(self, *, status: str | None = None, document_type: str | None = None) -> list[dict]:
        """Danh sách mẫu văn bản."""
        return self.repository.list_templates(status=status, document_type=document_type)

    def get_template(self, template_id: int) -> dict | None:
        """Chi tiết mẫu văn bản."""
        return self.repository.get_template(template_id)

    def mark_template_analyzed(
        self,
        template_id: int,
        *,
        summary: str | None = None,
        keywords: str | None = None,
        analysis_json: str | None = None,
    ) -> int:
        """Đánh dấu mẫu đã phân tích ở các patch Document Intelligence sau."""
        return self.repository.update_template(
            template_id,
            {
                "status": "Đã phân tích",
                "summary": summary,
                "keywords": keywords,
                "analysis_json": analysis_json,
            },
        )

    def add_sections(self, template_id: int, sections: list[DocumentSection]) -> None:
        """Lưu bố cục/section của mẫu văn bản."""
        self.repository.replace_sections(template_id, sections)

    def list_sections(self, template_id: int) -> list[dict]:
        """Danh sách section của mẫu."""
        return self.repository.list_sections(template_id)

    def create_draft(
        self,
        *,
        title: str,
        document_type: str = "Công văn",
        template_id: int | None = None,
        workspace_id: int | None = None,
        request_text: str | None = None,
        created_by: str = "Nguyễn Trung Hiền",
    ) -> int:
        """Tạo bản ghi dự thảo để người dùng/AI tiếp tục hoàn thiện."""
        draft = DocumentDraft(
            title=title,
            document_type=document_type,
            template_id=template_id,
            workspace_id=workspace_id,
            request_text=request_text,
            created_by=created_by,
        )
        if not draft.title:
            raise ValueError("Tiêu đề dự thảo là bắt buộc")
        return self.repository.create_draft(draft)

    def update_draft_content(self, draft_id: int, content: str, *, status: str = "Chờ duyệt") -> int:
        """Cập nhật nội dung dự thảo do người dùng hoặc AI tham mưu sinh ra."""
        if not content.strip():
            raise ValueError("Nội dung dự thảo không được rỗng")
        return self.repository.update_draft(draft_id, {"draft_content": content, "status": status})

    def list_drafts(self, *, status: str | None = None) -> list[dict]:
        """Danh sách dự thảo."""
        return self.repository.list_drafts(status=status)

    def ensure_template_directory(self) -> Path:
        """Đảm bảo thư mục lưu mẫu tồn tại."""
        DOCUMENT_TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        return DOCUMENT_TEMPLATE_DIR
