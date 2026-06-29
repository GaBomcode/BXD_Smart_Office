"""AI Knowledge Engine service.

Sprint 5 không tạo chatbot. Service này chỉ lập chỉ mục tri thức, quan hệ,
embedding và semantic search có citation để Sprint sau sử dụng.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from math import sqrt
from pathlib import Path
from typing import Any, Callable, Iterable, Protocol
import hashlib
import json
import logging
import re

import requests

from models.knowledge_chunk import KnowledgeChunk
from models.knowledge_document import KnowledgeDocument
from models.knowledge_entity import KnowledgeEntity
from models.knowledge_relation import KnowledgeRelation
from repositories.document_library_repository import DocumentLibraryRepository
from repositories.knowledge_repository import KnowledgeRepository
from services.chunk_service import ChunkEngine, ChunkService
from services.knowledge.document_snapshot import DocumentSnapshot
from services.knowledge.handoff_service import KnowledgeHandoffService, READY

logger = logging.getLogger(__name__)

SECTION_PATTERNS = [
    ("Header", r"CỘNG HÒA|ĐẢNG ỦY|BAN XÂY DỰNG"),
    ("Số ký hiệu", r"^Số\s*[:：]"),
    ("Kính gửi", r"Kính gửi"),
    ("Căn cứ", r"Căn cứ"),
    ("Điều", r"^(Điều|I\.|II\.|III\.|\d+\.)"),
    ("Nơi nhận", r"Nơi nhận"),
]

RELATION_ORDER = {
    "Quy định": 1,
    "Quyết định": 2,
    "Kế hoạch": 3,
    "Công văn": 4,
    "Báo cáo": 5,
}

FIELD_KEYWORDS = {
    "Tổ chức": ["tổ chức", "cán bộ", "đảng viên", "chi bộ", "biên chế"],
    "Tuyên giáo": ["tuyên giáo", "nghị quyết", "tuyên truyền", "học tập"],
    "Dân vận": ["dân vận", "mặt trận", "dân tộc", "tôn giáo"],
    "Tổng hợp": ["báo cáo", "tổng hợp", "chuyển đổi số", "phối hợp"],
    "Lãnh đạo điều hành": ["chỉ đạo", "lãnh đạo", "điều hành"],
}

EMBEDDING_VERSION = "knowledge-embedding-v1"


@dataclass(slots=True)
class BatchProgress:
    """Tiến độ batch index Knowledge Engine."""

    total: int
    processed: int = 0
    skipped: int = 0
    indexed: int = 0
    failed: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "total": self.total,
            "processed": self.processed,
            "skipped": self.skipped,
            "indexed": self.indexed,
            "failed": self.failed,
        }


class EmbeddingBackend(Protocol):
    """Backend embedding có thể thay thế mà không đổi nghiệp vụ."""

    name: str
    model: str

    def embed(self, text: str) -> list[float]:
        """Sinh vector embedding cho text."""


@dataclass(slots=True)
class LocalHashEmbeddingBackend:
    """Embedding offline deterministic dùng khi Ollama chưa sẵn sàng."""

    dimensions: int = 128
    name: str = "local_hash"
    model: str = "rule-hash-v1"

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = KnowledgeService.tokenize(text)
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1 if digest[4] % 2 == 0 else -1
            vector[index] += sign
        return KnowledgeService.normalize_vector(vector)


@dataclass(slots=True)
class OllamaEmbeddingBackend:
    """Embedding backend Ollama local, mặc định model Qwen3."""

    model: str = "qwen3"
    base_url: str = "http://localhost:11434"
    name: str = "ollama"
    timeout: int = 30

    def embed(self, text: str) -> list[float]:
        response = requests.post(
            f"{self.base_url.rstrip('/')}/api/embeddings",
            json={"model": self.model, "prompt": text},
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()
        embedding = data.get("embedding")
        if not isinstance(embedding, list) or not embedding:
            raise RuntimeError("Ollama không trả về embedding hợp lệ")
        return KnowledgeService.normalize_vector([float(value) for value in embedding])


class KnowledgeService:
    """Service chính của AI Knowledge Engine."""

    def __init__(
        self,
        repository: KnowledgeRepository | None = None,
        library_repository: DocumentLibraryRepository | None = None,
        embedding_backend: EmbeddingBackend | None = None,
        chunk_service: ChunkService | None = None,
    ) -> None:
        self.repository = repository or KnowledgeRepository()
        self.library_repository = library_repository or DocumentLibraryRepository()
        self.embedding_backend = embedding_backend or LocalHashEmbeddingBackend()
        self.chunk_service = chunk_service or ChunkService()
        self.handoff_service = KnowledgeHandoffService(repository=self.repository, chunk_service=self.chunk_service)

    def ingest_library_document(self, library_document_id: int, *, text: str | None = None) -> int:
        """Đưa một văn bản kho vào Knowledge Engine, chưa tự tạo nghiệp vụ mới."""
        source = self.library_repository.get_document(library_document_id)
        if not source:
            raise ValueError("Không tìm thấy văn bản kho")
        checksum = str(source.get("checksum") or "")
        existing_state = self.repository.get_index_state(library_document_id)
        existing_knowledge = self.repository.get_by_library_document(library_document_id)
        if (
            existing_state
            and existing_knowledge
            and str(existing_state.get("checksum") or "") == checksum
            and str(existing_state.get("status") or "") == "indexed"
            and str(existing_knowledge.get("full_text") or "").strip()
            and str(existing_knowledge.get("status") or "") == READY
        ):
            logger.info("Skip unchanged knowledge document library_id=%s checksum=%s", library_document_id, checksum)
            return int(existing_knowledge["id"])
        content = text or self._read_source_text(source) or "\n".join(
            value
            for value in [
                str(source.get("title") or ""),
                str(source.get("document_number") or ""),
                str(source.get("summary") or ""),
                str(source.get("keywords") or ""),
            ]
            if value
        )
        snapshot = DocumentSnapshot.from_library_document(source, full_text=content)
        result = self.handoff_service.handoff(snapshot)
        document_id = result.knowledge_document_id
        chunks = [
            KnowledgeChunk(section=str(chunk.get("section") or "Nội dung"), text=str(chunk["text"]), token_count=int(chunk.get("token_count") or 0))
            for chunk in self.repository.list_chunks(document_id)
        ]
        entities = self.extract_entities(document_id, chunks, source)
        self.repository.replace_entities(document_id, entities)
        self.build_relations(document_id)
        self.repository.update_document(
            document_id,
            {
                "source_checksum": checksum,
                "indexed_checksum": checksum,
                "last_indexed_at": datetime.now().isoformat(timespec="seconds"),
            },
        )
        self.repository.upsert_index_state(
            library_document_id=library_document_id,
            knowledge_document_id=document_id,
            file_path=str(source.get("file_path") or ""),
            checksum=checksum,
            status="indexed",
            detail="indexed",
        )
        logger.info("Ingested library document id=%s as knowledge id=%s", library_document_id, document_id)
        return document_id

    @staticmethod
    def _read_source_text(source: dict[str, Any]) -> str:
        path = Path(str(source.get("file_path") or ""))
        if not path.exists() or not path.is_file():
            return ""
        try:
            from services.readers import DocxReader, PdfReader, TxtReader, XlsxReader

            ext = path.suffix.lower()
            if ext in {".doc", ".docx"}:
                return DocxReader().read(path).text
            if ext == ".pdf":
                return PdfReader().read(path).text
            if ext in {".xls", ".xlsx"}:
                return XlsxReader().read(path).text
            if ext == ".txt":
                return TxtReader().read(path).text
        except Exception as exc:
            logger.warning("Cannot read source text for knowledge handoff: %s", exc)
        return ""

    def sync_from_library(
        self,
        *,
        status: str | None = None,
        batch_size: int = 50,
        progress_callback: Callable[[dict[str, int]], None] | None = None,
    ) -> dict[str, int]:
        """Đồng bộ Document Library sang Knowledge Engine theo incremental checksum."""
        if batch_size <= 0:
            raise ValueError("batch_size phải lớn hơn 0")
        documents = self.library_repository.list_documents(status=status, limit=None)
        progress = BatchProgress(total=len(documents))
        for batch in self._batched(documents, batch_size):
            for document in batch:
                progress.processed += 1
                try:
                    checksum = str(document.get("checksum") or "")
                    state = self.repository.get_index_state(int(document["id"]))
                    if state and str(state.get("checksum") or "") == checksum and str(state.get("status")) == "indexed":
                        progress.skipped += 1
                    else:
                        self.ingest_library_document(int(document["id"]))
                        progress.indexed += 1
                except Exception as exc:
                    progress.failed += 1
                    self.repository.log("ERROR", "Knowledge sync failed", detail=str(exc))
                if progress_callback:
                    progress_callback(progress.to_dict())
        return progress.to_dict()

    def sync_deleted_library_documents(self) -> int:
        """Đánh dấu index state stale khi văn bản nguồn đã bị xóa khỏi Document Library."""
        states = self.repository.fetch_all("SELECT * FROM knowledge_index_state")
        updated = 0
        for state in states:
            source = self.library_repository.get_document(int(state["library_document_id"]))
            if source is None or str(source.get("status") or "") == "deleted":
                self.repository.upsert_index_state(
                    library_document_id=int(state["library_document_id"]),
                    knowledge_document_id=state.get("knowledge_document_id"),
                    file_path=str(state.get("file_path") or ""),
                    checksum=str(state.get("checksum") or ""),
                    status="deleted",
                    detail="source document removed from library",
                )
                updated += 1
        return updated

    def chunk_text(self, text: str, *, max_tokens: int = 180) -> list[KnowledgeChunk]:
        """Tách văn bản thành chunk rule-based, không dùng AI."""
        return self.chunk_service.chunk_text(text, max_tokens=max_tokens)

    def extract_entities(
        self,
        document_id: int,
        chunks: list[KnowledgeChunk],
        source_document: dict[str, Any] | None = None,
    ) -> list[KnowledgeEntity]:
        """Sinh keyword/entity rule-based có trọng số."""
        source_document = source_document or {}
        text = "\n".join(chunk.text for chunk in chunks)
        entities: list[KnowledgeEntity] = []
        for key, entity_type, weight in [
            ("document_type", "document_type", 8),
            ("document_number", "document_number", 10),
            ("issuing_agency", "agency", 8),
            ("signer", "person", 6),
            ("field", "field", 7),
        ]:
            value = source_document.get(key)
            if value:
                entities.append(KnowledgeEntity(document_id=document_id, entity_type=entity_type, entity_value=str(value), weight=weight))
        field = source_document.get("field") or self.detect_field(text)
        if field and not any(entity.entity_type == "field" for entity in entities):
            entities.append(KnowledgeEntity(document_id=document_id, entity_type="field", entity_value=str(field), weight=7))
        keyword_weights = self.extract_keywords(text)
        for keyword, weight in keyword_weights.items():
            entities.append(KnowledgeEntity(document_id=document_id, entity_type="keyword", entity_value=keyword, weight=weight))
        for chunk in chunks:
            for number in re.findall(r"\b\d{1,4}[-/][A-Za-zÀ-ỹ0-9./-]+", chunk.text):
                entities.append(KnowledgeEntity(document_id=document_id, entity_type="reference_number", entity_value=number, weight=5))
        return self._dedupe_entities(entities)

    def build_relations(self, document_id: int) -> list[int]:
        """Sinh quan hệ giữa văn bản theo rule-based và lưu SQLite."""
        document = self.repository.get_document(document_id)
        if not document:
            raise ValueError("Không tìm thấy knowledge document")
        documents = self.repository.list_documents()
        entities = self.repository.list_entities(document_id)
        entity_values = {str(entity["entity_value"]).lower() for entity in entities}
        relations: list[KnowledgeRelation] = []
        for other in documents:
            other_id = int(other["id"])
            if other_id == document_id:
                continue
            other_entities = self.repository.list_entities(other_id)
            other_values = {str(entity["entity_value"]).lower() for entity in other_entities}
            shared = entity_values.intersection(other_values)
            relation_type = self.infer_relation_type(document, other, shared)
            if relation_type:
                relations.append(
                    KnowledgeRelation(
                        source_document_id=document_id,
                        target_document_id=other_id,
                        relation_type=relation_type,
                        weight=max(1, len(shared)),
                        evidence=", ".join(sorted(shared)[:8]),
                    )
                )
                if relation_type in {"related", "references"}:
                    relations.append(
                        KnowledgeRelation(
                            source_document_id=other_id,
                            target_document_id=document_id,
                            relation_type=relation_type,
                            weight=max(1, len(shared)),
                            confidence=min(1.0, 0.5 + len(shared) * 0.1),
                            is_bidirectional=1,
                            evidence=", ".join(sorted(shared)[:8]),
                        )
                    )
        for relation in relations:
            relation.confidence = min(1.0, max(0.1, relation.confidence or min(1.0, relation.weight / 10)))
        return self.repository.upsert_relations_for_document(document_id, relations)

    def build_graph(self) -> dict[str, Any]:
        """Sinh graph tri thức SQLite-friendly từ documents/relations."""
        documents = self.repository.list_documents()
        relations = self.repository.list_relations()
        nodes = [
            {
                "id": int(document["id"]),
                "label": document["title"],
                "type": document.get("document_type"),
                "field": document.get("field"),
            }
            for document in documents
        ]
        edges = [
            {
                "source": relation.get("source_document_id"),
                "target": relation.get("target_document_id"),
                "type": relation.get("relation_type"),
                "weight": relation.get("weight"),
                "evidence": relation.get("evidence"),
            }
            for relation in relations
        ]
        return {"nodes": nodes, "edges": edges}

    def embed_chunks(self, document_id: int | None = None) -> int:
        """Sinh embedding cho chunks bằng backend cấu hình."""
        chunks = self.repository.list_chunks(document_id)
        updated = 0
        for chunk in chunks:
            text = str(chunk["text"])
            source_checksum = str(chunk.get("source_checksum") or "")
            text_hash = self.hash_text(text)
            embedding_hash = self.embedding_hash(source_checksum=source_checksum, text_hash=text_hash)
            cached = self.repository.get_embedding_cache(embedding_hash)
            if cached:
                embedding_json = str(cached["embedding_json"])
                embedding_model = str(cached["embedding_model"])
                embedding_backend = str(cached["embedding_backend"])
            else:
                vector = self.embedding_backend.embed(text)
                embedding_json = json.dumps(vector)
                embedding_model = self.embedding_backend.model
                embedding_backend = self.embedding_backend.name
                self.repository.upsert_embedding_cache(
                    embedding_hash=embedding_hash,
                    source_checksum=source_checksum,
                    text_hash=text_hash,
                    embedding_version=EMBEDDING_VERSION,
                    embedding_model=embedding_model,
                    embedding_backend=embedding_backend,
                    embedding_json=embedding_json,
                )
            self.repository.update_chunk(
                int(chunk["id"]),
                {
                    "embedding_json": embedding_json,
                    "embedding_model": embedding_model,
                    "embedding_backend": embedding_backend,
                    "embedding_version": EMBEDDING_VERSION,
                    "embedding_hash": embedding_hash,
                    "embedding_updated_at": datetime.now().isoformat(timespec="seconds"),
                },
            )
            updated += 1
        return updated

    def semantic_search(self, query: str, *, top_k: int = 5) -> list[dict[str, Any]]:
        """Semantic search trên chunk embedding, trả citation."""
        if not query.strip():
            raise ValueError("query không được rỗng")
        query_vector = self.embedding_backend.embed(query)
        results: list[dict[str, Any]] = []
        for chunk in self.repository.list_chunks():
            embedding_json = chunk.get("embedding_json")
            if not embedding_json:
                continue
            vector = [float(value) for value in json.loads(str(embedding_json))]
            score = self.cosine_similarity(query_vector, vector)
            document = self.repository.get_document(int(chunk["document_id"])) or {}
            if str(document.get("status") or "").upper() != READY:
                continue
            metadata = self._metadata(document)
            results.append(
                {
                    "document": {
                        "id": document.get("id"),
                        "title": document.get("title"),
                        "document_number": document.get("document_number"),
                        "issued_date": metadata.get("issued_date"),
                        "source_path": document.get("source_path"),
                        "checksum": document.get("source_checksum") or metadata.get("checksum"),
                    },
                    "chunk": {
                        "id": chunk.get("id"),
                        "page": chunk.get("page"),
                        "section": chunk.get("section"),
                        "chunk_order": chunk.get("chunk_order"),
                        "text": chunk.get("text"),
                    },
                    "score": round(score, 6),
                    "citation": {
                        "title": document.get("title"),
                        "document_number": document.get("document_number"),
                        "issued_date": metadata.get("issued_date"),
                        "page": chunk.get("page"),
                        "chunk_id": chunk.get("id"),
                        "chunk_order": chunk.get("chunk_order"),
                        "section": chunk.get("section"),
                        "file_path": document.get("source_path"),
                        "checksum": document.get("source_checksum") or metadata.get("checksum"),
                        "relevance": round(score, 6),
                    },
                }
            )
        return sorted(results, key=lambda item: item["score"], reverse=True)[:top_k]

    @staticmethod
    def detect_section(line: str) -> str | None:
        for section, pattern in SECTION_PATTERNS:
            if re.search(pattern, line, flags=re.IGNORECASE):
                return section
        return None

    @classmethod
    def detect_field(cls, text: str) -> str | None:
        lower = text.lower()
        scores = {field: sum(1 for keyword in keywords if keyword in lower) for field, keywords in FIELD_KEYWORDS.items()}
        best = max(scores.items(), key=lambda item: item[1])
        return best[0] if best[1] > 0 else None

    @classmethod
    def extract_keywords(cls, text: str) -> dict[str, float]:
        tokens = [token for token in cls.tokenize(text) if len(token) >= 3 and token not in cls.stopwords()]
        counter = Counter(tokens)
        return {word: float(min(count + 1, 10)) for word, count in counter.most_common(20)}

    @staticmethod
    def infer_relation_type(source: dict[str, Any], target: dict[str, Any], shared_entities: set[str]) -> str | None:
        source_type = str(source.get("document_type") or "")
        target_type = str(target.get("document_type") or "")
        source_order = RELATION_ORDER.get(source_type, 99)
        target_order = RELATION_ORDER.get(target_type, 99)
        if not shared_entities and source.get("field") != target.get("field"):
            return None
        if source_type == "Báo cáo" and target_type in {"Kế hoạch", "Công văn"}:
            return "reports"
        if source_type in {"Công văn", "Kế hoạch"} and target_type in {"Quy định", "Quyết định"}:
            return "implements"
        if source_order > target_order:
            return "follows"
        if shared_entities:
            return "related"
        return None

    @staticmethod
    def hash_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @staticmethod
    def embedding_hash(*, source_checksum: str, text_hash: str) -> str:
        return hashlib.sha256(f"{EMBEDDING_VERSION}:{source_checksum}:{text_hash}".encode("utf-8")).hexdigest()

    @staticmethod
    def _metadata(document: dict[str, Any]) -> dict[str, Any]:
        raw = document.get("metadata_json")
        if not raw:
            return {}
        try:
            value = json.loads(str(raw))
            return value if isinstance(value, dict) else {}
        except json.JSONDecodeError:
            return {}

    @staticmethod
    def _batched(items: list[dict[str, Any]], batch_size: int) -> Iterable[list[dict[str, Any]]]:
        for index in range(0, len(items), batch_size):
            yield items[index : index + batch_size]

    def _flush_chunks(self, section: str, lines: list[str], *, max_tokens: int) -> list[KnowledgeChunk]:
        chunks: list[KnowledgeChunk] = []
        buffer: list[str] = []
        token_count = 0
        for line in lines:
            line_tokens = len(self.tokenize(line))
            if buffer and token_count + line_tokens > max_tokens:
                text = "\n".join(buffer)
                chunks.append(KnowledgeChunk(section=section, text=text, token_count=token_count))
                buffer = []
                token_count = 0
            buffer.append(line)
            token_count += line_tokens
        if buffer:
            text = "\n".join(buffer)
            chunks.append(KnowledgeChunk(section=section, text=text, token_count=token_count))
        return chunks

    @staticmethod
    def _dedupe_entities(entities: list[KnowledgeEntity]) -> list[KnowledgeEntity]:
        merged: dict[tuple[str, str], KnowledgeEntity] = {}
        for entity in entities:
            key = (entity.entity_type, entity.entity_value.lower())
            if key in merged:
                merged[key].weight = max(merged[key].weight, entity.weight)
            else:
                merged[key] = entity
        return list(merged.values())

    @staticmethod
    def tokenize(text: str) -> list[str]:
        return [token.lower() for token in ChunkEngine.tokenize(text)]

    @staticmethod
    def stopwords() -> set[str]:
        return {"của", "cho", "các", "văn", "bản", "ngày", "tháng", "năm", "theo", "trong", "với", "nơi", "nhận"}

    @staticmethod
    def normalize_vector(vector: list[float]) -> list[float]:
        length = sqrt(sum(value * value for value in vector))
        if length == 0:
            return vector
        return [round(value / length, 8) for value in vector]

    @staticmethod
    def cosine_similarity(a: list[float], b: list[float]) -> float:
        if len(a) != len(b):
            return 0.0
        return sum(x * y for x, y in zip(a, b))
