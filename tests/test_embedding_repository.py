"""Tests for Build 0.7.3 Embedding Repository."""

import json

from database.connection import get_connection
from database.init_db import init_database
from models.embedding_vector import EmbeddingVector
from models.knowledge_document import KnowledgeDocument
from repositories.chunk_repository import ChunkRepository
from repositories.embedding_repository import EmbeddingRepository
from repositories.knowledge_repository import KnowledgeRepository
from services.chunk_service import ChunkEngine, ChunkService


def _create_chunk() -> int:
    knowledge_repo = KnowledgeRepository()
    document_id = knowledge_repo.create_document(KnowledgeDocument(title="Cong van 01", document_type="Cong van"))
    chunk_service = ChunkService(repository=ChunkRepository(), engine=ChunkEngine(max_tokens=20, overlap_tokens=2))
    chunk_ids = chunk_service.replace_document_chunks(document_id, "noi dung can tao embedding", source_checksum="doc1")
    return chunk_ids[0]


def test_embedding_migration_creates_table_and_indexes() -> None:
    init_database()
    with get_connection() as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        indexes = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index'").fetchall()}
        migrations = {row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}

    assert "knowledge_embeddings" in tables
    assert "idx_knowledge_embeddings_chunk" in indexes
    assert "idx_knowledge_embeddings_document" in indexes
    assert "011_embedding_engine" in migrations


def test_embedding_repository_read_write_and_update() -> None:
    init_database()
    chunk_id = _create_chunk()
    chunk = ChunkRepository().get_chunk(chunk_id)
    assert chunk is not None
    repo = EmbeddingRepository()

    first_id = repo.upsert_embedding(
        EmbeddingVector(
            chunk_id=chunk_id,
            document_id=int(chunk["document_id"]),
            embedding_model="test-model",
            embedding_provider="local",
            vector_json=json.dumps([0.1, 0.2]),
            vector_dimension=2,
            chunk_checksum="checksum-1",
            status="completed",
        )
    )
    second_id = repo.upsert_embedding(
        EmbeddingVector(
            chunk_id=chunk_id,
            document_id=int(chunk["document_id"]),
            embedding_model="test-model",
            embedding_provider="local",
            vector_json=json.dumps([0.3, 0.4, 0.5]),
            vector_dimension=3,
            chunk_checksum="checksum-2",
            status="completed",
        )
    )
    row = repo.get_by_chunk_id(chunk_id)

    assert first_id == second_id
    assert row is not None
    assert row["vector_dimension"] == 3
    assert row["chunk_checksum"] == "checksum-2"
    assert len(repo.list_embeddings(document_id=int(chunk["document_id"]))) == 1
