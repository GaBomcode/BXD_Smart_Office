"""Model quy tắc KPI."""

from __future__ import annotations

from dataclasses import dataclass
from models.base import BaseModel


@dataclass(slots=True)
class KpiRule(BaseModel):
    """Quy tắc chấm điểm theo mức độ N1-N5."""

    name: str = ""
    level: str = "N3"
    point: float = 1.0
    coefficient: float = 1.0
    note: str | None = None
    created_at: str | None = None
