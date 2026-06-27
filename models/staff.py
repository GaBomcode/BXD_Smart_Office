"""Model nhân sự cơ quan."""

from __future__ import annotations

from dataclasses import dataclass
from models.base import BaseModel


@dataclass(slots=True)
class Staff(BaseModel):
    """Nhân sự có thể nhận việc, cập nhật tiến độ hoặc tham gia phân quyền."""

    full_name: str = ""
    position: str = ""
    field: str | None = None
    can_receive_task: int = 1
    system_role: str = "Chuyên viên"
    status: str = "Đang công tác"
    created_at: str | None = None

    @property
    def can_assign_task(self) -> bool:
        """Trưởng Ban và Phó Ban có quyền giao việc trong bản nền."""
        return self.system_role in {"Trưởng Ban", "Phó Ban"}
