"""Kiểm thử nền kiến trúc Build 0.2.3."""

from database.connection import get_connection
from database.init_db import init_database
from core.config import (
    ATTACHMENT_DIR,
    CACHE_DIR,
    DOCUMENT_DRAFT_DIR,
    DOCUMENT_EXPORT_DIR,
    DOCUMENT_TEMPLATE_DIR,
    TEMP_DIR,
)
from models import DocumentDraft, DocumentTemplate, Staff, Task, Workspace


def test_runtime_directories_exist() -> None:
    """Các thư mục runtime cốt lõi phải được tạo sẵn khi import config."""
    for path in [DOCUMENT_TEMPLATE_DIR, DOCUMENT_DRAFT_DIR, DOCUMENT_EXPORT_DIR, ATTACHMENT_DIR, CACHE_DIR, TEMP_DIR]:
        assert path.exists()
        assert path.is_dir()


def test_models_can_convert_to_dict() -> None:
    """Model nền phải có thể chuyển sang dict để truyền qua repository/service."""
    staff = Staff(full_name="Nguyễn Trung Hiền", position="Trưởng Ban", system_role="Trưởng Ban")
    task = Task(title="Kiểm thử model nhiệm vụ", progress=20)
    workspace = Workspace(name="Hồ sơ kiểm thử")
    template = DocumentTemplate(name="Mẫu công văn", source_path="documents/templates/mau.docx")
    draft = DocumentDraft(title="Dự thảo công văn", template_id=1)

    assert staff.can_assign_task is True
    assert task.to_dict()["title"] == "Kiểm thử model nhiệm vụ"
    assert workspace.to_dict()["status"] == "Đang xử lý"
    assert template.to_dict()["document_type"] == "Công văn"
    assert draft.to_dict()["status"] == "Nháp"


def test_sql_migrations_are_applied() -> None:
    """Migration SQL phải được ghi nhận để các commit sau nâng cấp an toàn."""
    init_database()
    with get_connection() as conn:
        migrations = {row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}
        indexes = {row[1] for row in conn.execute("PRAGMA index_list('tasks')").fetchall()}
    assert "002_architecture_hardening" in migrations
    assert "idx_tasks_status" in indexes
