"""Repository for the V1.0 AI Search workflow."""

from __future__ import annotations

from typing import Any

from repositories.base_repository import BaseRepository


class SearchRepository(BaseRepository):
    """Read-only search repository for READY knowledge documents."""

    DOCUMENT_TABLE = "knowledge_documents"
    CHUNK_TABLE = "knowledge_chunks"
    EMBEDDING_TABLE = "knowledge_embeddings"
    VECTOR_TABLE = "knowledge_vector_index"

    def keyword_search(self, query: str, *, limit: int = 10) -> list[dict[str, Any]]:
        """Find READY documents by title, document number, summary or keywords."""
        pattern = f"%{query}%"
        return self.fetch_all(
            f"""
            SELECT *
            FROM {self.DOCUMENT_TABLE}
            WHERE UPPER(status)=?
              AND (
                    title LIKE ?
                 OR COALESCE(document_number, '') LIKE ?
                 OR COALESCE(metadata_json, '') LIKE ?
              )
            ORDER BY updated_at DESC, id DESC
            LIMIT ?
            """,
            ("READY", pattern, pattern, pattern, limit),
        )

    def semantic_search(self, *, limit: int | None = None) -> list[dict[str, Any]]:
        """Return stored vector candidates for READY documents."""
        query = f"""
            SELECT
                d.*,
                c.id AS matched_chunk_id,
                c.text AS matched_chunk_text,
                c.chunk_order AS matched_chunk_order,
                c.section AS matched_chunk_section,
                v.id AS vector_index_id,
                e.id AS embedding_id,
                e.vector_json AS vector_json
            FROM {self.VECTOR_TABLE} v
            INNER JOIN {self.EMBEDDING_TABLE} e ON e.id=v.embedding_id
            INNER JOIN {self.CHUNK_TABLE} c ON c.id=v.chunk_id
            INNER JOIN {self.DOCUMENT_TABLE} d ON d.id=v.document_id
            WHERE v.is_active=1
              AND e.status='completed'
              AND UPPER(d.status)=?
            ORDER BY d.id ASC, c.chunk_order ASC, c.id ASC
        """
        params: tuple[Any, ...] = ("READY",)
        if limit is not None:
            query += " LIMIT ?"
            params = (*params, limit)
        return self.fetch_all(query, params)

    def merge_results(
        self,
        keyword_results: list[dict[str, Any]],
        semantic_results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Merge keyword and semantic results by document id and sort by score."""
        merged: dict[int, dict[str, Any]] = {}
        for item in [*keyword_results, *semantic_results]:
            document_id = int(item["document_id"])
            existing = merged.get(document_id)
            if existing is None:
                merged[document_id] = dict(item)
                continue
            existing["score"] = max(float(existing.get("score", 0.0)), float(item.get("score", 0.0)))
            existing["matched_chunks"] = self._merge_lists(
                existing.get("matched_chunks", []),
                item.get("matched_chunks", []),
            )
            existing["citations"] = self._merge_lists(existing.get("citations", []), item.get("citations", []))
        return sorted(merged.values(), key=lambda result: float(result.get("score", 0.0)), reverse=True)

    @staticmethod
    def _merge_lists(first: list[dict[str, Any]], second: list[dict[str, Any]]) -> list[dict[str, Any]]:
        seen: set[str] = set()
        merged: list[dict[str, Any]] = []
        for item in [*first, *second]:
            key = str(item.get("id") or item.get("chunk_id") or item.get("source_chunk_id") or item)
            if key in seen:
                continue
            seen.add(key)
            merged.append(item)
        return merged
