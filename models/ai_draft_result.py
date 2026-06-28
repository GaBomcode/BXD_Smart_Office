"""Models for AI Draft results and review states."""

from __future__ import annotations

from dataclasses import dataclass

from models.base import BaseModel


@dataclass(slots=True)
class AIDraftResult(BaseModel):
    """Draft artefact created from a reviewed AI outline."""

    request_id: int | None = None
    title: str = ""
    document_type: str = "Cong van"
    template_document_id: int | None = None
    outline_content: str | None = None
    draft_content: str | None = None
    status: str = "pending_outline_review"
    output_path: str | None = None
    review_note: str | None = None
    approved_by: str | None = None
    approved_at: str | None = None
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        self.document_type = self.document_type.strip() or "Cong van"
        self.status = self.status.strip() or "pending_outline_review"
        if self.request_id is not None and self.request_id <= 0:
            raise ValueError("request_id phai lon hon 0")
        if self.template_document_id is not None and self.template_document_id <= 0:
            raise ValueError("template_document_id phai lon hon 0")
        if not self.title:
            raise ValueError("title la bat buoc")
