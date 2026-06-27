"""Model lịch sử cập nhật tiến độ nhiệm vụ."""

from __future__ import annotations

from dataclasses import dataclass
from models.base import BaseModel


@dataclass(slots=True)
class TaskUpdate(BaseModel):
    """Một mốc cập nhật tiến độ trong timeline nhiệm vụ."""

    task_id: int = 0
    content: str = ""
    progress: int = 0
    evidence_path: str | None = None
    update_date: str | None = None
    created_by: str = "Người dùng"
    created_at: str | None = None
