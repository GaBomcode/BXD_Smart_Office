from __future__ import annotations

from typing import Any

import streamlit as st


def metric_card(container: Any, title: str, value: Any, delta: str | None = None, help_text: str | None = None) -> None:
    """Hiển thị một thẻ chỉ số trong container Streamlit."""
    container.metric(
        label=title,
        value=value,
        delta=delta,
        help=help_text,
    )


def metric_cards(stats: dict[str, Any]) -> None:
    """Hiển thị nhóm thẻ chỉ số mặc định cho dashboard."""
    cols = st.columns(5)
    items = [
        ("Tổng nhiệm vụ", stats.get("total") or 0),
        ("Đang thực hiện", stats.get("doing") or 0),
        ("Sắp đến hạn", stats.get("due_soon") or 0),
        ("Quá hạn", stats.get("overdue") or 0),
        ("Hoàn thành", stats.get("done") or 0),
    ]
    for col, (label, value) in zip(cols, items):
        metric_card(col, label, int(value or 0))
