-- Build 0.4.0 - Sprint 4
-- Phân hệ 3: Quản lý kho văn bản thông minh.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL UNIQUE,
    file_ext TEXT NOT NULL,
    file_size INTEGER NOT NULL DEFAULT 0 CHECK(file_size >= 0),
    checksum TEXT NOT NULL,
    document_type TEXT,
    document_number TEXT,
    issued_date TEXT,
    issuing_agency TEXT,
    signer TEXT,
    summary TEXT,
    keywords TEXT,
    field TEXT,
    status TEXT NOT NULL DEFAULT 'new',
    indexed_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS document_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    keyword TEXT NOT NULL,
    weight REAL NOT NULL DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE,
    UNIQUE(document_id, keyword)
);

CREATE TABLE IF NOT EXISTS document_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_document_id INTEGER NOT NULL,
    target_document_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY(target_document_id) REFERENCES documents(id) ON DELETE CASCADE,
    CHECK(source_document_id != target_document_id)
);

CREATE INDEX IF NOT EXISTS idx_documents_file_ext ON documents(file_ext);
CREATE INDEX IF NOT EXISTS idx_documents_checksum ON documents(checksum);
CREATE INDEX IF NOT EXISTS idx_documents_document_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_issued_date ON documents(issued_date);
CREATE INDEX IF NOT EXISTS idx_documents_issuing_agency ON documents(issuing_agency);
CREATE INDEX IF NOT EXISTS idx_documents_field ON documents(field);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_document_keywords_keyword ON document_keywords(keyword);
CREATE INDEX IF NOT EXISTS idx_document_relations_source ON document_relations(source_document_id);
CREATE INDEX IF NOT EXISTS idx_document_relations_target ON document_relations(target_document_id);
