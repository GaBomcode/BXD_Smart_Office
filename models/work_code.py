"""Model mã việc và sản phẩm đầu ra."""

from __future__ import annotations

from dataclasses import dataclass
from models.base import BaseModel


@dataclass(slots=True)
class WorkCode(BaseModel):
    """Mã việc chuẩn để gắn nhiệm vụ, sản phẩm và KPI."""

    code: str = ""
    axis: str = ""
    group_name: str | None = None
    task_name: str = ""
    output_product: str | None = None
    frequency: str | None = None
    level: str = "N3"
    point: float = 1.0
    coefficient: float = 1.0
    active: int = 1
    created_at: str | None = None
