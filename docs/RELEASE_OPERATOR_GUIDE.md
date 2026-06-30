# V1.0 Release Operator Guide

Build: RC2-001

This guide freezes the minimum offline operation steps for V1.0.

## Initialize

Run:

```bash
python -m database.init_db
```

The command creates or updates the local SQLite schema and validates critical V1.0 tables.

## Backup

Before upgrades or release testing:

1. Close the application.
2. Copy the SQLite database file to a dated backup folder.
3. Keep exported documents and uploaded source files with the same backup set.

## Restore

1. Close the application.
2. Replace the database file with the selected backup.
3. Restore the matching upload/export folders when available.
4. Run `python -m database.init_db` to verify schema compatibility.

## Index Documents

Use the Document Library folder indexing workflow. The indexer reads supported offline files, extracts metadata and full text, then syncs READY content through Knowledge, Chunk, Embedding, Vector and Citation stages.

## Export Documents

AI Draft export is allowed only after human approval and final draft validation. Invalid drafts are rejected before DOCX generation.

## Offline Package Check

Before handoff:

1. Confirm Python dependencies are installed in the offline environment.
2. Run database initialization.
3. Run the release test command.
4. Index a small sample folder.
5. Export one approved valid draft.
