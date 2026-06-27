from pathlib import Path
from database.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)

STAFF = [
    ("Nguyễn Trung Hiền", "Trưởng Ban", "Lãnh đạo điều hành", 1, "Trưởng Ban"),
    ("Phạm Duy Tân", "Phó Trưởng Ban", "Tổ chức xây dựng Đảng", 1, "Phó Ban"),
    ("Nguyễn Thị Nhuần", "Phó Trưởng Ban", "Tuyên giáo - Dân vận", 1, "Phó Ban"),
    ("Dương Ngọc Hậu", "Chuyên viên", "Tổ chức - Cán bộ", 1, "Chuyên viên"),
    ("Phạm Quốc Hoài", "Chuyên viên", "Tổ chức Đảng và Đảng viên", 1, "Chuyên viên"),
    ("Võ Thúy Hằng", "Chuyên viên, Thủ quỹ", "Tuyên giáo", 1, "Chuyên viên"),
    ("Châu Hoàng Dũng", "Chuyên viên", "Dân vận, Tổng hợp", 1, "Chuyên viên"),
    ("Nguyễn Thị Thanh Nguyên", "Chuyên viên", "Lịch sử Đảng, Văn thư - Lưu trữ", 1, "Chuyên viên"),
]

WORK_CODES = [
    ("LĐ-01", "LĐ", "Lãnh đạo điều hành", "Chỉ đạo, điều hành công việc chung", "Kết luận/Thông báo/Chương trình", "Thường xuyên", "N5", 5, 1.5),
    ("TC-01", "TC", "Tổ chức", "Tham mưu công tác tổ chức cán bộ", "Tờ trình/Báo cáo/Hồ sơ", "Theo vụ việc", "N4", 4, 1.3),
    ("TC-02", "TC", "Đảng viên", "Theo dõi tổ chức đảng và đảng viên", "Danh sách/Báo cáo/Hồ sơ", "Tháng", "N3", 3, 1.1),
    ("TG-01", "TG", "Tuyên giáo", "Tham mưu tuyên truyền, học tập nghị quyết", "Kế hoạch/Báo cáo/Tin bài", "Tháng", "N3", 3, 1.0),
    ("DV-01", "DV", "Dân vận", "Tham mưu dân vận, dân tộc, tôn giáo", "Báo cáo/Kế hoạch/Mô hình", "Tháng", "N3", 3, 1.0),
    ("PH-01", "PH", "Phối hợp", "Phối hợp báo cáo, chuyển đổi số, tổng hợp", "Báo cáo/Biểu mẫu/Dữ liệu", "Tuần", "N2", 2, 1.0),
    ("DX-01", "DX", "Đột xuất", "Xử lý nhiệm vụ đột xuất theo chỉ đạo", "Sản phẩm theo yêu cầu", "Đột xuất", "N4", 4, 1.2),
]

KPI_RULES = [
    ("Rất phức tạp", "N5", 5, 1.5, "Nhiệm vụ cấp lãnh đạo, tác động rộng"),
    ("Phức tạp", "N4", 4, 1.3, "Có phối hợp nhiều bên"),
    ("Trung bình", "N3", 3, 1.0, "Nhiệm vụ chuyên môn thường xuyên"),
    ("Đơn giản", "N2", 2, 0.8, "Biểu mẫu, tổng hợp ngắn"),
    ("Rất đơn giản", "N1", 1, 0.5, "Theo dõi, cập nhật dữ liệu"),
]


def _columns(conn, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def _safe_alter(conn, table: str, column_sql: str) -> None:
    column_name = column_sql.split()[0]
    if column_name not in _columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_sql}")


def migrate_database() -> None:
    """Bổ sung cột mới khi nâng cấp từ Build 0.2/0.2.1 lên 0.2.2."""
    with get_connection() as conn:
        if "staff" in {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}:
            _safe_alter(conn, "staff", "system_role TEXT DEFAULT 'Chuyên viên'")
        if "tasks" in {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}:
            _safe_alter(conn, "tasks", "workspace_id INTEGER")
        if "task_updates" in {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}:
            _safe_alter(conn, "task_updates", "created_by TEXT DEFAULT 'Người dùng'")


def init_database() -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    with get_connection() as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        migrate_database()
        conn.execute("INSERT OR IGNORE INTO roles(title, unit, scope, note) VALUES(?,?,?,?)", ("Trưởng Ban", "Ban Xây dựng Đảng", "Lãnh đạo, chỉ đạo, duyệt nhiệm vụ", "Vai trò quản trị nghiệp vụ"))
        conn.executemany("INSERT OR IGNORE INTO staff(full_name, position, field, can_receive_task, system_role) VALUES(?,?,?,?,?)", STAFF)
        for full_name, _position, _field, _can, system_role in STAFF:
            conn.execute("UPDATE staff SET system_role=? WHERE full_name=?", (system_role, full_name))
        conn.executemany("INSERT OR IGNORE INTO work_codes(code, axis, group_name, task_name, output_product, frequency, level, point, coefficient) VALUES(?,?,?,?,?,?,?,?,?)", WORK_CODES)
        conn.executemany("INSERT OR IGNORE INTO kpi_rules(name, level, point, coefficient, note) VALUES(?,?,?,?,?)", KPI_RULES)
        conn.execute("INSERT OR IGNORE INTO workspaces(name, description, field, status) VALUES(?,?,?,?)", ("Hồ sơ chung", "Nơi gom các nhiệm vụ chưa phân hồ sơ riêng", "Tổng hợp", "Đang xử lý"))
    logger.info("Database initialized and migrated")

if __name__ == "__main__":
    init_database()
    print("Database initialized successfully")
