from __future__ import annotations

import pandas as pd
import streamlit as st

from services.document_library_service import DocumentLibraryService


def _scan_rows(scan: dict) -> list[dict[str, object]]:
    """Build readable scan rows without exposing raw JSON."""
    return [
        {
            "TÃªn file": file.get("file_name"),
            "Loáº¡i": file.get("file_ext"),
            "KÃ­ch thÆ°á»›c": file.get("file_size"),
            "Tráº¡ng thÃ¡i": file.get("state"),
        }
        for file in scan.get("files", [])
    ]


def _document_detail_rows(document: dict) -> list[dict[str, object]]:
    """Build readable document detail rows."""
    fields = {
        "TiÃªu Ä‘á»": "title",
        "Sá»‘ vÄƒn báº£n": "document_number",
        "Loáº¡i vÄƒn báº£n": "document_type",
        "NgÃ y ban hÃ nh": "issued_date",
        "CÆ¡ quan ban hÃ nh": "issuing_agency",
        "NgÆ°á»i kÃ½": "signer",
        "TrÃ­ch yáº¿u": "summary",
        "Tá»« khÃ³a": "keywords",
        "Tráº¡ng thÃ¡i": "status",
        "ÄÆ°á»ng dáº«n": "file_path",
    }
    return [{"ThÃ´ng tin": label, "GiÃ¡ trá»‹": document.get(key) or ""} for label, key in fields.items()]


def render_document_library() -> None:
    """Giao diện Kho văn bản Sprint 4."""
    st.title("Phân hệ 3 - Kho văn bản")
    service = DocumentLibraryService()

    tab_scan, tab_list, tab_review = st.tabs(["Quét thư mục", "Danh sách văn bản", "Cần duyệt"])

    with tab_scan:
        st.subheader("Quét chỉ mục kho văn bản")
        root_path = st.text_input("Đường dẫn thư mục nguồn")
        if st.button("Quét & index thư mục"):
            try:
                result = service.index_folder(root_path)
                st.success("Đã quét và cập nhật chỉ mục.")
                counts = result["counts"]
                cols = st.columns(6)
                cols[0].metric("Đã index", counts.get("need_review", 0) + counts.get("indexed", 0))
                cols[1].metric("Đã có", counts.get("existing", 0))
                cols[2].metric("Trùng", counts.get("duplicate", 0))
                cols[3].metric("Cần OCR", counts.get("need_ocr", 0))
                cols[4].metric("Không hỗ trợ", counts.get("unsupported", 0))
                cols[5].metric("Lỗi", counts.get("failed", 0))
                rows = _scan_rows(result["scan"])
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            except Exception as exc:
                st.error(f"Không thể quét thư mục: {exc}")

    with tab_list:
        st.subheader("Danh sách văn bản")
        filters = service.filter_values()
        cols = st.columns(6)
        file_ext = cols[0].selectbox("Loại file", [""] + filters["file_ext"])
        document_type = cols[1].selectbox("Loại văn bản", [""] + filters["document_type"])
        status = cols[2].selectbox("Trạng thái", [""] + filters["status"])
        field = cols[3].selectbox("Lĩnh vực", [""] + filters["field"])
        issuing_agency = cols[4].selectbox("Cơ quan", [""] + filters["issuing_agency"])
        year = cols[5].text_input("Năm")
        keyword = st.text_input("Tìm nhanh theo tên file, số văn bản, từ khóa")
        documents = service.list_documents(
            file_ext=file_ext or None,
            document_type=document_type or None,
            status=status or None,
            field=field or None,
            issuing_agency=issuing_agency or None,
            year=year or None,
            keyword=keyword or None,
        )
        if documents:
            st.dataframe(pd.DataFrame(documents), use_container_width=True, hide_index=True)
            detail_map = {f'{doc["id"]} - {doc["title"]}': doc for doc in documents}
            selected_detail = st.selectbox("Xem chi tiết", list(detail_map.keys()))
            st.dataframe(
                pd.DataFrame(_document_detail_rows(detail_map[selected_detail])),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Chưa có văn bản phù hợp.")

    with tab_review:
        st.subheader("Văn bản cần duyệt metadata")
        review_status = st.selectbox("Nhóm cần xử lý", ["need_review", "need_ocr", "failed", "unsupported", "duplicate"])
        review_docs = service.list_documents(status=review_status)
        if not review_docs:
            st.info("Không có văn bản trong nhóm này.")
        else:
            doc_map = {f'{doc["id"]} - {doc["title"]}': doc for doc in review_docs}
            selected = st.selectbox("Chọn văn bản", list(doc_map.keys()))
            doc = doc_map[selected]
            with st.form("review_document_metadata"):
                title = st.text_input("Tiêu đề", value=doc.get("title") or "")
                document_number = st.text_input("Số ký hiệu", value=doc.get("document_number") or "")
                issued_date = st.text_input("Ngày văn bản", value=doc.get("issued_date") or "")
                issuing_agency = st.text_input("Cơ quan ban hành", value=doc.get("issuing_agency") or "")
                document_type = st.text_input("Loại văn bản", value=doc.get("document_type") or "")
                summary = st.text_area("Trích yếu", value=doc.get("summary") or "")
                keywords = st.text_input("Từ khóa", value=doc.get("keywords") or "")
                field = st.text_input("Lĩnh vực", value=doc.get("field") or "")
                signer = st.text_input("Người ký", value=doc.get("signer") or "")
                if st.form_submit_button("Lưu duyệt"):
                    service.update_review_metadata(
                        int(doc["id"]),
                        {
                            "title": title,
                            "document_number": document_number,
                            "issued_date": issued_date,
                            "issuing_agency": issuing_agency,
                            "document_type": document_type,
                            "summary": summary,
                            "keywords": keywords,
                            "field": field,
                            "signer": signer,
                            "status": "indexed",
                        },
                    )
                    st.success("Đã lưu metadata văn bản.")
                    st.rerun()
