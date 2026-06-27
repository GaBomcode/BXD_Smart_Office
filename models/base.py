"""Các model nền dùng chung cho BXD Smart Office.

Model trong dự án chỉ giữ dữ liệu nghiệp vụ. Repository chịu trách nhiệm
đọc/ghi SQLite, Service chịu trách nhiệm kiểm tra nghiệp vụ.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class BaseModel:
    """Lớp cha cho các model dataclass trong hệ thống."""

    id: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Chuyển model sang dict để truyền cho repository hoặc UI."""
        return asdict(self)
