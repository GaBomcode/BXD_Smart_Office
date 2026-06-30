# Performance Test Strategy

Build: RC2-001

V1.0 keeps performance regression coverage in the normal release test command.

## Decision

Run:

```bash
pytest -q
```

The suite currently covers the indexing, Knowledge, Chunk, Embedding, Vector, Search and AI Draft validation paths. Performance-sensitive tests should remain deterministic and use temporary folders.

## Rules

- No network calls.
- No external vector database.
- No background indexing jobs.
- Keep test data small enough for normal CI.
- Add larger benchmarks only to a separate V1.1 release profile.

## Release Gate

A release candidate passes this item when the full suite completes successfully on a clean database and no test writes outside the configured temporary or workspace paths.
