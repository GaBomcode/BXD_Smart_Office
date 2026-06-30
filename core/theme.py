import streamlit as st

from core.config import RESOURCE_DIR


def apply_theme() -> None:
    """Apply the offline Streamlit light design system."""
    css_path = RESOURCE_DIR / "static" / "css" / "design_system.css"
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
    else:
        css = ".stApp { background: #f8fafc; color: #0f172a; }"
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
