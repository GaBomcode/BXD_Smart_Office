"""Tests for Build 0.7.4 Vector Repository."""

from database.connection import get_connection
from database.init_db import init_database
from models.vector_index import VectorIndex
from repositories.embedding_repository import EmbeddingRepository
from repositories.vector_repository import VectorRepository
from services.embedding_service import EmbeddingService

from tests.test_embedding_engine import _create_chunks


def _create_embedding() -> dict:
    _document_id, chunk_ids = _create_chunks("mot hai ba bon")
    service = EmbeddingService()
    return service.generate_for_chunk(chunk_ids[0])


def test_vector_migration_creates_table_and_indexes() -> None:
    init_database()
    with get_connection() as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        indexes = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()}
        migrations = {row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}

    assert "knowledge_vector_index" in tables
    assert "idx_knowledge_vector_index_chunk" in indexes
    assert "idx_knowledge_vector_index_document" in indexes
    assert "idx_knowledge_vector_index_embedding" in indexes
    assert "idx_knowledge_vector_index_active" in indexes
    assert "012_vector_index" in migrations


def test_vector_repository_create_update_read_delete_count_exists() -> None:
    init_database()
    embedding = _create_embedding()
    repo = VectorRepository()

    vector_id = repo.create(
        VectorIndex(
            embedding_id=int(embedding["id"]),
            chunk_id=int(embedding["chunk_id"]),
            document_id=int(embedding["document_id"]),
            dimension=int(embedding["vector_dimension"]),
            checksum="checksum-1",
            norm=1.0,
        )
    )
    by_chunk = repo.find_by_chunk(int(embedding["chunk_id"]))
    repo.update(vector_id, {"checksum": "checksum-2", "norm": 2.0})
    updated = repo.find_by_chunk(int(embedding["chunk_id"]))
    by_document = repo.find_by_document(int(embedding["document_id"]))

    assert vector_id > 0
    assert by_chunk is not None
    assert by_chunk["embedding_id"] == embedding["id"]
    assert updated is not None
    assert updated["checksum"] == "checksum-2"
    assert updated["norm"] == 2.0
    assert len(by_document) == 1
    assert repo.count() == 1
    assert repo.exists(chunk_id=int(embedding["chunk_id"])) is True
    assert repo.exists(embedding_id=int(embedding["id"])) is True
    assert repo.delete(vector_id) == 1
    assert repo.count() == 0
    assert EmbeddingRepository().get_by_chunk_id(int(embedding["chunk_id"])) is not None
