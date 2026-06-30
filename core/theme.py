import streamlit as st

from core.config import RESOURCE_DIR


def apply_theme() -> None:
    """Apply the offline Streamlit theme."""
    css_path = RESOURCE_DIR / "static" / "css" / "dashboard.css"
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
    else:
        css = ".stApp { background: #08111f; color: #edf5ff; }"
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
