# TECHNICAL_DEBT

## Tong quan

Danh sach nay chi ghi technical debt co bang chung trong source Build 0.5.1. Khong dua cac gia dinh chua thay trong ma nguon.

## Pham vi da doc

- `services/document_library_service.py`
- `services/knowledge_service.py`
- `repositories/base_repository.py`
- `repositories/knowledge_repository.py`
- `database/migrations/007_ai_core_optimization.sql`
- `modules/document_library/page.py`
- `tests/test_ai_core_optimization.py`

## Diem dat

- Incremental indexing va embedding cache da co test.
- Rich citation da tra du truong can cho UI render sau nay.
- Relation duplicate duoc xu ly bang repository va unique index.
- Batch processing co progress callback.

## Van de phat hien

- **High - TD-001 Full-text handoff**: Knowledge Engine chua nhan toan van khi sync tu Document Library. Bang chung: `services/document_library_service.py:143`, `services/document_library_service.py:231`, `services/knowledge_service.py:160`.
- **Medium - TD-002 Path ownership**: `mark_missing_files_deleted()` dung `startswith` tren chuoi duong dan tai `services/document_library_service.py:226`.
- **Medium - TD-003 Vector search scalability**: `semantic_search()` duyet tat ca chunks tai `services/knowledge_service.py:403`.
- **Medium - TD-004 Migration recovery**: `database/migrations/007_ai_core_optimization.sql:6-15` dung `ALTER TABLE ADD COLUMN` khong co guard phuc hoi partial failure.
- **Medium - TD-005 BaseRepository update contract**: `repositories/base_repository.py:53` yeu cau bang co `updated_at`.
- **Low - TD-006 UI debug rendering**: `modules/document_library/page.py:31` va `modules/document_library/page.py:59` render JSON truc tiep.
- **Low - TD-007 Performance test runtime**: `tests/test_ai_core_optimization.py:151` tao 100/1000/5000 file trong pytest chinh.

## Muc do rui ro

- Critical: Khong co item.
- High: TD-001.
- Medium: TD-002, TD-003, TD-004, TD-005.
- Low: TD-006, TD-007.

## Khuyen nghi

- Xu ly TD-001 truoc Sprint 6.
- TD-002 va TD-004 nen xu ly truoc khi dung kho van ban that rong.
- TD-003 co the dua vao V1.1 khi du lieu tang.

## Viec nen lam ngay

- Tao issue cho TD-001 va TD-002.
- Ghi chu van hanh cho TD-004: backup DB truoc migration.

## Viec dua vao V1.1

- Content store/toan van.
- Path API an toan.
- Vector backend.
- Schema validator.
- UI indexing polish.

## Ket luan

Technical debt khong pha vo Build 0.5.1, nhung TD-001 la dieu kien quan trong truoc Sprint 6 vi anh huong truc tiep chat luong AI Draft va AI Advisory.
