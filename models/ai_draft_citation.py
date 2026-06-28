"""Citation model for AI Draft Engine."""

from __future__ import annotations

from dataclasses import dataclass

from models.base import BaseModel


@dataclass(slots=True)
class AIDraftCitation(BaseModel):
    """Source citation attached to templates, evidence, outlines, or drafts."""

    request_id: int | None = None
    result_id: int | None = None
    citation_type: str = "evidence"
    source_document_id: int | None = None
    source_chunk_id: int | None = None
    title: str | None = None
    document_number: str | None = None
    issued_date: str | None = None
    page: int | None = None
    section: str | None = None
    file_path: str | None = None
    checksum: str | None = None
    score: float = 0.0
    quote_text: str | None = None
    reason: str | None = None
    created_at: str | None = None

    def __post_init__(self) -> None:
        self.citation_type = self.citation_type.strip() or "evidence"
        if self.request_id is not None and self.request_id <= 0:
            raise ValueError("request_id phai lon hon 0")
        if self.result_id is not None and self.result_id <= 0:
            raise ValueError("result_id phai lon hon 0")
        if self.score < 0:
            raise ValueError("score khong duoc am")
