"""Rule-based Chunk Engine for Build 0.7.2."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import hashlib
import json
import re
import unicodedata

from models.knowledge_chunk import KnowledgeChunk
from models.knowledge_chunk_metadata import KnowledgeChunkMetadata
from repositories.chunk_repository import ChunkRepository


SECTION_PATTERNS = [
    ("Header", r"CONG HOA|DANG UY|BAN XAY DUNG"),
    ("Số ký hiệu", r"^So\s*[:：]"),
    ("Kính gửi", r"Kinh gui"),
    ("Căn cứ", r"Can cu"),
    ("Điều", r"^(Dieu|I\.|II\.|III\.|\d+\.)"),
    ("Nơi nhận", r"Noi nhan"),
]

DEFAULT_MAX_TOKENS = 180
DEFAULT_OVERLAP_TOKENS = 24
ENGINE_VERSION = "rule_chunk_v1"


@dataclass(slots=True)
class ChunkBuildResult:
    """Chunks and metadata generated from one source text."""

    chunks: list[KnowledgeChunk]
    metadata: list[KnowledgeChunkMetadata]


class ChunkEngine:
    """Split text into token-counted chunks with controlled overlap."""

    def __init__(self, *, max_tokens: int = DEFAULT_MAX_TOKENS, overlap_tokens: int = DEFAULT_OVERLAP_TOKENS) -> None:
        if max_tokens <= 0:
            raise ValueError("max_tokens must be greater than 0")
        if overlap_tokens < 0:
            raise ValueError("overlap_tokens cannot be negative")
        if overlap_tokens >= max_tokens:
            raise ValueError("overlap_tokens must be smaller than max_tokens")
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def build_chunks(
        self,
        text: str,
        *,
        document_id: int | None = None,
        source_checksum: str | None = None,
        max_tokens: int | None = None,
        overlap_tokens: int | None = None,
    ) -> ChunkBuildResult:
        """Create chunks and metadata without using embeddings or semantic search."""
        clean_text = text.strip()
        if not clean_text:
            raise ValueError("text is required")
        active_max = max_tokens or self.max_tokens
        active_overlap = self.overlap_tokens if overlap_tokens is None else overlap_tokens
        if active_max <= 0 or active_overlap < 0 or active_overlap >= active_max:
            raise ValueError("invalid chunk token settings")

        units = self._section_units(clean_text)
        chunks: list[KnowledgeChunk] = []
        metadata: list[KnowledgeChunkMetadata] = []
        order = 1
        for section, tokens, start_offset in units:
            window_start = 0
            while window_start < len(tokens):
                window_end = min(window_start + active_max, len(tokens))
                window_tokens = tokens[window_start:window_end]
                token_count = len(window_tokens)
                absolute_start = start_offset + window_start
                absolute_end = start_offset + window_end
                chunk_text = " ".join(window_tokens)
                text_hash = self.hash_text(chunk_text)
                has_overlap = 1 if window_start > 0 else 0
                overlap_count = min(active_overlap, token_count) if has_overlap else 0
                chunk = KnowledgeChunk(
                    document_id=document_id,
                    section=section,
                    chunk_order=order,
                    text=chunk_text,
                    token_count=token_count,
                    source_checksum=source_checksum,
                )
                chunks.append(chunk)
                metadata.append(
                    KnowledgeChunkMetadata(
                        document_id=document_id,
                        chunk_uid=self.chunk_uid(source_checksum or "", order, text_hash),
                        text_hash=text_hash,
                        start_token=absolute_start,
                        end_token=absolute_end,
                        overlap_tokens=overlap_count,
                        overlap_with_previous=has_overlap,
                        source_engine=ENGINE_VERSION,
                        metadata_json=json.dumps(
                            {
                                "section": section,
                                "chunk_order": order,
                                "max_tokens": active_max,
                                "configured_overlap_tokens": active_overlap,
                                "token_count": token_count,
                            },
                            ensure_ascii=True,
                        ),
                    )
                )
                order += 1
                if window_end >= len(tokens):
                    break
                window_start = max(window_end - active_overlap, window_start + 1)
        return ChunkBuildResult(chunks=chunks, metadata=metadata)

    def _section_units(self, text: str) -> list[tuple[str, list[str], int]]:
        units: list[tuple[str, list[str], int]] = []
        current_section = "Nội dung"
        current_tokens: list[str] = []
        token_offset = 0
        section_start = 0
        for line in [line.strip() for line in text.splitlines() if line.strip()]:
            detected = self.detect_section(line)
            line_tokens = self.tokenize(line)
            if detected and current_tokens:
                units.append((current_section, current_tokens, section_start))
                token_offset += len(current_tokens)
                current_tokens = []
                section_start = token_offset
            if detected:
                current_section = detected
            current_tokens.extend(line_tokens)
        if current_tokens:
            units.append((current_section, current_tokens, section_start))
        if not units:
            tokens = self.tokenize(text)
            units.append(("Nội dung", tokens, 0))
        return units

    @staticmethod
    def detect_section(line: str) -> str | None:
        normalized = ChunkEngine.normalize_text(line)
        for section, pattern in SECTION_PATTERNS:
            if re.search(pattern, normalized, flags=re.IGNORECASE):
                return section
        return None

    @staticmethod
    def tokenize(text: str) -> list[str]:
        return re.findall(r"[^\W_]+", text, flags=re.UNICODE)

    @staticmethod
    def normalize_text(text: str) -> str:
        decomposed = unicodedata.normalize("NFD", text)
        without_marks = "".join(char for char in decomposed if unicodedata.category(char) != "Mn")
        return without_marks.replace("Đ", "D").replace("đ", "d")

    @staticmethod
    def hash_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def chunk_uid(source_checksum: str, order: int, text_hash: str) -> str:
        payload = f"{ENGINE_VERSION}:{source_checksum}:{order}:{text_hash}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ChunkService:
    """Service layer for chunk creation and persistence."""

    def __init__(self, repository: ChunkRepository | None = None, engine: ChunkEngine | None = None) -> None:
        self.repository = repository or ChunkRepository()
        self.engine = engine or ChunkEngine()

    def chunk_text(
        self,
        text: str,
        *,
        document_id: int | None = None,
        source_checksum: str | None = None,
        max_tokens: int | None = None,
        overlap_tokens: int | None = None,
    ) -> list[KnowledgeChunk]:
        """Return chunk models for callers that do not need metadata."""
        return self.build(text, document_id=document_id, source_checksum=source_checksum, max_tokens=max_tokens, overlap_tokens=overlap_tokens).chunks

    def build(
        self,
        text: str,
        *,
        document_id: int | None = None,
        source_checksum: str | None = None,
        max_tokens: int | None = None,
        overlap_tokens: int | None = None,
    ) -> ChunkBuildResult:
        """Build chunks plus metadata."""
        return self.engine.build_chunks(
            text,
            document_id=document_id,
            source_checksum=source_checksum,
            max_tokens=max_tokens,
            overlap_tokens=overlap_tokens,
        )

    def replace_document_chunks(
        self,
        document_id: int,
        text: str,
        *,
        source_checksum: str | None = None,
        max_tokens: int | None = None,
        overlap_tokens: int | None = None,
    ) -> list[int]:
        """Chunk a document and replace persisted chunks atomically at repository level."""
        result = self.build(
            text,
            document_id=document_id,
            source_checksum=source_checksum,
            max_tokens=max_tokens,
            overlap_tokens=overlap_tokens,
        )
        return self.repository.replace_chunks(document_id, result.chunks, result.metadata)

    def list_chunks_with_metadata(self, document_id: int) -> list[dict[str, Any]]:
        """Return persisted chunks enriched with metadata."""
        metadata_by_chunk = {int(item["chunk_id"]): item for item in self.repository.list_metadata(document_id)}
        rows: list[dict[str, Any]] = []
        for chunk in self.repository.list_chunks(document_id):
            enriched = dict(chunk)
            enriched["metadata"] = metadata_by_chunk.get(int(chunk["id"]))
            rows.append(enriched)
        return rows
