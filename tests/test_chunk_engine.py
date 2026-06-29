"""Tests for Build 0.7.2 Chunk Engine."""

import pytest

from services.chunk_service import ChunkEngine, ChunkService


def test_chunk_engine_counts_tokens_and_applies_overlap() -> None:
    engine = ChunkEngine(max_tokens=5, overlap_tokens=2)
    result = engine.build_chunks(
        "Can cu quy dinh hien hanh ve cong tac to chuc can bo dang vien bao cao tong hop",
        source_checksum="abc123",
    )

    assert len(result.chunks) >= 3
    assert result.chunks[0].token_count == 5
    assert result.chunks[1].token_count == 5
    assert result.metadata[0].overlap_with_previous == 0
    assert result.metadata[1].overlap_with_previous == 1
    assert result.metadata[1].overlap_tokens == 2
    assert result.chunks[0].text.split()[-2:] == result.chunks[1].text.split()[:2]
    assert result.metadata[0].start_token == 0
    assert result.metadata[1].start_token == 3
    assert result.metadata[1].end_token == 8


def test_chunk_engine_detects_sections_and_rejects_invalid_settings() -> None:
    engine = ChunkEngine(max_tokens=20, overlap_tokens=4)
    result = engine.build_chunks(
        """
        So: 12-CV/BXD
        Kinh gui cac don vi
        Noi dung trien khai nhiem vu trong thang
        """,
    )

    sections = {chunk.section for chunk in result.chunks}
    assert "Số ký hiệu" in sections
    assert any(chunk.token_count > 0 for chunk in result.chunks)
    with pytest.raises(ValueError):
        ChunkEngine(max_tokens=10, overlap_tokens=10)


def test_chunk_service_returns_chunks_without_persistence() -> None:
    service = ChunkService(engine=ChunkEngine(max_tokens=4, overlap_tokens=1))

    chunks = service.chunk_text("mot hai ba bon nam sau bay")

    assert [chunk.chunk_order for chunk in chunks] == [1, 2]
    assert [chunk.token_count for chunk in chunks] == [4, 4]
