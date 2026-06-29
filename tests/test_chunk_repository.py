"""Tests for Build 0.7.2 Chunk Repository."""

from database.connection import get_connection
from database.init_db import init_database
from models.knowledge_document import KnowledgeDocument
from repositories.chunk_repository import ChunkRepository
from repositories.knowledge_repository import KnowledgeRepository
from services.chunk_service import ChunkEngine, ChunkService


def test_chunk_migration_creates_metadata_table_and_indexes() -> None:
    init_database()
    with get_connection() as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        indexes = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()}
        migrations = {row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}

    assert "knowledge_chunks" in tables
    assert "knowledge_chunk_metadata" in tables
    assert "idx_knowledge_chunks_document_order" in indexes
    assert "idx_knowledge_chunk_metadata_document" in indexes
    assert "010_chunk_engine" in migrations


def test_chunk_repository_replaces_chunks_and_metadata() -> None:
    init_database()
    knowledge_repo = KnowledgeRepository()
    document_id = knowledge_repo.create_document(KnowledgeDocument(title="Cong van 12", document_type="Cong van"))
    chunk_repo = ChunkRepository()
    service = ChunkService(repository=chunk_repo, engine=ChunkEngine(max_tokens=4, overlap_tokens=1))

    first_ids = service.replace_document_chunks(document_id, "mot hai ba bon nam sau bay", source_checksum="sum1")
    first_rows = service.list_chunks_with_metadata(document_id)
    second_ids = service.replace_document_chunks(document_id, "tam chin muoi muoi mot", source_checksum="sum2")
    second_rows = service.list_chunks_with_metadata(document_id)

    assert len(first_ids) == 2
    assert len(first_rows) == 2
    assert first_rows[1]["metadata"]["overlap_with_previous"] == 1
    assert first_rows[1]["metadata"]["overlap_tokens"] == 1
    assert len(second_ids) == 2
    assert len(second_rows) == 2
    assert {row["source_checksum"] for row in second_rows} == {"sum2"}
    assert {row["id"] for row in first_rows}.isdisjoint({row["id"] for row in second_rows})
    assert len(chunk_repo.list_metadata(document_id)) == 2
