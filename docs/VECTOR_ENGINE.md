# Build 0.7.4 - Vector Index Engine

Build 0.7.4 adds a SQLite-only Vector Index layer above the existing Embedding
Engine. The layer stores vector index metadata, refreshes changed vectors, and
provides deterministic nearest-neighbour helper APIs over already generated
embeddings.

## Scope

- Model: `models/vector_index.py`
- Repository: `repositories/vector_repository.py`
- Service: `services/vector_service.py`
- Migration: `database/migrations/012_vector_index.sql`
- Tests: `tests/test_vector_engine.py`, `tests/test_vector_repository.py`

This build does not implement semantic search, hybrid search, citation
retrieval, context building, chat, AI Assistant, AI Draft changes, Ollama calls
or a vector database dependency.

## Vector Lifecycle

1. The Embedding Engine writes completed embeddings to `knowledge_embeddings`.
2. `VectorService.build_index()` reads completed embeddings.
3. Each vector is parsed from JSON.
4. The service calculates vector dimension, checksum and norm.
5. `VectorRepository` writes one row per embedding into
   `knowledge_vector_index`.
6. If the stored checksum is unchanged, refresh is skipped.
7. Delete operations can remove vectors by document or chunk.

## Vector Storage

The index table stores metadata only:

- embedding id
- chunk id
- document id
- vector dimension
- vector checksum
- vector norm
- active flag

The numeric vector remains in `knowledge_embeddings.vector_json`.

## Cosine Similarity

`VectorService.cosine_similarity()` is a pure Python implementation:

```text
dot(a, b) / (norm(a) * norm(b))
```

Zero vectors return `0.0`. Dimension mismatch raises `ValueError`.

## Top K

Supported values are:

- top 1
- top 3
- top 5
- top 10

The API returns vector index rows with a numeric `score`. It does not perform
semantic search or citation retrieval.

## Cache

Vector index refresh uses a SHA-256 checksum over the vector payload. If the
checksum is unchanged, the existing row is reused.
