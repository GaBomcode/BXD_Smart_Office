# Build 0.7.4 - Vector Search Notes

Build 0.7.4 introduces low-level vector nearest-neighbour APIs, not product
semantic search.

## Current Vector Search

Current capabilities:

- Store vector index metadata in SQLite.
- Refresh vector indexes from completed embeddings.
- Compare a supplied query vector against stored embedding vectors.
- Return Top K vector rows ranked by cosine similarity.

These APIs are intended as internal infrastructure for later builds.

## Future Semantic Search

Future semantic search can build on this layer by adding:

- query embedding generation
- metadata and authority filtering
- ranking policies
- citation retrieval
- context builder
- UI workflow

Those features are intentionally outside Build 0.7.4.

## Limitations

- SQLite stores vector JSON and metadata; there is no vector database.
- Similarity scans active rows in Python.
- No hybrid search.
- No semantic search endpoint.
- No AI Assistant or chat flow.
- No Ollama calls are made by this layer.
