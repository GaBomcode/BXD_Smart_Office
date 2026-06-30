"""Evidence service for Advisory Report Engine."""

from __future__ import annotations

from typing import Any
import logging

from models.report_evidence import ReportEvidence
from models.report_request import ReportRequest
from repositories.document_library_repository import DocumentLibraryRepository
from repositories.report_repository import ReportRepository

logger = logging.getLogger(__name__)


class EvidenceService:
    """Collect and verify evidence from existing project data."""

    def __init__(
        self,
        *,
        repository: ReportRepository | None = None,
        document_repository: DocumentLibraryRepository | None = None,
    ) -> None:
        self.repository = repository or ReportRepository()
        self.document_repository = document_repository or DocumentLibraryRepository()

    def collect_evidence(self, request: ReportRequest, data: dict[str, Any]) -> list[ReportEvidence]:
        """Collect traceable evidence for a report request."""
        logger.info("Collect advisory report evidence type=%s", request.report_type)
        evidence: list[ReportEvidence] = []
        evidence.extend(self._task_evidence(data.get("tasks", [])))
        evidence.extend(self._update_evidence(data.get("task_updates", [])))
        evidence.extend(self._document_evidence(data.get("documents", [])))
        evidence.extend(self._knowledge_evidence(data.get("knowledge_documents", [])))
        verified = [item for item in evidence if self.verify_reference(item)]
        logger.info("Collected %s verified evidence items", len(verified))
        return verified

    def resolve_citations(self, citations: list[dict[str, Any]]) -> list[ReportEvidence]:
        """Resolve knowledge citations to report evidence."""
        resolved: list[ReportEvidence] = []
        for citation in citations:
            document_id = citation.get("source_knowledge_document_id")
            if not document_id:
                continue
            title = str(citation.get("title") or "Knowledge citation")
            resolved.append(
                ReportEvidence(
                    source_type="citation",
                    source_id=int(citation["id"]),
                    title=title,
                    excerpt=str(citation.get("section") or title),
                    citation=f"citation:{citation['id']}",
                    metadata=dict(citation),
                    confidence=float(citation.get("score") or 1.0),
                )
            )
        return [item for item in resolved if self.verify_reference(item)]

    def verify_reference(self, evidence: ReportEvidence) -> bool:
        """Return true when evidence points to an existing project record."""
        if evidence.source_type == "task":
            row = self.repository.fetch_one("SELECT id FROM tasks WHERE id=?", (evidence.source_id,))
            return row is not None
        if evidence.source_type == "task_update":
            row = self.repository.fetch_one(
                "SELECT id FROM task_updates WHERE id=?",
                (evidence.source_id,),
            )
            return row is not None
        if evidence.source_type == "document":
            return self.document_repository.get_document(evidence.source_id) is not None
        if evidence.source_type == "knowledge_document":
            return self.repository.fetch_one(
                "SELECT id FROM knowledge_documents WHERE id=? AND UPPER(status)='READY'",
                (evidence.source_id,),
            ) is not None
        if evidence.source_type == "citation":
            row = self.repository.fetch_one(
                """
                SELECT c.id
                FROM knowledge_citation_metadata c
                JOIN knowledge_documents d ON d.id=c.source_knowledge_document_id
                WHERE c.id=?
                """,
                (evidence.source_id,),
            )
            return row is not None
        return False

    def reject_missing_evidence(self, evidence: list[ReportEvidence]) -> list[str]:
        """Return validation errors for missing evidence."""
        if not evidence:
            return ["No evidence available for report"]
        return []

    @staticmethod
    def _task_evidence(tasks: list[dict[str, Any]]) -> list[ReportEvidence]:
        return [
            ReportEvidence(
                source_type="task",
                source_id=int(task["id"]),
                title=str(task.get("title") or "Task"),
                excerpt=str(task.get("description") or task.get("title") or ""),
                citation=f"task:{task['id']}",
                metadata=task,
                confidence=1.0,
            )
            for task in tasks
            if task.get("id") and (task.get("title") or task.get("description"))
        ]

    @staticmethod
    def _update_evidence(updates: list[dict[str, Any]]) -> list[ReportEvidence]:
        return [
            ReportEvidence(
                source_type="task_update",
                source_id=int(update["id"]),
                title=str(update.get("task_title") or "Task update"),
                excerpt=str(update.get("content") or ""),
                citation=f"task_update:{update['id']}",
                metadata=update,
                confidence=1.0,
            )
            for update in updates
            if update.get("id") and update.get("content")
        ]

    @staticmethod
    def _document_evidence(documents: list[dict[str, Any]]) -> list[ReportEvidence]:
        return [
            ReportEvidence(
                source_type="document",
                source_id=int(document["id"]),
                title=str(document.get("title") or document.get("file_name") or "Document"),
                excerpt=str(document.get("summary") or document.get("keywords") or document.get("title") or ""),
                citation=f"document:{document['id']}",
                metadata=document,
                confidence=1.0,
            )
            for document in documents
            if document.get("id") and (document.get("title") or document.get("summary"))
        ]

    @staticmethod
    def _knowledge_evidence(documents: list[dict[str, Any]]) -> list[ReportEvidence]:
        return [
            ReportEvidence(
                source_type="knowledge_document",
                source_id=int(document["id"]),
                title=str(document.get("title") or "Knowledge document"),
                excerpt=str(document.get("full_text") or document.get("title") or "")[:500],
                citation=f"knowledge_document:{document['id']}",
                metadata=document,
                confidence=1.0,
            )
            for document in documents
            if document.get("id") and document.get("title")
        ]
