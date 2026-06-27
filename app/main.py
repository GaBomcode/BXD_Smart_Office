import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import streamlit as st
from core.theme import apply_theme
from core.version import APP_NAME, APP_VERSION, BUILD_NAME
from database.init_db import init_database
from app.router import render_router

st.set_page_config(page_title=APP_NAME, page_icon="🏛️", layout="wide")
init_database()
apply_theme()
st.sidebar.title("🏛️ BXD Smart Office")
st.sidebar.caption(f"{BUILD_NAME} | v{APP_VERSION}")
render_router()
