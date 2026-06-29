"""Embedding Engine service for Build 0.7.3."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import Any, Protocol
import hashlib
import json
import re

from models.embedding_vector import EmbeddingVector
from repositories.chunk_repository import ChunkRepository
from repositories.embedding_repository import EmbeddingRepository


class EmbeddingBackend(Protocol):
    """Embedding backend interface prepared for local and future Ollama providers."""

    name: str
    model: str

    def embed(self, text: str) -> list[float]:
        """Return an embedding vector for text."""


@dataclass(slots=True)
class DeterministicLocalEmbeddingBackend:
    """Deterministic local embedding backend used by tests and offline builds."""

    dimensions: int = 32
    name: str = "local_deterministic"
    model: str = "deterministic-hash-v1"

    def embed(self, text: str) -> list[float]:
        if self.dimensions <= 0:
            raise ValueError("dimensions must be greater than 0")
        vector = [0.0] * self.dimensions
        for token in EmbeddingService.tokenize(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        return EmbeddingService.normalize(vector)


@dataclass(slots=True)
class OllamaEmbeddingBackend:
    """Future Ollama backend placeholder.

    The UI must not call Ollama directly. This class intentionally does not make
    network calls in Build 0.7.3; later builds can implement it behind service
    boundaries without changing callers.
    """

    model: str = "qwen3"
    name: str = "ollama"

    def embed(self, text: str) -> list[float]:
        raise NotImplementedError("Ollama embedding backend is not implemented in Build 0.7.3")


@dataclass(slots=True)
class EmbeddingBatchResult:
    """Batch embedding counters."""

    total: int = 0
    completed: int = 0
    skipped: int = 0
    failed: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "total": self.total,
            "completed": self.completed,
            "skipped": self.skipped,
            "failed": self.failed,
        }


class EmbeddingService:
    """Service layer for generating and storing chunk embeddings."""

    def __init__(
        self,
        repository: EmbeddingRepository | None = None,
        chunk_repository: ChunkRepository | None = None,
        backend: EmbeddingBackend | None = None,
    ) -> None:
        self.repository = repository or EmbeddingRepository()
        self.chunk_repository = chunk_repository or ChunkRepository()
        self.backend = backend or DeterministicLocalEmbeddingBackend()

    def generate_for_chunk(self, chunk_id: int, *, force: bool = False) -> dict[str, Any]:
        """Generate or reuse an embedding for one chunk."""
        chunk = self.chunk_repository.get_chunk(chunk_id)
        if not chunk:
            raise ValueError("chunk not found")
        document_id = int(chunk["document_id"])
        text = str(chunk["text"])
        checksum = self.chunk_checksum(text)
        existing = self.repository.get_by_chunk_id(chunk_id)
        if (
            existing
            and not force
            and existing.get("chunk_checksum") == checksum
            and existing.get("embedding_model") == self.backend.model
            and existing.get("embedding_provider") == self.backend.name
            and existing.get("status") == "completed"
        ):
            row = dict(existing)
            row["skipped"] = True
            return row

        try:
            vector = self.backend.embed(text)
            embedding = EmbeddingVector(
                chunk_id=chunk_id,
                document_id=document_id,
                embedding_model=self.backend.model,
                embedding_provider=self.backend.name,
                vector_json=json.dumps(vector),
                vector_dimension=len(vector),
                chunk_checksum=checksum,
                status="completed",
                error_message=None,
            )
            embedding_id = self.repository.upsert_embedding(embedding)
            row = self.repository.get_by_chunk_id(chunk_id) or {"id": embedding_id}
            row["skipped"] = False
            return row
        except Exception as exc:
            self.repository.mark_failed(
                chunk_id=chunk_id,
                document_id=document_id,
                embedding_model=self.backend.model,
                embedding_provider=self.backend.name,
                chunk_checksum=checksum,
                error_message=str(exc),
            )
            row = self.repository.get_by_chunk_id(chunk_id) or {}
            row["skipped"] = False
            return row

    def generate_all(self, *, document_id: int | None = None, force: bool = False, batch_size: int = 50) -> dict[str, int]:
        """Generate embeddings for all known chunks with safe per-row errors."""
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than 0")
        chunks = self.chunk_repository.list_chunks(document_id)
        result = EmbeddingBatchResult(total=len(chunks))
        for start in range(0, len(chunks), batch_size):
            for chunk in chunks[start : start + batch_size]:
                row = self.generate_for_chunk(int(chunk["id"]), force=force)
                if row.get("status") == "failed":
                    result.failed += 1
                elif row.get("skipped"):
                    result.skipped += 1
                else:
                    result.completed += 1
        return result.to_dict()

    def get_by_chunk_id(self, chunk_id: int) -> dict[str, Any] | None:
        """Retrieve persisted embedding for one chunk."""
        return self.repository.get_by_chunk_id(chunk_id)

    @staticmethod
    def chunk_checksum(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def tokenize(text: str) -> list[str]:
        return re.findall(r"[^\W_]+", text.lower(), flags=re.UNICODE)

    @staticmethod
    def normalize(vector: list[float]) -> list[float]:
        length = sqrt(sum(value * value for value in vector))
        if length == 0:
            return vector
        return [round(value / length, 8) for value in vector]
