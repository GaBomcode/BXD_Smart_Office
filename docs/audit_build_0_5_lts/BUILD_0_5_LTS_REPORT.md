# BUILD_0_5_LTS_REPORT

## Tong quan

Build 0.5 LTS tong hop Sprint 4 Document Library, Sprint 5 AI Knowledge Engine va Build 0.5.1 Optimization. He thong da co kho van ban, index incremental, embedding cache, relation graph, semantic search va rich citation o backend.

## Pham vi da doc

- `app/`
- `core/`
- `database/`
- `models/`
- `repositories/`
- `services/`
- `modules/`
- `tests/`
- `docs/`
- `README.md`
- `CHANGELOG.md`

## Diem dat

- Sprint 4: Document Library co scanner, reader, metadata extractor, review workflow.
- Sprint 5: Knowledge Engine co chunk, keyword/entity, relation, graph, embedding, semantic search, citation.
- Build 0.5.1: incremental indexing, embedding cache, rich citation, relation optimization, batch/progress, workspace integration.
- Test suite hien co gom 40 test theo thong tin workspace va file test da doc.
- Khong thay Chat UI, Agent, AI Draft moi trong router.

## Van de phat hien

- **High**: Knowledge Engine co kha nang chi index metadata khi dong bo tu Document Library. Bang chung: `services/document_library_service.py:231`, `services/knowledge_service.py:160`.
- **Medium**: Semantic search scan tat ca chunk trong SQLite tai `services/knowledge_service.py:403`.
- **Medium**: Path root/delete can chinh xac hon tai `services/document_library_service.py:226`.
- **Medium**: Migration 007 co `ALTER TABLE ... ADD COLUMN` khong guard tai `database/migrations/007_ai_core_optimization.sql:6-15`.
- **Low**: Performance test lon nam trong pytest chinh tai `tests/test_ai_core_optimization.py:151`.

## Muc do rui ro

- Critical: Khong phat hien.
- High: Full-text ingestion.
- Medium: Search scalability, path handling, migration recovery.
- Low: Test runtime va UI debug display.

## Khuyen nghi

- Dong bang Build 0.5 LTS sau khi tai lieu audit duoc chap thuan.
- Truoc Sprint 6, xu ly technical debt full-text ingestion va path safety.
- Khong them UI chat/AI Draft trong build nay.

## Viec nen lam ngay

- Chay pytest sau khi tao bo audit.
- Luu audit trong `docs/audit_build_0_5_lts/`.
- Tao danh sach debt uu tien truoc Sprint 6.

## Viec dua vao V1.1

- Full-text content store.
- Schema validation.
- Configured document library roots.
- Vector backend abstraction implementation.
- Indexing job dashboard sau khi core on dinh.

## Ket luan

Build 0.5 LTS du dieu kien lam moc dong bang AI Core ve mat kien truc. Chua nen bat dau Sprint 6 neu chua co ke hoach xu ly full-text ingestion, vi day anh huong truc tiep chat luong AI Draft/Advisory sau nay.
