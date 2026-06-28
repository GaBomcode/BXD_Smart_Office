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


def render_router() -> None:
    page = st.sidebar.radio("Chọn phân hệ", list(PAGES.keys()))
    PAGES[page]()
