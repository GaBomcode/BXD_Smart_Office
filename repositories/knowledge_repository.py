"""Repository cho AI Knowledge Engine."""

from __future__ import annotations

from typing import Any
import logging

from models.knowledge_chunk import KnowledgeChunk
from models.knowledge_citation_metadata import KnowledgeCitationMetadata
from models.knowledge_document import KnowledgeDocument
from models.knowledge_entity import KnowledgeEntity
from models.knowledge_metadata import KnowledgeMetadata
from models.knowledge_relation import KnowledgeRelation
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class KnowledgeRepository(BaseRepository):
    """Đọc/ghi tài liệu tri thức, chunk, entity, relation, job và log."""

    DOCUMENT_TABLE = "knowledge_documents"
    CHUNK_TABLE = "knowledge_chunks"
    ENTITY_TABLE = "knowledge_entities"
    RELATION_TABLE = "knowledge_relations"
    JOB_TABLE = "knowledge_jobs"
    LOG_TABLE = "knowledge_logs"
    EMBEDDING_CACHE_TABLE = "knowledge_embedding_cache"
    INDEX_STATE_TABLE = "knowledge_index_state"
    METADATA_TABLE = "knowledge_metadata"
    RELATIONSHIP_V2_TABLE = "knowledge_relationship_v2"
    CITATION_METADATA_TABLE = "knowledge_citation_metadata"
    METADATA_CACHE_TABLE = "knowledge_metadata_cache"

    def create_document(self, document: KnowledgeDocument) -> int:
        return self.insert(self.DOCUMENT_TABLE, document.to_dict())

    def save(self, document: KnowledgeDocument) -> int:
        """Save or update a knowledge document by source document id."""
        return self.upsert_document(document)

    def get_document(self, document_id: int) -> dict[str, Any] | None:
        return self.find(self.DOCUMENT_TABLE, document_id)

    def get_by_document(self, document_id: int) -> dict[str, Any] | None:
        """Fetch a knowledge document by document library id."""
        return self.fetch_one(
            f"""
            SELECT * FROM {self.DOCUMENT_TABLE}
            WHERE document_id=? OR library_document_id=?
            ORDER BY id DESC
            LIMIT 1
            """,
            (document_id, document_id),
        )

    def get_by_library_document(self, library_document_id: int) -> dict[str, Any] | None:
        return self.fetch_one(f"SELECT * FROM {self.DOCUMENT_TABLE} WHERE library_document_id=?", (library_document_id,))

    def upsert_document(self, document: KnowledgeDocument) -> int:
        source_id = document.document_id or document.library_document_id
        if source_id:
            existing = self.get_by_document(source_id)
            if existing:
                self.update(self.DOCUMENT_TABLE, int(existing["id"]), document.to_dict())
                return int(existing["id"])
        return self.create_document(document)

    def list_documents(self) -> list[dict[str, Any]]:
        return self.list(self.DOCUMENT_TABLE, order_by="updated_at DESC, id DESC")

    def update_document(self, document_id: int, data: dict[str, Any]) -> int:
        return self.update(self.DOCUMENT_TABLE, document_id, data)

    def exists(self, document_id: int) -> bool:
        """Return true when a source document has a knowledge record."""
        return self.get_by_document(document_id) is not None

    def delete(self, document_id: int) -> int:  # type: ignore[override]
        """Delete a knowledge document by source document id."""
        existing = self.get_by_document(document_id)
        if not existing:
            return 0
        return super().delete(self.DOCUMENT_TABLE, int(existing["id"]))

    def list_invalid(self) -> list[dict[str, Any]]:
        """List knowledge documents that failed integrity validation."""
        return self.list(
            self.DOCUMENT_TABLE,
            where="status=?",
            params=("INVALID",),
            order_by="updated_at DESC, id DESC",
            limit=None,
        )

    def replace_chunks(self, document_id: int, chunks: list[KnowledgeChunk]) -> list[int]:
        self.execute(f"DELETE FROM {self.CHUNK_TABLE} WHERE document_id=?", (document_id,))
        ids: list[int] = []
        for order, chunk in enumerate(chunks, start=1):
            chunk.document_id = document_id
            chunk.chunk_order = chunk.chunk_order or order
            ids.append(self.insert(self.CHUNK_TABLE, chunk.to_dict()))
        return ids

    def list_chunks(self, document_id: int | None = None) -> list[dict[str, Any]]:
        if document_id:
            return self.list(
                self.CHUNK_TABLE,
                where="document_id=?",
                params=(document_id,),
                order_by="chunk_order ASC, id ASC",
            )
        return self.list(self.CHUNK_TABLE, order_by="document_id ASC, chunk_order ASC, id ASC")

    def update_chunk(self, chunk_id: int, data: dict[str, Any]) -> int:
        return self.update(self.CHUNK_TABLE, chunk_id, data)

    def replace_entities(self, document_id: int, entities: list[KnowledgeEntity]) -> list[int]:
        self.execute(f"DELETE FROM {self.ENTITY_TABLE} WHERE document_id=?", (document_id,))
        ids: list[int] = []
        for entity in entities:
            entity.document_id = document_id
            ids.append(self.insert(self.ENTITY_TABLE, entity.to_dict()))
        return ids

    def list_entities(self, document_id: int | None = None) -> list[dict[str, Any]]:
        if document_id:
            return self.list(
                self.ENTITY_TABLE,
                where="document_id=?",
                params=(document_id,),
                order_by="weight DESC, entity_type ASC, entity_value ASC",
            )
        return self.list(self.ENTITY_TABLE, order_by="weight DESC, entity_value ASC")

    def replace_relations_for_document(self, document_id: int, relations: list[KnowledgeRelation]) -> list[int]:
        self.execute(
            f"DELETE FROM {self.RELATION_TABLE} WHERE source_document_id=? OR target_document_id=?",
            (document_id, document_id),
        )
        ids: list[int] = []
        for relation in relations:
            ids.append(self.insert(self.RELATION_TABLE, relation.to_dict()))
        return ids

    def upsert_relation(self, relation: KnowledgeRelation) -> int:
        """Tạo/cập nhật relation, tránh duplicate theo source/target/type."""
        existing = self.fetch_one(
            f"""
            SELECT id FROM {self.RELATION_TABLE}
            WHERE source_document_id IS ? AND target_document_id IS ? AND relation_type=?
            """,
            (relation.source_document_id, relation.target_document_id, relation.relation_type),
        )
        data = relation.to_dict()
        if existing:
            self.update(self.RELATION_TABLE, int(existing["id"]), data)
            return int(existing["id"])
        return self.insert(self.RELATION_TABLE, data)

    def upsert_relations_for_document(self, document_id: int, relations: list[KnowledgeRelation]) -> list[int]:
        """Lưu relations mới mà không xóa quan hệ của tài liệu khác."""
        self.execute(f"DELETE FROM {self.RELATION_TABLE} WHERE source_document_id=?", (document_id,))
        return [self.upsert_relation(relation) for relation in relations]

    def list_relations(self, document_id: int | None = None) -> list[dict[str, Any]]:
        if document_id:
            return self.fetch_all(
                f"""
                SELECT r.*, s.title AS source_title, t.title AS target_title
                FROM {self.RELATION_TABLE} r
                LEFT JOIN {self.DOCUMENT_TABLE} s ON s.id=r.source_document_id
                LEFT JOIN {self.DOCUMENT_TABLE} t ON t.id=r.target_document_id
                WHERE r.source_document_id=? OR r.target_document_id=?
                ORDER BY r.weight DESC, r.id DESC
                """,
                (document_id, document_id),
            )
        return self.list(self.RELATION_TABLE, order_by="weight DESC, id DESC")

    # TODO REMOVE AFTER BUILD 1.0: Job lifecycle is prepared but not currently invoked by services.
    def create_job(self, job_type: str, *, target_id: int | None = None, detail: str | None = None) -> int:
        return self.execute(
            f"INSERT INTO {self.JOB_TABLE}(job_type, status, target_id, detail, started_at) VALUES(?,?,?,?,CURRENT_TIMESTAMP)",
            (job_type, "running", target_id, detail),
        )

    # TODO REMOVE AFTER BUILD 1.0: Job lifecycle is prepared but not currently invoked by services.
    def finish_job(self, job_id: int, status: str, detail: str | None = None) -> int:
        return self.execute(
            f"UPDATE {self.JOB_TABLE} SET status=?, detail=COALESCE(?, detail), finished_at=CURRENT_TIMESTAMP WHERE id=?",
            (status, detail, job_id),
        )

    def log(self, level: str, message: str, *, job_id: int | None = None, detail: str | None = None) -> int:
        logger.log(getattr(logging, level.upper(), logging.INFO), message)
        return self.execute(
            f"INSERT INTO {self.LOG_TABLE}(job_id, level, message, detail) VALUES(?,?,?,?)",
            (job_id, level.upper(), message, detail),
        )

    def get_embedding_cache(self, embedding_hash: str) -> dict[str, Any] | None:
        return self.fetch_one(
            f"SELECT * FROM {self.EMBEDDING_CACHE_TABLE} WHERE embedding_hash=?",
            (embedding_hash,),
        )

    def upsert_embedding_cache(
        self,
        *,
        embedding_hash: str,
        source_checksum: str,
        text_hash: str,
        embedding_version: str,
        embedding_model: str,
        embedding_backend: str,
        embedding_json: str,
    ) -> int:
        existing = self.get_embedding_cache(embedding_hash)
        data = {
            "embedding_hash": embedding_hash,
            "source_checksum": source_checksum,
            "text_hash": text_hash,
            "embedding_version": embedding_version,
            "embedding_model": embedding_model,
            "embedding_backend": embedding_backend,
            "embedding_json": embedding_json,
        }
        if existing:
            self.update(self.EMBEDDING_CACHE_TABLE, int(existing["id"]), data)
            return int(existing["id"])
        return self.insert(self.EMBEDDING_CACHE_TABLE, data)

    def get_index_state(self, library_document_id: int) -> dict[str, Any] | None:
        return self.fetch_one(
            f"SELECT * FROM {self.INDEX_STATE_TABLE} WHERE library_document_id=?",
            (library_document_id,),
        )

    def upsert_index_state(
        self,
        *,
        library_document_id: int,
        knowledge_document_id: int | None,
        file_path: str,
        checksum: str,
        status: str,
        detail: str | None = None,
    ) -> int:
        existing = self.get_index_state(library_document_id)
        data = {
            "library_document_id": library_document_id,
            "knowledge_document_id": knowledge_document_id,
            "file_path": file_path,
            "checksum": checksum,
            "status": status,
            "last_seen_at": "CURRENT_TIMESTAMP",
            "last_indexed_at": "CURRENT_TIMESTAMP" if status == "indexed" else None,
            "detail": detail,
        }
        if existing:
            return self.execute(
                f"""
                UPDATE {self.INDEX_STATE_TABLE}
                SET knowledge_document_id=?, file_path=?, checksum=?, status=?,
                    last_seen_at=CURRENT_TIMESTAMP,
                    last_indexed_at=CASE WHEN ?='indexed' THEN CURRENT_TIMESTAMP ELSE last_indexed_at END,
                    detail=?, updated_at=CURRENT_TIMESTAMP
                WHERE library_document_id=?
                """,
                (knowledge_document_id, file_path, checksum, status, status, detail, library_document_id),
            )
        return self.execute(
            f"""
            INSERT INTO {self.INDEX_STATE_TABLE}
            (library_document_id, knowledge_document_id, file_path, checksum, status, last_seen_at, last_indexed_at, detail)
            VALUES(?,?,?,?,?,CURRENT_TIMESTAMP,CASE WHEN ?='indexed' THEN CURRENT_TIMESTAMP ELSE NULL END,?)
            """,
            (library_document_id, knowledge_document_id, file_path, checksum, status, status, detail),
        )

    def get_metadata(self, knowledge_document_id: int) -> dict[str, Any] | None:
        return self.fetch_one(
            f"SELECT * FROM {self.METADATA_TABLE} WHERE knowledge_document_id=?",
            (knowledge_document_id,),
        )

    def upsert_metadata(self, metadata: KnowledgeMetadata) -> int:
        if metadata.knowledge_document_id is None:
            raise ValueError("knowledge_document_id la bat buoc")
        existing = self.get_metadata(metadata.knowledge_document_id)
        data = metadata.to_dict()
        if existing:
            self.update(self.METADATA_TABLE, int(existing["id"]), data)
            return int(existing["id"])
        return self.insert(self.METADATA_TABLE, data)

    def list_metadata(self) -> list[dict[str, Any]]:
        return self.list(self.METADATA_TABLE, order_by="updated_at DESC, id DESC", limit=None)

    def replace_relationships_v2_for_document(self, document_id: int, relationships: list[dict[str, Any]]) -> list[int]:
        self.execute(
            f"DELETE FROM {self.RELATIONSHIP_V2_TABLE} WHERE source_knowledge_document_id=?",
            (document_id,),
        )
        ids: list[int] = []
        for relationship in relationships:
            existing = self.fetch_one(
                f"""
                SELECT id FROM {self.RELATIONSHIP_V2_TABLE}
                WHERE source_knowledge_document_id=? AND target_knowledge_document_id=? AND relation_type=?
                """,
                (
                    relationship["source_knowledge_document_id"],
                    relationship["target_knowledge_document_id"],
                    relationship["relation_type"],
                ),
            )
            if existing:
                self.update(self.RELATIONSHIP_V2_TABLE, int(existing["id"]), relationship)
                ids.append(int(existing["id"]))
            else:
                ids.append(self.insert(self.RELATIONSHIP_V2_TABLE, relationship))
        return ids

    def list_relationships_v2(self, document_id: int | None = None) -> list[dict[str, Any]]:
        if document_id:
            return self.list(
                self.RELATIONSHIP_V2_TABLE,
                where="source_knowledge_document_id=? OR target_knowledge_document_id=?",
                params=(document_id, document_id),
                order_by="confidence DESC, weight DESC, id DESC",
                limit=None,
            )
        return self.list(self.RELATIONSHIP_V2_TABLE, order_by="confidence DESC, weight DESC, id DESC", limit=None)

    def add_citation_metadata(self, citation: KnowledgeCitationMetadata) -> int:
        return self.insert(self.CITATION_METADATA_TABLE, citation.to_dict())

    def list_citation_metadata(self, *, query_text: str | None = None, limit: int | None = 50) -> list[dict[str, Any]]:
        return self.list(
            self.CITATION_METADATA_TABLE,
            where="query_text=?" if query_text else None,
            params=(query_text,) if query_text else (),
            order_by="score DESC, id DESC",
            limit=limit,
        )

    def get_metadata_cache(self, cache_key: str) -> dict[str, Any] | None:
        return self.fetch_one(f"SELECT * FROM {self.METADATA_CACHE_TABLE} WHERE cache_key=?", (cache_key,))

    def upsert_metadata_cache(
        self,
        *,
        cache_key: str,
        knowledge_document_id: int | None,
        source_checksum: str | None,
        metadata_hash: str,
        payload_json: str,
    ) -> int:
        data = {
            "cache_key": cache_key,
            "knowledge_document_id": knowledge_document_id,
            "source_checksum": source_checksum,
            "metadata_hash": metadata_hash,
            "payload_json": payload_json,
        }
        existing = self.get_metadata_cache(cache_key)
        if existing:
            self.update(self.METADATA_CACHE_TABLE, int(existing["id"]), data)
            return int(existing["id"])
        return self.insert(self.METADATA_CACHE_TABLE, data)
