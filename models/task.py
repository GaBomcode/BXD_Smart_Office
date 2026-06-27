"""Model nhiệm vụ."""

from __future__ import annotations

from dataclasses import dataclass
from models.base import BaseModel


@dataclass(slots=True)
class Task(BaseModel):
    """Nhiệm vụ gắn với mã việc, nhân sự, hạn xử lý, minh chứng và KPI."""

    title: str = ""
    description: str | None = None
    workspace_id: int | None = None
    work_code_id: int | None = None
    field: str | None = None
    assigned_to_id: int | None = None
    deadline: str | None = None
    priority: str = "Bình thường"
    status: str = "Chưa thực hiện"
    progress: int = 0
    evidence_path: str | None = None
    related_document: str | None = None
    point: float = 0.0
    created_by: str = "Nguyễn Trung Hiền"
    created_at: str | None = None
    updated_at: str | None = None

    def is_done(self) -> bool:
        """Trả về True nếu nhiệm vụ đã hoàn thành."""
        return self.status == "Hoàn thành" or self.progress >= 100
