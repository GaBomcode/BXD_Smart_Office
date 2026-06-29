# Build 0.7.2 - Chunk Schema

Build 0.7.2 keeps the existing `knowledge_chunks` table and adds dedicated
metadata storage for chunk lineage. The migration uses only idempotent
`CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS` statements.

## `knowledge_chunks`

Primary content table used by the Knowledge Engine.

Key fields:

- `id`: chunk id.
- `document_id`: parent `knowledge_documents.id`.
- `page`: optional source page, default `0`.
- `section`: rule-detected section label.
- `chunk_order`: stable order inside the document.
- `text`: chunk text.
- `token_count`: token count produced by the Chunk Engine.
- `source_checksum`: checksum of the source document when available.
- `embedding_*`: legacy fields kept for older Knowledge Engine compatibility.

Indexes:

- `idx_knowledge_chunks_document_order`
- `idx_knowledge_chunks_token_count`

## `knowledge_chunk_metadata`

Metadata table introduced in Build 0.7.2.

Fields:

- `id`: metadata id.
- `chunk_id`: unique reference to `knowledge_chunks.id`.
- `document_id`: parent document id for efficient replacement/listing.
- `chunk_uid`: deterministic hash for source checksum, order and text hash.
- `text_hash`: SHA-256 hash of chunk text.
- `start_token`: inclusive token offset in the source section stream.
- `end_token`: exclusive token offset in the source section stream.
- `overlap_tokens`: number of tokens intentionally overlapping with the
  previous chunk.
- `overlap_with_previous`: `1` when the chunk starts with overlap, else `0`.
- `source_engine`: chunking rule version, default `rule_chunk_v1`.
- `metadata_json`: JSON payload for engine settings and section context.

Indexes:

- `idx_knowledge_chunk_metadata_chunk`
- `idx_knowledge_chunk_metadata_document`
- `idx_knowledge_chunk_metadata_uid`

## Upgrade Notes

Fresh databases receive the chunk metadata table during `init_database()`.
Existing databases can run the same migration safely because every statement is
idempotent.
