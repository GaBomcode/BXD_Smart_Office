"""Repository cho phân hệ Soạn thảo văn bản."""

from __future__ import annotations

from typing import Any
import logging

from models.document_draft import DocumentDraft
from models.document_section import DocumentSection
from models.document_template import DocumentTemplate
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class DocumentRepository(BaseRepository):
    """Đọc/ghi mẫu văn bản, section và dự thảo trong SQLite."""

    TEMPLATE_TABLE = "document_templates"
    SECTION_TABLE = "document_sections"
    DRAFT_TABLE = "document_drafts"
    SETTING_TABLE = "document_settings"

    def create_template(self, template: DocumentTemplate) -> int:
        """Tạo mẫu văn bản mới."""
        logger.info("Create document template: %s", template.name)
        return self.insert(self.TEMPLATE_TABLE, template.to_dict())

    def get_template(self, template_id: int) -> dict[str, Any] | None:
        """Lấy mẫu văn bản theo id."""
        return self.find(self.TEMPLATE_TABLE, template_id)

    def list_templates(self, *, status: str | None = None, document_type: str | None = None) -> list[dict[str, Any]]:
        """Liệt kê mẫu văn bản, có thể lọc theo trạng thái hoặc loại văn bản."""
        clauses: list[str] = []
        params: list[Any] = []
        if status:
            clauses.append("status=?")
            params.append(status)
        if document_type:
            clauses.append("document_type=?")
            params.append(document_type)
        return self.list(
            self.TEMPLATE_TABLE,
            where=" AND ".join(clauses) if clauses else None,
            params=params,
            order_by="created_at DESC, id DESC",
        )

    def update_template(self, template_id: int, data: dict[str, Any]) -> int:
        """Cập nhật thông tin mẫu văn bản."""
        logger.info("Update document template id=%s", template_id)
        return self.update(self.TEMPLATE_TABLE, template_id, data)

    def delete_template(self, template_id: int) -> int:
        """Xóa mẫu văn bản và các section liên quan."""
        logger.info("Delete document template id=%s", template_id)
        return self.delete(self.TEMPLATE_TABLE, template_id)

    def create_section(self, section: DocumentSection) -> int:
        """Thêm section cho mẫu văn bản."""
        if section.template_id is None:
            raise ValueError("section.template_id là bắt buộc")
        return self.insert(self.SECTION_TABLE, section.to_dict())

    def list_sections(self, template_id: int) -> list[dict[str, Any]]:
        """Liệt kê section của một mẫu văn bản."""
        return self.list(
            self.SECTION_TABLE,
            where="template_id=?",
            params=(template_id,),
            order_by="section_order ASC, id ASC",
        )

    def replace_sections(self, template_id: int, sections: list[DocumentSection]) -> None:
        """Thay toàn bộ section của một mẫu văn bản."""
        if template_id <= 0:
            raise ValueError("template_id phải lớn hơn 0")
        self.execute(f"DELETE FROM {self.SECTION_TABLE} WHERE template_id=?", (template_id,))
        for order, section in enumerate(sections, start=1):
            section.template_id = template_id
            section.section_order = section.section_order or order
            self.create_section(section)

    def create_draft(self, draft: DocumentDraft) -> int:
        """Tạo dự thảo văn bản."""
        logger.info("Create document draft: %s", draft.title)
        return self.insert(self.DRAFT_TABLE, draft.to_dict())

    def get_draft(self, draft_id: int) -> dict[str, Any] | None:
        """Lấy dự thảo theo id."""
        return self.find(self.DRAFT_TABLE, draft_id)

    def list_drafts(self, *, status: str | None = None) -> list[dict[str, Any]]:
        """Liệt kê dự thảo văn bản."""
        return self.list(
            self.DRAFT_TABLE,
            where="status=?" if status else None,
            params=(status,) if status else (),
            order_by="created_at DESC, id DESC",
        )

    def update_draft(self, draft_id: int, data: dict[str, Any]) -> int:
        """Cập nhật dự thảo."""
        logger.info("Update document draft id=%s", draft_id)
        return self.update(self.DRAFT_TABLE, draft_id, data)

    def delete_draft(self, draft_id: int) -> int:
        """Xóa dự thảo."""
        logger.info("Delete document draft id=%s", draft_id)
        return self.delete(self.DRAFT_TABLE, draft_id)

    def list_settings(self) -> dict[str, str]:
        """Lấy toàn bộ cấu hình thể thức văn bản."""
        rows = self.fetch_all(f"SELECT setting_key, setting_value FROM {self.SETTING_TABLE}")
        return {str(row["setting_key"]): str(row["setting_value"]) for row in rows}

    def upsert_setting(self, key: str, value: str, description: str | None = None) -> int:
        """Tạo hoặc cập nhật một khóa cấu hình thể thức."""
        if not key.strip():
            raise ValueError("setting_key là bắt buộc")
        logger.info("Upsert document setting: %s", key)
        return self.execute(
            f"""
            INSERT INTO {self.SETTING_TABLE}(setting_key, setting_value, description)
            VALUES(?, ?, ?)
            ON CONFLICT(setting_key) DO UPDATE SET
                setting_value=excluded.setting_value,
                description=COALESCE(excluded.description, {self.SETTING_TABLE}.description),
                updated_at=CURRENT_TIMESTAMP
            """,
            (key.strip(), value.strip(), description),
        )
