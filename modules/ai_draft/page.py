from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from services.ai_draft_service import AIDraftService, SUPPORTED_DOCUMENT_TYPES

DOCUMENT_TYPE_LABELS = {
    "Cong van": "Công văn",
    "Bao cao": "Báo cáo",
    "Ke hoach": "Kế hoạch",
    "To trinh": "Tờ trình",
    "Thong bao": "Thông báo",
    "Giay moi": "Giấy mời",
}


def _request_label(request: dict[str, Any]) -> str:
    document_type = request.get("selected_document_type") or request.get("detected_document_type") or "chưa chọn"
    document_type = DOCUMENT_TYPE_LABELS.get(str(document_type), str(document_type))
    return f'{request["id"]} - {document_type} - {request["status"]}'


def _result_label(result: dict[str, Any]) -> str:
    return f'{result["id"]} - {result["title"]} - {result["status"]}'


def render_ai_draft() -> None:
    st.title("AI Soạn thảo")
    service = AIDraftService()

    tab_request, tab_sources, tab_outline, tab_draft, tab_export = st.tabs(
        ["Yêu cầu", "Mẫu & căn cứ", "Dàn ý", "Dự thảo", "Duyệt & xuất"]
    )

    with tab_request:
        st.subheader("Nhập yêu cầu tham mưu")
        with st.form("ai_draft_request_form"):
            request_text = st.text_area("Yêu cầu soạn thảo", height=150)
            requested_by = st.text_input("Người yêu cầu", value="Người dùng")
            submitted = st.form_submit_button("Nhận diện loại văn bản")
            if submitted:
                try:
                    request_id = service.create_request(request_text, requested_by=requested_by)
                    st.success(f"Đã tạo yêu cầu AI Draft #{request_id}.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Không thể tạo yêu cầu: {exc}")

        requests = service.list_requests()
        if requests:
            st.dataframe(
                pd.DataFrame(requests)[
                    ["id", "detected_document_type", "selected_document_type", "confidence", "status", "created_at"]
                ],
                use_container_width=True,
                hide_index=True,
            )
            pending = [item for item in requests if item.get("status") == "needs_document_type_selection"]
            if pending:
                st.markdown("### Cần người dùng chọn lại loại văn bản")
                options = {_request_label(item): int(item["id"]) for item in pending}
                selected = st.selectbox("Yêu cầu cần chọn loại", list(options.keys()))
                type_options = {DOCUMENT_TYPE_LABELS.get(item, item): item for item in SUPPORTED_DOCUMENT_TYPES}
                document_type_label = st.selectbox("Loại văn bản đúng", list(type_options.keys()))
                if st.button("Xác nhận loại văn bản"):
                    try:
                        service.select_document_type(options[selected], type_options[document_type_label])
                        st.success("Đã xác nhận loại văn bản.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Không thể xác nhận: {exc}")
        else:
            st.info("Chưa có yêu cầu AI Draft.")

    with tab_sources:
        st.subheader("Chọn mẫu và thu thập căn cứ")
        requests = [item for item in service.list_requests() if item.get("status") != "needs_document_type_selection"]
        if not requests:
            st.info("Cần tạo yêu cầu và xác nhận loại văn bản trước.")
        else:
            options = {_request_label(item): int(item["id"]) for item in requests}
            selected = st.selectbox("Yêu cầu", list(options.keys()), key="source_request")
            request_id = options[selected]
            col_template, col_evidence = st.columns(2)
            with col_template:
                if st.button("Gợi ý top 5 mẫu"):
                    try:
                        suggestions = service.suggest_templates(request_id)
                        if suggestions:
                            rows = [
                                {
                                    "id": item["document"]["id"],
                                    "title": item["document"].get("title"),
                                    "score": item["score"],
                                    "reason": item["reason"],
                                    "checksum": item["citation"].get("checksum"),
                                }
                                for item in suggestions
                            ]
                            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                        else:
                            st.warning("Chưa tìm thấy mẫu phù hợp.")
                    except Exception as exc:
                        st.error(f"Không thể gợi ý mẫu: {exc}")
            with col_evidence:
                if st.button("Tìm văn bản căn cứ"):
                    try:
                        evidence = service.collect_evidence(request_id)
                        if evidence:
                            rows = [
                                {
                                    "title": item["citation"].get("title"),
                                    "section": item["citation"].get("section"),
                                    "page": item["citation"].get("page"),
                                    "score": item["score"],
                                    "checksum": item["citation"].get("checksum"),
                                }
                                for item in evidence
                            ]
                            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                        else:
                            st.warning("Chưa có căn cứ. Hệ thống sẽ không khẳng định chắc chắn trong dự thảo.")
                    except Exception as exc:
                        st.error(f"Không thể tìm căn cứ: {exc}")

            template_citations = service.repository.list_citations(request_id=request_id, citation_type="template")
            evidence_citations = service.repository.list_citations(request_id=request_id, citation_type="evidence")
            if template_citations:
                st.markdown("### Mẫu đã gợi ý")
                st.dataframe(pd.DataFrame(template_citations), use_container_width=True, hide_index=True)
            if evidence_citations:
                st.markdown("### Căn cứ đã thu thập")
                st.dataframe(pd.DataFrame(evidence_citations), use_container_width=True, hide_index=True)

    with tab_outline:
        st.subheader("Sinh và duyệt dàn ý")
        requests = [item for item in service.list_requests() if item.get("status") != "needs_document_type_selection"]
        if not requests:
            st.info("Cần tạo yêu cầu trước.")
        else:
            options = {_request_label(item): int(item["id"]) for item in requests}
            selected = st.selectbox("Yêu cầu", list(options.keys()), key="outline_request")
            request_id = options[selected]
            template_rows = service.repository.list_citations(request_id=request_id, citation_type="template")
            template_map = {"Không chọn mẫu": None}
            for row in template_rows:
                if row.get("source_document_id"):
                    template_map[f'{row["source_document_id"]} - {row.get("title") or "Mẫu"}'] = int(row["source_document_id"])
            title = st.text_input("Tiêu đề dự thảo", value="Dự thảo văn bản", key="outline_title")
            template_choice = st.selectbox("Mẫu tham chiếu", list(template_map.keys()))
            if st.button("Sinh dàn ý cho người dùng duyệt"):
                try:
                    result_id = service.generate_outline(
                        request_id,
                        template_document_id=template_map[template_choice],
                        title=title,
                    )
                    st.success(f"Đã tạo dàn ý #{result_id}.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Không thể sinh dàn ý: {exc}")

            outlines = [item for item in service.list_results() if item.get("status") == "pending_outline_review"]
            if outlines:
                result_options = {_result_label(item): int(item["id"]) for item in outlines}
                selected_result = st.selectbox("Dàn ý chờ duyệt", list(result_options.keys()))
                result_id = result_options[selected_result]
                package = service.get_result_package(result_id)
                outline_text = st.text_area("Dàn ý", value=str(package["result"].get("outline_content") or ""), height=260)
                if st.button("Duyệt dàn ý"):
                    try:
                        service.approve_outline(result_id, approved_outline=outline_text)
                        st.success("Đã duyệt dàn ý.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Không thể duyệt dàn ý: {exc}")

    with tab_draft:
        st.subheader("Sinh nội dung sau khi duyệt dàn ý")
        ready = [item for item in service.list_results() if item.get("status") == "outline_approved"]
        if ready:
            options = {_result_label(item): int(item["id"]) for item in ready}
            selected = st.selectbox("Dàn ý đã duyệt", list(options.keys()))
            if st.button("Sinh nội dung dự thảo"):
                try:
                    service.generate_draft(options[selected])
                    st.success("Đã sinh dự thảo cho người dùng review.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Không thể sinh dự thảo: {exc}")
        else:
            st.info("Chưa có dàn ý đã duyệt.")

        drafts = [item for item in service.list_results() if item.get("status") == "pending_user_review"]
        if drafts:
            st.markdown("### Dự thảo cho người dùng review")
            options = {_result_label(item): int(item["id"]) for item in drafts}
            selected = st.selectbox("Dự thảo", list(options.keys()), key="review_ai_draft")
            result_id = options[selected]
            package = service.get_result_package(result_id)
            edited = st.text_area("Nội dung dự thảo", value=str(package["result"].get("draft_content") or ""), height=420)
            note = st.text_input("Ghi chú chỉnh sửa")
            col_save, col_approve = st.columns(2)
            with col_save:
                if st.button("Lưu chỉnh sửa"):
                    try:
                        service.save_user_review(result_id, edited, note=note)
                        st.success("Đã lưu chỉnh sửa.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Không thể lưu: {exc}")
            with col_approve:
                if st.button("Duyệt dự thảo"):
                    try:
                        service.save_user_review(result_id, edited, note=note)
                        service.approve_draft(result_id, note=note)
                        st.success("Đã duyệt dự thảo.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Không thể duyệt: {exc}")
            citations = package["citations"]
            if citations:
                st.markdown("### Citation")
                st.dataframe(pd.DataFrame(citations), use_container_width=True, hide_index=True)

    with tab_export:
        st.subheader("Xuất DOCX sau khi duyệt")
        approved = [item for item in service.list_results() if item.get("status") in {"approved", "exported"}]
        if not approved:
            st.info("Chỉ xuất DOCX khi dự thảo đã được người dùng duyệt.")
        else:
            options = {_result_label(item): int(item["id"]) for item in approved}
            selected = st.selectbox("Dự thảo đã duyệt", list(options.keys()))
            result_id = options[selected]
            result = service.repository.get_result(result_id) or {}
            if result.get("status") == "approved" and st.button("Xuất DOCX"):
                try:
                    output = service.export_docx(result_id)
                    st.success(f"Đã xuất: {output}")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Không thể xuất DOCX: {exc}")
            output_path = Path(str(result.get("output_path") or ""))
            if output_path.exists():
                st.download_button(
                    "Tải DOCX",
                    data=output_path.read_bytes(),
                    file_name=output_path.name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
