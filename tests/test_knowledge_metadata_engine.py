from __future__ import annotations

from pathlib import Path

from database.connection import get_connection
from database.init_db import init_database
from models.library_document import LibraryDocument
from repositories.document_library_repository import DocumentLibraryRepository
from services.knowledge_metadata_service import KnowledgeMetadataService
from services.knowledge_service import KnowledgeService, LocalHashEmbeddingBackend


def _library_document(
    *,
    title: str,
    file_name: str,
    document_type: str,
    document_number: str,
    field: str = "Tổ chức",
    issued_date: str = "2026-01-10",
    checksum: str,
) -> int:
    repository = DocumentLibraryRepository()
    return repository.create_document(
        LibraryDocument(
            title=title,
            file_name=file_name,
            file_path=f"workspace/library/{file_name}",
            file_ext=".txt",
            file_size=256,
            checksum=checksum,
            document_type=document_type,
            document_number=document_number,
            issued_date=issued_date,
            issuing_agency="Ban Xây dựng Đảng",
            signer="Nguyễn Trung Hiền",
            summary=f"{title} về công tác tổ chức cán bộ.",
            keywords="tổ chức, cán bộ, biên chế",
            field=field,
            status="indexed",
        )
    )


def _ingest(library_id: int, text: str) -> int:
    service = KnowledgeService(embedding_backend=LocalHashEmbeddingBackend(dimensions=64))
    knowledge_id = service.ingest_library_document(library_id, text=text)
    service.embed_chunks(knowledge_id)
    return knowledge_id


def test_knowledge_metadata_migration_creates_tables() -> None:
    init_database()
    with get_connection() as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        migrations = {row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}

    assert "knowledge_metadata" in tables
    assert "knowledge_relationship_v2" in tables
    assert "knowledge_citation_metadata" in tables
    assert "knowledge_metadata_cache" in tables
    assert "009_knowledge_metadata_engine" in migrations


def test_metadata_authority_validity_and_cache() -> None:
    init_database()
    library_id = _library_document(
        title="Kế hoạch biên chế",
        file_name="ke-hoach-bien-che.txt",
        document_type="Kế hoạch",
        document_number="12-KH/BXD",
        checksum="checksum-kh-12",
    )
    knowledge_id = _ingest(library_id, "Kế hoạch triển khai công tác biên chế và tổ chức cán bộ.")

    service = KnowledgeMetadataService()
    metadata = service.build_metadata(knowledge_id)
    cached = service.build_metadata(knowledge_id)
    cache_rows = service.repository.fetch_all("SELECT * FROM knowledge_metadata_cache")

    assert metadata.normalized_type == "ke_hoach"
    assert metadata.authority_level == "internal"
    assert metadata.authority_score > 0.8
    assert metadata.validity_status == "valid"
    assert cached.metadata_hash == metadata.metadata_hash
    assert len(cache_rows) == 1


def test_relationship_engine_v2_links_related_documents() -> None:
    init_database()
    plan_id = _library_document(
        title="Kế hoạch tổ chức cán bộ",
        file_name="ke-hoach-to-chuc.txt",
        document_type="Kế hoạch",
        document_number="12-KH/BXD",
        checksum="checksum-plan",
    )
    report_id = _library_document(
        title="Báo cáo tổ chức cán bộ",
        file_name="bao-cao-to-chuc.txt",
        document_type="Báo cáo",
        document_number="18-BC/BXD",
        checksum="checksum-report",
    )
    plan_knowledge = _ingest(plan_id, "Kế hoạch công tác tổ chức cán bộ.")
    report_knowledge = _ingest(report_id, "Báo cáo kết quả công tác tổ chức cán bộ.")

    service = KnowledgeMetadataService()
    service.build_metadata(plan_knowledge)
    service.build_metadata(report_knowledge)
    relation_ids = service.build_relationships_v2(report_knowledge)
    relations = service.repository.list_relationships_v2(report_knowledge)

    assert relation_ids
    assert relations[0]["relation_type"] in {"reports", "related"}
    assert float(relations[0]["confidence"]) > 0


def test_citation_metadata_enriches_semantic_search(tmp_path: Path) -> None:
    init_database()
    library_id = _library_document(
        title="Công văn biên chế",
        file_name="cong-van-bien-che.txt",
        document_type="Công văn",
        document_number="325-CV/BXD",
        checksum="checksum-cv-325",
    )
    _ingest(library_id, "Công văn hướng dẫn triển khai biên chế và tổ chức cán bộ.")

    service = KnowledgeMetadataService()
    results = service.enrich_semantic_search("biên chế tổ chức cán bộ", top_k=2)
    stored = service.repository.list_citation_metadata(query_text="biên chế tổ chức cán bộ")

    assert results
    assert results[0]["citation_metadata"]["authority_level"] == "internal"
    assert results[0]["citation_metadata"]["validity_status"] == "valid"
    assert stored
