from datetime import date
import pandas as pd
import streamlit as st
from services.profile_service import ProfileService
from services.task_service import TaskService

STATUSES = ["Chưa thực hiện", "Đang thực hiện", "Chờ duyệt", "Hoàn thành", "Tạm dừng"]
PRIORITIES = ["Thấp", "Bình thường", "Cao", "Khẩn"]


def _task_dataframe(tasks: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(tasks)
    if df.empty:
        return df
    columns = ["id", "workspace_name", "title", "work_code", "field", "assigned_to", "deadline", "priority", "status", "progress", "point"]
    return df[[col for col in columns if col in df.columns]]


def _maps(profile: ProfileService, task_service: TaskService) -> tuple[dict, dict, dict, dict]:
    staff = profile.get_staff()
    codes = profile.get_work_codes()
    workspaces = task_service.list_workspaces()
    staff_map = {s["full_name"]: s["id"] for s in staff}
    code_map = {f'{c["code"]} - {c["task_name"]}': c for c in codes}
    workspace_map = {w["name"]: w["id"] for w in workspaces}
    return staff_map, code_map, workspace_map, {s["id"]: s["full_name"] for s in staff}


def _task_form(profile: ProfileService, task_service: TaskService, task: dict | None = None) -> None:
    staff_map, code_map, workspace_map, id_to_staff = _maps(profile, task_service)
    codes = profile.get_work_codes()
    id_to_code_label = {c["id"]: f'{c["code"]} - {c["task_name"]}' for c in codes}
    id_to_workspace = {v: k for k, v in workspace_map.items()}

    is_edit = task is not None
    with st.form(f"task_form_{task['id']}" if is_edit else "create_task"):
        title = st.text_input("Tên nhiệm vụ", value=(task or {}).get("title", ""))
        description = st.text_area("Nội dung / yêu cầu xử lý", value=(task or {}).get("description", ""))
        workspace_names = list(workspace_map.keys()) or ["Hồ sơ chung"]
        current_workspace = id_to_workspace.get((task or {}).get("workspace_id"), workspace_names[0])
        workspace_name = st.selectbox("Hồ sơ công việc", workspace_names, index=workspace_names.index(current_workspace))
        current_code_label = id_to_code_label.get((task or {}).get("work_code_id"), list(code_map.keys())[0])
        code_label = st.selectbox("Mã việc", list(code_map.keys()), index=list(code_map.keys()).index(current_code_label))
        current_staff = id_to_staff.get((task or {}).get("assigned_to_id"), list(staff_map.keys())[0])
        assigned_name = st.selectbox("Người phụ trách", list(staff_map.keys()), index=list(staff_map.keys()).index(current_staff))
        current_deadline = date.fromisoformat(task["deadline"]) if task and task.get("deadline") else date.today()
        deadline = st.date_input("Hạn xử lý", value=current_deadline)
        priority = st.selectbox("Mức độ ưu tiên", PRIORITIES, index=PRIORITIES.index((task or {}).get("priority", "Bình thường")))
        status = st.selectbox("Trạng thái", STATUSES, index=STATUSES.index((task or {}).get("status", "Chưa thực hiện")))
        progress = st.slider("Tiến độ %", 0, 100, int((task or {}).get("progress", 0)))
        related_document = st.text_input("Tài liệu liên quan / nguồn giao việc", value=(task or {}).get("related_document", ""))
        submitted = st.form_submit_button("Cập nhật nhiệm vụ" if is_edit else "Ghi nhiệm vụ")
        if submitted:
            selected_code = code_map[code_label]
            data = {
                "workspace_id": workspace_map.get(workspace_name),
                "title": title,
                "description": description,
                "work_code_id": selected_code["id"],
                "field": selected_code.get("group_name"),
                "assigned_to_id": staff_map[assigned_name],
                "deadline": deadline.isoformat() if deadline else None,
                "priority": priority,
                "status": status,
                "progress": progress,
                "related_document": related_document,
                "point": float(selected_code.get("point") or 0) * float(selected_code.get("coefficient") or 1),
            }
            try:
                if is_edit:
                    task_service.update_task(int(task["id"]), data)
                    st.success("Đã cập nhật nhiệm vụ.")
                else:
                    task_service.create_task(data)
                    st.success("Đã ghi nhiệm vụ.")
                st.rerun()
            except Exception as exc:
                st.error(f"Không thể lưu nhiệm vụ: {exc}")


def render_tasks() -> None:
    st.title("Phân hệ 1 - Quản lý nhiệm vụ")
    profile = ProfileService()
    task_service = TaskService()
    staff = profile.get_staff()
    staff_map = {s["full_name"]: s["id"] for s in staff}

    stats = task_service.get_stats()
    cols = st.columns(6)
    cols[0].metric("Tổng nhiệm vụ", int(stats.get("total") or 0))
    cols[1].metric("Đang làm", int(stats.get("doing") or 0))
    cols[2].metric("Chờ duyệt", int(stats.get("waiting") or 0))
    cols[3].metric("Sắp hạn", int(stats.get("due_soon") or 0))
    cols[4].metric("Quá hạn", int(stats.get("overdue") or 0))
    cols[5].metric("Hoàn thành", int(stats.get("done") or 0))

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Danh sách", "Thêm/Sửa", "Tiến độ & timeline", "Minh chứng", "Hồ sơ công việc", "AI Review", "KPI & Audit"
    ])

    with tab1:
        filter_cols = st.columns(5)
        status_filter = filter_cols[0].selectbox("Trạng thái", ["Tất cả"] + STATUSES)
        staff_filter_name = filter_cols[1].selectbox("Người phụ trách", ["Tất cả"] + list(staff_map.keys()))
        field_filter = filter_cols[2].selectbox("Lĩnh vực", ["Tất cả"] + sorted({s.get("field") or "" for s in staff if s.get("field")}))
        workspaces = task_service.list_workspaces()
        workspace_map = {w["name"]: w["id"] for w in workspaces}
        workspace_filter = filter_cols[3].selectbox("Hồ sơ", ["Tất cả"] + list(workspace_map.keys()))
        keyword = filter_cols[4].text_input("Tìm nhanh")
        staff_id = None if staff_filter_name == "Tất cả" else staff_map[staff_filter_name]
        workspace_id = None if workspace_filter == "Tất cả" else workspace_map[workspace_filter]
        tasks = task_service.list_tasks(status_filter, staff_id, field_filter, keyword, workspace_id)
        df = _task_dataframe(tasks)
        if not df.empty:
            st.dataframe(df, use_container_width=True, hide_index=True)
            if st.button("Xuất Excel gồm nhiệm vụ + KPI + timeline + minh chứng + audit"):
                path = task_service.export_excel(tasks)
                st.success(f"Đã xuất: {path}")
        else:
            st.info("Chưa có nhiệm vụ phù hợp bộ lọc.")

    with tab2:
        st.subheader("Thêm nhiệm vụ")
        _task_form(profile, task_service)
        st.divider()
        tasks = task_service.list_tasks()
        if tasks:
            task_map = {f'{t["id"]} - {t["title"]}': t for t in tasks}
            selected_label = st.selectbox("Chọn nhiệm vụ cần sửa/xóa", list(task_map.keys()))
            selected_task = task_map[selected_label]
            _task_form(profile, task_service, selected_task)
            if st.button("Xóa nhiệm vụ này", type="primary"):
                task_service.delete_task(int(selected_task["id"]))
                st.success("Đã xóa nhiệm vụ.")
                st.rerun()

    with tab3:
        tasks = task_service.list_tasks()
        if not tasks:
            st.info("Chưa có nhiệm vụ để cập nhật.")
        else:
            task_label_map = {f'{t["id"]} - {t["title"]}': t["id"] for t in tasks}
            with st.form("progress_update"):
                task_label = st.selectbox("Chọn nhiệm vụ", list(task_label_map.keys()))
                content = st.text_area("Nội dung cập nhật")
                progress = st.slider("Tiến độ %", 0, 100, 0)
                status = st.selectbox("Trạng thái sau cập nhật", STATUSES, index=STATUSES.index("Đang thực hiện"))
                actor = st.selectbox("Người cập nhật", list(staff_map.keys()))
                evidence = st.file_uploader("File minh chứng kèm cập nhật", type=["pdf", "docx", "xlsx", "png", "jpg", "jpeg"])
                ok = st.form_submit_button("Lưu cập nhật")
                if ok:
                    path = None
                    if evidence:
                        task_service.add_task_file(task_label_map[task_label], evidence.name, evidence.getvalue(), "Minh chứng cập nhật", actor)
                        path = evidence.name
                    task_service.add_progress_update(task_label_map[task_label], content, progress, path, status, actor)
                    st.success("Đã cập nhật tiến độ.")
                    st.rerun()
            st.subheader("Timeline")
            updates = pd.DataFrame(task_service.list_updates())
            if not updates.empty:
                st.dataframe(updates, use_container_width=True, hide_index=True)

    with tab4:
        tasks = task_service.list_tasks()
        if not tasks:
            st.info("Chưa có nhiệm vụ.")
        else:
            task_label_map = {f'{t["id"]} - {t["title"]}': t["id"] for t in tasks}
            selected = st.selectbox("Chọn nhiệm vụ để upload nhiều file", list(task_label_map.keys()))
            files = st.file_uploader("Upload nhiều file minh chứng", accept_multiple_files=True)
            note = st.text_input("Ghi chú file")
            if st.button("Lưu các file minh chứng"):
                for file in files:
                    task_service.add_task_file(task_label_map[selected], file.name, file.getvalue(), note)
                st.success(f"Đã lưu {len(files)} file.")
                st.rerun()
            df_files = pd.DataFrame(task_service.list_task_files(task_label_map[selected]))
            if not df_files.empty:
                st.dataframe(df_files, use_container_width=True, hide_index=True)

    with tab5:
        st.subheader("Tạo hồ sơ công việc")
        with st.form("workspace_form"):
            name = st.text_input("Tên hồ sơ")
            description = st.text_area("Mô tả")
            field = st.text_input("Lĩnh vực")
            status = st.selectbox("Trạng thái", ["Đang xử lý", "Hoàn thành", "Tạm dừng"])
            if st.form_submit_button("Lưu hồ sơ"):
                task_service.create_workspace({"name": name, "description": description, "field": field, "status": status})
                st.success("Đã tạo hồ sơ công việc.")
                st.rerun()
        st.dataframe(pd.DataFrame(task_service.list_workspaces()), use_container_width=True, hide_index=True)

    with tab6:
        st.info("Build 0.2.2 tạo luồng AI Review dạng offline: AI/Người dùng nhập đề xuất, kiểm tra, chỉnh sửa rồi mới ghi thành nhiệm vụ.")
        codes = profile.get_work_codes()
        code_values = [c["code"] for c in codes]
        with st.form("ai_review_form"):
            source_file = st.text_input("Nguồn văn bản / file")
            title = st.text_input("AI gợi ý nhiệm vụ")
            description = st.text_area("AI gợi ý nội dung")
            work_code = st.selectbox("AI gợi ý mã việc", code_values)
            staff_name = st.selectbox("AI gợi ý người phụ trách", list(staff_map.keys()))
            deadline = st.date_input("AI gợi ý deadline", value=date.today())
            priority = st.selectbox("AI gợi ý ưu tiên", PRIORITIES)
            if st.form_submit_button("Lưu vào danh sách chờ duyệt"):
                task_service.create_manual_ai_suggestion(source_file, title, description, work_code, staff_name, deadline.isoformat(), priority)
                st.success("Đã lưu đề xuất. Chưa ghi vào nhiệm vụ chính thức.")
                st.rerun()
        suggestions = task_service.list_ai_suggestions("Chờ duyệt")
        if suggestions:
            st.subheader("Danh sách chờ duyệt")
            st.dataframe(pd.DataFrame(suggestions), use_container_width=True, hide_index=True)
            selected = st.selectbox("Chọn đề xuất để ghi nhiệm vụ", [f'{x["id"]} - {x["suggested_title"]}' for x in suggestions])
            review = next(x for x in suggestions if selected.startswith(str(x["id"]) + " - "))
            if st.button("Duyệt và ghi thành nhiệm vụ"):
                code = next(c for c in codes if c["code"] == review["suggested_work_code"])
                task_service.create_task({
                    "workspace_id": task_service.list_workspaces()[0]["id"] if task_service.list_workspaces() else None,
                    "title": review["suggested_title"],
                    "description": review["suggested_description"],
                    "work_code_id": code["id"],
                    "field": code.get("group_name"),
                    "assigned_to_id": staff_map[review["suggested_staff"]],
                    "deadline": review["suggested_deadline"],
                    "priority": review["suggested_priority"],
                    "status": "Chưa thực hiện",
                    "progress": 0,
                    "related_document": review["source_file"],
                    "point": float(code.get("point") or 0) * float(code.get("coefficient") or 1),
                })
                task_service.mark_ai_suggestion(int(review["id"]), "Đã ghi nhiệm vụ")
                st.success("Đã duyệt và ghi nhiệm vụ.")
                st.rerun()

    with tab7:
        st.subheader("KPI theo nhân sự")
        st.dataframe(pd.DataFrame(task_service.get_kpi_by_staff()), use_container_width=True, hide_index=True)
        st.subheader("Nhật ký hệ thống / Audit Log")
        logs = pd.DataFrame(task_service.list_audit_logs())
        if not logs.empty:
            st.dataframe(logs, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có nhật ký thao tác.")
