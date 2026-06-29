# Build 0.7.3 - Embedding Engine

Build 0.7.3 adds a standalone Embedding Engine for persisted chunk vectors.
It follows MVC + Repository Pattern + Service Layer and does not change the
business workflow.

## Scope

- Model: `models/embedding_vector.py`
- Repository: `repositories/embedding_repository.py`
- Service: `services/embedding_service.py`
- Migration: `database/migrations/011_embedding_engine.sql`
- Tests: `tests/test_embedding_engine.py`, `tests/test_embedding_repository.py`

This build does not implement semantic search, hybrid search, ranking, context
building, AI Assistant, AI Draft changes or direct Ollama calls from UI.

## Backends

`EmbeddingBackend` is a service-level protocol. Build 0.7.3 includes:

- `DeterministicLocalEmbeddingBackend`: offline deterministic hash vectors for
  tests and local development.
- `OllamaEmbeddingBackend`: placeholder interface for future implementation.

The deterministic backend makes no external API calls.

## Features

- Generate an embedding for one chunk.
- Generate embeddings for all chunks or one document's chunks.
- Skip unchanged chunks when checksum, model and provider are unchanged.
- Regenerate changed chunks when chunk text checksum changes.
- Mark failed embedding attempts in `knowledge_embeddings`.
- Retrieve embedding by `chunk_id`.
- Process batches with per-chunk error handling.

## Service Flow

1. `EmbeddingService` reads chunk text from `ChunkRepository`.
2. It calculates a SHA-256 chunk checksum.
3. It checks existing `knowledge_embeddings` by `chunk_id`.
4. If the stored checksum/model/provider still match, the chunk is skipped.
5. Otherwise the configured backend generates a vector.
6. `EmbeddingRepository` upserts the embedding row.
7. Backend errors are caught and persisted with `status='failed'`.

The UI layer should call the service layer only. It must not call an embedding
backend directly.
