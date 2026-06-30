import sys
from datetime import datetime
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st

from app.router import render_router
from core.theme import apply_theme
from core.version import APP_NAME, APP_VERSION, BUILD_NAME
from database.init_db import init_database

st.set_page_config(page_title=APP_NAME, page_icon=":office:", layout="wide")
init_database()
apply_theme()
st.sidebar.markdown(
    f"""
    <div class="bxd-sidebar-brand">
        <div class="bxd-sidebar-logo">BX</div>
        <div>
            <div class="bxd-sidebar-brand__title">BXD Smart Office</div>
            <div class="bxd-sidebar-brand__subtitle">Offline Office System</div>
        </div>
    </div>
    <div class="bxd-version-badge">{BUILD_NAME} | v{APP_VERSION}</div>
    <div class="bxd-menu-caption">MENU CHÍNH</div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    f"""
    <div class="bxd-topbar">
        <div>
            <div class="bxd-topbar__eyebrow">Ban Xây dựng Đảng</div>
            <div class="bxd-topbar__title">{APP_NAME}</div>
        </div>
        <div class="bxd-topbar__actions">
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
render_router()
