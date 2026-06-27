import streamlit as st


def apply_theme() -> None:
    st.markdown("""
    <style>
    .stApp { background: #0f172a; color: #e5e7eb; }
    section[data-testid="stSidebar"] { background: #111827; }
    div[data-testid="stMetric"] { background:#111827; border:1px solid #334155; padding:16px; border-radius:14px; }
    .bxd-card { background:#111827; border:1px solid #334155; border-radius:16px; padding:18px; margin:10px 0; }
    .small-muted { color:#94a3b8; font-size: 0.9rem; }
    </style>
    """, unsafe_allow_html=True)
