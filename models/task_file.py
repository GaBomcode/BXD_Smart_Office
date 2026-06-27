"""Model file minh chứng của nhiệm vụ."""

from __future__ import annotations

from dataclasses import dataclass
from models.base import BaseModel


@dataclass(slots=True)
class TaskFile(BaseModel):
    """File đính kèm/minh chứng cho nhiệm vụ."""

    task_id: int = 0
    file_name: str = ""
    file_path: str = ""
    file_type: str | None = None
    note: str | None = None
    uploaded_by: str = "Người dùng"
    created_at: str | None = None
