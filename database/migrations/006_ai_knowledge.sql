-- Build 0.5.0 - Sprint 5
-- AI Knowledge Engine nền, không chat UI và không tự ghi dữ liệu nghiệp vụ.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS knowledge_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    library_document_id INTEGER,
    title TEXT NOT NULL,
    source_path TEXT,
    document_type TEXT,
    document_number TEXT,
    field TEXT,
    status TEXT NOT NULL DEFAULT 'ready',
    metadata_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(library_document_id) REFERENCES documents(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    page INTEGER DEFAULT 0,
    section TEXT NOT NULL DEFAULT 'Nội dung',
    chunk_order INTEGER NOT NULL DEFAULT 0,
    text TEXT NOT NULL,
    token_count INTEGER NOT NULL DEFAULT 0 CHECK(token_count >= 0),
    embedding_json TEXT,
    embedding_model TEXT,
    embedding_backend TEXT,
    embedding_updated_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS knowledge_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    chunk_id INTEGER,
    entity_type TEXT NOT NULL,
    entity_value TEXT NOT NULL,
    weight REAL NOT NULL DEFAULT 1 CHECK(weight > 0),
    source TEXT NOT NULL DEFAULT 'rule',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    FOREIGN KEY(chunk_id) REFERENCES knowledge_chunks(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS knowledge_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_document_id INTEGER,
    target_document_id INTEGER,
    source_entity_id INTEGER,
    target_entity_id INTEGER,
    relation_type TEXT NOT NULL,
    weight REAL NOT NULL DEFAULT 1 CHECK(weight > 0),
    evidence TEXT,
    source TEXT NOT NULL DEFAULT 'rule',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    FOREIGN KEY(target_document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    FOREIGN KEY(source_entity_id) REFERENCES knowledge_entities(id) ON DELETE CASCADE,
    FOREIGN KEY(target_entity_id) REFERENCES knowledge_entities(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS knowledge_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    target_id INTEGER,
    detail TEXT,
    started_at TEXT,
    finished_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    level TEXT NOT NULL DEFAULT 'INFO',
    message TEXT NOT NULL,
    detail TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(job_id) REFERENCES knowledge_jobs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_knowledge_documents_library ON knowledge_documents(library_document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_type ON knowledge_documents(document_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_field ON knowledge_documents(field);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_document ON knowledge_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_section ON knowledge_chunks(section);
CREATE INDEX IF NOT EXISTS idx_knowledge_entities_document ON knowledge_entities(document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_entities_value ON knowledge_entities(entity_value);
CREATE INDEX IF NOT EXISTS idx_knowledge_relations_source_doc ON knowledge_relations(source_document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_relations_target_doc ON knowledge_relations(target_document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_jobs_status ON knowledge_jobs(status);
