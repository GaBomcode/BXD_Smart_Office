# Build 0.7.3 - Vector Schema

Build 0.7.3 introduces `knowledge_embeddings` as the persistence table for
chunk embedding vectors. The migration is idempotent and uses only
`CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS`.

## `knowledge_embeddings`

Fields:

- `id`: primary key.
- `chunk_id`: unique reference to `knowledge_chunks.id`.
- `document_id`: parent `knowledge_documents.id`.
- `embedding_model`: backend model name.
- `embedding_provider`: backend/provider name.
- `vector_json`: JSON encoded numeric vector.
- `vector_dimension`: vector length.
- `chunk_checksum`: SHA-256 checksum of the chunk text.
- `status`: `pending`, `completed`, `failed` or `skipped`.
- `error_message`: failure detail when status is `failed`.
- `created_at`: row creation timestamp.
- `updated_at`: row update timestamp.

Indexes:

- `idx_knowledge_embeddings_chunk`
- `idx_knowledge_embeddings_document`
- `idx_knowledge_embeddings_model_provider`
- `idx_knowledge_embeddings_checksum`
- `idx_knowledge_embeddings_status`

## Notes

`chunk_id` is unique because Build 0.7.3 stores the current embedding for each
chunk. Re-running the engine updates the row when the chunk checksum changes.

This schema stores vectors but does not provide vector search, ranking, hybrid
search or semantic retrieval in this build.
