"""Model tài liệu trong AI Knowledge Engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import json

from models.base import BaseModel


@dataclass(slots=True)
class KnowledgeDocument(BaseModel):
    """Bản đại diện tri thức của một văn bản đã được người dùng/engine duyệt."""

    library_document_id: int | None = None
    title: str = ""
    source_path: str | None = None
    document_type: str | None = None
    document_number: str | None = None
    field: str | None = None
    status: str = "ready"
    source_checksum: str | None = None
    indexed_checksum: str | None = None
    last_indexed_at: str | None = None
    metadata_json: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        self.status = self.status.strip() or "ready"
        if self.library_document_id is not None and self.library_document_id <= 0:
            raise ValueError("library_document_id phải lớn hơn 0")
        if not self.title:
            raise ValueError("title là bắt buộc")

    @classmethod
    def from_library_document(cls, document: dict[str, Any]) -> "KnowledgeDocument":
        metadata = {
            key: document.get(key)
            for key in ("summary", "keywords", "issued_date", "issuing_agency", "signer", "file_ext", "checksum")
        }
        return cls(
            library_document_id=int(document["id"]),
            title=str(document.get("title") or document.get("file_name") or "Văn bản"),
            source_path=document.get("file_path"),
            document_type=document.get("document_type"),
            document_number=document.get("document_number"),
            field=document.get("field"),
            source_checksum=document.get("checksum"),
            indexed_checksum=document.get("checksum"),
            metadata_json=json.dumps(metadata, ensure_ascii=False),
        )
