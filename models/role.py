"""Model hồ sơ vai trò của Ban Xây dựng Đảng."""

from __future__ import annotations

from dataclasses import dataclass
from models.base import BaseModel


@dataclass(slots=True)
class Role(BaseModel):
    """Vai trò nghiệp vụ trong cơ quan."""

    title: str = ""
    unit: str = "Ban Xây dựng Đảng"
    scope: str | None = None
    note: str | None = None
    created_at: str | None = None
