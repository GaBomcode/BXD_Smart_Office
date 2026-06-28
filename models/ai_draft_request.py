"""Models for AI Draft request intake."""

from __future__ import annotations

from dataclasses import dataclass
import logging

from models.base import BaseModel

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class AIDraftRequest(BaseModel):
    """A user request for an AI-assisted draft."""

    request_text: str = ""
    requested_by: str = "Nguoi dung"
    detected_document_type: str | None = None
    selected_document_type: str | None = None
    confidence: float = 0.0
    status: str = "draft_requested"
    created_at: str | None = None
    updated_at: str | None = None

    def __post_init__(self) -> None:
        self.request_text = self.request_text.strip()
        self.requested_by = self.requested_by.strip() or "Nguoi dung"
        self.status = self.status.strip() or "draft_requested"
        if not self.request_text:
            logger.error("AI draft request is empty")
            raise ValueError("request_text la bat buoc")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence phai nam trong khoang 0..1")
