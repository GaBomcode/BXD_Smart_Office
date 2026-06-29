"""Tests for Build 0.7.4 Vector Index Engine."""

import json

import pytest

from database.init_db import init_database
from repositories.chunk_repository import ChunkRepository
from repositories.embedding_repository import EmbeddingRepository
from repositories.vector_repository import VectorRepository
from services.embedding_service import EmbeddingService
from services.vector_service import VectorService

from tests.test_embedding_engine import _create_chunks


def _create_embeddings(text: str = "mot hai ba bon nam sau bay tam") -> list[dict]:
    _document_id, chunk_ids = _create_chunks(text)
    embedding_service = EmbeddingService()
    return [embedding_service.generate_for_chunk(chunk_id) for chunk_id in chunk_ids]


def test_build_index_and_checksum_skip() -> None:
    init_database()
    embeddings = _create_embeddings()
    service = VectorService()

    first = service.build_index()
    second = service.build_index()
    row = service.repository.find_by_chunk(int(embeddings[0]["chunk_id"]))

    assert first["indexed"] == len(embeddings)
    assert first["failed"] == 0
    assert second["skipped"] == len(embeddings)
    assert row is not None
    assert row["checksum"]


def test_refresh_regenerates_changed_vector() -> None:
    init_database()
    embeddings = _create_embeddings()
    vector_service = VectorService()
    vector_service.build_index()
    first = vector_service.repository.find_by_chunk(int(embeddings[0]["chunk_id"]))

    chunk_id = int(embeddings[0]["chunk_id"])
    ChunkRepository().update_chunk(chunk_id, {"text": "noi dung vector moi"})
    changed = EmbeddingService().generate_for_chunk(chunk_id)
    refreshed = vector_service.refresh_vector(changed)

    assert first is not None
    assert refreshed["skipped"] is False
    assert refreshed["id"] == first["id"]
    assert refreshed["checksum"] != first["checksum"]


def test_delete_document_and_chunk_vectors() -> None:
    init_database()
    embeddings = _create_embeddings()
    service = VectorService()
    service.build_index()

    deleted_chunk = service.delete_chunk_vectors(int(embeddings[0]["chunk_id"]))
    remaining = service.repository.count()
    deleted_document = service.delete_document_vectors(int(embeddings[0]["document_id"]))

    assert deleted_chunk == 1
    assert remaining == len(embeddings) - 1
    assert deleted_document == remaining
    assert service.repository.count() == 0


def test_top_k_and_cosine_similarity() -> None:
    init_database()
    embeddings = _create_embeddings("alpha beta gamma delta epsilon zeta eta theta iota kappa lambda")
    service = VectorService()
    service.build_index()
    query_vector = json.loads(embeddings[0]["vector_json"])

    top_one = service.find_similar(query_vector, top_k=1)
    top_three = service.find_similar(query_vector, top_k=3)

    assert len(top_one) == 1
    assert len(top_three) <= 3
    assert top_one[0]["chunk_id"] == embeddings[0]["chunk_id"]
    assert round(top_one[0]["score"], 6) == 1.0
    assert VectorService.cosine_similarity([1.0, 0.0], [1.0, 0.0]) == 1.0
    assert VectorService.cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0
    assert VectorService.normalize_vector([3.0, 4.0]) == [0.6, 0.8]
    with pytest.raises(ValueError):
        service.find_similar(query_vector, top_k=2)


def test_batch_index_delete_and_rebuild() -> None:
    init_database()
    embeddings = _create_embeddings("mot hai ba bon nam sau bay tam chin muoi")
    service = VectorService()

    indexed = service.batch_index(batch_size=1)
    refreshed = service.batch_refresh(embedding_ids=[int(item["id"]) for item in embeddings], force=True)
    deleted = service.batch_delete(chunk_ids=[int(embeddings[0]["chunk_id"])])
    rebuilt = service.rebuild_index()

    assert indexed["indexed"] == len(embeddings)
    assert refreshed["indexed"] == len(embeddings)
    assert deleted["deleted"] == 1
    assert rebuilt["indexed"] == len(embeddings)
    assert VectorRepository().count() == len(embeddings)


def test_batch_index_handles_bad_embedding_safely() -> None:
    init_database()
    embeddings = _create_embeddings()
    embedding_repo = EmbeddingRepository()
    embedding_repo.update_embedding = getattr(embedding_repo, "upsert_embedding")
    embedding_repo.update(
        embedding_repo.TABLE,
        int(embeddings[0]["id"]),
        {"vector_json": "not-json", "status": "completed"},
    )
    service = VectorService(embedding_repository=embedding_repo)

    result = service.batch_index()

    assert result["failed"] == 1
    assert result["indexed"] == len(embeddings) - 1
