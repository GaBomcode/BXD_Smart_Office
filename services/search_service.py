"""Service layer for the V1.0 AI Search workflow."""

from __future__ import annotations

from typing import Any
import json
import logging
import re

from models.search_request import SearchRequest
from models.search_result import SearchResult
from repositories.knowledge_repository import KnowledgeRepository
from repositories.search_repository import SearchRepository
from services.embedding_service import EmbeddingService
from services.knowledge.citation_builder import CitationBuilder
from services.vector_service import VectorService

logger = logging.getLogger(__name__)

READY_STATUS = "READY"
SEARCH_MODES = {"keyword", "semantic", "hybrid"}


class SearchService:
    """Backend-only document retrieval workflow for READY knowledge documents."""

    def __init__(
        self,
        repository: SearchRepository | None = None,
        knowledge_repository: KnowledgeRepository | None = None,
        embedding_service: EmbeddingService | None = None,
        vector_service: VectorService | None = None,
    ) -> None:
        self.repository = repository or SearchRepository()
        self.knowledge_repository = knowledge_repository or KnowledgeRepository()
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_service = vector_service or VectorService()

    def search(self, request: SearchRequest) -> dict[str, Any]:
        """Validate and execute keyword, semantic or hybrid document retrieval."""
        errors = self.validate(request)
        if errors:
            return {"valid": False, "errors": errors, "results": []}
        query = self.normalize_query(request.query)
        try:
            if request.normalized_mode() == "keyword":
                results = self.keyword_search(query, top_k=request.top_k)
            elif request.normalized_mode() == "semantic":
                results = self.semantic_search(query, top_k=request.top_k)
            else:
                keyword_results = [
                    result.to_dict()
                    for result in self.keyword_search(query, top_k=request.top_k)
                ]
                semantic_results = [
                    result.to_dict()
                    for result in self.semantic_search(query, top_k=request.top_k)
                ]
                merged = self.repository.merge_results(keyword_results, semantic_results)
                results = [self._result_from_dict(item) for item in merged[: request.top_k]]
            return {"valid": True, "errors": [], "results": [result.to_dict() for result in results]}
        except Exception as exc:
            logger.exception("Search workflow failed mode=%s", request.mode)
            return {"valid": False, "errors": [str(exc)], "results": []}

    def validate(self, request: SearchRequest) -> list[str]:
        """Return validation errors without raising unhandled exceptions."""
        errors: list[str] = []
        query = request.query or ""
        if not query.strip():
            errors.append("query must not be empty")
        if len(query.strip()) > request.max_query_length:
            errors.append(f"query must be {request.max_query_length} characters or fewer")
        if request.normalized_mode() not in SEARCH_MODES:
            errors.append("mode must be keyword, semantic or hybrid")
        if request.top_k not in {1, 3, 5, 10}:
            errors.append("top_k must be one of 1, 3, 5, 10")
        return errors

    def keyword_search(self, query: str, *, top_k: int = 5) -> list[SearchResult]:
        """Run keyword search against indexed document metadata."""
        normalized_query = self.normalize_query(query)
        rows = self.repository.keyword_search(normalized_query, limit=top_k)
        results = [
            self._document_result(
                row,
                normalized_query,
                score=self._keyword_score(row, normalized_query),
            )
            for row in rows
        ]
        return self._ready_with_citations(results)[:top_k]

    def semantic_search(self, query: str, *, top_k: int = 5) -> list[SearchResult]:
        """Run nearest-neighbour search against persisted vector index rows."""
        query_vector = self.embedding_service.backend.embed(self.normalize_query(query))
        candidates = self.repository.semantic_search()
        scored: dict[int, SearchResult] = {}
        for row in candidates:
            vector = self._parse_vector(row.get("vector_json"))
            if len(vector) != len(query_vector):
                continue
            score = self.vector_service.cosine_similarity(query_vector, vector)
            knowledge_document_id = int(row["id"])
            current = scored.get(knowledge_document_id)
            chunk = self._matched_chunk_from_semantic(row, score)
            if current is None or score > current.score:
                result = self._document_result(row, self.normalize_query(query), score=score, chunks=[chunk])
                scored[knowledge_document_id] = result
            elif current is not None:
                current.matched_chunks.append(chunk)
        results = self.vector_service.top_k(
            [result.to_dict() for result in self._ready_with_citations(list(scored.values()))],
            k=top_k,
        )
        return [self._result_from_dict(item) for item in results]

    @staticmethod
    def normalize_query(query: str) -> str:
        """Trim and collapse whitespace in a search query."""
        return re.sub(r"\s+", " ", query.strip())

    def _document_result(
        self,
        row: dict[str, Any],
        query: str,
        *,
        score: float,
        chunks: list[dict[str, Any]] | None = None,
    ) -> SearchResult:
        knowledge_document_id = int(row["id"])
        metadata = self._metadata(row)
        return SearchResult(
            document_id=int(row.get("document_id") or row.get("library_document_id") or knowledge_document_id),
            title=str(row.get("title") or ""),
            summary=metadata.get("summary"),
            score=round(float(score), 6),
            matched_chunks=chunks if chunks is not None else self._keyword_chunks(knowledge_document_id, query),
            citations=self._citations(knowledge_document_id),
            status=str(row.get("status") or READY_STATUS).upper(),
        )

    def _ready_with_citations(self, results: list[SearchResult]) -> list[SearchResult]:
        return [result for result in results if result.status.upper() == READY_STATUS and result.citations]

    def _citations(self, knowledge_document_id: int) -> list[dict[str, Any]]:
        rows = self.knowledge_repository.list_citation_metadata(
            query_text=CitationBuilder.query_key(knowledge_document_id),
            limit=None,
        )
        return [
            {
                "id": row.get("id"),
                "source_chunk_id": row.get("source_chunk_id"),
                "title": row.get("title"),
                "document_number": row.get("document_number"),
                "page": row.get("page"),
                "section": row.get("section"),
                "file_path": row.get("file_path"),
                "score": row.get("score"),
            }
            for row in rows
        ]

    def _keyword_chunks(self, knowledge_document_id: int, query: str) -> list[dict[str, Any]]:
        query_lower = query.lower()
        chunks: list[dict[str, Any]] = []
        for chunk in self.knowledge_repository.list_chunks(knowledge_document_id):
            text = str(chunk.get("text") or "")
            if query_lower not in text.lower():
                continue
            chunks.append(
                {
                    "id": chunk.get("id"),
                    "chunk_id": chunk.get("id"),
                    "chunk_order": chunk.get("chunk_order"),
                    "section": chunk.get("section"),
                    "text": text,
                }
            )
            if len(chunks) >= 3:
                break
        return chunks

    @staticmethod
    def _matched_chunk_from_semantic(row: dict[str, Any], score: float) -> dict[str, Any]:
        return {
            "id": row.get("matched_chunk_id"),
            "chunk_id": row.get("matched_chunk_id"),
            "chunk_order": row.get("matched_chunk_order"),
            "section": row.get("matched_chunk_section"),
            "text": row.get("matched_chunk_text"),
            "score": round(float(score), 6),
        }

    @staticmethod
    def _keyword_score(row: dict[str, Any], query: str) -> float:
        query_lower = query.lower()
        fields = [
            str(row.get("title") or ""),
            str(row.get("document_number") or ""),
            str(row.get("metadata_json") or ""),
        ]
        hits = sum(1 for value in fields if query_lower in value.lower())
        return min(1.0, max(0.1, hits / len(fields)))

    @staticmethod
    def _metadata(row: dict[str, Any]) -> dict[str, Any]:
        raw = row.get("metadata_json")
        if not raw:
            return {}
        try:
            loaded = json.loads(str(raw))
        except json.JSONDecodeError:
            return {}
        return loaded if isinstance(loaded, dict) else {}

    @staticmethod
    def _parse_vector(vector_json: Any) -> list[float]:
        values = json.loads(str(vector_json or "[]"))
        if not isinstance(values, list):
            return []
        return [float(value) for value in values]

    @staticmethod
    def _result_from_dict(item: dict[str, Any]) -> SearchResult:
        return SearchResult(
            document_id=int(item["document_id"]),
            title=str(item.get("title") or ""),
            summary=item.get("summary"),
            score=float(item.get("score", 0.0)),
            matched_chunks=list(item.get("matched_chunks") or []),
            citations=list(item.get("citations") or []),
            status=str(item.get("status") or READY_STATUS),
        )
