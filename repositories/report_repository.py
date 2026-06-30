"""Repository for Advisory Report Engine."""

from __future__ import annotations

from typing import Any
import json

from models.report_result import ReportResult
from repositories.base_repository import BaseRepository


class ReportRepository(BaseRepository):
    """Persistence and data loading for advisory reports."""

    TABLE = "advisory_reports"

    def load_report_data(
        self,
        *,
        workspace_id: int | None = None,
        topic: str | None = None,
    ) -> dict[str, Any]:
        """Load existing project data used by advisory reports."""
        return {
            "workspace": self.load_workspace(workspace_id) if workspace_id else None,
            "tasks": self.load_tasks(workspace_id=workspace_id, topic=topic),
            "task_updates": self.load_task_updates(workspace_id=workspace_id, topic=topic),
            "documents": self.load_documents(topic=topic),
            "knowledge_documents": self.load_knowledge_documents(topic=topic),
            "citations": self.load_citations(),
        }

    def load_workspace(self, workspace_id: int) -> dict[str, Any] | None:
        """Load one workspace by id."""
        return self.fetch_one("SELECT * FROM workspaces WHERE id=?", (workspace_id,))

    def load_tasks(
        self,
        *,
        workspace_id: int | None = None,
        topic: str | None = None,
    ) -> list[dict[str, Any]]:
        """Load tasks filtered by workspace or topic."""
        query = """
            SELECT t.*, ws.name AS workspace_name
            FROM tasks t
            LEFT JOIN workspaces ws ON ws.id=t.workspace_id
            WHERE 1=1
        """
        params: list[Any] = []
        if workspace_id:
            query += " AND t.workspace_id=?"
            params.append(workspace_id)
        if topic:
            like = f"%{topic}%"
            query += " AND (t.title LIKE ? OR COALESCE(t.description, '') LIKE ? OR COALESCE(t.field, '') LIKE ?)"
            params.extend([like, like, like])
        query += " ORDER BY COALESCE(t.deadline,'9999-12-31'), t.id DESC"
        return self.fetch_all(query, tuple(params))

    def load_task_updates(
        self,
        *,
        workspace_id: int | None = None,
        topic: str | None = None,
    ) -> list[dict[str, Any]]:
        """Load task updates filtered by workspace or topic."""
        query = """
            SELECT u.*, t.title AS task_title, t.workspace_id
            FROM task_updates u
            JOIN tasks t ON t.id=u.task_id
            WHERE 1=1
        """
        params: list[Any] = []
        if workspace_id:
            query += " AND t.workspace_id=?"
            params.append(workspace_id)
        if topic:
            like = f"%{topic}%"
            query += " AND (u.content LIKE ? OR t.title LIKE ?)"
            params.extend([like, like])
        query += " ORDER BY u.update_date DESC, u.id DESC"
        return self.fetch_all(query, tuple(params))

    def load_documents(self, *, topic: str | None = None) -> list[dict[str, Any]]:
        """Load document metadata filtered by topic."""
        query = "SELECT * FROM documents WHERE status!='deleted'"
        params: list[Any] = []
        if topic:
            like = f"%{topic}%"
            query += """
                AND (
                    title LIKE ?
                    OR COALESCE(summary, '') LIKE ?
                    OR COALESCE(keywords, '') LIKE ?
                    OR COALESCE(document_number, '') LIKE ?
                )
            """
            params.extend([like, like, like, like])
        query += " ORDER BY updated_at DESC, id DESC"
        return self.fetch_all(query, tuple(params))

    def load_knowledge_documents(self, *, topic: str | None = None) -> list[dict[str, Any]]:
        """Load READY knowledge documents filtered by topic."""
        query = "SELECT * FROM knowledge_documents WHERE UPPER(status)='READY'"
        params: list[Any] = []
        if topic:
            like = f"%{topic}%"
            query += " AND (title LIKE ? OR COALESCE(metadata_json, '') LIKE ?)"
            params.extend([like, like])
        query += " ORDER BY updated_at DESC, id DESC"
        return self.fetch_all(query, tuple(params))

    def load_citations(self) -> list[dict[str, Any]]:
        """Load document citation metadata."""
        return self.fetch_all("SELECT * FROM knowledge_citation_metadata ORDER BY score DESC, id DESC")

    def load_evidence(self, evidence_id: int) -> dict[str, Any] | None:
        """Load a stored report history row by id."""
        return self.find(self.TABLE, evidence_id)

    def store_report_history(self, report: ReportResult) -> int:
        """Store advisory report history."""
        data = {
            "report_type": report.request.normalized_type(),
            "title": report.request.title,
            "workspace_id": report.request.workspace_id,
            "topic": report.request.topic,
            "request_json": json.dumps(report.to_dict()["request"], ensure_ascii=False),
            "result_json": json.dumps(report.to_dict(), ensure_ascii=False),
            "status": report.status,
            "created_by": report.request.requested_by,
        }
        return self.insert(self.TABLE, data)

    def update_report_status(self, report_id: int, status: str, *, approved_by: str | None = None) -> int:
        """Update report history status."""
        if approved_by:
            return self.execute(
                f"""
                UPDATE {self.TABLE}
                SET status=?, approved_by=?, approved_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP
                WHERE id=?
                """,
                (status, approved_by, report_id),
            )
        return self.update(self.TABLE, report_id, {"status": status})

    def get_report(self, report_id: int) -> dict[str, Any] | None:
        """Load stored report history by id."""
        return self.find(self.TABLE, report_id)
