"""Repository cho phân hệ Kho văn bản."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any
import logging

from models.document_keyword import DocumentKeyword
from models.document_relation import DocumentRelation
from models.library_document import LibraryDocument
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class DocumentLibraryRepository(BaseRepository):
    """Đọc/ghi chỉ mục văn bản, từ khóa và quan hệ trong SQLite."""

    DOCUMENT_TABLE = "documents"
    KEYWORD_TABLE = "document_keywords"
    RELATION_TABLE = "document_relations"

    def create_document(self, document: LibraryDocument) -> int:
        logger.info("Create library document: %s", document.file_name)
        return self.insert(self.DOCUMENT_TABLE, document.to_dict())

    def get_document(self, document_id: int) -> dict[str, Any] | None:
        return self.find(self.DOCUMENT_TABLE, document_id)

    def get_by_path(self, file_path: str) -> dict[str, Any] | None:
        return self.fetch_one(f"SELECT * FROM {self.DOCUMENT_TABLE} WHERE file_path=?", (file_path,))

    def get_by_checksum(self, checksum: str) -> dict[str, Any] | None:
        return self.fetch_one(f"SELECT * FROM {self.DOCUMENT_TABLE} WHERE checksum=?", (checksum,))

    def upsert_document(self, document: LibraryDocument) -> int:
        existing = self.get_by_path(document.file_path)
        if existing:
            self.update_document(int(existing["id"]), document.to_dict())
            return int(existing["id"])
        return self.create_document(document)

    def update_document(self, document_id: int, data: dict[str, Any]) -> int:
        logger.info("Update library document id=%s", document_id)
        return self.update(self.DOCUMENT_TABLE, document_id, data)

    def list_documents(
        self,
        *,
        status: str | None = None,
        file_ext: str | None = None,
        document_type: str | None = None,
        field: str | None = None,
        issuing_agency: str | None = None,
        year: str | None = None,
        keyword: str | None = None,
        limit: int | None = 500,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if status:
            clauses.append("status=?")
            params.append(status)
        if file_ext:
            clauses.append("file_ext=?")
            params.append(file_ext)
        if document_type:
            clauses.append("document_type=?")
            params.append(document_type)
        if field:
            clauses.append("field=?")
            params.append(field)
        if issuing_agency:
            clauses.append("issuing_agency=?")
            params.append(issuing_agency)
        if year:
            clauses.append("issued_date LIKE ?")
            params.append(f"{year}-%")
        if keyword:
            like = f"%{keyword}%"
            clauses.append(
                "(title LIKE ? OR file_name LIKE ? OR document_number LIKE ? OR keywords LIKE ? OR summary LIKE ?)"
            )
            params.extend([like, like, like, like, like])
        return self.list(
            self.DOCUMENT_TABLE,
            where=" AND ".join(clauses) if clauses else None,
            params=params,
            order_by="updated_at DESC, id DESC",
            limit=limit,
        )

    def replace_keywords(self, document_id: int, keywords: Sequence[DocumentKeyword]) -> None:
        self.execute(f"DELETE FROM {self.KEYWORD_TABLE} WHERE document_id=?", (document_id,))
        for keyword in keywords:
            keyword.document_id = document_id
            self.insert(self.KEYWORD_TABLE, keyword.to_dict())

    def list_keywords(self, document_id: int) -> list[dict[str, Any]]:
        return self.list(
            self.KEYWORD_TABLE,
            where="document_id=?",
            params=(document_id,),
            order_by="weight DESC, keyword ASC",
        )

    def create_relation(self, relation: DocumentRelation) -> int:
        return self.insert(self.RELATION_TABLE, relation.to_dict())

    def list_relations(self, document_id: int) -> list[dict[str, Any]]:
        return self.fetch_all(
            f"""
            SELECT r.*, s.title AS source_title, t.title AS target_title
            FROM {self.RELATION_TABLE} r
            JOIN {self.DOCUMENT_TABLE} s ON s.id=r.source_document_id
            JOIN {self.DOCUMENT_TABLE} t ON t.id=r.target_document_id
            WHERE r.source_document_id=? OR r.target_document_id=?
            ORDER BY r.created_at DESC, r.id DESC
            """,
            (document_id, document_id),
        )

    def status_counts(self) -> dict[str, int]:
        rows = self.fetch_all(f"SELECT status, COUNT(*) total FROM {self.DOCUMENT_TABLE} GROUP BY status")
        return {str(row["status"]): int(row["total"] or 0) for row in rows}

    def distinct_values(self, column: str) -> list[str]:
        allowed = {"file_ext", "document_type", "field", "issuing_agency", "status"}
        if column not in allowed:
            raise ValueError("Cột lọc không hợp lệ")
        rows = self.fetch_all(
            f"SELECT DISTINCT {column} value FROM {self.DOCUMENT_TABLE} WHERE {column} IS NOT NULL AND {column}!='' ORDER BY {column}"
        )
        return [str(row["value"]) for row in rows]
