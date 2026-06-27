"""Kiểm thử upload engine cho mẫu văn bản."""

from io import BytesIO
from pathlib import Path

from database.init_db import init_database
from models import DocumentUploadResult
from services.document_service import DocumentService
from services.document_upload_service import DocumentUploadService
from services.template_service import TemplateService


def test_upload_service_copies_local_docx_into_template_store(tmp_path: Path) -> None:
    """Upload engine phải sao chép DOCX vào documents/templates và trả metadata."""
    source = tmp_path / "Mẫu Công văn số 01.docx"
    source.write_bytes(b"docx-content")

    service = DocumentUploadService(template_dir=tmp_path / "templates")
    result = service.save_local_file(source)

    assert isinstance(result, DocumentUploadResult)
    assert result.file_ext == ".docx"
    assert result.file_size == len(b"docx-content")
    assert result.path.exists()
    assert result.path.read_bytes() == b"docx-content"
    assert len(result.checksum_sha256) == 64


def test_upload_service_saves_stream_pdf_and_rejects_empty_file(tmp_path: Path) -> None:
    """Upload stream phải hỗ trợ PDF và từ chối file rỗng."""
    service = DocumentUploadService(template_dir=tmp_path / "templates")
    result = service.save_uploaded_file(BytesIO(b"%PDF-1.4 demo"), "bao cao mau.pdf")
    assert result.file_ext == ".pdf"
    assert result.path.exists()

    try:
        service.save_uploaded_file(BytesIO(b""), "rong.pdf")
    except ValueError as exc:
        assert "rỗng" in str(exc)
    else:
        raise AssertionError("File rỗng phải bị từ chối")


def test_document_service_upload_template_registers_database_record(tmp_path: Path) -> None:
    """DocumentService phải upload file và tạo bản ghi document_templates."""
    init_database()
    source = tmp_path / "Ke hoach mau.docx"
    source.write_bytes(b"template-docx")

    service = DocumentService()
    template_id = service.upload_template_file(source, document_type="Kế hoạch", field="Tổ chức")
    template = service.get_template(template_id)

    assert template is not None
    assert template["document_type"] == "Kế hoạch"
    assert template["field"] == "Tổ chức"
    assert Path(template["source_path"]).exists()
    assert str(template["source_path"]).endswith(".docx")


def test_template_service_upload_rejects_unsupported_file(tmp_path: Path) -> None:
    """TemplateService không được nhận file TXT làm mẫu văn bản."""
    init_database()
    source = tmp_path / "ghi chu.txt"
    source.write_text("không phải mẫu văn bản", encoding="utf-8")

    service = TemplateService()
    try:
        service.upload_template_file(source)
    except ValueError as exc:
        assert "DOC" in str(exc)
    else:
        raise AssertionError("File TXT phải bị từ chối")
