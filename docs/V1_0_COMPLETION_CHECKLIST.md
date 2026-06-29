# V1_0_COMPLETION_CHECKLIST

Build: `0.7.5-planning`

This checklist lists every current module and supporting engine needed for V1.0 completion. Status values are audit labels, not implementation approval.

## Application Shell

| Module | Status | V1.0 Checklist |
|---|---|---|
| `app/main.py` | PASS | App starts through Streamlit; keep final smoke test. |
| `app/router.py` | PASS | Sidebar routes current user modules; keep route labels stable. |
| `core/config.py` | PASS | Runtime paths centralized. |
| `core/logger.py` | PASS | Logging helper exists. |
| `core/theme.py` | PASS | Theme helper exists. |
| `core/version.py` | PASS | Version file exists; planning version recorded in docs/changelog only. |

## UI Modules

| Module | Status | V1.0 Checklist |
|---|---|---|
| `modules/dashboard` | PASS | Dashboard metrics and KPI table present; final visual smoke check. |
| `modules/profile` | PASS | Staff, roles, work codes and KPI rules present; final seed data review. |
| `modules/tasks` | PASS | Task CRUD, workspace assignment, progress, evidence and Excel export present; final export smoke check. |
| `modules/documents` | PASS | Template upload, analysis, draft, review and export present; final DOCX format QA. |
| `modules/document_library` | PARTIAL | Scan, list, review and metadata edit present; remove technical JSON exposure and complete full-text handoff. |
| `modules/knowledge_engine` | PARTIAL | Backend module marker exists; no user-facing AI Search page yet. |
| `modules/ai_draft` | PARTIAL | AI Draft workflow exists; final validation depends on full-text Knowledge quality. |

## Service Modules

| Service | Status | V1.0 Checklist |
|---|---|---|
| `TaskService` | PASS | Keep KPI/export behavior stable. |
| `ProfileService` | PASS | Keep seed/reference data stable. |
| `DocumentService` | PASS | Final template and export QA. |
| `TemplateService` | PASS | Decide post-V1.0 fate of methods marked for removal. |
| `DocumentUploadService` | PASS | Keep extension/size validation. |
| `DocumentLibraryService` | PARTIAL | Fix full-text handoff and path ownership risk. |
| `DocumentMetadataExtractor` | PASS | Rule-based extraction exists; final sample QA. |
| `KnowledgeService` | PARTIAL | Backend works; full-text ingestion and product search flow remain. |
| `KnowledgeMetadataService` | PASS | Metadata, authority, validity and citation metadata layer exists. |
| `ChunkService` | PASS | Chunking, overlap and metadata layer exists. |
| `EmbeddingService` | PASS | Deterministic embedding layer and future backend interface exist. |
| `VectorService` | PASS | SQLite vector index and nearest-neighbour helpers exist. |
| `AIDraftService` | PARTIAL | Review-gated workflow exists; needs final evidence quality validation. |

## Repository Modules

| Repository | Status | V1.0 Checklist |
|---|---|---|
| `BaseRepository` | PARTIAL | Update contract assumes `updated_at`; document or harden before V1.0. |
| `TaskRepository` | PASS | Task persistence exists. |
| `ProfileRepository` | PASS | Profile/reference persistence exists. |
| `DocumentRepository` | PASS | Template/draft persistence exists. |
| `DocumentLibraryRepository` | PASS | Library persistence exists. |
| `KnowledgeRepository` | PARTIAL | Works; job lifecycle helpers marked for removal after Build 1.0. |
| `ChunkRepository` | PASS | Chunk persistence exists. |
| `EmbeddingRepository` | PASS | Embedding persistence exists. |
| `VectorRepository` | PASS | Vector index persistence exists. |
| `AIDraftRepository` | PASS | AI Draft persistence exists. |

## Data / Migration Layer

| Area | Status | V1.0 Checklist |
|---|---|---|
| Base schema | PASS | `database/schema.sql` exists. |
| Migration runner | PASS | `schema_migrations` prevents reruns in normal flow. |
| Migrations `002`-`006` | PASS | Foundation/document/library/knowledge tables exist. |
| Migration `007` | PARTIAL | Normal runner safe; manual rerun has `ALTER TABLE` debt. |
| Migrations `008`-`012` | PASS | AI Draft, metadata, chunk, embedding and vector tables exist. |
| Schema validation | MISSING | Add final validation/checklist before V1.0. |

## Tests

| Test Area | Status | V1.0 Checklist |
|---|---|---|
| Architecture/foundation tests | PASS | Keep green. |
| Task/profile tests | PASS | Keep green. |
| Document module tests | PASS | Keep green. |
| Document library tests | PASS | Add final full-text handoff coverage when fixed. |
| Knowledge tests | PASS | Keep green. |
| Metadata/chunk/embedding/vector tests | PASS | Keep green. |
| AI Draft tests | PASS | Add final evidence quality checks after full-text handoff. |
| Performance tests | PARTIAL | Useful but slow; decide V1.0 CI strategy. |

## Release Readiness

| Area | Status | V1.0 Checklist |
|---|---|---|
| README / CHANGELOG | PARTIAL | Add final V1.0 release status. |
| User-facing docs | PARTIAL | Current build docs exist; final operator guide missing. |
| Packaging | MISSING | PyInstaller/final distribution workflow not complete. |
| Backup / upgrade notes | PARTIAL | README has upgrade notes; final V1.0 backup/restore checklist needed. |
