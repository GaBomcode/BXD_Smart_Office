from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from services.document_service import DocumentService

DOCUMENT_TYPES = ["Công văn", "Báo cáo", "Kế hoạch", "Tờ trình", "Thông báo", "Quyết định"]
FIELDS = ["Tổng hợp", "Tổ chức", "Tuyên giáo", "Dân vận", "Phối hợp", "Lãnh đạo điều hành"]


def _template_label(template: dict[str, Any]) -> str:
    score = template.get("match_score")
    suffix = f" - {score}%" if score is not None else ""
    return f'{template["id"]} - {template["name"]} ({template["document_type"]}){suffix}'


def _draft_label(draft: dict[str, Any]) -> str:
    return f'{draft["id"]} - {draft["title"]} ({draft["status"]})'


def _template_options(templates: list[dict[str, Any]]) -> dict[str, int]:
    return {_template_label(template): int(template["id"]) for template in templates}


def render_documents() -> None:
    st.title("Phân hệ 2 - Soạn thảo văn bản")
    service = DocumentService()

    tab_upload, tab_analyze, tab_draft, tab_review, tab_settings = st.tabs(
        ["Kho mẫu", "Phân tích mẫu", "Soạn dự thảo", "Duyệt & xuất", "Cấu hình thể thức"]
    )

    with tab_upload:
        st.subheader("Nạp mẫu văn bản chuẩn")
        with st.form("document_template_upload", clear_on_submit=True):
            uploaded_file = st.file_uploader("File mẫu DOC, DOCX hoặc PDF", type=["doc", "docx", "pdf"])
            document_type = st.selectbox("Loại văn bản", DOCUMENT_TYPES)
            field = st.selectbox("Lĩnh vực", FIELDS)
            created_by = st.text_input("Người nạp mẫu", value="Nguyễn Trung Hiền")
            submitted = st.form_submit_button("Lưu mẫu")
            if submitted:
                if uploaded_file is None:
                    st.error("Vui lòng chọn file mẫu.")
                else:
                    try:
                        template_id = service.upload_template_stream(
                            BytesIO(uploaded_file.getvalue()),
                            uploaded_file.name,
                            document_type=document_type,
                            field=field,
                            created_by=created_by,
                        )
                        st.success(f"Đã nạp mẫu #{template_id}.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Không thể nạp mẫu: {exc}")

        templates = service.list_templates()
        if templates:
            st.dataframe(pd.DataFrame(templates), use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có mẫu văn bản trong kho.")

    with tab_analyze:
        st.subheader("Phân tích bố cục và thể thức mẫu")
        templates = service.list_templates()
        if not templates:
            st.info("Cần nạp mẫu trước khi phân tích.")
        else:
            options = _template_options(templates)
            selected = st.selectbox("Chọn mẫu", list(options.keys()), key="analyze_template")
            template_id = options[selected]
            if st.button("Phân tích mẫu"):
                try:
                    analysis = service.analyze_template(template_id)
                    st.success("Đã phân tích mẫu và lưu bố cục.")
                    st.json(analysis)
                except Exception as exc:
                    st.error(f"Không thể phân tích mẫu: {exc}")
            sections = service.list_sections(template_id)
            if sections:
                st.markdown("### Bố cục đã nhận diện")
                st.dataframe(pd.DataFrame(sections), use_container_width=True, hide_index=True)

    with tab_draft:
        st.subheader("Nhập yêu cầu và sinh dự thảo")
        document_type = st.selectbox("Loại văn bản cần soạn", DOCUMENT_TYPES, key="draft_type")
        field = st.selectbox("Lĩnh vực", FIELDS, key="draft_field")
        title = st.text_input("Tiêu đề dự thảo", value=f"Dự thảo {document_type.lower()}")
        request_text = st.text_area("Yêu cầu soạn thảo", height=140)
        extra_info = st.text_area("Thông tin bổ sung", height=100)

        suggestions: list[dict[str, Any]] = []
        if request_text.strip():
            suggestions = service.suggest_templates(request_text=request_text, document_type=document_type, field=field)
            missing = service.missing_information(request_text=request_text, document_type=document_type)
            if missing:
                st.warning("Cần kiểm tra/bổ sung: " + "; ".join(missing))
        template_id: int | None = None
        if suggestions:
            st.markdown("### Mẫu gợi ý")
            st.dataframe(
                pd.DataFrame(suggestions)[["id", "name", "document_type", "field", "status", "match_score", "match_reason"]],
                use_container_width=True,
                hide_index=True,
            )
            options = _template_options(suggestions)
            selected = st.selectbox("Chọn mẫu tham chiếu", list(options.keys()), key="draft_template")
            template_id = options[selected]
        elif service.list_templates():
            st.info("Chưa có mẫu khớp cao, có thể sinh dự thảo không kèm mẫu.")

        if st.button("Sinh dự thảo chờ duyệt", type="primary"):
            try:
                draft_id = service.generate_draft(
                    title=title,
                    document_type=document_type,
                    request_text=request_text,
                    template_id=template_id,
                    extra_info=extra_info,
                )
                st.success(f"Đã tạo dự thảo #{draft_id}.")
                st.rerun()
            except Exception as exc:
                st.error(f"Không thể sinh dự thảo: {exc}")

    with tab_review:
        st.subheader("Duyệt thể thức và xuất DOCX")
        drafts = service.list_drafts()
        if not drafts:
            st.info("Chưa có dự thảo.")
        else:
            options = {_draft_label(draft): int(draft["id"]) for draft in drafts}
            selected = st.selectbox("Chọn dự thảo", list(options.keys()), key="review_draft")
            draft_id = options[selected]
            draft = service.get_draft(draft_id) or {}
            content = str(draft.get("draft_content") or "")
            edited_content = st.text_area("Nội dung dự thảo", value=content, height=360)
            col_save, col_check, col_export = st.columns(3)
            with col_save:
                if st.button("Lưu chỉnh sửa"):
                    try:
                        service.update_draft_content(draft_id, edited_content)
                        st.success("Đã lưu chỉnh sửa.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Không thể lưu: {exc}")
            with col_check:
                if st.button("Kiểm tra thể thức"):
                    try:
                        service.update_draft_content(draft_id, edited_content)
                        st.dataframe(pd.DataFrame(service.review_draft_format(draft_id)), use_container_width=True, hide_index=True)
                    except Exception as exc:
                        st.error(f"Không thể kiểm tra: {exc}")
            with col_export:
                if st.button("Xuất DOCX"):
                    try:
                        service.update_draft_content(draft_id, edited_content)
                        output = service.export_draft_docx(draft_id)
                        st.success(f"Đã xuất: {output}")
                    except Exception as exc:
                        st.error(f"Không thể xuất DOCX: {exc}")

            if draft.get("output_path"):
                output_path = Path(str(draft["output_path"]))
                if output_path.exists():
                    st.download_button(
                        "Tải DOCX đã xuất",
                        data=output_path.read_bytes(),
                        file_name=output_path.name,
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    )

    with tab_settings:
        st.subheader("Cấu hình thể thức văn bản")
        settings = service.get_document_settings()
        with st.form("document_settings_form"):
            col_left, col_right = st.columns(2)
            with col_left:
                agency_name = st.text_input("Tên cơ quan", value=settings["agency_name"])
                document_code_prefix = st.text_input("Ký hiệu văn bản", value=settings["document_code_prefix"])
                location_name = st.text_input("Địa danh", value=settings["location_name"])
                recipient_placeholder = st.text_input("Nơi nhận mặc định", value=settings["recipient_placeholder"])
                signer_title = st.text_input("Chức vụ người ký", value=settings["signer_title"])
                signer_name = st.text_input("Người ký", value=settings["signer_name"])
            with col_right:
                font_name = st.text_input("Font chữ", value=settings["font_name"])
                font_size = st.number_input("Cỡ chữ", min_value=8.0, max_value=20.0, value=float(settings["font_size"]), step=0.5)
                margin_top_cm = st.number_input("Lề trên (cm)", min_value=0.5, max_value=5.0, value=float(settings["margin_top_cm"]), step=0.1)
                margin_bottom_cm = st.number_input("Lề dưới (cm)", min_value=0.5, max_value=5.0, value=float(settings["margin_bottom_cm"]), step=0.1)
                margin_left_cm = st.number_input("Lề trái (cm)", min_value=0.5, max_value=5.0, value=float(settings["margin_left_cm"]), step=0.1)
                margin_right_cm = st.number_input("Lề phải (cm)", min_value=0.5, max_value=5.0, value=float(settings["margin_right_cm"]), step=0.1)
            if st.form_submit_button("Lưu cấu hình"):
                try:
                    service.update_document_settings(
                        {
                            "agency_name": agency_name,
                            "document_code_prefix": document_code_prefix,
                            "location_name": location_name,
                            "recipient_placeholder": recipient_placeholder,
                            "signer_title": signer_title,
                            "signer_name": signer_name,
                            "font_name": font_name,
                            "font_size": str(font_size),
                            "margin_top_cm": str(margin_top_cm),
                            "margin_bottom_cm": str(margin_bottom_cm),
                            "margin_left_cm": str(margin_left_cm),
                            "margin_right_cm": str(margin_right_cm),
                        }
                    )
                    st.success("Đã lưu cấu hình thể thức.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Không thể lưu cấu hình: {exc}")
