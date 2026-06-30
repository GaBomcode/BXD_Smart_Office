import pandas as pd
import streamlit as st

from modules.dashboard.widgets import metric_card
from services.task_service import TaskService


def _section_title(title: str) -> None:
    """Render a styled dashboard section title."""
    st.markdown(f'<div class="bxd-section-title">{title}</div>', unsafe_allow_html=True)


def _empty_state(title: str, guidance: str, icon: str = "i") -> None:
    """Render a styled empty state card."""
    st.markdown(
        f"""
        <div class="bxd-empty-state">
            <div class="bxd-empty-state__icon">{icon}</div>
            <div>
                <div class="bxd-empty-state__title">{title}</div>
                <div class="bxd-empty-state__body">{guidance}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard() -> None:
    """Render the executive dashboard."""
    st.title("Dashboard điều hành")
    service = TaskService()
    stats = service.get_stats()
    cols = st.columns(5)
    metric_card(
        cols[0],
        "Tổng nhiệm vụ",
        int(stats.get("total") or 0),
        variant="blue",
        icon="T",
    )
    metric_card(
        cols[1],
        "Đang thực hiện",
        int(stats.get("doing") or 0),
        variant="purple",
        icon="D",
    )
    metric_card(
        cols[2],
        "Sắp đến hạn",
        int(stats.get("due_soon") or 0),
        variant="orange",
        icon="!",
    )
    metric_card(
        cols[3],
        "Quá hạn",
        int(stats.get("overdue") or 0),
        variant="red",
        icon="Q",
    )
    metric_card(
        cols[4],
        "Tiến độ TB",
        f"{stats.get('avg_progress') or 0}%",
        variant="green",
        icon="%",
    )

    _section_title("Việc cần chú ý")
    urgent = service.list_tasks(keyword=None)
    urgent = [task for task in urgent if task.get("status") != "Hoàn thành"][:10]
    if urgent:
        st.dataframe(
            pd.DataFrame(urgent)[
                ["id", "title", "assigned_to", "deadline", "priority", "status", "progress"]
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        _empty_state(
            "Chưa có nhiệm vụ đang xử lý",
            "Khi có nhiệm vụ mới hoặc nhiệm vụ sắp đến hạn, "
            "danh sách ưu tiên sẽ xuất hiện tại đây.",
            icon="OK",
        )

    _section_title("KPI nhân sự")
    kpi = pd.DataFrame(service.get_kpi_by_staff())
    if not kpi.empty:
        st.dataframe(kpi, use_container_width=True, hide_index=True)
    else:
        _empty_state(
            "Chưa có dữ liệu KPI",
            "KPI sẽ được tổng hợp sau khi nhiệm vụ được giao và cập nhật tiến độ.",
        )
