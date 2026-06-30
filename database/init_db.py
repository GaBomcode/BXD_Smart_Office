from pathlib import Path
import sqlite3

from database.connection import get_connection
from core.logger import get_logger

logger = get_logger(__name__)

REQUIRED_SCHEMA: dict[str, set[str]] = {
    "documents": {"id", "title", "file_name", "file_path", "checksum", "status"},
    "document_keywords": {"id", "document_id", "keyword", "weight"},
    "ai_draft_requests": {"id", "request_text", "status"},
    "ai_draft_results": {"id", "request_id", "title", "draft_content", "status"},
    "ai_draft_citations": {"id", "request_id", "result_id", "source_document_id"},
    "knowledge_documents": {
        "id",
        "document_id",
        "title",
        "full_text",
        "checksum",
        "status",
    },
    "knowledge_chunks": {"id", "document_id", "text", "chunk_order"},
    "knowledge_embeddings": {
        "id",
        "chunk_id",
        "document_id",
        "vector_json",
        "status",
    },
    "knowledge_vector_index": {
        "id",
        "embedding_id",
        "chunk_id",
        "document_id",
        "is_active",
    },
    "knowledge_citation_metadata": {
        "id",
        "query_text",
        "source_knowledge_document_id",
    },
    "advisory_reports": {
        "id",
        "report_type",
        "title",
        "request_json",
        "result_json",
        "status",
    },
    "schema_migrations": {"id", "version", "name", "applied_at"},
}

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


def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})").fetchall()}


def _safe_alter(conn: sqlite3.Connection, table: str, column_sql: str) -> None:
    column_name = column_sql.split()[0]
    if column_name not in _columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column_sql}")


def migrate_database() -> None:
    """Bổ sung các cột tương thích khi nâng cấp database qua các build."""
    with get_connection() as conn:
        if "staff" in {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}:
            _safe_alter(conn, "staff", "system_role TEXT DEFAULT 'Chuyên viên'")
        if "tasks" in {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}:
            _safe_alter(conn, "tasks", "workspace_id INTEGER")
        if "task_updates" in {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}:
            _safe_alter(conn, "task_updates", "created_by TEXT DEFAULT 'Người dùng'")




def _existing_migrations(conn: sqlite3.Connection) -> set[str]:
    """Lấy danh sách migration đã được ghi nhận."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            applied_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    return {row[0] for row in conn.execute("SELECT version FROM schema_migrations").fetchall()}


def run_sql_migrations(conn: sqlite3.Connection) -> None:
    """Chạy các migration SQL idempotent trong database/migrations."""
    migrations_dir = Path(__file__).with_name("migrations")
    if not migrations_dir.exists():
        return
    applied = _existing_migrations(conn)
    for path in sorted(migrations_dir.glob("*.sql")):
        version = path.stem
        if version in applied:
            continue
        tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
        if "knowledge_documents" in tables:
            _safe_alter(conn, "knowledge_documents", "document_id INTEGER")
            _safe_alter(conn, "knowledge_documents", "full_text TEXT")
            _safe_alter(conn, "knowledge_documents", "checksum TEXT")
            _safe_alter(conn, "knowledge_documents", "chunk_count INTEGER NOT NULL DEFAULT 0")
            _safe_alter(conn, "knowledge_documents", "embedding_version TEXT")
            _safe_alter(conn, "knowledge_documents", "indexed_time TEXT")
        conn.executescript(path.read_text(encoding="utf-8"))
        conn.execute(
            "INSERT OR IGNORE INTO schema_migrations(version, name) VALUES(?, ?)",
            (version, path.name),
        )
        logger.info("Applied migration %s", path.name)
    tables = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    if "knowledge_documents" in tables:
        _safe_alter(conn, "knowledge_documents", "document_id INTEGER")
        _safe_alter(conn, "knowledge_documents", "full_text TEXT")
        _safe_alter(conn, "knowledge_documents", "checksum TEXT")
        _safe_alter(conn, "knowledge_documents", "chunk_count INTEGER NOT NULL DEFAULT 0")
        _safe_alter(conn, "knowledge_documents", "embedding_version TEXT")
        _safe_alter(conn, "knowledge_documents", "indexed_time TEXT")


def validate_schema(conn: sqlite3.Connection) -> None:
    """Validate V1.0 critical tables and columns after migrations."""
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    missing_tables = sorted(set(REQUIRED_SCHEMA).difference(tables))
    if missing_tables:
        raise RuntimeError("Missing required table(s): " + ", ".join(missing_tables))
    missing_columns: list[str] = []
    for table, required_columns in REQUIRED_SCHEMA.items():
        existing_columns = _columns(conn, table)
        for column in sorted(required_columns.difference(existing_columns)):
            missing_columns.append(f"{table}.{column}")
    if missing_columns:
        raise RuntimeError("Missing required column(s): " + ", ".join(missing_columns))


def init_database() -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    with get_connection() as conn:
        conn.executescript(schema_path.read_text(encoding="utf-8"))
        migrate_database()
        run_sql_migrations(conn)
        conn.execute("INSERT OR IGNORE INTO roles(title, unit, scope, note) VALUES(?,?,?,?)", ("Trưởng Ban", "Ban Xây dựng Đảng", "Lãnh đạo, chỉ đạo, duyệt nhiệm vụ", "Vai trò quản trị nghiệp vụ"))
        conn.executemany("INSERT OR IGNORE INTO staff(full_name, position, field, can_receive_task, system_role) VALUES(?,?,?,?,?)", STAFF)
        for full_name, _position, _field, _can, system_role in STAFF:
            conn.execute("UPDATE staff SET system_role=? WHERE full_name=?", (system_role, full_name))
        conn.executemany("INSERT OR IGNORE INTO work_codes(code, axis, group_name, task_name, output_product, frequency, level, point, coefficient) VALUES(?,?,?,?,?,?,?,?,?)", WORK_CODES)
        conn.executemany("INSERT OR IGNORE INTO kpi_rules(name, level, point, coefficient, note) VALUES(?,?,?,?,?)", KPI_RULES)
        conn.execute("INSERT OR IGNORE INTO workspaces(name, description, field, status) VALUES(?,?,?,?)", ("Hồ sơ chung", "Nơi gom các nhiệm vụ chưa phân hồ sơ riêng", "Tổng hợp", "Đang xử lý"))
        validate_schema(conn)
    logger.info("Database initialized and migrated")

if __name__ == "__main__":
    init_database()
    logger.info("Database initialized successfully")
