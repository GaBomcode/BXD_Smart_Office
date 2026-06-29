"""Tests for Build 0.7.3 Embedding Engine."""

import json

from database.init_db import init_database
from models.knowledge_document import KnowledgeDocument
from repositories.chunk_repository import ChunkRepository
from repositories.embedding_repository import EmbeddingRepository
from repositories.knowledge_repository import KnowledgeRepository
from services.chunk_service import ChunkEngine, ChunkService
from services.embedding_service import DeterministicLocalEmbeddingBackend, EmbeddingService


class FailingEmbeddingBackend:
    name = "failing"
    model = "failing-v1"

    def embed(self, text: str) -> list[float]:
        raise RuntimeError("backend failed")


def _create_chunks(text: str = "mot hai ba bon nam sau bay tam") -> tuple[int, list[int]]:
    knowledge_repo = KnowledgeRepository()
    document_id = knowledge_repo.create_document(KnowledgeDocument(title="Cong van embedding", document_type="Cong van"))
    chunk_service = ChunkService(repository=ChunkRepository(), engine=ChunkEngine(max_tokens=4, overlap_tokens=1))
    chunk_ids = chunk_service.replace_document_chunks(document_id, text, source_checksum="doc-embedding")
    return document_id, chunk_ids


def test_create_embedding_for_chunk() -> None:
    init_database()
    _document_id, chunk_ids = _create_chunks()
    service = EmbeddingService(backend=DeterministicLocalEmbeddingBackend(dimensions=8))

    row = service.generate_for_chunk(chunk_ids[0])

    assert row["status"] == "completed"
    assert row["vector_dimension"] == 8
    assert row["embedding_provider"] == "local_deterministic"
    assert len(json.loads(row["vector_json"])) == 8


def test_skip_unchanged_chunk() -> None:
    init_database()
    _document_id, chunk_ids = _create_chunks()
    service = EmbeddingService(backend=DeterministicLocalEmbeddingBackend(dimensions=8))

    first = service.generate_for_chunk(chunk_ids[0])
    second = service.generate_for_chunk(chunk_ids[0])

    assert first["id"] == second["id"]
    assert second["skipped"] is True
    assert second["chunk_checksum"] == first["chunk_checksum"]


def test_regenerate_changed_chunk() -> None:
    init_database()
    _document_id, chunk_ids = _create_chunks()
    chunk_repo = ChunkRepository()
    service = EmbeddingService(chunk_repository=chunk_repo, backend=DeterministicLocalEmbeddingBackend(dimensions=8))

    first = service.generate_for_chunk(chunk_ids[0])
    chunk_repo.update_chunk(chunk_ids[0], {"text": "noi dung da thay doi"})
    second = service.generate_for_chunk(chunk_ids[0])

    assert first["id"] == second["id"]
    assert second["skipped"] is False
    assert second["chunk_checksum"] != first["chunk_checksum"]
    assert second["status"] == "completed"


def test_batch_embedding() -> None:
    init_database()
    document_id, chunk_ids = _create_chunks()
    service = EmbeddingService(backend=DeterministicLocalEmbeddingBackend(dimensions=8))

    result = service.generate_all(document_id=document_id, batch_size=1)
    second = service.generate_all(document_id=document_id, batch_size=2)

    assert result["total"] == len(chunk_ids)
    assert result["completed"] == len(chunk_ids)
    assert result["failed"] == 0
    assert second["skipped"] == len(chunk_ids)


def test_failed_embedding_handling() -> None:
    init_database()
    _document_id, chunk_ids = _create_chunks()
    service = EmbeddingService(backend=FailingEmbeddingBackend())

    row = service.generate_for_chunk(chunk_ids[0])
    batch = service.generate_all(batch_size=2)
    stored = EmbeddingRepository().get_by_chunk_id(chunk_ids[0])

    assert row["status"] == "failed"
    assert row["error_message"] == "backend failed"
    assert batch["failed"] >= 1
    assert stored is not None
    assert stored["status"] == "failed"
