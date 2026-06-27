from database.init_db import init_database
from services.profile_service import ProfileService
from services.task_service import TaskService


def test_build_0_2_2_workspace_and_audit() -> None:
    init_database()
    service = TaskService()
    workspace_id = service.create_workspace({"name": "TEST Hồ sơ 0.2.2", "description": "Test", "field": "Tổng hợp", "status": "Đang xử lý"})
    assert workspace_id > 0
    assert any(w["name"] == "TEST Hồ sơ 0.2.2" for w in service.list_workspaces())
    assert len(service.list_audit_logs()) >= 1


def test_build_0_2_2_task_files_and_ai_review() -> None:
    init_database()
    profile = ProfileService()
    service = TaskService()
    staff = profile.get_staff()[0]
    code = profile.get_work_codes()[0]
    workspace = service.list_workspaces()[0]
    task_id = service.create_task({
        "workspace_id": workspace["id"],
        "title": "TEST nhiệm vụ 0.2.2",
        "description": "Nội dung test",
        "work_code_id": code["id"],
        "field": code["group_name"],
        "assigned_to_id": staff["id"],
        "deadline": "2026-06-30",
        "priority": "Bình thường",
        "status": "Chưa thực hiện",
        "progress": 0,
        "related_document": "test.docx",
        "point": 1,
    })
    service.add_task_file(task_id, "minh_chung.txt", b"ok", "test")
    assert len(service.list_task_files(task_id)) >= 1
    review_id = service.create_manual_ai_suggestion("cv.pdf", "TEST AI Review", "Mô tả", code["code"], staff["full_name"], "2026-06-30", "Cao")
    assert review_id > 0
    assert len(service.list_ai_suggestions("Chờ duyệt")) >= 1
