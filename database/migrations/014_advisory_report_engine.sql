-- RC2 EPIC-01 - Advisory Report Engine
-- Idempotent SQLite storage for advisory report history only.

CREATE TABLE IF NOT EXISTS advisory_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_type TEXT NOT NULL,
    title TEXT NOT NULL,
    workspace_id INTEGER,
    topic TEXT,
    request_json TEXT NOT NULL,
    result_json TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending_human_review',
    created_by TEXT,
    approved_by TEXT,
    approved_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_advisory_reports_type ON advisory_reports(report_type);
CREATE INDEX IF NOT EXISTS idx_advisory_reports_workspace ON advisory_reports(workspace_id);
CREATE INDEX IF NOT EXISTS idx_advisory_reports_status ON advisory_reports(status);
