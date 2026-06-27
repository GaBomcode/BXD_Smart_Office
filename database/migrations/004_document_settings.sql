-- Build 0.3.0 - Sprint 3
-- Cấu hình thể thức văn bản cho phân hệ Soạn thảo văn bản.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS document_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_document_settings_key ON document_settings(setting_key);
