"""Model hồ sơ công việc."""

from __future__ import annotations

from dataclasses import dataclass
from models.base import BaseModel


@dataclass(slots=True)
class Workspace(BaseModel):
    """Hồ sơ gom nhiệm vụ, văn bản, minh chứng và ghi chú AI."""

    name: str = ""
    description: str | None = None
    field: str | None = None
    status: str = "Đang xử lý"
    created_by: str = "Nguyễn Trung Hiền"
    created_at: str | None = None
    updated_at: str | None = None
