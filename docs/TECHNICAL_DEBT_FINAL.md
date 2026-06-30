# TECHNICAL_DEBT_FINAL

Build: `0.7.5-planning`

This file merges existing audit findings and removes duplicate wording. It classifies debt into V1.0 blockers and V1.1 deferrals.

## Sources Merged

- `docs/ARCHITECTURE_AUDIT.md`
- `docs/audit/*.md`
- `docs/audit_build_0_5_lts/*.md`
- Build docs through 0.7.4

## Must Fix Before V1.0

RC2-001 status: V1.0 blocker items are closed by implementation or release documentation. V1.1 deferrals remain unchanged.

### TD-V1-001 Full-text Knowledge handoff

- Source audits: Build 0.5 LTS technical debt and master compliance audit.
- Risk: AI Search and AI Draft evidence quality can be weak if Knowledge Engine receives only metadata.
- Required V1.0 action: pass source document text from Document Library into Knowledge ingestion and preserve chunk lineage.
- RC2-001 status: Closed by RC1 TD-V1-001 full-text handoff.

### TD-V1-002 Document Library path ownership safety

- Source audits: `TECHNICAL_DEBT.md` TD-002.
- Risk: string prefix path checks can misclassify files outside the intended library root.
- Required V1.0 action: use resolved path ownership checks before marking missing files deleted.
- RC2-001 status: Closed by resolved path ownership checks in Document Library cleanup.

### TD-V1-003 User-facing technical JSON in Document Library

- Source audits: UI/UX audit and technical debt.
- Risk: V1.0 users see implementation/debug details.
- Required V1.0 action: replace JSON dumps with user-readable summaries/details.
- RC2-001 status: Closed for Document Library scan and detail views.

### TD-V1-004 V1.0 schema validation / migration recovery note

- Source audits: migration audit and architecture audit.
- Risk: standard runner is safe, but manual partial migration recovery is not documented.
- Required V1.0 action: add final schema validation or release checklist for required tables/indexes/columns.
- RC2-001 status: Closed by `database.init_db.validate_schema` and `docs/SCHEMA_RELEASE_CHECKLIST.md`.

### TD-V1-005 AI Draft evidence validation after Knowledge fix

- Source audits: master compliance audit and AI Draft build docs.
- Risk: AI Draft quality depends on evidence retrieval quality.
- Required V1.0 action: re-test AI Draft evidence/outline/export after full-text Knowledge handoff.
- RC2-001 status: Closed by RC1-003 validation and regression test coverage.

### TD-V1-006 Release packaging and operator guide

- Source audits: MASTER DESIGN final-stage technology and release readiness review.
- Risk: V1.0 cannot be distributed or operated consistently.
- Required V1.0 action: finalize offline package, init, backup, restore, index and export instructions.
- RC2-001 status: Closed by `docs/RELEASE_OPERATOR_GUIDE.md`.

### TD-V1-007 Performance test CI strategy

- Source audits: test audit and technical debt.
- Risk: full test suite can be slow because performance tests create many files.
- Required V1.0 action: decide and document whether performance tests remain in the normal release test command or move to a separate release profile.
- RC2-001 status: Closed by `docs/PERFORMANCE_TEST_STRATEGY.md`.

## Move To V1.1

### TD-V1.1-001 Static type checker in CI

- Source audits: type hint audit and architecture audit.
- Reason for deferral: current type hints are adequate for V1.0; adding mypy/pyright changes CI policy.

### TD-V1.1-002 Mature plugin lifecycle

- Source audits: master architecture notes.
- Reason for deferral: module separation exists; full plugin lifecycle is not required for V1.0 daily workflows.

### TD-V1.1-003 Vector scalability beyond SQLite/Python scan

- Source audits: technical debt TD-003 and Vector Search docs.
- Reason for deferral: V1.0 remains SQLite-only; vector database dependency is out of scope.

### TD-V1.1-004 Automated schema validator beyond release checklist

- Source audits: migration audit.
- Reason for deferral: V1.0 needs release validation; full automated schema validation can be hardened in V1.1.

### TD-V1.1-005 Dead-code removal for marked helper APIs

- Source audits: dead code audit.
- Reason for deferral: helpers were deliberately marked for review after Build 1.0 to avoid behavioral change.

### TD-V1.1-006 Advanced indexing/citation operations UI

- Source audits: LTS audit recommendations.
- Reason for deferral: V1.0 needs user-facing AI Search; broader operations panels can wait.

## Removed As Duplicates

- Full-text handoff appeared in master compliance, technical debt and architecture audit; merged into TD-V1-001.
- Migration 007 idempotency appeared in migration audit and architecture audit; merged into TD-V1-004.
- UI JSON/debug rendering appeared in UI/UX and technical debt docs; merged into TD-V1-003.
- Vector scalability appeared in technical debt and Vector Search limitations; merged into TD-V1.1-003.
