-- Build 0.7.3 - Embedding Engine
-- Idempotent schema for chunk embedding persistence.

CREATE TABLE IF NOT EXISTS knowledge_embeddings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chunk_id INTEGER NOT NULL UNIQUE,
    document_id INTEGER NOT NULL,
    embedding_model TEXT NOT NULL,
    embedding_provider TEXT NOT NULL,
    vector_json TEXT,
    vector_dimension INTEGER NOT NULL DEFAULT 0 CHECK(vector_dimension >= 0),
    chunk_checksum TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(chunk_id) REFERENCES knowledge_chunks(id) ON DELETE CASCADE,
    FOREIGN KEY(document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_knowledge_embeddings_chunk ON knowledge_embeddings(chunk_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_embeddings_document ON knowledge_embeddings(document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_embeddings_model_provider ON knowledge_embeddings(embedding_model, embedding_provider);
CREATE INDEX IF NOT EXISTS idx_knowledge_embeddings_checksum ON knowledge_embeddings(chunk_checksum);
CREATE INDEX IF NOT EXISTS idx_knowledge_embeddings_status ON knowledge_embeddings(status);
