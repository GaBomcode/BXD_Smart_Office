"""Knowledge Metadata Engine.

Build 0.7.1 adds metadata analysis around the existing Knowledge Engine.
It does not change document business workflow and does not assert facts without
stored source metadata.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import hashlib
import json
import logging
import re
import unicodedata
from typing import Any

from models.knowledge_citation_metadata import KnowledgeCitationMetadata
from models.knowledge_metadata import KnowledgeMetadata
from repositories.document_library_repository import DocumentLibraryRepository
from repositories.knowledge_repository import KnowledgeRepository
from services.knowledge_service import KnowledgeService

logger = logging.getLogger(__name__)

METADATA_ENGINE_VERSION = "knowledge-metadata-v1"


@dataclass(slots=True)
class AuthorityResult:
    authority_level: str
    authority_score: float
    reason: str


@dataclass(slots=True)
class ValidityResult:
    validity_status: str
    reason: str
    effective_date: str | None = None
    expiry_date: str | None = None


class KnowledgeMetadataService:
    """Builds normalized knowledge metadata without changing source documents."""

    def __init__(
        self,
        *,
        repository: KnowledgeRepository | None = None,
        library_repository: DocumentLibraryRepository | None = None,
        knowledge_service: KnowledgeService | None = None,
    ) -> None:
        self.repository = repository or KnowledgeRepository()
        self.library_repository = library_repository or DocumentLibraryRepository()
        self.knowledge_service = knowledge_service or KnowledgeService(
            repository=self.repository,
            library_repository=self.library_repository,
        )

    def build_metadata(self, knowledge_document_id: int) -> KnowledgeMetadata:
        """Create or update normalized metadata for one knowledge document."""
        document = self._require_document(knowledge_document_id)
        library_document = self._library_document(document)
        payload = self._metadata_payload(document, library_document)
        metadata_hash = self._hash_json(payload)
        cache_key = self._cache_key(document, metadata_hash)
        cached = self.repository.get_metadata_cache(cache_key)
        if cached:
            existing = self.repository.get_metadata(knowledge_document_id)
            if existing:
                logger.info("Reuse knowledge metadata cache for document_id=%s", knowledge_document_id)
                return self._metadata_from_row(existing)

        authority = self.evaluate_authority(
            issuing_agency=str(payload.get("issuing_agency") or ""),
            document_type=str(payload.get("document_type") or ""),
        )
        validity = self.evaluate_validity(
            issued_date=payload.get("issued_date"),
            effective_date=payload.get("effective_date"),
            expiry_date=payload.get("expiry_date"),
        )
        metadata = KnowledgeMetadata(
            knowledge_document_id=knowledge_document_id,
            library_document_id=int(document["library_document_id"]) if document.get("library_document_id") else None,
            title=str(document.get("title") or payload.get("title") or "Văn bản"),
            document_number=payload.get("document_number"),
            document_type=payload.get("document_type"),
            normalized_type=self.normalize_document_type(str(payload.get("document_type") or document.get("document_type") or "")),
            field=payload.get("field") or document.get("field"),
            issuing_agency=payload.get("issuing_agency"),
            signer=payload.get("signer"),
            issued_date=payload.get("issued_date"),
            effective_date=validity.effective_date,
            expiry_date=validity.expiry_date,
            authority_level=authority.authority_level,
            authority_score=authority.authority_score,
            validity_status=validity.validity_status,
            validity_reason=validity.reason,
            source_checksum=str(document.get("source_checksum") or payload.get("checksum") or ""),
            metadata_hash=metadata_hash,
            metadata_json=json.dumps({**payload, "authority_reason": authority.reason}, ensure_ascii=False),
        )
        self.repository.upsert_metadata(metadata)
        self.repository.upsert_metadata_cache(
            cache_key=cache_key,
            knowledge_document_id=knowledge_document_id,
            source_checksum=metadata.source_checksum,
            metadata_hash=metadata_hash,
            payload_json=json.dumps(metadata.to_dict(), ensure_ascii=False),
        )
        logger.info("Built knowledge metadata document_id=%s hash=%s", knowledge_document_id, metadata_hash)
        return metadata

    def build_all_metadata(self) -> list[KnowledgeMetadata]:
        return [self.build_metadata(int(document["id"])) for document in self.repository.list_documents()]

    def evaluate_authority(self, *, issuing_agency: str, document_type: str) -> AuthorityResult:
        """Rule-based authority engine."""
        agency = self._normalize(issuing_agency)
        doc_type = self._normalize(document_type)
        if any(signal in agency for signal in ("trung uong", "bo chinh tri", "ban bi thu")):
            return AuthorityResult("central", 0.95, "Cơ quan cấp trung ương")
        if "ban xay dung dang" in agency or ("ban" in agency and "dang" in agency):
            return AuthorityResult("internal", 0.88, "Văn bản nội bộ Ban Xây dựng Đảng")
        if any(signal in agency for signal in ("dang uy", "huyen uy", "tinh uy")):
            return AuthorityResult("party_committee", 0.84, "Cơ quan Đảng cấp ủy")
        if any(signal in doc_type for signal in ("quyet dinh", "quy dinh")):
            return AuthorityResult("normative", 0.78, "Loại văn bản có tính quy định")
        if issuing_agency.strip():
            return AuthorityResult("known_agency", 0.62, "Có cơ quan ban hành")
        return AuthorityResult("unknown", 0.2, "Thiếu cơ quan ban hành")

    def evaluate_validity(
        self,
        *,
        issued_date: Any,
        effective_date: Any = None,
        expiry_date: Any = None,
    ) -> ValidityResult:
        """Rule-based validity engine; never asserts validity without metadata."""
        issued = self._date_text(issued_date)
        effective = self._date_text(effective_date) or issued
        expiry = self._date_text(expiry_date)
        today = date.today().isoformat()
        if expiry and expiry < today:
            return ValidityResult("expired", "Đã quá ngày hết hiệu lực", effective, expiry)
        if effective and effective > today:
            return ValidityResult("pending", "Chưa đến ngày hiệu lực", effective, expiry)
        if issued:
            return ValidityResult("valid", "Có ngày văn bản; chưa phát hiện hết hiệu lực", effective, expiry)
        return ValidityResult("unknown", "Thiếu ngày văn bản nên cần người dùng kiểm chứng", effective, expiry)

    def build_relationships_v2(self, knowledge_document_id: int) -> list[int]:
        """Relationship Engine V2 using normalized metadata."""
        source = self.build_metadata(knowledge_document_id)
        relationships: list[dict[str, Any]] = []
        for target_row in self.repository.list_metadata():
            target_id = int(target_row["knowledge_document_id"])
            if target_id == knowledge_document_id:
                continue
            relation = self._relationship_from_metadata(source, target_row)
            if relation:
                relationships.append(relation)
        ids = self.repository.replace_relationships_v2_for_document(knowledge_document_id, relationships)
        logger.info("Built relationship V2 document_id=%s count=%s", knowledge_document_id, len(ids))
        return ids

    def enrich_semantic_search(self, query: str, *, top_k: int = 5) -> list[dict[str, Any]]:
        """Semantic search with citation metadata enrichment."""
        results = self.knowledge_service.semantic_search(query, top_k=top_k)
        enriched: list[dict[str, Any]] = []
        for result in results:
            citation = self.build_citation_metadata(query, result)
            enriched.append({**result, "citation_metadata": citation.to_dict()})
        return enriched

    def build_citation_metadata(self, query: str, search_result: dict[str, Any]) -> KnowledgeCitationMetadata:
        """Citation Metadata engine."""
        document = search_result.get("document") or {}
        chunk = search_result.get("chunk") or {}
        citation = search_result.get("citation") or {}
        knowledge_document_id = int(document["id"]) if document.get("id") else None
        metadata = self.build_metadata(knowledge_document_id) if knowledge_document_id else None
        citation_metadata = KnowledgeCitationMetadata(
            query_text=query,
            source_knowledge_document_id=knowledge_document_id,
            source_chunk_id=int(chunk["id"]) if chunk.get("id") else None,
            title=citation.get("title") or document.get("title"),
            document_number=citation.get("document_number") or document.get("document_number"),
            document_type=metadata.document_type if metadata else document.get("document_type"),
            authority_level=metadata.authority_level if metadata else None,
            validity_status=metadata.validity_status if metadata else None,
            issued_date=citation.get("issued_date") or (metadata.issued_date if metadata else None),
            page=citation.get("page") or chunk.get("page"),
            section=citation.get("section") or chunk.get("section"),
            file_path=citation.get("file_path") or document.get("source_path"),
            checksum=citation.get("checksum") or document.get("checksum"),
            score=float(search_result.get("score") or 0),
            citation_json=json.dumps(citation, ensure_ascii=False),
        )
        self.repository.add_citation_metadata(citation_metadata)
        return citation_metadata

    def _relationship_from_metadata(
        self,
        source: KnowledgeMetadata,
        target: dict[str, Any],
    ) -> dict[str, Any] | None:
        source_type = source.normalized_type or ""
        target_type = str(target.get("normalized_type") or "")
        same_field = bool(source.field and target.get("field") and source.field == target.get("field"))
        same_number = bool(source.document_number and source.document_number == target.get("document_number"))
        if same_number:
            relation_type = "references"
            confidence = 0.92
            reason = "Trùng số/ký hiệu văn bản"
        elif source_type == "bao_cao" and target_type in {"ke_hoach", "cong_van"} and same_field:
            relation_type = "reports"
            confidence = 0.78
            reason = "Báo cáo cùng lĩnh vực với văn bản triển khai"
        elif source_type in {"cong_van", "ke_hoach"} and target_type in {"quy_dinh", "quyet_dinh"}:
            relation_type = "implements"
            confidence = 0.72
            reason = "Văn bản triển khai liên hệ văn bản quy định/quyết định"
        elif same_field:
            relation_type = "related"
            confidence = 0.58
            reason = "Cùng lĩnh vực"
        else:
            return None
        return {
            "source_knowledge_document_id": source.knowledge_document_id,
            "target_knowledge_document_id": int(target["knowledge_document_id"]),
            "relation_type": relation_type,
            "direction": "forward",
            "weight": round(max(confidence, 0.1), 4),
            "confidence": confidence,
            "evidence_json": json.dumps(
                {
                    "reason": reason,
                    "source_type": source_type,
                    "target_type": target_type,
                    "source_field": source.field,
                    "target_field": target.get("field"),
                },
                ensure_ascii=False,
            ),
            "source": "metadata_rule_v2",
        }

    def _metadata_payload(self, document: dict[str, Any], library_document: dict[str, Any] | None) -> dict[str, Any]:
        metadata_json = str(document.get("metadata_json") or "{}")
        try:
            embedded = json.loads(metadata_json)
        except json.JSONDecodeError:
            embedded = {}
        payload: dict[str, Any] = {
            "title": document.get("title"),
            "document_number": document.get("document_number"),
            "document_type": document.get("document_type"),
            "field": document.get("field"),
            "checksum": document.get("source_checksum") or document.get("indexed_checksum"),
            **embedded,
        }
        if library_document:
            for key in (
                "title",
                "document_number",
                "document_type",
                "field",
                "issued_date",
                "issuing_agency",
                "signer",
                "checksum",
            ):
                if library_document.get(key):
                    payload[key] = library_document.get(key)
        return payload

    def _library_document(self, document: dict[str, Any]) -> dict[str, Any] | None:
        library_id = document.get("library_document_id")
        if not library_id:
            return None
        return self.library_repository.get_document(int(library_id))

    def _require_document(self, knowledge_document_id: int) -> dict[str, Any]:
        document = self.repository.get_document(knowledge_document_id)
        if not document:
            raise ValueError("Không tìm thấy knowledge document")
        return document

    def _metadata_from_row(self, row: dict[str, Any]) -> KnowledgeMetadata:
        return KnowledgeMetadata(
            id=row.get("id"),
            knowledge_document_id=row.get("knowledge_document_id"),
            library_document_id=row.get("library_document_id"),
            title=str(row.get("title") or ""),
            document_number=row.get("document_number"),
            document_type=row.get("document_type"),
            normalized_type=row.get("normalized_type"),
            field=row.get("field"),
            issuing_agency=row.get("issuing_agency"),
            signer=row.get("signer"),
            issued_date=row.get("issued_date"),
            effective_date=row.get("effective_date"),
            expiry_date=row.get("expiry_date"),
            authority_level=str(row.get("authority_level") or "unknown"),
            authority_score=float(row.get("authority_score") or 0),
            validity_status=str(row.get("validity_status") or "unknown"),
            validity_reason=row.get("validity_reason"),
            source_checksum=row.get("source_checksum"),
            metadata_hash=row.get("metadata_hash"),
            metadata_json=row.get("metadata_json"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    @staticmethod
    def normalize_document_type(value: str) -> str | None:
        normalized = KnowledgeMetadataService._normalize(value)
        mapping = {
            "cong van": "cong_van",
            "bao cao": "bao_cao",
            "ke hoach": "ke_hoach",
            "to trinh": "to_trinh",
            "thong bao": "thong_bao",
            "giay moi": "giay_moi",
            "quy dinh": "quy_dinh",
            "quyet dinh": "quyet_dinh",
        }
        for signal, normalized_type in mapping.items():
            if signal in normalized:
                return normalized_type
        return None

    @staticmethod
    def _date_text(value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text) else None

    @staticmethod
    def _cache_key(document: dict[str, Any], metadata_hash: str) -> str:
        checksum = str(document.get("source_checksum") or document.get("indexed_checksum") or "")
        return f"{METADATA_ENGINE_VERSION}:{document['id']}:{checksum}:{metadata_hash}"

    @staticmethod
    def _hash_json(payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _normalize(value: str) -> str:
        text = unicodedata.normalize("NFD", value.lower())
        text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
        text = text.replace("đ", "d")
        return re.sub(r"\s+", " ", text).strip()
