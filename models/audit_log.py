"""Model nhật ký hệ thống."""

from __future__ import annotations

from dataclasses import dataclass
from models.base import BaseModel


@dataclass(slots=True)
class AuditLog(BaseModel):
    """Nhật ký thao tác để truy vết xử lý công việc."""

    actor: str = "Người dùng"
    action: str = ""
    entity_type: str = ""
    entity_id: int | None = None
    detail: str | None = None
    created_at: str | None = None
