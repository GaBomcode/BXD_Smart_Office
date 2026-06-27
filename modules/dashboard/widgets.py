import streamlit as st


def metric_cards(stats: dict) -> None:
    cols = st.columns(5)
    items = [
        ("Tổng nhiệm vụ", stats.get("total") or 0),
        ("Đang thực hiện", stats.get("doing") or 0),
        ("Sắp đến hạn", stats.get("due_soon") or 0),
        ("Quá hạn", stats.get("overdue") or 0),
        ("Hoàn thành", stats.get("done") or 0),
    ]
    for col, (label, value) in zip(cols, items):
        col.metric(label, int(value or 0))
