from typing import Any
from repositories.base_repository import BaseRepository


class TaskRepository(BaseRepository):
    """Repository xử lý dữ liệu nhiệm vụ, hồ sơ công việc, minh chứng, AI review và audit log."""

    def list_workspaces(self) -> list[dict[str, Any]]:
        return self.fetch_all("SELECT * FROM workspaces ORDER BY updated_at DESC, id DESC")

    def create_workspace(self, data: dict[str, Any]) -> int:
        return self.execute(
            "INSERT INTO workspaces(name, description, field, status) VALUES(:name,:description,:field,:status)", data
        )

    def list_tasks(self, status: str | None = None, staff_id: int | None = None, field: str | None = None, keyword: str | None = None, workspace_id: int | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT t.*, s.full_name AS assigned_to, w.code AS work_code, w.task_name AS work_name, ws.name AS workspace_name
            FROM tasks t
            LEFT JOIN staff s ON s.id=t.assigned_to_id
            LEFT JOIN work_codes w ON w.id=t.work_code_id
            LEFT JOIN workspaces ws ON ws.id=t.workspace_id
            WHERE 1=1
        """
        params: list[Any] = []
        if status and status != "Tất cả":
            query += " AND t.status=?"
            params.append(status)
        if staff_id:
            query += " AND t.assigned_to_id=?"
            params.append(staff_id)
        if field and field != "Tất cả":
            query += " AND t.field=?"
            params.append(field)
        if workspace_id:
            query += " AND t.workspace_id=?"
            params.append(workspace_id)
        if keyword:
            query += " AND (t.title LIKE ? OR t.description LIKE ? OR t.related_document LIKE ? OR ws.name LIKE ?)"
            like = f"%{keyword}%"
            params.extend([like, like, like, like])
        query += " ORDER BY COALESCE(t.deadline,'9999-12-31'), t.id DESC"
        return self.fetch_all(query, tuple(params))

    def get_task(self, task_id: int) -> dict[str, Any] | None:
        return self.fetch_one("""
            SELECT t.*, s.full_name AS assigned_to, w.code AS work_code, w.task_name AS work_name, ws.name AS workspace_name
            FROM tasks t
            LEFT JOIN staff s ON s.id=t.assigned_to_id
            LEFT JOIN work_codes w ON w.id=t.work_code_id
            LEFT JOIN workspaces ws ON ws.id=t.workspace_id
            WHERE t.id=?
        """, (task_id,))

    def create_task(self, data: dict[str, Any]) -> int:
        return self.execute("""
            INSERT INTO tasks(workspace_id, title, description, work_code_id, field, assigned_to_id, deadline, priority, status, progress, related_document, point)
            VALUES(:workspace_id, :title, :description, :work_code_id, :field, :assigned_to_id, :deadline, :priority, :status, :progress, :related_document, :point)
        """, data)

    def update_task(self, task_id: int, data: dict[str, Any]) -> int:
        data = {**data, "id": task_id}
        return self.execute("""
            UPDATE tasks SET workspace_id=:workspace_id, title=:title, description=:description, work_code_id=:work_code_id, field=:field,
                assigned_to_id=:assigned_to_id, deadline=:deadline, priority=:priority, status=:status,
                progress=:progress, related_document=:related_document, updated_at=CURRENT_TIMESTAMP
            WHERE id=:id
        """, data)

    def delete_task(self, task_id: int) -> int:
        return self.execute("DELETE FROM tasks WHERE id=?", (task_id,))

    def add_update(self, task_id: int, content: str, progress: int, evidence_path: str | None, status: str | None = None, actor: str = "Người dùng") -> int:
        next_status = status or ("Hoàn thành" if progress >= 100 else "Đang thực hiện")
        self.execute("""
            UPDATE tasks SET progress=?, status=?, evidence_path=COALESCE(?, evidence_path), updated_at=CURRENT_TIMESTAMP WHERE id=?
        """, (progress, next_status, evidence_path, task_id))
        return self.execute(
            "INSERT INTO task_updates(task_id, content, progress, evidence_path, created_by) VALUES(?,?,?,?,?)",
            (task_id, content, progress, evidence_path, actor),
        )

    def list_updates(self, task_id: int | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT u.*, t.title AS task_title, s.full_name AS assigned_to
            FROM task_updates u
            JOIN tasks t ON t.id=u.task_id
            LEFT JOIN staff s ON s.id=t.assigned_to_id
            WHERE 1=1
        """
        params: list[Any] = []
        if task_id:
            query += " AND u.task_id=?"
            params.append(task_id)
        query += " ORDER BY u.update_date DESC, u.id DESC"
        return self.fetch_all(query, tuple(params))

    def add_task_file(self, task_id: int, file_name: str, file_path: str, file_type: str | None, note: str | None, uploaded_by: str = "Người dùng") -> int:
        return self.execute(
            "INSERT INTO task_files(task_id, file_name, file_path, file_type, note, uploaded_by) VALUES(?,?,?,?,?,?)",
            (task_id, file_name, file_path, file_type, note, uploaded_by),
        )

    def list_task_files(self, task_id: int | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT f.*, t.title AS task_title FROM task_files f
            JOIN tasks t ON t.id=f.task_id WHERE 1=1
        """
        params: list[Any] = []
        if task_id:
            query += " AND f.task_id=?"
            params.append(task_id)
        query += " ORDER BY f.created_at DESC, f.id DESC"
        return self.fetch_all(query, tuple(params))

    def log_action(self, actor: str, action: str, entity_type: str, entity_id: int | None, detail: str | None) -> int:
        return self.execute(
            "INSERT INTO audit_logs(actor, action, entity_type, entity_id, detail) VALUES(?,?,?,?,?)",
            (actor, action, entity_type, entity_id, detail),
        )

    def list_audit_logs(self, limit: int = 200) -> list[dict[str, Any]]:
        return self.fetch_all("SELECT * FROM audit_logs ORDER BY created_at DESC, id DESC LIMIT ?", (limit,))

    def create_ai_suggestion(self, data: dict[str, Any]) -> int:
        return self.execute("""
            INSERT INTO ai_task_reviews(source_file, suggested_title, suggested_description, suggested_work_code, suggested_staff, suggested_deadline, suggested_priority, selected, status)
            VALUES(:source_file,:suggested_title,:suggested_description,:suggested_work_code,:suggested_staff,:suggested_deadline,:suggested_priority,:selected,:status)
        """, data)

    def list_ai_suggestions(self, status: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM ai_task_reviews WHERE 1=1"
        params: list[Any] = []
        if status:
            query += " AND status=?"
            params.append(status)
        query += " ORDER BY created_at DESC, id DESC"
        return self.fetch_all(query, tuple(params))

    def update_ai_suggestion_status(self, review_id: int, status: str) -> int:
        return self.execute("UPDATE ai_task_reviews SET status=? WHERE id=?", (status, review_id))

    def stats(self) -> dict[str, Any]:
        return self.fetch_one("""
            SELECT COUNT(*) total,
            SUM(CASE WHEN status='Chưa thực hiện' THEN 1 ELSE 0 END) pending,
            SUM(CASE WHEN status='Đang thực hiện' THEN 1 ELSE 0 END) doing,
            SUM(CASE WHEN status='Chờ duyệt' THEN 1 ELSE 0 END) waiting,
            SUM(CASE WHEN status='Hoàn thành' THEN 1 ELSE 0 END) done,
            SUM(CASE WHEN deadline < date('now') AND status!='Hoàn thành' THEN 1 ELSE 0 END) overdue,
            SUM(CASE WHEN deadline BETWEEN date('now') AND date('now','+3 day') AND status!='Hoàn thành' THEN 1 ELSE 0 END) due_soon,
            ROUND(AVG(progress),1) avg_progress FROM tasks
        """) or {}

    def kpi_by_staff(self) -> list[dict[str, Any]]:
        return self.fetch_all("""
            SELECT s.full_name, s.position, s.field, s.system_role,
                COUNT(t.id) AS total_tasks,
                SUM(CASE WHEN t.status='Hoàn thành' THEN 1 ELSE 0 END) AS completed_tasks,
                SUM(CASE WHEN t.deadline < date('now') AND t.status!='Hoàn thành' THEN 1 ELSE 0 END) AS overdue_tasks,
                ROUND(SUM(CASE WHEN t.status='Hoàn thành' THEN COALESCE(t.point,0) ELSE 0 END),2) AS completed_points,
                ROUND(SUM(COALESCE(t.point,0)),2) AS assigned_points,
                ROUND(AVG(COALESCE(t.progress,0)),1) AS avg_progress
            FROM staff s LEFT JOIN tasks t ON t.assigned_to_id=s.id
            GROUP BY s.id ORDER BY completed_points DESC, total_tasks DESC, s.full_name
        """)
