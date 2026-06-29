-- RC1 TD-V1-001 - Full-text Knowledge Handoff
-- Table declaration is idempotent. Existing deployments receive new columns
-- through database.init_db safe-alter compatibility.

CREATE TABLE IF NOT EXISTS knowledge_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER,
    library_document_id INTEGER,
    title TEXT NOT NULL,
    full_text TEXT,
    checksum TEXT,
    chunk_count INTEGER NOT NULL DEFAULT 0,
    embedding_version TEXT,
    indexed_time TEXT,
    source_path TEXT,
    document_type TEXT,
    document_number TEXT,
    field TEXT,
    status TEXT NOT NULL DEFAULT 'READY',
    source_checksum TEXT,
    indexed_checksum TEXT,
    last_indexed_at TEXT,
    metadata_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_knowledge_documents_document_id ON knowledge_documents(document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_checksum ON knowledge_documents(checksum);
CREATE INDEX IF NOT EXISTS idx_knowledge_documents_status ON knowledge_documents(status);
