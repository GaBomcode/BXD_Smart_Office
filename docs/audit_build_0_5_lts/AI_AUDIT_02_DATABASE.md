# AI_AUDIT_02_DATABASE

## Tong quan

SQLite duoc dung nhat quan cho toan bo he thong. Cac migration tu Sprint 3 den Build 0.5.1 da tao bang tai lieu, kho van ban, Knowledge Engine, cache embedding va trang thai index.

## Pham vi da doc

- `database/schema.sql`
- `database/init_db.py`
- `database/migrations/002_architecture_hardening.sql`
- `database/migrations/003_document_module.sql`
- `database/migrations/004_document_settings.sql`
- `database/migrations/005_document_library.sql`
- `database/migrations/006_ai_knowledge.sql`
- `database/migrations/007_ai_core_optimization.sql`
- `repositories/*.py`
- `tests/test_*migration*.py`, `tests/test_ai_core_optimization.py`

## Diem dat

- `database/init_db.py:63` tao bang `schema_migrations`, va `database/init_db.py:73` chay migration SQL theo thu tu.
- Document Library co cac bang `documents`, `document_keywords`, `document_relations` trong `database/migrations/005_document_library.sql`.
- Knowledge Engine co `knowledge_documents`, `knowledge_chunks`, `knowledge_entities`, `knowledge_relations`, `knowledge_jobs`, `knowledge_logs` trong `database/migrations/006_ai_knowledge.sql`.
- Build 0.5.1 bo sung `knowledge_embedding_cache` va `knowledge_index_state` trong `database/migrations/007_ai_core_optimization.sql:17` va `database/migrations/007_ai_core_optimization.sql:30`.
- Co index cho checksum, relation, chunk, entity, job status trong migration `005`, `006`, `007`.
- Cascade delete da co tren nhieu quan he quan trong, vi du `knowledge_chunks.document_id` tai `database/migrations/006_ai_knowledge.sql:35`.

## Van de phat hien

- **Medium**: `database/migrations/007_ai_core_optimization.sql:6-15` dung `ALTER TABLE ... ADD COLUMN` khong co guard. Trong luong chay binh thuong, `schema_migrations` ngan chay lai; tuy nhien neu migration bi dung giua chung, chay lai co the gap loi cot da ton tai.
- **Medium**: Unique index relation tai `database/migrations/007_ai_core_optimization.sql:46` chi bao ve bo `(source_document_id, target_document_id, relation_type)`. Quan he hai chieu duoc luu bang ban ghi rieng trong code, nen duplicate nguoc chieu van la mot thuc the hop le; can quy uoc ro de tranh hieu sai khi dung graph.
- **Low**: SQLite luu embedding bang JSON trong `knowledge_chunks.embedding_json` va `knowledge_embedding_cache.embedding_json`. `services/knowledge_service.py:403` duyet tat ca chunk khi semantic search, nen day la thiet ke chap nhan duoc cho LTS nho/trung binh nhung can theo doi khi du lieu lon.

## Muc do rui ro

- Critical: Khong phat hien.
- High: Khong phat hien.
- Medium: Kha nang migration 007 kho phuc hoi neu fail giua chung; can quy uoc quan he hai chieu.
- Low: Vector luu SQLite JSON co gioi han hieu nang.

## Khuyen nghi

- Them ghi chu van hanh cho migration: backup DB truoc khi len 0.5.1, khong sua tay `schema_migrations`.
- V1.1 nen bo sung migration recovery pattern hoac script validate schema.
- Dinh nghia ro semantic cua relation nguoc chieu trong tai lieu graph.

## Viec nen lam ngay

- Luu danh sach migration da ap dung vao bao cao release.
- Kiem tra DB that co cac bang `knowledge_embedding_cache`, `knowledge_index_state`, cac index relation/checksum sau khi deploy.

## Viec dua vao V1.1

- Xay schema validation tu dong sau migration.
- Can nhac backend vector thay the qua interface da co, khong doi Service Layer.

## Ket luan

Database dat muc on dinh cho Build 0.5 LTS. Diem can chu y nhat la kha nang phuc hoi migration va gioi han hieu nang cua semantic search tren SQLite JSON.
