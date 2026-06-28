-- Build 0.5.1 - AI Knowledge Engine Integration & Optimization
-- Incremental indexing, embedding cache, richer citation, relation confidence.

PRAGMA foreign_keys = ON;

ALTER TABLE knowledge_documents ADD COLUMN source_checksum TEXT;
ALTER TABLE knowledge_documents ADD COLUMN indexed_checksum TEXT;
ALTER TABLE knowledge_documents ADD COLUMN last_indexed_at TEXT;

ALTER TABLE knowledge_chunks ADD COLUMN source_checksum TEXT;
ALTER TABLE knowledge_chunks ADD COLUMN embedding_version TEXT;
ALTER TABLE knowledge_chunks ADD COLUMN embedding_hash TEXT;

ALTER TABLE knowledge_relations ADD COLUMN confidence REAL NOT NULL DEFAULT 1 CHECK(confidence > 0);
ALTER TABLE knowledge_relations ADD COLUMN is_bidirectional INTEGER NOT NULL DEFAULT 0 CHECK(is_bidirectional IN (0,1));

CREATE TABLE IF NOT EXISTS knowledge_embedding_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    embedding_hash TEXT NOT NULL UNIQUE,
    source_checksum TEXT NOT NULL,
    text_hash TEXT NOT NULL,
    embedding_version TEXT NOT NULL,
    embedding_model TEXT NOT NULL,
    embedding_backend TEXT NOT NULL,
    embedding_json TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS knowledge_index_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    library_document_id INTEGER NOT NULL UNIQUE,
    knowledge_document_id INTEGER,
    file_path TEXT NOT NULL,
    checksum TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'indexed',
    last_seen_at TEXT DEFAULT CURRENT_TIMESTAMP,
    last_indexed_at TEXT,
    detail TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(library_document_id) REFERENCES documents(id) ON DELETE CASCADE,
    FOREIGN KEY(knowledge_document_id) REFERENCES knowledge_documents(id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_knowledge_relations_unique_docs
ON knowledge_relations(source_document_id, target_document_id, relation_type);

CREATE INDEX IF NOT EXISTS idx_knowledge_documents_source_checksum ON knowledge_documents(source_checksum);
CREATE INDEX IF NOT EXISTS idx_knowledge_chunks_source_checksum ON knowledge_chunks(source_checksum);
CREATE INDEX IF NOT EXISTS idx_embedding_cache_hash ON knowledge_embedding_cache(embedding_hash);
CREATE INDEX IF NOT EXISTS idx_embedding_cache_checksum ON knowledge_embedding_cache(source_checksum);
CREATE INDEX IF NOT EXISTS idx_index_state_checksum ON knowledge_index_state(checksum);
