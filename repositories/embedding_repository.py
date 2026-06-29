"""Repository for Build 0.7.3 Embedding Engine."""

from __future__ import annotations

from typing import Any

from models.embedding_vector import EmbeddingVector
from repositories.base_repository import BaseRepository


class EmbeddingRepository(BaseRepository):
    """Read/write access for persisted chunk embeddings."""

    TABLE = "knowledge_embeddings"

    def upsert_embedding(self, embedding: EmbeddingVector) -> int:
        """Create or update the embedding row for one chunk."""
        if embedding.chunk_id is None:
            raise ValueError("chunk_id is required")
        existing = self.get_by_chunk_id(embedding.chunk_id)
        data = embedding.to_dict()
        if existing:
            self.update(self.TABLE, int(existing["id"]), data)
            return int(existing["id"])
        return self.insert(self.TABLE, data)

    def get_by_chunk_id(self, chunk_id: int) -> dict[str, Any] | None:
        """Fetch the current embedding for one chunk."""
        if chunk_id <= 0:
            raise ValueError("chunk_id must be greater than 0")
        return self.fetch_one(f"SELECT * FROM {self.TABLE} WHERE chunk_id=?", (chunk_id,))

    def list_embeddings(
        self,
        *,
        document_id: int | None = None,
        status: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """List embeddings with optional filters."""
        clauses: list[str] = []
        params: list[Any] = []
        if document_id is not None:
            clauses.append("document_id=?")
            params.append(document_id)
        if status is not None:
            clauses.append("status=?")
            params.append(status)
        return self.list(
            self.TABLE,
            where=" AND ".join(clauses) if clauses else None,
            params=tuple(params),
            order_by="document_id ASC, chunk_id ASC, id ASC",
            limit=limit,
        )

    def mark_failed(
        self,
        *,
        chunk_id: int,
        document_id: int,
        embedding_model: str,
        embedding_provider: str,
        chunk_checksum: str,
        error_message: str,
    ) -> int:
        """Persist a failed embedding attempt without raising further."""
        return self.upsert_embedding(
            EmbeddingVector(
                chunk_id=chunk_id,
                document_id=document_id,
                embedding_model=embedding_model,
                embedding_provider=embedding_provider,
                vector_json=None,
                vector_dimension=0,
                chunk_checksum=chunk_checksum,
                status="failed",
                error_message=error_message,
            )
        )
