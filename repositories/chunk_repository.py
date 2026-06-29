"""Repository for Knowledge Chunk Engine persistence."""

from __future__ import annotations

from typing import Any

from models.knowledge_chunk import KnowledgeChunk
from models.knowledge_chunk_metadata import KnowledgeChunkMetadata
from repositories.base_repository import BaseRepository


class ChunkRepository(BaseRepository):
    """Read/write access for chunks and chunk metadata."""

    CHUNK_TABLE = "knowledge_chunks"
    METADATA_TABLE = "knowledge_chunk_metadata"

    def replace_chunks(
        self,
        document_id: int,
        chunks: list[KnowledgeChunk],
        metadata: list[KnowledgeChunkMetadata] | None = None,
    ) -> list[int]:
        """Replace all chunks for one document and persist matching metadata."""
        if document_id <= 0:
            raise ValueError("document_id must be greater than 0")
        if metadata is not None and len(metadata) != len(chunks):
            raise ValueError("metadata length must match chunks length")

        self.execute(f"DELETE FROM {self.METADATA_TABLE} WHERE document_id=?", (document_id,))
        self.execute(f"DELETE FROM {self.CHUNK_TABLE} WHERE document_id=?", (document_id,))
        ids: list[int] = []
        for order, chunk in enumerate(chunks, start=1):
            chunk.document_id = document_id
            chunk.chunk_order = chunk.chunk_order or order
            chunk_id = self.insert(self.CHUNK_TABLE, chunk.to_dict())
            ids.append(chunk_id)
            if metadata is not None:
                item = metadata[order - 1]
                item.chunk_id = chunk_id
                item.document_id = document_id
                self.upsert_metadata(item)
        return ids

    def list_chunks(self, document_id: int | None = None) -> list[dict[str, Any]]:
        """List chunks in stable document/order order."""
        if document_id:
            return self.list(
                self.CHUNK_TABLE,
                where="document_id=?",
                params=(document_id,),
                order_by="chunk_order ASC, id ASC",
                limit=None,
            )
        return self.list(self.CHUNK_TABLE, order_by="document_id ASC, chunk_order ASC, id ASC", limit=None)

    def get_chunk(self, chunk_id: int) -> dict[str, Any] | None:
        """Fetch one chunk by id."""
        return self.find(self.CHUNK_TABLE, chunk_id)

    def update_chunk(self, chunk_id: int, data: dict[str, Any]) -> int:
        """Update one chunk."""
        return self.update(self.CHUNK_TABLE, chunk_id, data)

    def upsert_metadata(self, metadata: KnowledgeChunkMetadata) -> int:
        """Create or update metadata for a chunk."""
        if metadata.chunk_id is None:
            raise ValueError("chunk_id is required")
        existing = self.get_metadata(metadata.chunk_id)
        data = metadata.to_dict()
        if existing:
            self.update(self.METADATA_TABLE, int(existing["id"]), data)
            return int(existing["id"])
        return self.insert(self.METADATA_TABLE, data)

    def get_metadata(self, chunk_id: int) -> dict[str, Any] | None:
        """Fetch metadata by chunk id."""
        return self.fetch_one(f"SELECT * FROM {self.METADATA_TABLE} WHERE chunk_id=?", (chunk_id,))

    def list_metadata(self, document_id: int | None = None) -> list[dict[str, Any]]:
        """List chunk metadata."""
        if document_id:
            return self.list(
                self.METADATA_TABLE,
                where="document_id=?",
                params=(document_id,),
                order_by="start_token ASC, id ASC",
                limit=None,
            )
        return self.list(self.METADATA_TABLE, order_by="document_id ASC, start_token ASC, id ASC", limit=None)
