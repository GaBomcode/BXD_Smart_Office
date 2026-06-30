"""Tests for EPIC-01 Advisory Report Engine."""

from __future__ import annotations

import pytest

from database.init_db import init_database
from models.knowledge_citation_metadata import KnowledgeCitationMetadata
from models.knowledge_document import KnowledgeDocument
from models.library_document import LibraryDocument
from models.report_evidence import ReportEvidence
from models.report_request import ReportRequest
from repositories.document_library_repository import DocumentLibraryRepository
from repositories.knowledge_repository import KnowledgeRepository
from repositories.report_repository import ReportRepository
from repositories.task_repository import TaskRepository
from services.evidence_service import EvidenceService
from services.recommendation_service import RecommendationService
from services.report_service import ReportService


def _seed_project_data() -> dict[str, int]:
    init_database()
    task_repo = TaskRepository()
    workspace_id = task_repo.create_workspace(
        {
            "name": "Ho so bao cao tu van",
            "description": "Theo doi noi dung can bao cao",
            "field": "Tong hop",
            "status": "Dang xu ly",
        }
    )
    task_id = task_repo.create_task(
        {
            "workspace_id": workspace_id,
            "title": "Tong hop bao cao tuan",
            "description": "Tong hop tien do va minh chung bao cao tuan",
            "work_code_id": None,
            "field": "Tong hop",
            "assigned_to_id": None,
            "deadline": "2026-06-30",
            "priority": "Cao",
            "status": "Dang thuc hien",
            "progress": 40,
            "related_document": "01-BC/BXD",
            "point": 1.0,
        }
    )
    task_repo.add_update(task_id, "Da thu thap minh chung va dang tong hop", 40, None)
    document_id = DocumentLibraryRepository().create_document(
        LibraryDocument(
            title="Bao cao nguon",
            file_name="bao-cao.txt",
            file_path="workspace/library/bao-cao.txt",
            file_ext=".txt",
            file_size=100,
            checksum="checksum-report",
            document_type="Bao cao",
            document_number="01-BC/BXD",
            summary="Minh chung cho bao cao tu van.",
            keywords="bao cao, tu van",
            field="Tong hop",
            status="indexed",
        )
    )
    knowledge_id = KnowledgeRepository().save(
        KnowledgeDocument(
            document_id=document_id,
            library_document_id=document_id,
            title="Knowledge bao cao",
            full_text="Noi dung tri thuc co the dung lam bang chung bao cao.",
            checksum="knowledge-checksum",
            status="READY",
        )
    )
    citation_id = KnowledgeRepository().add_citation_metadata(
        KnowledgeCitationMetadata(
            query_text="report",
            source_knowledge_document_id=knowledge_id,
            title="Knowledge bao cao",
            document_number="01-BC/BXD",
            score=1.0,
        )
    )
    return {
        "workspace_id": workspace_id,
        "task_id": task_id,
        "document_id": document_id,
        "knowledge_id": knowledge_id,
        "citation_id": citation_id,
    }


@pytest.mark.parametrize("report_type", ["weekly", "monthly", "quarterly", "topic", "work_dossier"])
def test_all_report_types_generate_with_evidence(report_type: str) -> None:
    ids = _seed_project_data()
    request = ReportRequest(
        report_type=report_type,
        title=f"{report_type} advisory report",
        workspace_id=ids["workspace_id"],
        topic="bao cao" if report_type in {"topic", "work_dossier"} else None,
    )

    result = ReportService().generate_report(request)

    assert result.validation.passed is True
    assert result.report_id is not None
    assert result.sections
    assert result.evidence
    assert all(section.evidence for section in result.sections)


def test_evidence_validation_rejects_missing_workspace() -> None:
    _seed_project_data()

    result = ReportService().generate_report(
        ReportRequest(report_type="weekly", title="Missing workspace", workspace_id=999)
    )

    assert result.validation.passed is False
    assert "Missing workspace" in result.validation.errors


def test_citation_resolution_requires_existing_source() -> None:
    ids = _seed_project_data()
    citations = KnowledgeRepository().list_citation_metadata(query_text="report", limit=None)

    resolved = EvidenceService().resolve_citations(citations)

    assert len(resolved) == 1
    assert resolved[0].source_id == ids["citation_id"]


def test_broken_citation_rejects_report() -> None:
    _seed_project_data()
    KnowledgeRepository().add_citation_metadata(
        KnowledgeCitationMetadata(
            query_text="broken",
            source_knowledge_document_id=999,
            title="Broken citation",
            score=1.0,
        )
    )

    result = ReportService().generate_report(ReportRequest(report_type="monthly", title="Broken citation report"))

    assert result.validation.passed is False
    assert any("Unknown document for citation" in error for error in result.validation.errors)


def test_recommendation_ranking_and_duplicate_removal() -> None:
    _seed_project_data()
    evidence = ReportEvidence(
        source_type="task",
        source_id=1,
        title="Task",
        excerpt="Task evidence",
        citation="task:1",
        metadata={"priority": "Cao", "progress": 20, "status": "Dang thuc hien"},
    )
    service = RecommendationService()

    recommendations = service.remove_duplicates(
        service.build_recommendations([evidence, evidence])
    )

    assert len(recommendations) == 1
    assert recommendations[0].supporting_evidence
    assert recommendations[0].priority == "high"


def test_missing_evidence_rejects_report() -> None:
    init_database()

    result = ReportService().generate_report(
        ReportRequest(report_type="topic", title="No evidence", topic="khong-co-du-lieu")
    )

    assert result.validation.passed is False
    assert "No evidence available for report" in result.validation.errors


def test_export_ready_requires_human_approval() -> None:
    ids = _seed_project_data()
    result = ReportService().generate_report(
        ReportRequest(
            report_type="weekly",
            title="Export ready report",
            workspace_id=ids["workspace_id"],
        )
    )
    assert result.report_id is not None

    export_ready = ReportService().approve_for_export(result.report_id, approved_by="Tester")

    assert export_ready.report_id == result.report_id
    assert export_ready.approved_by == "Tester"
    assert export_ready.payload["export_ready"] is True


def test_invalid_report_cannot_be_export_ready() -> None:
    init_database()
    result = ReportService().generate_report(
        ReportRequest(report_type="topic", title="Invalid export", topic="empty")
    )
    assert result.report_id is not None

    with pytest.raises(ValueError, match="Invalid report"):
        ReportService().approve_for_export(result.report_id, approved_by="Tester")


def test_report_history_is_stored() -> None:
    ids = _seed_project_data()
    result = ReportService().generate_report(
        ReportRequest(report_type="quarterly", title="Stored report", workspace_id=ids["workspace_id"])
    )
    assert result.report_id is not None

    stored = ReportRepository().get_report(result.report_id)

    assert stored is not None
    assert stored["title"] == "Stored report"
    assert stored["status"] == "pending_human_review"
