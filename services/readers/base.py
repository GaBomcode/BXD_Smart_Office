"""Kiểu kết quả đọc file dùng chung."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ReaderResult:
    """Kết quả chuẩn hóa từ các reader DOCX/PDF/XLSX/TXT."""

    text: str
    pages: int = 0
    tables: list[list[list[str]]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    status: str = "read"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "pages": self.pages,
            "tables": self.tables,
            "metadata": self.metadata,
            "status": self.status,
            "error": self.error,
        }
