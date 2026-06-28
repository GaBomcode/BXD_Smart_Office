"""Kiểm thử tích hợp index kho văn bản Sprint 4."""

from pathlib import Path

from database.init_db import init_database
from services.document_library_service import DocumentLibraryService


def test_index_folder_persists_documents_and_updates_changed_file(tmp_path: Path) -> None:
    init_database()
    root = tmp_path / "library"
    root.mkdir()
    document = root / "15-CV-BXD.txt"
    document.write_text(
        """
        ĐẢNG ỦY XÃ VĨNH HÒA
        BAN XÂY DỰNG ĐẢNG
        Số: 15-CV/BXD
        Vĩnh Hòa, ngày 12 tháng 5 năm 2026
        CÔNG VĂN
        V/v phối hợp báo cáo công tác tổ chức cán bộ
        TRƯỞNG BAN
        Nguyễn Trung Hiền
        """,
        encoding="utf-8",
    )

    service = DocumentLibraryService()
    result = service.index_folder(root)
    assert result["counts"]["need_review"] == 1
    records = service.list_documents(keyword="15-CV")
    assert len(records) == 1
    assert records[0]["document_number"] == "15-CV/BXD"

    document.write_text("Số: 16-CV/BXD\nCÔNG VĂN\nV/v báo cáo tuyên giáo", encoding="utf-8")
    changed = service.index_folder(root)
    assert changed["scan"]["changed_files"] == 1
    updated = service.list_documents(keyword="16-CV")
    assert len(updated) == 1


def test_review_workflow_updates_metadata_and_audit(tmp_path: Path) -> None:
    init_database()
    root = tmp_path / "library"
    root.mkdir()
    document = root / "review.txt"
    document.write_text("Số: 01-TB/BXD\nTHÔNG BÁO\nNội dung cần duyệt", encoding="utf-8")
    service = DocumentLibraryService()
    service.index_folder(root)
    record = service.list_documents(status="need_review")[0]

    service.update_review_metadata(
        int(record["id"]),
        {
            "title": "Thông báo đã duyệt",
            "document_type": "Thông báo",
            "document_number": "01-TB/BXD",
            "keywords": "thông báo, duyệt",
            "field": "Tổng hợp",
            "status": "indexed",
        },
    )
    updated = service.get_document(int(record["id"]))
    assert updated is not None
    assert updated["status"] == "indexed"
    assert updated["title"] == "Thông báo đã duyệt"
