from pathlib import Path
from typing import Any
import pandas as pd
from core.config import EXPORT_DIR, UPLOAD_DIR
from core.logger import get_logger
from repositories.task_repository import TaskRepository

logger = get_logger(__name__)


class TaskService:
    """Service nghiệp vụ quản lý nhiệm vụ Build 0.2.2."""

    def __init__(self) -> None:
        self.repo = TaskRepository()

    def list_workspaces(self) -> list[dict[str, Any]]:
        return self.repo.list_workspaces()

    def create_workspace(self, data: dict[str, Any]) -> int:
        if not data.get("name"):
            raise ValueError("Tên hồ sơ không được để trống")
        workspace_id = self.repo.create_workspace(data)
        self.repo.log_action("Nguyễn Trung Hiền", "Tạo hồ sơ công việc", "workspace", workspace_id, data.get("name"))
        return workspace_id

    def list_tasks(self, status: str | None = None, staff_id: int | None = None, field: str | None = None, keyword: str | None = None, workspace_id: int | None = None) -> list[dict[str, Any]]:
        return self.repo.list_tasks(status, staff_id, field, keyword, workspace_id)

    def get_task(self, task_id: int) -> dict[str, Any] | None:
        return self.repo.get_task(task_id)

    def create_task(self, data: dict[str, Any], actor: str = "Nguyễn Trung Hiền") -> int:
        if not data.get("title"):
            raise ValueError("Tên nhiệm vụ không được để trống")
        task_id = self.repo.create_task(data)
        self.repo.log_action(actor, "Tạo nhiệm vụ", "task", task_id, data.get("title"))
        logger.info("Create task id=%s title=%s", task_id, data.get("title"))
        return task_id

    def update_task(self, task_id: int, data: dict[str, Any], actor: str = "Nguyễn Trung Hiền") -> int:
        if not data.get("title"):
            raise ValueError("Tên nhiệm vụ không được để trống")
        result = self.repo.update_task(task_id, data)
        self.repo.log_action(actor, "Cập nhật nhiệm vụ", "task", task_id, data.get("title"))
        return result

    def delete_task(self, task_id: int, actor: str = "Nguyễn Trung Hiền") -> int:
        result = self.repo.delete_task(task_id)
        self.repo.log_action(actor, "Xóa nhiệm vụ", "task", task_id, f"task_id={task_id}")
        return result

    def add_progress_update(self, task_id: int, content: str, progress: int, evidence_path: str | None, status: str | None = None, actor: str = "Người dùng") -> int:
        if not content.strip():
            raise ValueError("Nội dung cập nhật không được để trống")
        if progress < 0 or progress > 100:
            raise ValueError("Tiến độ phải từ 0 đến 100")
        update_id = self.repo.add_update(task_id, content, progress, evidence_path, status, actor)
        self.repo.log_action(actor, "Cập nhật tiến độ", "task", task_id, f"{progress}% - {content[:120]}")
        return update_id

    def list_updates(self, task_id: int | None = None) -> list[dict[str, Any]]:
        return self.repo.list_updates(task_id)

    def add_task_file(self, task_id: int, file_name: str, content: bytes, note: str | None = None, actor: str = "Người dùng") -> int:
        task_dir = UPLOAD_DIR / f"task_{task_id}"
        task_dir.mkdir(parents=True, exist_ok=True)
        safe_name = Path(file_name).name
        target = task_dir / safe_name
        target.write_bytes(content)
        file_id = self.repo.add_task_file(task_id, safe_name, str(target), target.suffix.lower(), note, actor)
        self.repo.log_action(actor, "Tải minh chứng", "task_file", file_id, safe_name)
        return file_id

    def list_task_files(self, task_id: int | None = None) -> list[dict[str, Any]]:
        return self.repo.list_task_files(task_id)

    def list_audit_logs(self) -> list[dict[str, Any]]:
        return self.repo.list_audit_logs()

    def get_stats(self) -> dict[str, Any]:
        return self.repo.stats()

    def get_kpi_by_staff(self) -> list[dict[str, Any]]:
        return self.repo.kpi_by_staff()

    def create_manual_ai_suggestion(self, source_file: str, title: str, description: str, work_code: str, staff: str, deadline: str | None, priority: str) -> int:
        """Tạo đề xuất AI giả lập/offline để người dùng duyệt trước khi ghi dữ liệu."""
        data = {
            "source_file": source_file,
            "suggested_title": title,
            "suggested_description": description,
            "suggested_work_code": work_code,
            "suggested_staff": staff,
            "suggested_deadline": deadline,
            "suggested_priority": priority,
            "selected": 1,
            "status": "Chờ duyệt",
        }
        review_id = self.repo.create_ai_suggestion(data)
        self.repo.log_action("AI Offline", "Sinh đề xuất nhiệm vụ", "ai_task_review", review_id, title)
        return review_id

    def list_ai_suggestions(self, status: str | None = "Chờ duyệt") -> list[dict[str, Any]]:
        return self.repo.list_ai_suggestions(status)

    def mark_ai_suggestion(self, review_id: int, status: str) -> int:
        return self.repo.update_ai_suggestion_status(review_id, status)

    def export_excel(self, tasks: list[dict[str, Any]], file_name: str = "danh_sach_nhiem_vu_build_0_2_2.xlsx") -> Path:
        output = EXPORT_DIR / file_name
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            pd.DataFrame(tasks).to_excel(writer, index=False, sheet_name="Danh sách nhiệm vụ")
            pd.DataFrame(self.get_kpi_by_staff()).to_excel(writer, index=False, sheet_name="KPI nhân sự")
            pd.DataFrame(self.list_updates()).to_excel(writer, index=False, sheet_name="Timeline")
            pd.DataFrame(self.list_task_files()).to_excel(writer, index=False, sheet_name="Minh chứng")
            pd.DataFrame(self.list_audit_logs()).to_excel(writer, index=False, sheet_name="Audit Log")
        return output
