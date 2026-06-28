-- Build 0.6 - AI Draft Engine foundation

CREATE TABLE IF NOT EXISTS ai_draft_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_text TEXT NOT NULL,
    requested_by TEXT NOT NULL DEFAULT 'Nguoi dung',
    detected_document_type TEXT,
    selected_document_type TEXT,
    confidence REAL NOT NULL DEFAULT 0 CHECK(confidence >= 0 AND confidence <= 1),
    status TEXT NOT NULL DEFAULT 'draft_requested',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_draft_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    document_type TEXT NOT NULL,
    template_document_id INTEGER,
    outline_content TEXT,
    draft_content TEXT,
    status TEXT NOT NULL DEFAULT 'pending_outline_review',
    output_path TEXT,
    review_note TEXT,
    approved_by TEXT,
    approved_at TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(request_id) REFERENCES ai_draft_requests(id) ON DELETE CASCADE,
    FOREIGN KEY(template_document_id) REFERENCES documents(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS ai_draft_citations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    request_id INTEGER NOT NULL,
    result_id INTEGER,
    citation_type TEXT NOT NULL DEFAULT 'evidence',
    source_document_id INTEGER,
    source_chunk_id INTEGER,
    title TEXT,
    document_number TEXT,
    issued_date TEXT,
    page INTEGER,
    section TEXT,
    file_path TEXT,
    checksum TEXT,
    score REAL NOT NULL DEFAULT 0,
    quote_text TEXT,
    reason TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(request_id) REFERENCES ai_draft_requests(id) ON DELETE CASCADE,
    FOREIGN KEY(result_id) REFERENCES ai_draft_results(id) ON DELETE CASCADE,
    FOREIGN KEY(source_document_id) REFERENCES documents(id) ON DELETE SET NULL,
    FOREIGN KEY(source_chunk_id) REFERENCES knowledge_chunks(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS ai_draft_revisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    result_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    status TEXT NOT NULL,
    edited_by TEXT NOT NULL DEFAULT 'Nguoi dung',
    note TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(result_id) REFERENCES ai_draft_results(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ai_draft_requests_status ON ai_draft_requests(status);
CREATE INDEX IF NOT EXISTS idx_ai_draft_results_request ON ai_draft_results(request_id);
CREATE INDEX IF NOT EXISTS idx_ai_draft_results_status ON ai_draft_results(status);
CREATE INDEX IF NOT EXISTS idx_ai_draft_citations_request ON ai_draft_citations(request_id);
CREATE INDEX IF NOT EXISTS idx_ai_draft_citations_result ON ai_draft_citations(result_id);
CREATE INDEX IF NOT EXISTS idx_ai_draft_citations_type ON ai_draft_citations(citation_type);
