import pandas as pd
import streamlit as st
from modules.dashboard.widgets import metric_card
from services.task_service import TaskService


def render_dashboard() -> None:
    st.title("Dashboard điều hành")
    service = TaskService()
    stats = service.get_stats()
    cols = st.columns(5)
    metric_card(cols[0], "Tổng nhiệm vụ", int(stats.get("total") or 0))
    metric_card(cols[1], "Đang thực hiện", int(stats.get("doing") or 0))
    metric_card(cols[2], "Sắp đến hạn", int(stats.get("due_soon") or 0))
    metric_card(cols[3], "Quá hạn", int(stats.get("overdue") or 0))
    metric_card(cols[4], "Tiến độ TB", f"{stats.get('avg_progress') or 0}%")

    st.markdown("### Việc cần chú ý")
    urgent = service.list_tasks(keyword=None)
    urgent = [t for t in urgent if t.get("status") != "Hoàn thành"][:10]
    if urgent:
        st.dataframe(pd.DataFrame(urgent)[["id", "title", "assigned_to", "deadline", "priority", "status", "progress"]], use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có nhiệm vụ đang xử lý.")

    st.markdown("### KPI nhân sự")
    kpi = pd.DataFrame(service.get_kpi_by_staff())
    if not kpi.empty:
        st.dataframe(kpi, use_container_width=True, hide_index=True)
