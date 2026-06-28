from __future__ import annotations

from pathlib import Path

import pytest

from database.init_db import init_database
from models.library_document import LibraryDocument
from repositories.ai_draft_repository import AIDraftRepository
from repositories.document_library_repository import DocumentLibraryRepository
from services.ai_draft_service import AIDraftService
from services.knowledge_service import KnowledgeService


def _seed_document_library() -> int:
    init_database()
    repository = DocumentLibraryRepository()
    return repository.create_document(
        LibraryDocument(
            title="Ke hoach noi bo ve cong tac bien che",
            file_name="ke-hoach-bien-che.txt",
            file_path="workspace/library/ke-hoach-bien-che.txt",
            file_ext=".txt",
            file_size=128,
            checksum="checksum-bien-che",
            document_type="Ke hoach",
            document_number="12-KH/BXD",
            issued_date="2026-01-10",
            issuing_agency="Ban Xay dung Dang",
            summary="Ke hoach ve cong tac bien che va to chuc can bo.",
            keywords="bien che, can bo, to chuc",
            field="To chuc",
            status="indexed",
        )
    )


def _seed_knowledge(document_id: int) -> None:
    service = KnowledgeService()
    service.ingest_library_document(
        document_id,
        text="Can cu ke hoach cong tac bien che. Noi dung trien khai ve to chuc can bo va bao cao ket qua.",
    )
    service.embed_chunks()


def test_ai_draft_migration_creates_tables() -> None:
    init_database()
    rows = AIDraftRepository().fetch_all(
        "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ai_draft_%' ORDER BY name"
    )
    assert [row["name"] for row in rows] == [
        "ai_draft_citations",
        "ai_draft_requests",
        "ai_draft_results",
        "ai_draft_revisions",
    ]


def test_request_intent_detection_and_manual_type_selection() -> None:
    init_database()
    service = AIDraftService()
    request_id = service.create_request("Can tham muu van ban ve noi dung moi chua ro loai")
    request = service.repository.get_request(request_id)
    assert request is not None
    assert request["status"] == "needs_document_type_selection"

    updated = service.select_document_type(request_id, "Cong van")
    assert updated["selected_document_type"] == "Cong van"
    assert updated["status"] == "ready_for_template_selection"

    detection = service.detect_intent("Lap ke hoach trien khai cong tac bien che nam 2026")
    assert detection.document_type == "Ke hoach"
    assert detection.confidence >= 0.55


def test_template_selector_returns_top_five_with_citation() -> None:
    document_id = _seed_document_library()
    service = AIDraftService()
    request_id = service.create_request("Lap ke hoach cong tac bien che va to chuc can bo")
    suggestions = service.suggest_templates(request_id)
    assert suggestions
    assert suggestions[0]["document"]["id"] == document_id
    assert suggestions[0]["citation"]["checksum"] == "checksum-bien-che"
    assert len(suggestions) <= 5


def test_evidence_outline_draft_review_and_export(tmp_path: Path) -> None:
    document_id = _seed_document_library()
    _seed_knowledge(document_id)
    service = AIDraftService()
    request_id = service.create_request("Lap ke hoach trien khai cong tac bien che va to chuc can bo")

    evidence = service.collect_evidence(request_id, top_k=3)
    assert evidence
    assert evidence[0]["citation"]["checksum"]

    result_id = service.generate_outline(request_id, template_document_id=document_id, title="Du thao ke hoach bien che")
    result = service.repository.get_result(result_id)
    assert result is not None
    assert result["status"] == "pending_outline_review"
    assert "Dàn ý" in str(result["outline_content"])

    with pytest.raises(ValueError):
        service.generate_draft(result_id)

    approved_outline = str(result["outline_content"]) + "\n5. Kiem tra citation truoc khi ban hanh"
    service.approve_outline(result_id, approved_outline=approved_outline, actor="Tester")
    draft = service.generate_draft(result_id)
    assert draft["status"] == "pending_user_review"
    assert "[1]" in str(draft["draft_content"])

    service.save_user_review(result_id, str(draft["draft_content"]) + "\nDa duoc nguoi dung ra soat.", actor="Tester")
    approved = service.approve_draft(result_id, actor="Tester")
    assert approved["status"] == "approved"

    output = service.export_docx(result_id)
    assert output.exists()
    assert output.suffix == ".docx"
    exported = service.repository.get_result(result_id)
    assert exported is not None
    assert exported["status"] == "exported"
