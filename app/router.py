from datetime import datetime

import streamlit as st

from modules.ai_draft.page import render_ai_draft
from modules.dashboard.page import render_dashboard
from modules.document_library.page import render_document_library
from modules.documents.page import render_documents
from modules.profile.page import render_profile
from modules.tasks.page import render_tasks

PAGES = {
    "Dashboard": render_dashboard,
    "Hồ sơ vai trò & công việc": render_profile,
    "Quản lý nhiệm vụ": render_tasks,
    "Soạn thảo văn bản": render_documents,
    "AI Soạn thảo": render_ai_draft,
    "Kho văn bản": render_document_library,
}

MENU_ICONS = {
    "Dashboard": "▦",
    "Hồ sơ vai trò & công việc": "ID",
    "Quản lý nhiệm vụ": "✓",
    "Soạn thảo văn bản": "VB",
    "AI Soạn thảo": "AI",
    "Kho văn bản": "KV",
}

PAGE_SUBTITLES = {
    "Dashboard": "Tổng quan điều hành và theo dõi tiến độ",
    "Hồ sơ vai trò & công việc": "Nhân sự, mã việc và quy tắc KPI",
    "Quản lý nhiệm vụ": "Theo dõi giao việc, tiến độ và minh chứng",
    "Soạn thảo văn bản": "Kho mẫu, dự thảo và xuất văn bản",
    "AI Soạn thảo": "Luồng hỗ trợ soạn thảo offline có kiểm duyệt",
    "Kho văn bản": "Quản lý metadata và chỉ mục văn bản nội bộ",
}


def _menu_label(page: str) -> str:
    """Return a compact visual label for the sidebar menu."""
    return f"{MENU_ICONS.get(page, '•')}  {page}"


def _render_topbar(page: str) -> None:
    """Render the compact premium topbar for the selected page."""
    subtitle = PAGE_SUBTITLES.get(page, "BXD Smart Office - Offline")
    st.markdown(
        f"""
        <div class="bxd-topbar">
            <div class="bxd-topbar__left">
                <div class="bxd-breadcrumb">BXD Smart Office / {page}</div>
                <div class="bxd-topbar__title">{page}</div>
                <div class="bxd-topbar__subtitle">{subtitle}</div>
            </div>
            <div class="bxd-topbar__actions">
                <span class="bxd-date-pill">{datetime.now().strftime("%d/%m/%Y")}</span>
                <span class="bxd-ollama-badge">Ollama Online</span>
                <span class="bxd-sqlite-badge">SQLite Ready</span>
                <span class="bxd-icon-button">!</span>
                <span class="bxd-backup-pill">Sao lưu</span>
                <div class="bxd-user-chip">
                    <span class="bxd-avatar">NH</span>
                    <span>
                        <strong>Nguyễn Trung Hiền</strong>
                        <small>Trưởng ban · {datetime.now().strftime("%d/%m/%Y")}</small>
                    </span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_router() -> None:
    page = st.sidebar.radio(
        "Chọn phân hệ",
        list(PAGES.keys()),
        format_func=_menu_label,
        label_visibility="collapsed",
    )
    st.sidebar.markdown(
        """
        <div class="bxd-menu-caption">HỆ THỐNG</div>
        <div class="bxd-sidebar-menu-card">
            <span>TK</span><strong>Tìm kiếm AI</strong>
        </div>
        <div class="bxd-sidebar-menu-card">
            <span>HS</span><strong>Hồ sơ công việc</strong>
        </div>
        <div class="bxd-sidebar-menu-card">
            <span>BC</span><strong>Báo cáo</strong>
        </div>
        <div class="bxd-sidebar-menu-card">
            <span>CH</span><strong>Cấu hình</strong>
        </div>
        <div class="bxd-sidebar-note">
            Nhân sự · Cấu hình · Sao lưu & phục hồi · Nhật ký hệ thống · Trợ giúp
        </div>
        <div class="bxd-sidebar-note">
            <strong>Ban Xây dựng Đảng</strong><br>
            Đảng ủy xã Vĩnh Hòa
        </div>
        """,
        unsafe_allow_html=True,
    )
    _render_topbar(page)
    PAGES[page]()
