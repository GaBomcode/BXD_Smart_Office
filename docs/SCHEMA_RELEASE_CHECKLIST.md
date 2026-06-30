# Schema Release Checklist

Build: RC2-001

This checklist covers the final V1.0 schema recovery and validation step.

## Required Command

Run before packaging or release:

```bash
python -m database.init_db
```

The initializer now validates V1.0 critical tables and columns after all SQL migrations run. A missing table or required column raises `RuntimeError` and must block release.

## Required Tables

- `documents`
- `document_keywords`
- `ai_draft_requests`
- `ai_draft_results`
- `ai_draft_citations`
- `knowledge_documents`
- `knowledge_chunks`
- `knowledge_embeddings`
- `knowledge_vector_index`
- `knowledge_citation_metadata`
- `schema_migrations`

## Manual Recovery

If a release database was partially migrated:

1. Back up the SQLite file before repair.
2. Run `python -m database.init_db`.
3. If validation fails, inspect the named missing table or column.
4. Restore from backup if the database cannot be repaired by idempotent migrations.
5. Do not manually edit `schema_migrations` unless the database has been backed up and the matching table/columns have been verified.
