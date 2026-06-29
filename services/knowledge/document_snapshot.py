"""Immutable document snapshot used by the Knowledge handoff pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class DocumentSnapshot:
    """Stable document data captured before indexing starts."""

    document_id: int
    title: str
    full_text: str
    checksum: str
    metadata: dict[str, Any]

    def __post_init__(self) -> None:
        if self.document_id <= 0:
            raise ValueError("document_id must be greater than 0")
        if not self.title.strip():
            raise ValueError("title is required")
        if not self.full_text.strip():
            raise ValueError("full_text is required")
        if not self.checksum.strip():
            raise ValueError("checksum is required")

    @classmethod
    def from_library_document(cls, document: dict[str, Any], *, full_text: str) -> "DocumentSnapshot":
        """Create a snapshot from a Document Library row and parsed text."""
        metadata = {
            key: document.get(key)
            for key in (
                "document_type",
                "document_number",
                "issued_date",
                "issuing_agency",
                "signer",
                "summary",
                "keywords",
                "field",
                "file_path",
                "file_ext",
            )
        }
        return cls(
            document_id=int(document["id"]),
            title=str(document.get("title") or document.get("file_name") or "Van ban"),
            full_text=full_text,
            checksum=str(document.get("checksum") or ""),
            metadata=metadata,
        )
