"""Kiểm thử Build 0.5.1 - AI Knowledge Engine optimization."""

from __future__ import annotations

from pathlib import Path
from time import perf_counter
import tracemalloc

from database.connection import get_connection
from database.init_db import init_database
from services.document_library_service import DocumentLibraryService
from services.knowledge_service import EmbeddingBackend, KnowledgeService, LocalHashEmbeddingBackend


class CountingEmbeddingBackend:
    """Backend thật trong test để đếm số lần embed được gọi."""

    name = "counting"
    model = "counting-v1"

    def __init__(self) -> None:
        self.calls = 0
        self.local = LocalHashEmbeddingBackend(dimensions=32)

    def embed(self, text: str) -> list[float]:
        self.calls += 1
        return self.local.embed(text)


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def _indexed_library_document(tmp_path: Path, text: str, name: str = "doc.txt") -> int:
    root = tmp_path / "library"
    root.mkdir(exist_ok=True)
    _write_text(root / name, text)
    service = DocumentLibraryService()
    result = service.index_folder(root, sync_knowledge=False)
    assert result["indexed_ids"]
    return int(result["indexed_ids"][0])


def test_optimization_migration_creates_cache_and_state_tables() -> None:
    init_database()
    with get_connection() as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        migrations = {row[0] for row in conn.execute("SELECT version FROM schema_migrations")}
        columns = {row[1] for row in conn.execute("PRAGMA table_info(knowledge_chunks)").fetchall()}
    assert "knowledge_embedding_cache" in tables
    assert "knowledge_index_state" in tables
    assert "007_ai_core_optimization" in migrations
    assert "embedding_hash" in columns
    assert "embedding_version" in columns


def test_incremental_ingest_skips_unchanged_document(tmp_path: Path) -> None:
    init_database()
    library_id = _indexed_library_document(
        tmp_path,
        "Số: 01-CV/BXD\nCÔNG VĂN\nNội dung biên chế tổ chức cán bộ",
    )
    service = KnowledgeService()
    first_id = service.ingest_library_document(library_id)
    first_chunks = service.repository.list_chunks(first_id)
    second_id = service.ingest_library_document(library_id)
    second_chunks = service.repository.list_chunks(second_id)

    assert first_id == second_id
    assert [chunk["id"] for chunk in first_chunks] == [chunk["id"] for chunk in second_chunks]


def test_embedding_cache_reuses_existing_embedding(tmp_path: Path) -> None:
    init_database()
    library_id = _indexed_library_document(
        tmp_path,
        "Số: 02-CV/BXD\nCÔNG VĂN\nNội dung biên chế tổ chức cán bộ",
    )
    backend = CountingEmbeddingBackend()
    service = KnowledgeService(embedding_backend=backend)
    knowledge_id = service.ingest_library_document(library_id)

    first_updated = service.embed_chunks(knowledge_id)
    first_calls = backend.calls
    second_updated = service.embed_chunks(knowledge_id)

    assert first_updated >= 1
    assert second_updated == first_updated
    assert backend.calls == first_calls


def test_rich_citation_contains_render_ready_fields(tmp_path: Path) -> None:
    init_database()
    library_id = _indexed_library_document(
        tmp_path,
        "BAN XÂY DỰNG ĐẢNG\nSố: 03-CV/BXD\nVĩnh Hòa, ngày 1 tháng 6 năm 2026\nCÔNG VĂN\nNội dung biên chế",
    )
    service = KnowledgeService(embedding_backend=LocalHashEmbeddingBackend(dimensions=32))
    knowledge_id = service.ingest_library_document(library_id)
    service.embed_chunks(knowledge_id)
    result = service.semantic_search("biên chế", top_k=1)[0]
    citation = result["citation"]

    assert citation["title"]
    assert citation["document_number"] == "03-CV/BXD"
    assert citation["issued_date"] == "2026-06-01"
    assert citation["chunk_id"]
    assert citation["section"]
    assert citation["file_path"]
    assert citation["checksum"]
    assert isinstance(citation["relevance"], float)


def test_relation_optimization_avoids_duplicates_and_sets_confidence(tmp_path: Path) -> None:
    init_database()
    first = _indexed_library_document(tmp_path, "Số: 01-KH/BXD\nKẾ HOẠCH\nTổ chức cán bộ", "plan.txt")
    second = _indexed_library_document(tmp_path, "Số: 02-BC/BXD\nBÁO CÁO\nTổ chức cán bộ", "report.txt")
    service = KnowledgeService()
    first_id = service.ingest_library_document(first)
    second_id = service.ingest_library_document(second)

    service.build_relations(second_id)
    service.build_relations(second_id)
    relations = service.repository.list_relations(second_id)

    keys = {(row["source_document_id"], row["target_document_id"], row["relation_type"]) for row in relations}
    assert len(keys) == len(relations)
    assert all(float(row["confidence"]) > 0 for row in relations)


def test_batch_processing_reports_progress_and_deleted_files(tmp_path: Path) -> None:
    init_database()
    root = tmp_path / "library"
    root.mkdir()
    first = root / "a.txt"
    second = root / "b.txt"
    _write_text(first, "Số: 01-CV/BXD\nCÔNG VĂN\nTổ chức cán bộ")
    _write_text(second, "Số: 02-CV/BXD\nCÔNG VĂN\nTuyên giáo")
    progress: list[dict[str, int]] = []
    service = DocumentLibraryService()

    result = service.index_folder(root, batch_size=1, progress_callback=progress.append)
    first.unlink()
    deleted_result = service.index_folder(root, batch_size=1)

    assert progress
    assert result["counts"]["need_review"] == 2
    assert deleted_result["counts"]["deleted"] == 1


def test_performance_scan_100_1000_5000_files(tmp_path: Path) -> None:
    init_database()
    service = DocumentLibraryService()
    measurements: list[dict[str, float]] = []
    for count in (100, 1000, 5000):
        root = tmp_path / f"library_{count}"
        root.mkdir()
        for index in range(count):
            _write_text(root / f"doc_{index:05d}.txt", f"Số: {index}-CV/BXD\nNội dung biên chế {index}")
        tracemalloc.start()
        started = perf_counter()
        result = service.scan_folder(root)
        elapsed = perf_counter() - started
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        measurements.append({"count": count, "elapsed": elapsed, "peak": float(peak)})
        assert result.accepted_files == count
        assert peak > 0
    assert [item["count"] for item in measurements] == [100, 1000, 5000]


def test_performance_chunk_embedding_search_sqlite(tmp_path: Path) -> None:
    init_database()
    root = tmp_path / "library"
    root.mkdir()
    for index in range(100):
        _write_text(root / f"knowledge_{index:03d}.txt", f"Số: {index}-CV/BXD\nCÔNG VĂN\nNội dung biên chế tổ chức cán bộ {index}")
    library_service = DocumentLibraryService()
    library_result = library_service.index_folder(root, batch_size=20)
    service = KnowledgeService(embedding_backend=LocalHashEmbeddingBackend(dimensions=64))
    sync_result = service.sync_from_library(batch_size=25)
    embedded = service.embed_chunks()
    search_started = perf_counter()
    results = service.semantic_search("biên chế cán bộ", top_k=5)
    search_elapsed = perf_counter() - search_started

    assert library_result["counts"]["need_review"] == 100
    assert sync_result["skipped"] >= 100
    assert embedded >= 100
    assert len(results) == 5
    assert search_elapsed >= 0
