"""Full-text handoff pipeline from Document Library to Knowledge Engine."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
import json
import logging

from models.knowledge_document import KnowledgeDocument
from repositories.embedding_repository import EmbeddingRepository
from repositories.knowledge_repository import KnowledgeRepository
from services.chunk_service import ChunkService
from services.embedding_service import EmbeddingService
from services.knowledge.citation_builder import CitationBuilder
from services.knowledge.document_snapshot import DocumentSnapshot
from services.knowledge.knowledge_validator import KnowledgeValidator
from services.vector_service import VectorService

logger = logging.getLogger(__name__)

READY = "READY"
INVALID = "INVALID"
INDEXING = "INDEXING"


@dataclass(frozen=True, slots=True)
class KnowledgeResult:
    """Result returned by the full-text handoff pipeline."""

    knowledge_document_id: int
    document_id: int
    status: str
    checksum: str
    chunk_count: int
    embedding_count: int
    citation_count: int
    missing: tuple[str, ...] = ()


class KnowledgeHandoffService:
    """Coordinate metadata, full text, chunk, embedding, vector and citation persistence."""

    def __init__(
        self,
        repository: KnowledgeRepository | None = None,
        chunk_service: ChunkService | None = None,
        embedding_service: EmbeddingService | None = None,
        vector_service: VectorService | None = None,
        citation_builder: CitationBuilder | None = None,
        validator: KnowledgeValidator | None = None,
    ) -> None:
        self.repository = repository or KnowledgeRepository()
        self.chunk_service = chunk_service or ChunkService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.vector_service = vector_service or VectorService()
        self.citation_builder = citation_builder or CitationBuilder(self.repository)
        self.validator = validator or KnowledgeValidator(self.repository, EmbeddingRepository())

    def handoff(self, snapshot: DocumentSnapshot) -> KnowledgeResult:
        """Persist and validate one full-text document handoff."""
        checksum = self.generate_checksum(snapshot.full_text)
        document = KnowledgeDocument(
            document_id=snapshot.document_id,
            library_document_id=snapshot.document_id,
            title=snapshot.title,
            full_text=snapshot.full_text,
            checksum=checksum,
            source_checksum=snapshot.checksum,
            indexed_checksum=snapshot.checksum,
            source_path=snapshot.metadata.get("file_path"),
            document_type=snapshot.metadata.get("document_type"),
            document_number=snapshot.metadata.get("document_number"),
            field=snapshot.metadata.get("field"),
            status=INDEXING,
            metadata_json=json.dumps(
                {
                    "summary": snapshot.metadata.get("summary"),
                    "keywords": snapshot.metadata.get("keywords"),
                    "issued_date": snapshot.metadata.get("issued_date"),
                    "issuing_agency": snapshot.metadata.get("issuing_agency"),
                    "signer": snapshot.metadata.get("signer"),
                    "file_ext": snapshot.metadata.get("file_ext"),
                    "checksum": snapshot.checksum,
                },
                ensure_ascii=False,
            ),
        )
        knowledge_document_id = self.repository.save(document)
        chunk_ids = self.chunk_service.replace_document_chunks(
            knowledge_document_id,
            snapshot.full_text,
            source_checksum=checksum,
        )
        embedding_result = self.embedding_service.generate_all(document_id=knowledge_document_id)
        self.vector_service.batch_index(document_id=knowledge_document_id)
        citation_ids = self.citation_builder.build(knowledge_document_id)
        validation = self.validator.validate(knowledge_document_id)
        status = READY if validation.valid else INVALID
        indexed_time = datetime.now().isoformat(timespec="seconds")
        self.repository.update_document(
            knowledge_document_id,
            {
                "full_text": snapshot.full_text,
                "checksum": checksum,
                "chunk_count": len(chunk_ids),
                "embedding_version": "knowledge-embedding-v1",
                "indexed_time": indexed_time,
                "last_indexed_at": indexed_time,
                "status": status,
            },
        )
        logger.info("Knowledge handoff document_id=%s status=%s", snapshot.document_id, status)
        return KnowledgeResult(
            knowledge_document_id=knowledge_document_id,
            document_id=snapshot.document_id,
            status=status,
            checksum=checksum,
            chunk_count=len(chunk_ids),
            embedding_count=int(embedding_result.get("completed", 0)) + int(embedding_result.get("skipped", 0)),
            citation_count=len(citation_ids),
            missing=validation.missing,
        )

    @staticmethod
    def generate_checksum(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
