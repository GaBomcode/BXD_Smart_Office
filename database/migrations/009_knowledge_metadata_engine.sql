-- Build 0.7.1 - Knowledge Metadata Engine
-- Metadata, authority, validity, relationship V2, citation metadata, cache.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS knowledge_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knowledge_document_id INTEGER NOT NULL UNIQUE,
    library_document_id INTEGER,
    title TEXT NOT NULL,
    document_number TEXT,
    document_type TEXT,
    normalized_type TEXT,
    field TEXT,
    issuing_agency TEXT,
    signer TEXT,
    issued_date TEXT,
    effective_date TEXT,
    expiry_date TEXT,
    authority_level TEXT NOT NULL DEFAULT 'unknown',
    authority_score REAL NOT NULL DEFAULT 0 CHECK(authority_score >= 0 AND authority_score <= 1),
    validity_status TEXT NOT NULL DEFAULT 'unknown',
    validity_reason TEXT,
    source_checksum TEXT,
    metadata_hash TEXT,
    metadata_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(knowledge_document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    FOREIGN KEY(library_document_id) REFERENCES documents(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS knowledge_relationship_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_knowledge_document_id INTEGER NOT NULL,
    target_knowledge_document_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL DEFAULT 'related',
    direction TEXT NOT NULL DEFAULT 'forward',
    weight REAL NOT NULL DEFAULT 1 CHECK(weight > 0),
    confidence REAL NOT NULL DEFAULT 0 CHECK(confidence >= 0 AND confidence <= 1),
    evidence_json TEXT,
    source TEXT NOT NULL DEFAULT 'metadata_rule',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_knowledge_document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    FOREIGN KEY(target_knowledge_document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE,
    UNIQUE(source_knowledge_document_id, target_knowledge_document_id, relation_type)
);

CREATE TABLE IF NOT EXISTS knowledge_citation_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_text TEXT NOT NULL,
    source_knowledge_document_id INTEGER,
    source_chunk_id INTEGER,
    title TEXT,
    document_number TEXT,
    document_type TEXT,
    authority_level TEXT,
    validity_status TEXT,
    issued_date TEXT,
    page INTEGER,
    section TEXT,
    file_path TEXT,
    checksum TEXT,
    score REAL NOT NULL DEFAULT 0,
    citation_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(source_knowledge_document_id) REFERENCES knowledge_documents(id) ON DELETE SET NULL,
    FOREIGN KEY(source_chunk_id) REFERENCES knowledge_chunks(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS knowledge_metadata_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key TEXT NOT NULL UNIQUE,
    knowledge_document_id INTEGER,
    source_checksum TEXT,
    metadata_hash TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(knowledge_document_id) REFERENCES knowledge_documents(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_knowledge_metadata_doc ON knowledge_metadata(knowledge_document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_metadata_library ON knowledge_metadata(library_document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_metadata_type ON knowledge_metadata(normalized_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_metadata_authority ON knowledge_metadata(authority_level);
CREATE INDEX IF NOT EXISTS idx_knowledge_metadata_validity ON knowledge_metadata(validity_status);
CREATE INDEX IF NOT EXISTS idx_knowledge_relationship_v2_source ON knowledge_relationship_v2(source_knowledge_document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_relationship_v2_target ON knowledge_relationship_v2(target_knowledge_document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_relationship_v2_type ON knowledge_relationship_v2(relation_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_citation_metadata_query ON knowledge_citation_metadata(query_text);
CREATE INDEX IF NOT EXISTS idx_knowledge_citation_metadata_doc ON knowledge_citation_metadata(source_knowledge_document_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_metadata_cache_key ON knowledge_metadata_cache(cache_key);
