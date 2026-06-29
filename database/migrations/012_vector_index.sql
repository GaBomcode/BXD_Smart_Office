-- Build 0.7.4 - Vector Index Engine
-- Idempotent schema for SQLite vector index metadata.

CREATE TABLE IF NOT EXISTS knowledge_vector_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    embedding_id INTEGER NOT NULL UNIQUE,
    chunk_id INTEGER NOT NULL UNIQUE,
    document_id INTEGER NOT NULL,
    vector_dimension INTEGER NOT NULL DEFAULT 0 CHECK(vector_dimension >= 0),
    vector_checksum TEXT NOT NULL,
    vector_norm REAL NOT NULL DEFAULT 0 CHECK(vector_norm >= 0),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK(is_active IN (0,1)),
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(embedding_id) REFERENCES knowledge_embeddings(id) ON DELETE CASCADE,
    FOREIGN KEY(chunk_id) REFERENCES knowledge_chunks(id) ON DELETE CASCADE,
    FOREIGN KEY(document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_knowledge_vector_index_chunk ON knowledge_vector_index(chunk_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_vector_index_document ON knowledge_vector_index(document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_vector_index_embedding ON knowledge_vector_index(embedding_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_vector_index_active ON knowledge_vector_index(is_active);
