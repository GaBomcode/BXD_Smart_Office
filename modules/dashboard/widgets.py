from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st


def metric_card(
    container: Any,
    title: str,
    value: Any,
    delta: str | None = None,
    help_text: str | None = None,
    *,
    variant: str = "blue",
    icon: str = "*",
    progress: int | float = 0,
) -> None:
    """Render a styled dashboard KPI card."""
    hint = delta or help_text or "Theo dữ liệu hiện có"
    progress_value = max(0, min(100, int(progress or 0)))
    container.markdown(
        f"""
        <div class="bxd-kpi-card bxd-kpi-{escape(variant)}">
            <div class="bxd-kpi-card__top">
                <div class="bxd-kpi-card__title">{escape(title)}</div>
                <div class="bxd-kpi-card__icon">{escape(icon)}</div>
            </div>
            <div class="bxd-kpi-card__value">{escape(str(value))}</div>
            <div class="bxd-kpi-card__hint">{escape(str(hint))}</div>
            <div class="bxd-progress" aria-hidden="true">
                <span class="bxd-progress__bar" style="--progress: {progress_value}%"></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_cards(stats: dict[str, Any]) -> None:
    """Render the default dashboard KPI card group."""
    cols = st.columns(5)
    items = [
        ("Tổng nhiệm vụ", stats.get("total") or 0, "blue", "CB", 100),
        ("Đang thực hiện", stats.get("doing") or 0, "purple", "TD", 55),
        ("Sắp đến hạn", stats.get("due_soon") or 0, "orange", "CL", 45),
        ("Quá hạn", stats.get("overdue") or 0, "red", "!", 30),
        ("Hoàn thành", stats.get("done") or 0, "green", "+", stats.get("avg_progress") or 0),
    ]
    for col, (label, value, variant, icon, progress) in zip(cols, items):
        metric_card(col, label, int(value or 0), variant=variant, icon=icon, progress=progress)
