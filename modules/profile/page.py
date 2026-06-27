import pandas as pd
import streamlit as st
from services.profile_service import ProfileService


def render_profile() -> None:
    st.title("Phân hệ 0 - Hồ sơ vai trò & công việc")
    service = ProfileService()
    tab1, tab2, tab3 = st.tabs(["Nhân sự", "Mã việc", "Quy tắc KPI"])
    with tab1:
        st.subheader("Danh sách nhân sự")
        st.dataframe(pd.DataFrame(service.get_staff()), use_container_width=True, hide_index=True)
    with tab2:
        st.subheader("Danh mục mã việc")
        st.dataframe(pd.DataFrame(service.get_work_codes()), use_container_width=True, hide_index=True)
    with tab3:
        st.subheader("Quy tắc KPI")
        st.dataframe(pd.DataFrame(service.get_kpi_rules()), use_container_width=True, hide_index=True)
