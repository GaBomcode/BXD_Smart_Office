"""Kiểm thử tầng dữ liệu phân hệ Soạn thảo văn bản."""

from pathlib import Path

from database.connection import get_connection
from database.init_db import init_database
from models import DocumentDraft, DocumentSection, DocumentTemplate
from repositories.document_repository import DocumentRepository
from services.document_service import DocumentService
from services.template_service import TemplateService


def test_document_migration_creates_tables() -> None:
    """Migration 003 phải tạo đủ bảng tài liệu và được ghi nhận."""
    init_database()
    with get_connection() as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        migrations = {row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}
    assert "document_templates" in tables
    assert "document_sections" in tables
    assert "document_drafts" in tables
    assert "document_settings" in tables
    assert "003_document_module" in migrations
    assert "004_document_settings" in migrations


def test_document_repository_crud_template_section_and_draft(tmp_path: Path) -> None:
    """Repository phải tạo/đọc/sửa/xóa được mẫu, section và dự thảo."""
    init_database()
    sample = tmp_path / "mau_cong_van.docx"
    sample.write_text("Mẫu công văn kiểm thử", encoding="utf-8")

    repo = DocumentRepository()
    template_id = repo.create_template(
        DocumentTemplate(
            name="Mẫu công văn kiểm thử",
            source_path=str(sample),
            file_ext=".docx",
            file_size=sample.stat().st_size,
        )
    )
    assert template_id > 0
    template = repo.get_template(template_id)
    assert template is not None
    assert template["document_type"] == "Công văn"

    repo.replace_sections(
        template_id,
        [
            DocumentSection(section_type="Tiêu đề", title="Tên văn bản", content="CÔNG VĂN"),
            DocumentSection(section_type="Nội dung", title="Nội dung chính", content="Kính gửi..."),
        ],
    )
    sections = repo.list_sections(template_id)
    assert len(sections) == 2
    assert sections[0]["section_type"] == "Tiêu đề"

    draft_id = repo.create_draft(DocumentDraft(title="Dự thảo công văn", template_id=template_id))
    assert draft_id > 0
    repo.update_draft(draft_id, {"draft_content": "Nội dung dự thảo", "status": "Chờ duyệt"})
    draft = repo.get_draft(draft_id)
    assert draft is not None
    assert draft["status"] == "Chờ duyệt"

    assert repo.delete_draft(draft_id) >= 0
    assert repo.delete_template(template_id) >= 0


def test_document_service_registers_template_and_creates_draft(tmp_path: Path) -> None:
    """Service phải kiểm tra nghiệp vụ trước khi ghi dữ liệu."""
    init_database()
    sample = tmp_path / "bao_cao_mau.pdf"
    sample.write_bytes(b"%PDF-1.4 test")

    service = DocumentService()
    template_id = service.register_template(
        name="Báo cáo mẫu",
        source_path=str(sample),
        document_type="Báo cáo",
        field="Tuyên giáo",
    )
    assert service.get_template(template_id)["field"] == "Tuyên giáo"  # type: ignore[index]

    service.add_sections(
        template_id,
        [DocumentSection(section_type="Nơi nhận", content="Như trên")],
    )
    assert len(service.list_sections(template_id)) == 1

    draft_id = service.create_draft(title="Dự thảo báo cáo", template_id=template_id, request_text="Soạn báo cáo tháng")
    assert draft_id > 0
    service.update_draft_content(draft_id, "Nội dung dự thảo báo cáo")
    drafts = service.list_drafts(status="Chờ duyệt")
    assert len(drafts) == 1


def test_template_service_rejects_unsupported_extension(tmp_path: Path) -> None:
    """Không ghi nhận file ngoài DOC/DOCX/PDF."""
    init_database()
    sample = tmp_path / "khong_ho_tro.txt"
    sample.write_text("test", encoding="utf-8")

    service = TemplateService()
    try:
        service.register_existing_file(sample)
    except ValueError as exc:
        assert "DOC" in str(exc)
    else:
        raise AssertionError("File TXT phải bị từ chối")
