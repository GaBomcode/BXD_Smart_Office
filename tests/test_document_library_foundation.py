"""Kiểm thử foundation phân hệ Kho văn bản Sprint 4."""

from pathlib import Path
import sqlite3

from database.connection import get_connection
from database.init_db import init_database, validate_schema
from models import DocumentKeyword, DocumentRelation, LibraryDocument
from repositories.document_library_repository import DocumentLibraryRepository
from services.document_library_service import DocumentLibraryService


def test_document_library_migration_creates_tables() -> None:
    init_database()
    with get_connection() as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        migrations = {row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}
    assert "documents" in tables
    assert "document_keywords" in tables
    assert "document_relations" in tables
    assert "005_document_library" in migrations


def test_document_library_repository_crud(tmp_path: Path) -> None:
    init_database()
    sample = tmp_path / "cong_van.txt"
    sample.write_text("Số: 01-CV/BXD\nNội dung kiểm thử", encoding="utf-8")
    service = DocumentLibraryService()
    checksum = service.calculate_checksum(sample)
    repo = DocumentLibraryRepository()

    document_id = repo.create_document(
        LibraryDocument(
            title="Công văn kiểm thử",
            file_name=sample.name,
            file_path=str(sample),
            file_ext=".txt",
            file_size=sample.stat().st_size,
            checksum=checksum,
        )
    )
    assert document_id > 0
    assert repo.get_by_path(str(sample))["id"] == document_id  # type: ignore[index]

    repo.replace_keywords(
        document_id,
        [DocumentKeyword(keyword="công văn", weight=3), DocumentKeyword(keyword="kiểm thử", weight=2)],
    )
    assert len(repo.list_keywords(document_id)) == 2

    second_id = repo.create_document(
        LibraryDocument(
            title="Văn bản liên quan",
            file_name="lien_quan.txt",
            file_path=str(tmp_path / "lien_quan.txt"),
            file_ext=".txt",
            file_size=1,
            checksum="abc",
        )
    )
    repo.create_relation(
        DocumentRelation(
            source_document_id=document_id,
            target_document_id=second_id,
            relation_type="liên quan",
        )
    )
    assert len(repo.list_relations(document_id)) == 1


def test_folder_scanner_detects_new_existing_changed_and_ignored(tmp_path: Path) -> None:
    init_database()
    source = tmp_path / "library"
    source.mkdir()
    first = source / "a.txt"
    first.write_text("noi dung", encoding="utf-8")
    ignored = source / "~$temp.docx"
    ignored.write_text("ignored", encoding="utf-8")
    unsupported = source / "image.png"
    unsupported.write_bytes(b"png")

    service = DocumentLibraryService()
    result = service.scan_folder(source)
    assert result.accepted_files == 1
    assert result.ignored_files == 1
    assert result.unsupported_files == 1
    service.register_file_metadata(result.files[0])  # type: ignore[index]

    second = service.scan_folder(source)
    assert second.existing_files == 1

    first.write_text("noi dung moi", encoding="utf-8")
    third = service.scan_folder(source)
    assert third.changed_files == 1


def test_mark_missing_files_deleted_uses_resolved_path_ownership(tmp_path: Path) -> None:
    init_database()
    root = tmp_path / "library"
    root.mkdir()
    outside = tmp_path / "library-other" / "missing.txt"
    repo = DocumentLibraryRepository()
    document_id = repo.create_document(
        LibraryDocument(
            title="Outside prefix collision",
            file_name="missing.txt",
            file_path=str(outside),
            file_ext=".txt",
            file_size=1,
            checksum="outside-checksum",
            status="indexed",
        )
    )

    deleted = DocumentLibraryService().mark_missing_files_deleted(root)
    document = repo.get_document(document_id)

    assert deleted == 0
    assert document is not None
    assert document["status"] == "indexed"


def test_schema_validation_reports_missing_required_table() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE TABLE documents(id INTEGER PRIMARY KEY)")
        try:
            validate_schema(conn)
        except RuntimeError as exc:
            assert "Missing required table" in str(exc)
        else:
            raise AssertionError("schema validation should fail for partial schema")
    finally:
        conn.close()
