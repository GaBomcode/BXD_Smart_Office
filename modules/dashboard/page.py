from __future__ import annotations

from datetime import date
from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from modules.dashboard.widgets import metric_card
from services.document_library_service import DocumentLibraryService
from services.task_service import TaskService

TRACKED_FIELDS = [
    "Tổ chức xây dựng Đảng",
    "Tuyên giáo",
    "Dân vận",
    "Tổng hợp",
    "Văn thư - lưu trữ",
]


def _section_title(title: str) -> None:
    """Render a styled dashboard section title."""
    st.markdown(f'<div class="bxd-section-title">{escape(title)}</div>', unsafe_allow_html=True)


def _page_hero() -> None:
    """Render the dashboard title block."""
    st.markdown(
        """
        <div class="bxd-page-hero">
            <div class="bxd-page-hero__eyebrow">Dashboard</div>
            <div class="bxd-page-hero__title">Dashboard điều hành</div>
            <div class="bxd-page-hero__subtitle">
                Tổng quan tình hình công việc của Ban Xây dựng Đảng
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _empty_state(title: str, guidance: str, icon: str = "i") -> None:
    """Render a styled empty state card."""
    st.markdown(
        f"""
        <div class="bxd-empty-state">
            <div class="bxd-empty-state__icon">{escape(icon)}</div>
            <div>
                <div class="bxd-empty-state__title">{escape(title)}</div>
                <div class="bxd-empty-state__body">{escape(guidance)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _parse_date(value: Any) -> date | None:
    """Parse a task deadline date."""
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _is_completed(task: dict[str, Any]) -> bool:
    """Return whether a task is completed."""
    return str(task.get("status") or "") == "Hoàn thành"


def _priority_badge(priority: Any) -> str:
    """Return a priority badge."""
    text = escape(str(priority or "Bình thường"))
    priority_text = str(priority or "").lower()
    if "khẩn" in priority_text or "cao" in priority_text:
        css_class = "badge-danger"
    elif "thấp" in priority_text:
        css_class = "badge-muted"
    else:
        css_class = "badge-primary"
    return f'<span class="{css_class}">{text}</span>'


def _task_card(task: dict[str, Any], *, detail: str = "") -> str:
    """Build a compact task card."""
    title = escape(str(task.get("title") or "Nhiệm vụ chưa đặt tên"))
    assignee = escape(str(task.get("assigned_to") or "Chưa phân công"))
    field = escape(str(task.get("field") or "Chưa phân loại"))
    deadline = escape(str(task.get("deadline") or "Chưa có hạn"))
    detail_html = f'<div class="bxd-list-card__meta">{escape(detail)}</div>' if detail else ""
    return f"""
    <div class="bxd-list-card">
        <div class="bxd-list-card__title">{title}</div>
        <div class="bxd-list-card__meta">Phụ trách: {assignee} · Lĩnh vực: {field}</div>
        <div class="bxd-list-card__meta">Hạn xử lý: {deadline}</div>
        {detail_html}
        <div style="margin-top:0.55rem">{_priority_badge(task.get("priority"))}</div>
    </div>
    """


def _staff_initials(name: str) -> str:
    """Build initials for a staff avatar."""
    words = [word for word in name.split() if word]
    if not words:
        return "NS"
    return "".join(word[0] for word in words[-2:]).upper()


def _render_staff_cards(kpi_rows: list[dict[str, Any]]) -> None:
    """Render KPI rows as staff cards."""
    if not kpi_rows:
        _empty_state(
            "Chưa có dữ liệu KPI",
            "KPI sẽ được tổng hợp sau khi nhiệm vụ được giao và cập nhật tiến độ.",
        )
        return
    for row in kpi_rows[:6]:
        name = str(row.get("full_name") or "Nhân sự")
        position = escape(str(row.get("position") or row.get("field") or "Chưa cập nhật chức danh"))
        progress = max(0, min(100, int(float(row.get("avg_progress") or 0))))
        total = int(row.get("total_tasks") or 0)
        completed = int(row.get("completed_tasks") or 0)
        active = max(0, total - completed)
        st.markdown(
            f"""
            <div class="bxd-staff-card">
                <div class="bxd-staff-avatar">{escape(_staff_initials(name))}</div>
                <div class="bxd-staff-card__body">
                    <div class="bxd-staff-card__name">{escape(name)}</div>
                    <div class="bxd-staff-card__meta">{position}</div>
                    <div class="bxd-progress" aria-hidden="true">
                        <span class="bxd-progress__bar" style="--progress: {progress}%"></span>
                    </div>
                    <div class="bxd-staff-card__meta">
                        Tổng: {total} · Hoàn thành: {completed} · Đang xử lý: {active}
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_field_progress(tasks: list[dict[str, Any]]) -> None:
    """Render progress by configured office field."""
    if not tasks:
        _empty_state(
            "Chưa có dữ liệu tiến độ",
            "Khi nhiệm vụ có lĩnh vực, tiến độ sẽ được tổng hợp tại đây.",
        )
        return
    for field in TRACKED_FIELDS:
        field_tasks = [
            task
            for task in tasks
            if field.lower() in str(task.get("field") or "").lower()
        ]
        progress = 0
        if field_tasks:
            total_progress = sum(int(task.get("progress") or 0) for task in field_tasks)
            progress = int(total_progress / len(field_tasks))
        st.markdown(
            f"""
            <div class="bxd-list-card">
                <div class="bxd-list-card__title">{escape(field)}</div>
                <div class="bxd-progress" aria-hidden="true">
                    <span class="bxd-progress__bar" style="--progress: {progress}%"></span>
                </div>
                <div class="bxd-list-card__meta">{progress}% · {len(field_tasks)} nhiệm vụ</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_monthly_progress(tasks: list[dict[str, Any]]) -> None:
    """Render progress for tasks due in the current month."""
    current_month = date.today().strftime("%Y-%m")
    month_tasks = [
        task
        for task in tasks
        if str(task.get("deadline") or "").startswith(current_month)
    ]
    if not month_tasks:
        _empty_state(
            "Chưa có tiến độ trong tháng",
            "Các nhiệm vụ có hạn trong tháng hiện tại sẽ được tổng hợp tại đây.",
        )
        return
    progress = int(sum(int(task.get("progress") or 0) for task in month_tasks) / len(month_tasks))
    completed = sum(1 for task in month_tasks if _is_completed(task))
    active = len(month_tasks) - completed
    summary = (
        f"{progress}% · Tổng: {len(month_tasks)} · "
        f"Hoàn thành: {completed} · Đang xử lý: {active}"
    )
    st.markdown(
        f"""
        <div class="bxd-list-card bxd-month-card">
            <div class="bxd-list-card__title">Tiến độ nhiệm vụ theo tháng</div>
            <div class="bxd-progress" aria-hidden="true">
                <span class="bxd-progress__bar" style="--progress: {progress}%"></span>
            </div>
            <div class="bxd-list-card__meta">{summary}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_documents() -> None:
    """Render recently updated document metadata."""
    documents = DocumentLibraryService().list_documents(limit=5)
    if not documents:
        _empty_state("Chưa có văn bản mới", "Văn bản sau khi index sẽ xuất hiện trong khu vực này.")
        return
    for document in documents[:5]:
        title = escape(str(document.get("title") or "Văn bản"))
        st.markdown(
            f"""
            <div class="bxd-document-card">
                <div class="bxd-document-card__title">{title}</div>
                <div class="bxd-document-card__meta">
                    {escape(str(document.get("document_number") or "Chưa có số"))}
                    · {escape(str(document.get("document_type") or "Chưa phân loại"))}
                    · {escape(str(document.get("status") or "unknown"))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_recent_activity(service: TaskService) -> None:
    """Render recent task updates or audit logs."""
    rows = service.list_updates()[:5] or service.list_audit_logs()[:5]
    if not rows:
        _empty_state(
            "Chưa có hoạt động gần đây",
            "Các cập nhật nhiệm vụ và nhật ký thao tác sẽ hiển thị tại đây.",
        )
        return
    for row in rows:
        title = row.get("content") or row.get("action") or "Hoạt động"
        actor = row.get("actor") or row.get("updated_by") or row.get("created_by") or "Hệ thống"
        created_at = row.get("created_at") or row.get("updated_at") or ""
        st.markdown(
            f"""
            <div class="bxd-list-card">
                <div class="bxd-list-card__title">{escape(str(title))}</div>
                <div class="bxd-list-card__meta">
                    {escape(str(actor))} · {escape(str(created_at))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_dashboard() -> None:
    """Render the executive dashboard."""
    _page_hero()
    service = TaskService()
    stats = service.get_stats()
    tasks = service.list_tasks(keyword=None)
    today = date.today()

    active_tasks = [task for task in tasks if not _is_completed(task)]
    today_tasks = [task for task in active_tasks if _parse_date(task.get("deadline")) == today]
    due_soon = [
        task
        for task in active_tasks
        if (deadline := _parse_date(task.get("deadline"))) and 0 <= (deadline - today).days <= 7
    ]
    overdue = [
        task
        for task in active_tasks
        if (deadline := _parse_date(task.get("deadline"))) and (today - deadline).days > 0
    ]

    cols = st.columns(5)
    metric_card(
        cols[0],
        "Tổng nhiệm vụ",
        int(stats.get("total") or 0),
        help_text="Theo dữ liệu hiện có",
        variant="blue",
        icon="CB",
        progress=100,
    )
    metric_card(
        cols[1],
        "Đang thực hiện",
        int(stats.get("doing") or 0),
        help_text="Đang xử lý",
        variant="purple",
        icon="TD",
        progress=55,
    )
    metric_card(
        cols[2],
        "Sắp đến hạn",
        int(stats.get("due_soon") or 0),
        help_text="Cần chú ý",
        variant="orange",
        icon="CL",
        progress=45,
    )
    metric_card(
        cols[3],
        "Quá hạn",
        int(stats.get("overdue") or 0),
        help_text="Cần xử lý ngay",
        variant="red",
        icon="!",
        progress=30,
    )
    metric_card(
        cols[4],
        "Tiến độ TB",
        f"{stats.get('avg_progress') or 0}%",
        help_text="Hiệu suất chung",
        variant="green",
        icon="PT",
        progress=int(stats.get("avg_progress") or 0),
    )

    left, middle, right = st.columns(3)
    with left:
        _section_title("Công việc hôm nay")
        if today_tasks:
            for task in today_tasks[:4]:
                st.markdown(_task_card(task, detail="Trong ngày hôm nay"), unsafe_allow_html=True)
        else:
            _empty_state(
                "Chưa có nhiệm vụ hôm nay",
                "Các nhiệm vụ có hạn xử lý trong ngày sẽ xuất hiện tại đây.",
            )

    with middle:
        _section_title("Nhiệm vụ sắp đến hạn")
        if due_soon:
            for task in due_soon[:4]:
                deadline = _parse_date(task.get("deadline"))
                remaining = (deadline - today).days if deadline else 0
                st.markdown(
                    _task_card(task, detail=f"Còn {remaining} ngày"),
                    unsafe_allow_html=True,
                )
        else:
            _empty_state(
                "Không có nhiệm vụ sắp hạn",
                "Danh sách sẽ được cập nhật khi có hạn xử lý gần tới.",
            )

    with right:
        _section_title("Nhiệm vụ quá hạn")
        if overdue:
            for task in overdue[:4]:
                deadline = _parse_date(task.get("deadline"))
                days = (today - deadline).days if deadline else 0
                st.markdown(_task_card(task, detail=f"Quá hạn {days} ngày"), unsafe_allow_html=True)
        else:
            _empty_state(
                "Không có nhiệm vụ quá hạn",
                "Các cảnh báo quá hạn sẽ được hiển thị rõ tại đây.",
            )

    staff_col, month_col = st.columns(2)
    with staff_col:
        _section_title("KPI nhân sự")
        _render_staff_cards(service.get_kpi_by_staff())

    with month_col:
        _section_title("Tiến độ nhiệm vụ theo tháng")
        _render_monthly_progress(tasks)

    field_col, doc_col, activity_col = st.columns(3)
    with field_col:
        _section_title("Tiến độ theo lĩnh vực")
        _render_field_progress(tasks)

    with doc_col:
        _section_title("Văn bản mới cập nhật")
        _render_documents()

    with activity_col:
        _section_title("Hoạt động gần đây")
        _render_recent_activity(service)

    if tasks:
        _section_title("Bảng nhiệm vụ tổng hợp")
        st.dataframe(
            pd.DataFrame(tasks)[
                ["id", "title", "assigned_to", "deadline", "priority", "status", "progress"]
            ],
            use_container_width=True,
            hide_index=True,
        )
