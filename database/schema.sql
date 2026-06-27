PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    unit TEXT NOT NULL,
    scope TEXT,
    note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staff (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL UNIQUE,
    position TEXT NOT NULL,
    field TEXT,
    can_receive_task INTEGER DEFAULT 1,
    system_role TEXT DEFAULT 'Chuyên viên',
    status TEXT DEFAULT 'Đang công tác',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS work_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    axis TEXT NOT NULL,
    group_name TEXT,
    task_name TEXT NOT NULL,
    output_product TEXT,
    frequency TEXT,
    level TEXT DEFAULT 'N3',
    point REAL DEFAULT 1,
    coefficient REAL DEFAULT 1,
    active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS kpi_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    level TEXT NOT NULL,
    point REAL NOT NULL,
    coefficient REAL NOT NULL DEFAULT 1,
    note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS workspaces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    field TEXT,
    status TEXT DEFAULT 'Đang xử lý',
    created_by TEXT DEFAULT 'Nguyễn Trung Hiền',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workspace_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    work_code_id INTEGER,
    field TEXT,
    assigned_to_id INTEGER,
    deadline TEXT,
    priority TEXT DEFAULT 'Bình thường',
    status TEXT DEFAULT 'Chưa thực hiện',
    progress INTEGER DEFAULT 0 CHECK(progress >= 0 AND progress <= 100),
    evidence_path TEXT,
    related_document TEXT,
    point REAL DEFAULT 0,
    created_by TEXT DEFAULT 'Nguyễn Trung Hiền',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE SET NULL,
    FOREIGN KEY(work_code_id) REFERENCES work_codes(id),
    FOREIGN KEY(assigned_to_id) REFERENCES staff(id)
);

CREATE TABLE IF NOT EXISTS task_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    update_date TEXT DEFAULT CURRENT_TIMESTAMP,
    content TEXT NOT NULL,
    progress INTEGER DEFAULT 0 CHECK(progress >= 0 AND progress <= 100),
    evidence_path TEXT,
    created_by TEXT DEFAULT 'Người dùng',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS task_files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT,
    note TEXT,
    uploaded_by TEXT DEFAULT 'Người dùng',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER,
    detail TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_task_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT,
    suggested_title TEXT NOT NULL,
    suggested_description TEXT,
    suggested_work_code TEXT,
    suggested_staff TEXT,
    suggested_deadline TEXT,
    suggested_priority TEXT DEFAULT 'Bình thường',
    selected INTEGER DEFAULT 1,
    status TEXT DEFAULT 'Chờ duyệt',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
