"""Tests for RC1 TD-V1-001 full-text Knowledge handoff."""

from pathlib import Path

from database.connection import get_connection
from database.init_db import init_database
from models.knowledge_document import KnowledgeDocument
from models.library_document import LibraryDocument
from repositories.document_library_repository import DocumentLibraryRepository
from repositories.embedding_repository import EmbeddingRepository
from repositories.knowledge_repository import KnowledgeRepository
from services.document_library_service import DocumentLibraryService
from services.knowledge.citation_builder import CitationBuilder
from services.knowledge.document_snapshot import DocumentSnapshot
from services.knowledge.handoff_service import INVALID, READY, KnowledgeHandoffService
from services.knowledge.knowledge_validator import KnowledgeValidator


class NoEmbeddingService:
    """Embedding service stub used to force validation failure."""

    def generate_all(self, *, document_id: int | None = None) -> dict[str, int]:
        return {"total": 0, "completed": 0, "skipped": 0, "failed": 1}


def _library_document(path: Path, text: str = "So: 01-CV/BXD\nNoi dung to chuc can bo") -> dict:
    path.write_text(text, encoding="utf-8")
    repo = DocumentLibraryRepository()
    document_id = repo.create_document(
        LibraryDocument(
            title="Cong van 01",
            file_name=path.name,
            file_path=str(path),
            file_ext=path.suffix,
            file_size=path.stat().st_size,
            checksum=DocumentLibraryService.calculate_checksum(path),
            document_type="Cong van",
            document_number="01-CV/BXD",
            field="To chuc",
            status="indexed",
        )
    )
    document = repo.get_document(document_id)
    assert document is not None
    return document


def test_fulltext_migration_adds_required_columns() -> None:
    init_database()
    with get_connection() as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(knowledge_documents)").fetchall()}
        migrations = {row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}

    assert "document_id" in columns
    assert "full_text" in columns
    assert "checksum" in columns
    assert "chunk_count" in columns
    assert "embedding_version" in columns
    assert "indexed_time" in columns
    assert "013_fulltext_knowledge_handoff" in migrations


def test_knowledge_repository_crud_and_invalid_listing() -> None:
    init_database()
    repo = KnowledgeRepository()
    doc = KnowledgeDocument(
        document_id=1,
        library_document_id=1,
        title="Cong van",
        full_text="Noi dung",
        checksum="checksum",
        status=INVALID,
    )

    knowledge_id = repo.save(doc)
    repo.update_document(knowledge_id, {"title": "Cong van cap nhat"})
    stored = repo.get_by_document(1)
    invalid = repo.list_invalid()

    assert knowledge_id > 0
    assert repo.exists(1) is True
    assert stored is not None
    assert stored["title"] == "Cong van cap nhat"
    assert len(invalid) == 1
    assert repo.delete(1) == 1
    assert repo.exists(1) is False


def test_handoff_checksum_pipeline_success_and_citation(tmp_path: Path) -> None:
    init_database()
    document = _library_document(tmp_path / "source.txt")
    snapshot = DocumentSnapshot.from_library_document(document, full_text="Noi dung to chuc can bo can chunk va embedding")
    service = KnowledgeHandoffService()

    result = service.handoff(snapshot)
    stored = KnowledgeRepository().get_document(result.knowledge_document_id)
    citations = KnowledgeRepository().list_citation_metadata(
        query_text=CitationBuilder.query_key(result.knowledge_document_id),
        limit=None,
    )

    assert result.status == READY
    assert result.checksum == KnowledgeHandoffService.generate_checksum(snapshot.full_text)
    assert result.chunk_count > 0
    assert result.embedding_count == result.chunk_count
    assert result.citation_count == result.chunk_count
    assert stored is not None
    assert stored["full_text"] == snapshot.full_text
    assert stored["status"] == READY
    assert citations
    assert KnowledgeValidator().validate(result.knowledge_document_id).valid is True


def test_handoff_pipeline_failure_marks_invalid(tmp_path: Path) -> None:
    init_database()
    document = _library_document(tmp_path / "invalid.txt")
    snapshot = DocumentSnapshot.from_library_document(document, full_text="Noi dung khong tao embedding")
    service = KnowledgeHandoffService(embedding_service=NoEmbeddingService())  # type: ignore[arg-type]

    result = service.handoff(snapshot)
    stored = KnowledgeRepository().get_document(result.knowledge_document_id)
    validation = KnowledgeValidator().validate(result.knowledge_document_id)

    assert result.status == INVALID
    assert "embedding" in result.missing
    assert stored is not None
    assert stored["status"] == INVALID
    assert validation.valid is False


def test_document_library_indexing_creates_fulltext_ready_record(tmp_path: Path) -> None:
    init_database()
    root = tmp_path / "library"
    root.mkdir()
    text = "So: 02-CV/BXD\nNoi dung day du de chuyen sang Knowledge Engine"
    (root / "doc.txt").write_text(text, encoding="utf-8")

    result = DocumentLibraryService().index_folder(root, sync_knowledge=True)
    library_id = result["indexed_ids"][0]
    knowledge = KnowledgeRepository().get_by_document(library_id)

    assert knowledge is not None
    assert knowledge["full_text"] == text
    assert knowledge["chunk_count"] > 0
    assert knowledge["status"] == READY
    chunks = KnowledgeRepository().list_chunks(int(knowledge["id"]))
    assert chunks
    for chunk in chunks:
        embedding = EmbeddingRepository().get_by_chunk_id(int(chunk["id"]))
        assert embedding is not None
        assert embedding["status"] == "completed"
