"""Tests for RC1-002 AI Search workflow."""

from __future__ import annotations

from pathlib import Path

from database.init_db import init_database
from models.knowledge_document import KnowledgeDocument
from models.library_document import LibraryDocument
from models.search_request import SearchRequest
from repositories.document_library_repository import DocumentLibraryRepository
from repositories.embedding_repository import EmbeddingRepository
from repositories.knowledge_repository import KnowledgeRepository
from repositories.vector_repository import VectorRepository
from services.document_library_service import DocumentLibraryService
from services.knowledge.document_snapshot import DocumentSnapshot
from services.knowledge.handoff_service import INVALID, READY, KnowledgeHandoffService
from services.search_service import SearchService


def _create_ready_document(
    tmp_path: Path,
    *,
    file_name: str,
    title: str,
    text: str,
    document_number: str,
    summary: str,
    keywords: str,
) -> int:
    path = tmp_path / file_name
    path.write_text(text, encoding="utf-8")
    document_id = DocumentLibraryRepository().create_document(
        LibraryDocument(
            title=title,
            file_name=file_name,
            file_path=str(path),
            file_ext=path.suffix,
            file_size=path.stat().st_size,
            checksum=DocumentLibraryService.calculate_checksum(path),
            document_type="Cong van",
            document_number=document_number,
            summary=summary,
            keywords=keywords,
            field="Quan ly",
            status="indexed",
        )
    )
    document = DocumentLibraryRepository().get_document(document_id)
    assert document is not None
    result = KnowledgeHandoffService().handoff(DocumentSnapshot.from_library_document(document, full_text=text))
    assert result.status == READY
    return result.knowledge_document_id


def _create_invalid_document() -> int:
    return KnowledgeRepository().save(
        KnowledgeDocument(
            document_id=999,
            library_document_id=999,
            title="Invalid document",
            full_text="invalid full text",
            checksum="invalid-checksum",
            document_number="INVALID-001",
            metadata_json='{"summary":"invalid summary","keywords":"invalid"}',
            status=INVALID,
        )
    )


def test_keyword_search_returns_ready_document_with_citation(tmp_path: Path) -> None:
    init_database()
    _create_ready_document(
        tmp_path,
        file_name="keyword.txt",
        title="Quy che van thu",
        text="Noi dung ve van thu luu tru va ho so.",
        document_number="12-QC/BXD",
        summary="Quy dinh van thu noi bo",
        keywords="van thu, ho so",
    )

    response = SearchService().search(SearchRequest(query="van thu", mode="keyword"))

    assert response["valid"] is True
    assert len(response["results"]) == 1
    result = response["results"][0]
    assert result["title"] == "Quy che van thu"
    assert result["status"] == READY
    assert result["citations"]


def test_semantic_search_returns_ready_document_with_matched_chunk_and_citation(tmp_path: Path) -> None:
    init_database()
    _create_ready_document(
        tmp_path,
        file_name="semantic.txt",
        title="Huong dan cai tao nha cong vu",
        text="Cai tao nha cong vu can lap ke hoach von va bao cao tien do.",
        document_number="22-HD/BXD",
        summary="Huong dan cai tao nha cong vu",
        keywords="cai tao, nha cong vu",
    )

    response = SearchService().search(SearchRequest(query="cai tao nha cong vu", mode="semantic"))

    assert response["valid"] is True
    assert response["results"]
    result = response["results"][0]
    assert result["status"] == READY
    assert result["matched_chunks"]
    assert result["citations"]


def test_hybrid_search_merges_duplicate_keyword_and_semantic_results(tmp_path: Path) -> None:
    init_database()
    _create_ready_document(
        tmp_path,
        file_name="hybrid.txt",
        title="Ke hoach chuyen doi so",
        text="Chuyen doi so nganh xay dung can du lieu so va quy trinh so.",
        document_number="33-KH/BXD",
        summary="Ke hoach chuyen doi so",
        keywords="chuyen doi so, du lieu so",
    )

    response = SearchService().search(SearchRequest(query="chuyen doi so", mode="hybrid"))
    result_ids = [item["document_id"] for item in response["results"]]

    assert response["valid"] is True
    assert len(result_ids) == len(set(result_ids))
    assert len(response["results"]) == 1
    assert response["results"][0]["title"] == "Ke hoach chuyen doi so"


def test_search_excludes_invalid_documents(tmp_path: Path) -> None:
    init_database()
    _create_ready_document(
        tmp_path,
        file_name="ready.txt",
        title="Bao cao hop le",
        text="Bao cao hop le ve cap phep xay dung.",
        document_number="44-BC/BXD",
        summary="cap phep xay dung",
        keywords="cap phep",
    )
    _create_invalid_document()

    response = SearchService().search(SearchRequest(query="invalid", mode="semantic"))

    assert response["valid"] is True
    assert all(item["status"] == READY for item in response["results"])
    assert all(item["title"] != "Invalid document" for item in response["results"])


def test_empty_and_long_query_return_validation_errors() -> None:
    init_database()
    service = SearchService()

    empty_response = service.search(SearchRequest(query="   ", mode="keyword"))
    long_response = service.search(SearchRequest(query="x" * 301, mode="keyword"))

    assert empty_response["valid"] is False
    assert "query must not be empty" in empty_response["errors"]
    assert long_response["valid"] is False
    assert long_response["errors"]


def test_search_reuses_existing_embedding_and_vector_indexes(tmp_path: Path) -> None:
    init_database()
    _create_ready_document(
        tmp_path,
        file_name="reuse.txt",
        title="Quy trinh nghiem thu",
        text="Nghiem thu cong trinh can bien ban va ho so chat luong.",
        document_number="55-QT/BXD",
        summary="Quy trinh nghiem thu cong trinh",
        keywords="nghiem thu, chat luong",
    )
    embedding_count = len(EmbeddingRepository().list_embeddings())
    vector_count = VectorRepository().count()

    response = SearchService().search(SearchRequest(query="nghiem thu cong trinh", mode="semantic"))

    assert response["valid"] is True
    assert len(EmbeddingRepository().list_embeddings()) == embedding_count
    assert VectorRepository().count() == vector_count
