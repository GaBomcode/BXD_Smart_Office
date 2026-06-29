"""Tests for RC1-003 AI Draft final validation."""

from __future__ import annotations

import pytest

from database.init_db import init_database
from models.ai_draft_request import AIDraftRequest
from models.ai_draft_result import AIDraftResult
from models.library_document import LibraryDocument
from repositories.ai_draft_repository import AIDraftRepository
from repositories.document_library_repository import DocumentLibraryRepository
from services.ai_draft_service import AIDraftService
from services.document_validation.draft_validator import DraftValidator


def _source_document() -> int:
    return DocumentLibraryRepository().create_document(
        LibraryDocument(
            title="Nguon can cu hop le",
            file_name="nguon.txt",
            file_path="workspace/library/nguon.txt",
            file_ext=".txt",
            file_size=100,
            checksum="checksum-validation",
            document_type="Cong van",
            document_number="01-CV/BXD",
            summary="Nguon dung de kiem tra citation.",
            keywords="citation, validation",
            status="indexed",
        )
    )


def _draft(content: str | None = None, *, title: str = "Du thao hop le") -> dict:
    return {
        "id": 1,
        "request_id": 1,
        "title": title,
        "document_type": "Cong van",
        "draft_content": content if content is not None else _valid_content(),
        "status": "approved",
    }


def _valid_content() -> str:
    return "\n".join(
        [
            "DU THAO",
            "DU THAO HOP LE",
            "",
            "So: 01/BXD",
            "",
            "Can cu nguon da thu thap: [1]",
            "",
            "Noi dung tham muu:",
            "1. Can cu va boi canh",
            "Noi dung phan tich du dai de dam bao body khong rong va co du thong tin can thiet.",
            "2. To chuc thuc hien",
            "Noi dung trien khai duoc trinh bay theo citation da gan.",
            "",
            "Ket luan:",
            "Kinh de nghi xem xet, phe duyet noi dung neu phu hop.",
            "",
            "Nguoi ky",
            "Nguyen Van A",
        ]
    )


def _citation(source_document_id: int | None = None) -> dict:
    return {
        "id": 1,
        "source_document_id": source_document_id,
        "source_chunk_id": 10,
        "title": "Nguon can cu hop le",
        "document_number": "01-CV/BXD",
        "checksum": "checksum-validation",
        "score": 1.0,
    }


def test_valid_draft_passes_and_generates_report() -> None:
    init_database()
    source_id = _source_document()

    result = DraftValidator().validate(_draft(), citations=[_citation(source_id)])

    assert result.passed is True
    assert result.report["status"] in {"PASS", "WARNING"}
    assert result.errors == []
    assert result.score > 0


def test_missing_title_fails_validation() -> None:
    init_database()
    source_id = _source_document()

    result = DraftValidator().validate(_draft(title=""), citations=[_citation(source_id)])

    assert result.passed is False
    assert "title" in result.empty_fields


def test_missing_body_fails_validation() -> None:
    init_database()
    source_id = _source_document()

    result = DraftValidator().validate(_draft(content=""), citations=[_citation(source_id)])

    assert result.passed is False
    assert "body" in result.missing_sections


def test_missing_conclusion_fails_validation() -> None:
    init_database()
    source_id = _source_document()
    content = _valid_content().replace("Ket luan:", "Tong hop:")

    result = DraftValidator().validate(_draft(content=content), citations=[_citation(source_id)])

    assert result.passed is False
    assert "conclusion" in result.missing_sections


def test_missing_signature_fails_validation() -> None:
    init_database()
    source_id = _source_document()
    content = _valid_content().replace("\nNguoi ky\nNguyen Van A", "")

    result = DraftValidator().validate(_draft(content=content), citations=[_citation(source_id)])

    assert result.passed is False
    assert "signature" in result.missing_sections


def test_broken_citation_fails_validation() -> None:
    init_database()

    result = DraftValidator().validate(_draft(), citations=[_citation(999)])

    assert result.passed is False
    assert result.invalid_citations


def test_unknown_placeholder_fails_validation() -> None:
    init_database()
    source_id = _source_document()
    content = _valid_content() + "\n{{TODO}}\n[[UNKNOWN]]\n<MISSING>"

    result = DraftValidator().validate(_draft(content=content), citations=[_citation(source_id)])

    assert result.passed is False
    assert any("Invalid placeholders" in error for error in result.errors)


def test_duplicate_citation_is_removed_and_warned() -> None:
    init_database()
    source_id = _source_document()
    duplicate = _citation(source_id)

    result = DraftValidator().validate(_draft(), citations=[duplicate, dict(duplicate)])

    assert result.passed is True
    assert any("Duplicate citations removed" in warning for warning in result.warnings)


def test_empty_paragraph_is_detected() -> None:
    init_database()
    source_id = _source_document()
    content = _valid_content() + "\n   "

    result = DraftValidator().validate(_draft(content=content), citations=[_citation(source_id)])

    assert result.passed is True
    assert any("Empty paragraphs" in warning for warning in result.warnings)


def test_export_rejects_invalid_draft() -> None:
    init_database()
    repository = AIDraftRepository()
    request_id = repository.create_request(
        AIDraftRequest(
            request_text="Lap cong van kiem tra xuat file",
            selected_document_type="Cong van",
            status="ready_for_template_selection",
        )
    )
    result_id = repository.create_result(
        AIDraftResult(
            request_id=request_id,
            title="Du thao khong hop le",
            document_type="Cong van",
            draft_content="Noi dung {{TODO}}",
            status="approved",
        )
    )

    with pytest.raises(ValueError, match="Draft validation failed"):
        AIDraftService(repository=repository).export_docx(result_id)


def test_validation_regression_accepts_existing_generated_draft_flow() -> None:
    init_database()
    source_id = _source_document()
    service = AIDraftService()
    request_id = service.create_request("Lap ke hoach trien khai citation validation")
    result_id = service.generate_outline(request_id, title="Du thao validation")
    outline = service.repository.get_result(result_id)
    assert outline is not None
    service.approve_outline(result_id, approved_outline=str(outline["outline_content"]), actor="Tester")
    draft = service.generate_draft(result_id)

    result = DraftValidator().validate(draft, citations=[_citation(source_id)])

    assert result.passed is True
