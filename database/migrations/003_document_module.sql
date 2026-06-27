-- Build 0.3.0 - Sprint 3
-- Phân hệ 2: Soạn thảo văn bản - nền dữ liệu tài liệu.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS document_templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    document_type TEXT NOT NULL DEFAULT 'Công văn',
    field TEXT,
    source_path TEXT NOT NULL UNIQUE,
    file_ext TEXT NOT NULL,
    file_size INTEGER NOT NULL DEFAULT 0 CHECK(file_size >= 0),
    status TEXT NOT NULL DEFAULT 'Mới nạp',
    summary TEXT,
    keywords TEXT,
    analysis_json TEXT,
    created_by TEXT NOT NULL DEFAULT 'Nguyễn Trung Hiền',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    template_id INTEGER NOT NULL,
    section_order INTEGER NOT NULL DEFAULT 0,
    section_type TEXT NOT NULL DEFAULT 'Nội dung',
    title TEXT,
    content TEXT,
    style_name TEXT,
    metadata_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(template_id) REFERENCES document_templates(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS document_drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    document_type TEXT NOT NULL DEFAULT 'Công văn',
    template_id INTEGER,
    workspace_id INTEGER,
    request_text TEXT,
    draft_content TEXT,
    output_path TEXT,
    status TEXT NOT NULL DEFAULT 'Nháp',
    review_note TEXT,
    created_by TEXT NOT NULL DEFAULT 'Nguyễn Trung Hiền',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(template_id) REFERENCES document_templates(id) ON DELETE SET NULL,
    FOREIGN KEY(workspace_id) REFERENCES workspaces(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_document_templates_type ON document_templates(document_type);
CREATE INDEX IF NOT EXISTS idx_document_templates_status ON document_templates(status);
CREATE INDEX IF NOT EXISTS idx_document_templates_field ON document_templates(field);
CREATE INDEX IF NOT EXISTS idx_document_sections_template ON document_sections(template_id);
CREATE INDEX IF NOT EXISTS idx_document_drafts_template ON document_drafts(template_id);
CREATE INDEX IF NOT EXISTS idx_document_drafts_workspace ON document_drafts(workspace_id);
CREATE INDEX IF NOT EXISTS idx_document_drafts_status ON document_drafts(status);
