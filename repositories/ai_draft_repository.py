"""Repository for AI Draft Engine."""

from __future__ import annotations

from typing import Any
import logging

from models.ai_draft_citation import AIDraftCitation
from models.ai_draft_request import AIDraftRequest
from models.ai_draft_result import AIDraftResult
from repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class AIDraftRepository(BaseRepository):
    """Read and write AI Draft requests, results, citations, and revisions."""

    REQUEST_TABLE = "ai_draft_requests"
    RESULT_TABLE = "ai_draft_results"
    CITATION_TABLE = "ai_draft_citations"
    REVISION_TABLE = "ai_draft_revisions"

    def create_request(self, request: AIDraftRequest) -> int:
        logger.info("Create AI draft request")
        return self.insert(self.REQUEST_TABLE, request.to_dict())

    def get_request(self, request_id: int) -> dict[str, Any] | None:
        return self.find(self.REQUEST_TABLE, request_id)

    def list_requests(self, *, status: str | None = None, limit: int | None = 100) -> list[dict[str, Any]]:
        return self.list(
            self.REQUEST_TABLE,
            where="status=?" if status else None,
            params=(status,) if status else (),
            order_by="updated_at DESC, id DESC",
            limit=limit,
        )

    def update_request(self, request_id: int, data: dict[str, Any]) -> int:
        return self.update(self.REQUEST_TABLE, request_id, data)

    def create_result(self, result: AIDraftResult) -> int:
        logger.info("Create AI draft result request_id=%s", result.request_id)
        return self.insert(self.RESULT_TABLE, result.to_dict())

    def get_result(self, result_id: int) -> dict[str, Any] | None:
        return self.find(self.RESULT_TABLE, result_id)

    def get_result_by_request(self, request_id: int) -> dict[str, Any] | None:
        return self.fetch_one(
            f"SELECT * FROM {self.RESULT_TABLE} WHERE request_id=? ORDER BY updated_at DESC, id DESC LIMIT 1",
            (request_id,),
        )

    def list_results(self, *, status: str | None = None, limit: int | None = 100) -> list[dict[str, Any]]:
        return self.list(
            self.RESULT_TABLE,
            where="status=?" if status else None,
            params=(status,) if status else (),
            order_by="updated_at DESC, id DESC",
            limit=limit,
        )

    def update_result(self, result_id: int, data: dict[str, Any]) -> int:
        return self.update(self.RESULT_TABLE, result_id, data)

    def add_citation(self, citation: AIDraftCitation) -> int:
        return self.insert(self.CITATION_TABLE, citation.to_dict())

    def replace_citations(
        self,
        *,
        request_id: int,
        result_id: int | None,
        citation_type: str,
        citations: list[AIDraftCitation],
    ) -> list[int]:
        if result_id:
            self.execute(
                f"DELETE FROM {self.CITATION_TABLE} WHERE request_id=? AND result_id=? AND citation_type=?",
                (request_id, result_id, citation_type),
            )
        else:
            self.execute(
                f"DELETE FROM {self.CITATION_TABLE} WHERE request_id=? AND result_id IS NULL AND citation_type=?",
                (request_id, citation_type),
            )
        ids: list[int] = []
        for citation in citations:
            citation.request_id = request_id
            citation.result_id = result_id
            citation.citation_type = citation_type
            ids.append(self.add_citation(citation))
        return ids

    def list_citations(
        self,
        *,
        request_id: int | None = None,
        result_id: int | None = None,
        citation_type: str | None = None,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if request_id:
            clauses.append("request_id=?")
            params.append(request_id)
        if result_id:
            clauses.append("result_id=?")
            params.append(result_id)
        if citation_type:
            clauses.append("citation_type=?")
            params.append(citation_type)
        return self.list(
            self.CITATION_TABLE,
            where=" AND ".join(clauses) if clauses else None,
            params=params,
            order_by="score DESC, id ASC",
            limit=None,
        )

    def add_revision(
        self,
        *,
        result_id: int,
        content: str,
        status: str,
        edited_by: str,
        note: str | None = None,
    ) -> int:
        return self.execute(
            f"""
            INSERT INTO {self.REVISION_TABLE}(result_id, content, status, edited_by, note)
            VALUES(?,?,?,?,?)
            """,
            (result_id, content, status, edited_by, note),
        )

    def list_revisions(self, result_id: int) -> list[dict[str, Any]]:
        return self.list(
            self.REVISION_TABLE,
            where="result_id=?",
            params=(result_id,),
            order_by="created_at DESC, id DESC",
            limit=None,
        )

    def log_audit(
        self,
        *,
        action: str,
        entity_type: str,
        entity_id: int,
        actor: str,
        detail: str | None = None,
    ) -> int:
        return self.execute(
            """
            INSERT INTO audit_logs(action, entity_type, entity_id, actor, detail)
            VALUES(?,?,?,?,?)
            """,
            (action, entity_type, entity_id, actor, detail),
        )
