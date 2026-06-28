"""Kiểm thử foundation AI Knowledge Engine Sprint 5."""

from database.connection import get_connection
from database.init_db import init_database
from models import KnowledgeChunk, KnowledgeDocument, KnowledgeEntity, KnowledgeRelation
from repositories.knowledge_repository import KnowledgeRepository


def test_knowledge_migration_creates_tables() -> None:
    init_database()
    with get_connection() as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        migrations = {row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}

    assert "knowledge_documents" in tables
    assert "knowledge_chunks" in tables
    assert "knowledge_entities" in tables
    assert "knowledge_relations" in tables
    assert "knowledge_jobs" in tables
    assert "knowledge_logs" in tables
    assert "006_ai_knowledge" in migrations


def test_knowledge_repository_crud() -> None:
    init_database()
    repo = KnowledgeRepository()
    document_id = repo.create_document(KnowledgeDocument(title="Công văn 325", document_type="Công văn"))
    chunk_ids = repo.replace_chunks(
        document_id,
        [KnowledgeChunk(section="Số ký hiệu", text="Số: 325-CV/BXD", token_count=3)],
    )
    entity_ids = repo.replace_entities(
        document_id,
        [KnowledgeEntity(entity_type="document_number", entity_value="325-CV/BXD", weight=10)],
    )
    second_id = repo.create_document(KnowledgeDocument(title="Kế hoạch 12", document_type="Kế hoạch"))
    relation_ids = repo.replace_relations_for_document(
        document_id,
        [KnowledgeRelation(source_document_id=document_id, target_document_id=second_id, relation_type="related")],
    )

    assert document_id > 0
    assert chunk_ids and entity_ids and relation_ids
    assert len(repo.list_chunks(document_id)) == 1
    assert len(repo.list_entities(document_id)) == 1
    assert len(repo.list_relations(document_id)) == 1
