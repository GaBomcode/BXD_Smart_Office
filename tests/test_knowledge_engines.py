"""Kiểm thử chunk, keyword, relation, graph, embedding và semantic search."""

from pathlib import Path

from database.init_db import init_database
from repositories.document_library_repository import DocumentLibraryRepository
from services.document_library_service import DocumentLibraryService
from services.knowledge_service import KnowledgeService, LocalHashEmbeddingBackend


def _index_library_text(tmp_path: Path, name: str, text: str) -> int:
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    library_service = DocumentLibraryService()
    result = library_service.index_folder(tmp_path)
    assert result["indexed_ids"]
    return int(result["indexed_ids"][-1])


def test_chunk_engine_splits_party_admin_sections() -> None:
    service = KnowledgeService()
    chunks = service.chunk_text(
        """
        ĐẢNG ỦY XÃ VĨNH HÒA
        Số: 325-CV/BXD
        Kính gửi: Các chi bộ
        Điều 1. Triển khai biên chế
        Nơi nhận: Lưu VT
        """
    )
    sections = {chunk.section for chunk in chunks}
    assert "Header" in sections
    assert "Số ký hiệu" in sections
    assert "Kính gửi" in sections
    assert "Nơi nhận" in sections


def test_keyword_engine_extracts_weighted_entities(tmp_path: Path) -> None:
    init_database()
    library_id = _index_library_text(
        tmp_path,
        "325-CV-BXD.txt",
        "Số: 325-CV/BXD\nCÔNG VĂN\nV/v triển khai biên chế tổ chức cán bộ\nTRƯỞNG BAN\nNguyễn Trung Hiền",
    )
    service = KnowledgeService()
    knowledge_id = service.ingest_library_document(library_id)
    entities = service.repository.list_entities(knowledge_id)

    values = {entity["entity_value"] for entity in entities}
    assert "325-CV/BXD" in values
    assert "Tổ chức" in values
    assert any(entity["entity_type"] == "keyword" for entity in entities)


def test_relation_engine_and_graph(tmp_path: Path) -> None:
    init_database()
    plan_id = _index_library_text(
        tmp_path,
        "12-KH-BXD.txt",
        "Số: 12-KH/BXD\nKẾ HOẠCH\nV/v triển khai công tác tổ chức cán bộ",
    )
    report_id = _index_library_text(
        tmp_path,
        "18-BC-BXD.txt",
        "Số: 18-BC/BXD\nBÁO CÁO\nV/v báo cáo công tác tổ chức cán bộ",
    )
    service = KnowledgeService()
    plan_knowledge = service.ingest_library_document(plan_id)
    report_knowledge = service.ingest_library_document(report_id)
    relation_ids = service.build_relations(report_knowledge)
    graph = service.build_graph()

    assert relation_ids
    assert len(graph["nodes"]) == 2
    assert graph["edges"]


def test_embedding_and_semantic_search_returns_citations(tmp_path: Path) -> None:
    init_database()
    library_id = _index_library_text(
        tmp_path,
        "bien-che.txt",
        "Số: 01-CV/BXD\nCÔNG VĂN\nNội dung về biên chế và tổ chức cán bộ",
    )
    service = KnowledgeService(embedding_backend=LocalHashEmbeddingBackend(dimensions=64))
    knowledge_id = service.ingest_library_document(library_id)
    updated = service.embed_chunks(knowledge_id)
    results = service.semantic_search("biên chế", top_k=3)

    assert updated >= 1
    assert results
    assert results[0]["score"] > 0
    assert "citation" in results[0]
