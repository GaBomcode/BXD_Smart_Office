-- Build 0.7.2 - Chunk Engine
-- Idempotent schema for rule-based chunking, token counts, overlap and metadata.

CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL,
    page INTEGER DEFAULT 0,
    section TEXT NOT NULL DEFAULT 'Noi dung',
    chunk_order INTEGER NOT NULL DEFAULT 0,
    text TEXT NOT NULL,
    token_count INTEGER NOT NULL DEFAULT 0 CHECK(token_count >= 0),
    source_checksum TEXT,
    embedding_json TEXT,
    embedding_model TEXT,
    embedding_backend TEXT,
    embedding_version TEXT,
    embedding_hash TEXT,
    embedding_updated_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS knowledge_chunk_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id INTEGER NOT NULL UNIQUE,
    document_id INTEGER NOT NULL,
    chunk_uid TEXT NOT NULL UNIQUE,
    text_hash TEXT NOT NULL,
    start_token INTEGER NOT NULL DEFAULT 0 CHECK(start_token >= 0),
    end_token INTEGER NOT NULL DEFAULT 0 CHECK(end_token >= start_token),
    overlap_tokens INTEGER NOT NULL DEFAULT 0 CHECK(overlap_tokens >= 0),
    overlap_with_previous INTEGER NOT NULL DEFAULT 0 CHECK(overlap_with_previous IN (0,1)),
    source_engine TEXT NOT NULL DEFAULT 'rule_chunk_v1',
    metadata_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(chunk_id) REFERENCES knowledge_chunks(id) ON DELETE CASCADE,
    FOREIGN KEY(document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_document_order ON knowledge_chunks(document_id, chunk_order);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_token_count ON knowledge_chunks(token_count);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunk_metadata_chunk ON knowledge_chunk_metadata(chunk_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunk_metadata_document ON knowledge_chunk_metadata(document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunk_metadata_uid ON knowledge_chunk_metadata(chunk_uid);
