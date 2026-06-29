"""Vector Index Engine service for Build 0.7.4."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Any
import hashlib
import json
import logging

from models.vector_index import VectorIndex
from repositories.embedding_repository import EmbeddingRepository
from repositories.vector_repository import VectorRepository

logger = logging.getLogger(__name__)

SUPPORTED_TOP_K = {1, 3, 5, 10}


@dataclass(slots=True)
class VectorBatchResult:
    """Counters for vector index batch operations."""

    total: int = 0
    indexed: int = 0
    skipped: int = 0
    deleted: int = 0
    failed: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "total": self.total,
            "indexed": self.indexed,
            "skipped": self.skipped,
            "deleted": self.deleted,
            "failed": self.failed,
        }


class VectorService:
    """Service layer for indexing and querying stored embedding vectors."""

    def __init__(
        self,
        repository: VectorRepository | None = None,
        embedding_repository: EmbeddingRepository | None = None,
    ) -> None:
        self.repository = repository or VectorRepository()
        self.embedding_repository = embedding_repository or EmbeddingRepository()

    def build_index(self, *, embedding_id: int | None = None, force: bool = False) -> dict[str, int]:
        """Build vector index for one embedding or all completed embeddings."""
        if embedding_id is not None:
            embedding = self._get_embedding_by_id(embedding_id)
            row = self.refresh_vector(embedding, force=force)
            if row.get("skipped"):
                return {"total": 1, "indexed": 0, "skipped": 1, "failed": 0}
            if row.get("status") == "failed":
                return {"total": 1, "indexed": 0, "skipped": 0, "failed": 1}
            return {"total": 1, "indexed": 1, "skipped": 0, "failed": 0}
        return self.batch_index(force=force)

    def rebuild_index(self) -> dict[str, int]:
        """Force rebuild all completed embedding vector indexes."""
        return self.batch_index(force=True)

    def delete_document_vectors(self, document_id: int) -> int:
        """Delete all vectors for one document."""
        try:
            return self.repository.delete_by_document(document_id)
        except Exception:
            logger.exception("Failed to delete document vectors document_id=%s", document_id)
            raise

    def delete_chunk_vectors(self, chunk_id: int) -> int:
        """Delete vector index row for one chunk."""
        try:
            return self.repository.delete_by_chunk(chunk_id)
        except Exception:
            logger.exception("Failed to delete chunk vectors chunk_id=%s", chunk_id)
            raise

    def refresh_vector(self, embedding: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
        """Create or refresh a vector index row from one completed embedding."""
        try:
            if str(embedding.get("status") or "") != "completed":
                raise ValueError("embedding must be completed")
            vector = self._parse_vector(embedding.get("vector_json"))
            checksum = self.vector_checksum(vector)
            embedding_id = int(embedding["id"])
            chunk_id = int(embedding["chunk_id"])
            existing = self.repository.find_by_embedding(embedding_id)
            if existing and not force and existing.get("checksum") == checksum:
                row = dict(existing)
                row["skipped"] = True
                return row
            index = VectorIndex(
                embedding_id=embedding_id,
                chunk_id=chunk_id,
                document_id=int(embedding["document_id"]),
                dimension=len(vector),
                checksum=checksum,
                norm=self.vector_norm(vector),
            )
            vector_id = self.repository.upsert(index)
            row = self.repository.find_by_embedding(embedding_id) or {"id": vector_id}
            row["skipped"] = False
            return row
        except Exception:
            logger.exception("Failed to refresh vector embedding_id=%s", embedding.get("id"))
            raise

    def find_similar(self, query_vector: list[float], *, top_k: int = 5) -> list[dict[str, Any]]:
        """Find nearest vectors by cosine similarity against a supplied vector."""
        limit = self._validate_top_k(top_k)
        normalized_query = self.normalize_vector(query_vector)
        scored: list[dict[str, Any]] = []
        for row in self.repository.list_vectors(active_only=True):
            embedding = self.embedding_repository.get_by_chunk_id(int(row["chunk_id"]))
            if not embedding or not embedding.get("vector_json"):
                continue
            vector = self._parse_vector(embedding["vector_json"])
            if len(vector) != len(normalized_query):
                continue
            item = dict(row)
            item["score"] = self.cosine_similarity(normalized_query, vector)
            scored.append(item)
        return self.top_k(scored, k=limit)

    def top_k(self, items: list[dict[str, Any]], *, k: int = 5) -> list[dict[str, Any]]:
        """Return supported top-k scored items."""
        limit = self._validate_top_k(k)
        return sorted(items, key=lambda item: float(item.get("score", 0.0)), reverse=True)[:limit]

    def batch_index(self, *, document_id: int | None = None, force: bool = False, batch_size: int = 50) -> dict[str, int]:
        """Index completed embeddings in batches with safe row-level errors."""
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than 0")
        embeddings = self.embedding_repository.list_embeddings(document_id=document_id, status="completed")
        result = VectorBatchResult(total=len(embeddings))
        for start in range(0, len(embeddings), batch_size):
            for embedding in embeddings[start : start + batch_size]:
                try:
                    row = self.refresh_vector(embedding, force=force)
                    if row.get("skipped"):
                        result.skipped += 1
                    else:
                        result.indexed += 1
                except Exception as exc:
                    result.failed += 1
                    logger.exception("Vector batch index failed embedding_id=%s: %s", embedding.get("id"), exc)
        return result.to_dict()

    def batch_delete(
        self,
        *,
        document_ids: list[int] | None = None,
        chunk_ids: list[int] | None = None,
    ) -> dict[str, int]:
        """Delete vector rows for documents and/or chunks."""
        document_ids = document_ids or []
        chunk_ids = chunk_ids or []
        result = VectorBatchResult(total=len(document_ids) + len(chunk_ids))
        for document_id in document_ids:
            try:
                result.deleted += self.delete_document_vectors(document_id)
            except Exception:
                result.failed += 1
        for chunk_id in chunk_ids:
            try:
                result.deleted += self.delete_chunk_vectors(chunk_id)
            except Exception:
                result.failed += 1
        return result.to_dict()

    def batch_refresh(self, *, embedding_ids: list[int], force: bool = False) -> dict[str, int]:
        """Refresh selected embeddings by id."""
        result = VectorBatchResult(total=len(embedding_ids))
        for embedding_id in embedding_ids:
            try:
                row = self.refresh_vector(self._get_embedding_by_id(embedding_id), force=force)
                if row.get("skipped"):
                    result.skipped += 1
                else:
                    result.indexed += 1
            except Exception:
                result.failed += 1
        return result.to_dict()

    def _get_embedding_by_id(self, embedding_id: int) -> dict[str, Any]:
        if embedding_id <= 0:
            raise ValueError("embedding_id must be greater than 0")
        row = self.embedding_repository.fetch_one(
            f"SELECT * FROM {self.embedding_repository.TABLE} WHERE id=?",
            (embedding_id,),
        )
        if not row:
            raise ValueError("embedding not found")
        return row

    @staticmethod
    def _parse_vector(vector_json: Any) -> list[float]:
        if not vector_json:
            raise ValueError("vector_json is required")
        values = json.loads(str(vector_json))
        if not isinstance(values, list):
            raise ValueError("vector_json must be a list")
        return [float(value) for value in values]

    @staticmethod
    def _validate_top_k(k: int) -> int:
        if k not in SUPPORTED_TOP_K:
            raise ValueError("top_k must be one of 1, 3, 5, 10")
        return k

    @staticmethod
    def vector_checksum(vector: list[float]) -> str:
        payload = json.dumps(vector, separators=(",", ":"), sort_keys=False)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def vector_norm(vector: list[float]) -> float:
        return sqrt(sum(value * value for value in vector))

    @classmethod
    def normalize_vector(cls, vector: list[float]) -> list[float]:
        norm = cls.vector_norm(vector)
        if norm == 0:
            return vector
        return [round(value / norm, 8) for value in vector]

    @classmethod
    def cosine_similarity(cls, a: list[float], b: list[float]) -> float:
        if len(a) != len(b):
            raise ValueError("vectors must have the same dimension")
        norm_a = cls.vector_norm(a)
        norm_b = cls.vector_norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return sum(x * y for x, y in zip(a, b)) / (norm_a * norm_b)
