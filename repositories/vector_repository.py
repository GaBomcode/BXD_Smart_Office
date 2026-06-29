"""Repository for Build 0.7.4 Vector Index Engine."""

from __future__ import annotations

from typing import Any

from models.vector_index import VectorIndex
from repositories.base_repository import BaseRepository


class VectorRepository(BaseRepository):
    """Read/write access for vector index rows."""

    TABLE = "knowledge_vector_index"

    @staticmethod
    def _to_db(data: dict[str, Any]) -> dict[str, Any]:
        mapped = dict(data)
        if "dimension" in mapped:
            mapped["vector_dimension"] = mapped.pop("dimension")
        if "checksum" in mapped:
            mapped["vector_checksum"] = mapped.pop("checksum")
        if "norm" in mapped:
            mapped["vector_norm"] = mapped.pop("norm")
        return mapped

    @staticmethod
    def _from_db(row: dict[str, Any] | None) -> dict[str, Any] | None:
        if row is None:
            return None
        mapped = dict(row)
        mapped["dimension"] = mapped.get("vector_dimension")
        mapped["checksum"] = mapped.get("vector_checksum")
        mapped["norm"] = mapped.get("vector_norm")
        return mapped

    def create(self, vector: VectorIndex) -> int:
        """Create a vector index row."""
        return self.insert(self.TABLE, self._to_db(vector.to_dict()))

    def update(self, vector_id: int, data: dict[str, Any]) -> int:  # type: ignore[override]
        """Update a vector index row."""
        return super().update(self.TABLE, vector_id, self._to_db(data))

    def delete(self, vector_id: int) -> int:  # type: ignore[override]
        """Delete a vector index row."""
        return super().delete(self.TABLE, vector_id)

    def upsert(self, vector: VectorIndex) -> int:
        """Create or update one vector index row by embedding id."""
        if vector.embedding_id is None:
            raise ValueError("embedding_id is required")
        existing = self.find_by_embedding(vector.embedding_id)
        data = self._to_db(vector.to_dict())
        if existing:
            super().update(self.TABLE, int(existing["id"]), data)
            return int(existing["id"])
        return self.insert(self.TABLE, data)

    def find_by_embedding(self, embedding_id: int) -> dict[str, Any] | None:
        """Find vector index row by embedding id."""
        if embedding_id <= 0:
            raise ValueError("embedding_id must be greater than 0")
        return self._from_db(self.fetch_one(f"SELECT * FROM {self.TABLE} WHERE embedding_id=?", (embedding_id,)))

    def find_by_chunk(self, chunk_id: int) -> dict[str, Any] | None:
        """Find active vector index row by chunk id."""
        if chunk_id <= 0:
            raise ValueError("chunk_id must be greater than 0")
        return self._from_db(
            self.fetch_one(f"SELECT * FROM {self.TABLE} WHERE chunk_id=? AND is_active=1", (chunk_id,))
        )

    def find_by_document(self, document_id: int) -> list[dict[str, Any]]:
        """List active vector index rows for one document."""
        if document_id <= 0:
            raise ValueError("document_id must be greater than 0")
        rows = self.list(
            self.TABLE,
            where="document_id=? AND is_active=1",
            params=(document_id,),
            order_by="chunk_id ASC, id ASC",
            limit=None,
        )
        return [self._from_db(row) or {} for row in rows]

    def list_vectors(self, *, active_only: bool = True, limit: int | None = None) -> list[dict[str, Any]]:
        """List vector index rows."""
        rows = self.list(
            self.TABLE,
            where="is_active=1" if active_only else None,
            order_by="document_id ASC, chunk_id ASC, id ASC",
            limit=limit,
        )
        return [self._from_db(row) or {} for row in rows]

    def count(self, *, active_only: bool = True) -> int:
        """Count vector index rows."""
        where = " WHERE is_active=1" if active_only else ""
        row = self.fetch_one(f"SELECT COUNT(*) AS total FROM {self.TABLE}{where}")
        return int(row["total"]) if row else 0

    def exists(self, *, embedding_id: int | None = None, chunk_id: int | None = None) -> bool:
        """Check whether an active vector exists by embedding or chunk id."""
        if embedding_id is None and chunk_id is None:
            raise ValueError("embedding_id or chunk_id is required")
        if embedding_id is not None:
            row = self.fetch_one(f"SELECT id FROM {self.TABLE} WHERE embedding_id=? AND is_active=1", (embedding_id,))
        else:
            row = self.fetch_one(f"SELECT id FROM {self.TABLE} WHERE chunk_id=? AND is_active=1", (chunk_id,))
        return row is not None

    def delete_by_document(self, document_id: int) -> int:
        """Delete vectors for one document."""
        if document_id <= 0:
            raise ValueError("document_id must be greater than 0")
        return self.execute(f"DELETE FROM {self.TABLE} WHERE document_id=?", (document_id,))

    def delete_by_chunk(self, chunk_id: int) -> int:
        """Delete vector for one chunk."""
        if chunk_id <= 0:
            raise ValueError("chunk_id must be greater than 0")
        return self.execute(f"DELETE FROM {self.TABLE} WHERE chunk_id=?", (chunk_id,))
