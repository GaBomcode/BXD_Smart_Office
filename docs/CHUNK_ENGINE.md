# Build 0.7.2 - Chunk Engine

Build 0.7.2 separates the rule-based chunk layer from the wider Knowledge Engine.
The scope is deliberately narrow: split source text into reusable chunks, count
tokens, apply controlled overlap and persist chunk metadata.

## Scope

- Chunk Engine: `services/chunk_service.py`
- Chunk Repository: `repositories/chunk_repository.py`
- Chunk metadata model: `models/knowledge_chunk_metadata.py`
- Migration: `database/migrations/010_chunk_engine.sql`
- Tests: `tests/test_chunk_engine.py`, `tests/test_chunk_repository.py`

This build does not implement embeddings, vector search, Ollama integration,
semantic search or a chatbot workflow.

## Flow

1. `ChunkEngine` normalizes input text into non-empty lines.
2. Section hints are detected with rule-based patterns.
3. Lines are tokenized with a Unicode word tokenizer.
4. Tokens are split into windows controlled by `max_tokens`.
5. Later windows reuse the configured number of trailing tokens from the
   previous window as overlap.
6. Each chunk receives `token_count`, `chunk_order`, section and optional source
   checksum.
7. `KnowledgeChunkMetadata` records lineage fields such as `chunk_uid`,
   `text_hash`, token offsets and overlap flags.
8. `ChunkRepository` replaces a document's chunks and matching metadata through
   the repository layer.

## Defaults

- `max_tokens`: 180
- `overlap_tokens`: 24
- `source_engine`: `rule_chunk_v1`

The overlap value must be smaller than `max_tokens`.

## Compatibility

`KnowledgeService.chunk_text()` now delegates to `ChunkService`, so existing
Knowledge Engine callers continue using the old public API while the new chunk
layer owns splitting rules. Document ingestion persists chunks through
`ChunkService.replace_document_chunks()`.

The build keeps MVC + Repository Pattern + Service Layer:

- model: `KnowledgeChunk`, `KnowledgeChunkMetadata`
- repository: `ChunkRepository`
- service: `ChunkEngine`, `ChunkService`
- existing controller/UI layers are unchanged
