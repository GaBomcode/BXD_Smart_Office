from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from services.ai_draft_service import AIDraftService, SUPPORTED_DOCUMENT_TYPES


def _request_label(request: dict[str, Any]) -> str:
    document_type = request.get("selected_document_type") or request.get("detected_document_type") or "chua chon"
    return f'{request["id"]} - {document_type} - {request["status"]}'


def _result_label(result: dict[str, Any]) -> str:
    return f'{result["id"]} - {result["title"]} - {result["status"]}'


def render_ai_draft() -> None:
    st.title("AI Soan thao")
    service = AIDraftService()

    tab_request, tab_sources, tab_outline, tab_draft, tab_export = st.tabs(
        ["Yeu cau", "Mau & can cu", "Dan y", "Du thao", "Duyet & xuat"]
    )

    with tab_request:
        st.subheader("Nhap yeu cau tham muu")
        with st.form("ai_draft_request_form"):
            request_text = st.text_area("Yeu cau soan thao", height=150)
            requested_by = st.text_input("Nguoi yeu cau", value="Nguoi dung")
            submitted = st.form_submit_button("Nhan dien loai van ban")
            if submitted:
                try:
                    request_id = service.create_request(request_text, requested_by=requested_by)
                    st.success(f"Da tao yeu cau AI Draft #{request_id}.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Khong the tao yeu cau: {exc}")

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
                st.markdown("### Can nguoi dung chon lai loai van ban")
                options = {_request_label(item): int(item["id"]) for item in pending}
                selected = st.selectbox("Yeu cau can chon loai", list(options.keys()))
                document_type = st.selectbox("Loai van ban dung", SUPPORTED_DOCUMENT_TYPES)
                if st.button("Xac nhan loai van ban"):
                    try:
                        service.select_document_type(options[selected], document_type)
                        st.success("Da xac nhan loai van ban.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Khong the xac nhan: {exc}")
        else:
            st.info("Chua co yeu cau AI Draft.")

    with tab_sources:
        st.subheader("Chon mau va thu thap can cu")
        requests = [item for item in service.list_requests() if item.get("status") != "needs_document_type_selection"]
        if not requests:
            st.info("Can tao yeu cau va xac nhan loai van ban truoc.")
        else:
            options = {_request_label(item): int(item["id"]) for item in requests}
            selected = st.selectbox("Yeu cau", list(options.keys()), key="source_request")
            request_id = options[selected]
            col_template, col_evidence = st.columns(2)
            with col_template:
                if st.button("Goi y top 5 mau"):
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
                            st.warning("Chua tim thay mau phu hop.")
                    except Exception as exc:
                        st.error(f"Khong the goi y mau: {exc}")
            with col_evidence:
                if st.button("Tim van ban can cu"):
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
                            st.warning("Chua co can cu. He thong se khong khang dinh chac chan trong du thao.")
                    except Exception as exc:
                        st.error(f"Khong the tim can cu: {exc}")

            template_citations = service.repository.list_citations(request_id=request_id, citation_type="template")
            evidence_citations = service.repository.list_citations(request_id=request_id, citation_type="evidence")
            if template_citations:
                st.markdown("### Mau da goi y")
                st.dataframe(pd.DataFrame(template_citations), use_container_width=True, hide_index=True)
            if evidence_citations:
                st.markdown("### Can cu da thu thap")
                st.dataframe(pd.DataFrame(evidence_citations), use_container_width=True, hide_index=True)

    with tab_outline:
        st.subheader("Sinh va duyet dan y")
        requests = [item for item in service.list_requests() if item.get("status") != "needs_document_type_selection"]
        if not requests:
            st.info("Can tao yeu cau truoc.")
        else:
            options = {_request_label(item): int(item["id"]) for item in requests}
            selected = st.selectbox("Yeu cau", list(options.keys()), key="outline_request")
            request_id = options[selected]
            template_rows = service.repository.list_citations(request_id=request_id, citation_type="template")
            template_map = {"Khong chon mau": None}
            for row in template_rows:
                if row.get("source_document_id"):
                    template_map[f'{row["source_document_id"]} - {row.get("title") or "Mau"}'] = int(row["source_document_id"])
            title = st.text_input("Tieu de du thao", value="Du thao van ban", key="outline_title")
            template_choice = st.selectbox("Mau tham chieu", list(template_map.keys()))
            if st.button("Sinh dan y cho nguoi dung duyet"):
                try:
                    result_id = service.generate_outline(
                        request_id,
                        template_document_id=template_map[template_choice],
                        title=title,
                    )
                    st.success(f"Da tao dan y #{result_id}.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Khong the sinh dan y: {exc}")

            outlines = [item for item in service.list_results() if item.get("status") == "pending_outline_review"]
            if outlines:
                result_options = {_result_label(item): int(item["id"]) for item in outlines}
                selected_result = st.selectbox("Dan y cho duyet", list(result_options.keys()))
                result_id = result_options[selected_result]
                package = service.get_result_package(result_id)
                outline_text = st.text_area("Dan y", value=str(package["result"].get("outline_content") or ""), height=260)
                if st.button("Duyet dan y"):
                    try:
                        service.approve_outline(result_id, approved_outline=outline_text)
                        st.success("Da duyet dan y.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Khong the duyet dan y: {exc}")

    with tab_draft:
        st.subheader("Sinh noi dung sau khi duyet dan y")
        ready = [item for item in service.list_results() if item.get("status") == "outline_approved"]
        if ready:
            options = {_result_label(item): int(item["id"]) for item in ready}
            selected = st.selectbox("Dan y da duyet", list(options.keys()))
            if st.button("Sinh noi dung du thao"):
                try:
                    service.generate_draft(options[selected])
                    st.success("Da sinh du thao cho nguoi dung review.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Khong the sinh du thao: {exc}")
        else:
            st.info("Chua co dan y da duyet.")

        drafts = [item for item in service.list_results() if item.get("status") == "pending_user_review"]
        if drafts:
            st.markdown("### Du thao cho nguoi dung review")
            options = {_result_label(item): int(item["id"]) for item in drafts}
            selected = st.selectbox("Du thao", list(options.keys()), key="review_ai_draft")
            result_id = options[selected]
            package = service.get_result_package(result_id)
            edited = st.text_area("Noi dung du thao", value=str(package["result"].get("draft_content") or ""), height=420)
            note = st.text_input("Ghi chu chinh sua")
            col_save, col_approve = st.columns(2)
            with col_save:
                if st.button("Luu chinh sua"):
                    try:
                        service.save_user_review(result_id, edited, note=note)
                        st.success("Da luu chinh sua.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Khong the luu: {exc}")
            with col_approve:
                if st.button("Duyet du thao"):
                    try:
                        service.save_user_review(result_id, edited, note=note)
                        service.approve_draft(result_id, note=note)
                        st.success("Da duyet du thao.")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Khong the duyet: {exc}")
            citations = package["citations"]
            if citations:
                st.markdown("### Citation")
                st.dataframe(pd.DataFrame(citations), use_container_width=True, hide_index=True)

    with tab_export:
        st.subheader("Xuat DOCX sau khi duyet")
        approved = [item for item in service.list_results() if item.get("status") in {"approved", "exported"}]
        if not approved:
            st.info("Chi xuat DOCX khi du thao da duoc nguoi dung duyet.")
        else:
            options = {_result_label(item): int(item["id"]) for item in approved}
            selected = st.selectbox("Du thao da duyet", list(options.keys()))
            result_id = options[selected]
            result = service.repository.get_result(result_id) or {}
            if result.get("status") == "approved" and st.button("Xuat DOCX"):
                try:
                    output = service.export_docx(result_id)
                    st.success(f"Da xuat: {output}")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Khong the xuat DOCX: {exc}")
            output_path = Path(str(result.get("output_path") or ""))
            if output_path.exists():
                st.download_button(
                    "Tai DOCX",
                    data=output_path.read_bytes(),
                    file_name=output_path.name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
