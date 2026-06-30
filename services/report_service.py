"""Service layer for Advisory Report Engine."""

from __future__ import annotations

from typing import Any
import json
import logging

from models.report_evidence import ReportEvidence
from models.report_request import ReportRequest
from models.report_result import ExportReadyReport, ReportResult, ReportValidationResult
from models.report_section import ReportSection
from repositories.report_repository import ReportRepository
from services.evidence_service import EvidenceService
from services.recommendation_service import RecommendationService

logger = logging.getLogger(__name__)


class ReportService:
    """Build evidence-backed advisory reports without export side effects."""

    def __init__(
        self,
        *,
        repository: ReportRepository | None = None,
        evidence_service: EvidenceService | None = None,
        recommendation_service: RecommendationService | None = None,
    ) -> None:
        self.repository = repository or ReportRepository()
        self.evidence_service = evidence_service or EvidenceService(repository=self.repository)
        self.recommendation_service = recommendation_service or RecommendationService()

    def generate_report(self, request: ReportRequest) -> ReportResult:
        """Run the advisory report pipeline and store report history."""
        logger.info("Start advisory report generation type=%s", request.report_type)
        data = self.collect(request)
        evidence = self.evidence_service.collect_evidence(request, data)
        validation = self.validate(request, data, evidence)
        if not validation.passed:
            result = ReportResult(
                request=request,
                sections=[],
                recommendations=[],
                evidence=evidence,
                validation=validation,
                status="invalid",
            )
            result.report_id = self.repository.store_report_history(result)
            logger.info("Finish advisory report generation status=invalid")
            return result

        sections = self.aggregate(request, evidence)
        recommendations = self.build_recommendations(evidence)
        result = ReportResult(
            request=request,
            sections=sections,
            recommendations=recommendations,
            evidence=evidence,
            validation=validation,
        )
        result.report_id = self.repository.store_report_history(result)
        logger.info("Finish advisory report generation report_id=%s", result.report_id)
        return result

    def collect(self, request: ReportRequest) -> dict[str, Any]:
        """Collect report data from existing repositories."""
        return self.repository.load_report_data(
            workspace_id=request.workspace_id,
            topic=request.topic,
        )

    def validate(
        self,
        request: ReportRequest,
        data: dict[str, Any],
        evidence: list[ReportEvidence],
    ) -> ReportValidationResult:
        """Validate report request, workspace, evidence and citations."""
        errors = request.validate()
        warnings: list[str] = []
        errors.extend(self.evidence_service.reject_missing_evidence(evidence))
        if request.workspace_id and not data.get("workspace"):
            errors.append("Missing workspace")
        errors.extend(self._metadata_errors(data.get("documents", [])))
        errors.extend(self._citation_errors(data.get("citations", [])))
        if not data.get("task_updates"):
            warnings.append("No task updates available for this report")
        return ReportValidationResult(passed=not errors, errors=errors, warnings=warnings)

    def aggregate(self, request: ReportRequest, evidence: list[ReportEvidence]) -> list[ReportSection]:
        """Group evidence into report sections."""
        grouped: dict[str, list[ReportEvidence]] = {
            "Task Progress": [],
            "Document Evidence": [],
            "Knowledge Evidence": [],
        }
        for item in evidence:
            if item.source_type in {"task", "task_update"}:
                grouped["Task Progress"].append(item)
            elif item.source_type == "document":
                grouped["Document Evidence"].append(item)
            else:
                grouped["Knowledge Evidence"].append(item)
        sections: list[ReportSection] = []
        for title, items in grouped.items():
            if not items:
                continue
            sections.append(
                ReportSection(
                    title=f"{request.title} - {title}",
                    statements=[self._statement(item) for item in items],
                    evidence=items,
                )
            )
        return sections

    def build_recommendations(self, evidence: list[ReportEvidence]) -> list[Any]:
        """Build ranked evidence-backed recommendations."""
        return self.recommendation_service.build_recommendations(evidence)

    def approve_for_export(self, report_id: int, *, approved_by: str) -> ExportReadyReport:
        """Create an export-ready object after human approval."""
        if not approved_by.strip():
            raise ValueError("approved_by is required")
        row = self.repository.get_report(report_id)
        if not row:
            raise ValueError("Report not found")
        payload = json.loads(str(row["result_json"]))
        validation = payload.get("validation") or {}
        if not validation.get("passed"):
            raise ValueError("Invalid report cannot be export ready")
        self.repository.update_report_status(report_id, "export_ready", approved_by=approved_by)
        payload["status"] = "export_ready"
        payload["export_ready"] = True
        return ExportReadyReport(
            report_id=report_id,
            title=str(row["title"]),
            payload=payload,
            approved_by=approved_by,
        )

    @staticmethod
    def _statement(evidence: ReportEvidence) -> str:
        return f"{evidence.title}: {evidence.excerpt} [{evidence.citation}]"

    @staticmethod
    def _metadata_errors(documents: list[dict[str, Any]]) -> list[str]:
        errors: list[str] = []
        for document in documents:
            if not document.get("title") or not document.get("checksum"):
                errors.append(f"Missing metadata for document {document.get('id')}")
        return errors

    def _citation_errors(self, citations: list[dict[str, Any]]) -> list[str]:
        errors: list[str] = []
        for citation in citations:
            source_id = citation.get("source_knowledge_document_id")
            if not source_id:
                errors.append(f"Broken citation {citation.get('id')}")
                continue
            row = self.repository.fetch_one(
                "SELECT id FROM knowledge_documents WHERE id=?",
                (int(source_id),),
            )
            if not row:
                errors.append(f"Unknown document for citation {citation.get('id')}")
        return errors
