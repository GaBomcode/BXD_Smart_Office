# ROADMAP_V1_1

## Tong quan

Roadmap V1.1 duoc rut ra tu audit Build 0.5 LTS. Tai lieu nay khong mo Sprint 6 va khong dinh nghia tinh nang chatbot/agent; chi sap xep cac viec nen lam de AI Core on dinh truoc khi phat trien AI Draft.

## Pham vi da doc

- Toan bo source trong `app/`, `core/`, `database/`, `models/`, `repositories/`, `services/`, `modules/`, `tests/`, `docs/`
- `README.md`
- `CHANGELOG.md`
- Cac bao cao audit trong `docs/audit_build_0_5_lts/`

## Diem dat

- Nen tang Document Library da co.
- Nen tang Knowledge Engine da co.
- Incremental indexing va embedding cache da co.
- Rich citation da san sang cho UI tuong lai.
- Build 0.5.1 chua vuot pham vi sang Sprint 6.

## Van de phat hien

- **High**: Can full-text handoff tu Document Library sang Knowledge Engine.
- **Medium**: Can path safety cho root/delete.
- **Medium**: Can schema validation va migration recovery.
- **Medium**: Can chuan bi vector backend khi du lieu lon.
- **Low**: Can polish UI indexing va tach performance test neu CI cham.

## Muc do rui ro

- Critical: Khong phat hien.
- High: Full-text handoff.
- Medium: Path, migration, vector scalability.
- Low: UI/test polish.

## Khuyen nghi

- Phase 1: On dinh AI Core data lineage.
- Phase 2: On dinh migration/operation.
- Phase 3: Chuan bi vector backend va indexing dashboard.
- Phase 4: Moi bat dau Sprint 6 AI Draft khi citation/toan van da dang tin.

## Viec nen lam ngay

- Khoa pham vi Build 0.5 LTS.
- Xu ly backlog TD-001 va TD-002.
- Xac nhan pytest pass sau audit.

## Viec dua vao V1.1

- Full-text content store gan `document_id`, `checksum`, `source_path`, `extracted_at`.
- Knowledge ingestion nhan toan van va luu citation lineage theo chunk.
- Configured document library roots.
- Schema validator sau migration.
- Vector backend thay the duoc qua interface.
- Health check Ollama/model embedding.
- UI indexing/citation sau khi AI Core on dinh.

## Ket luan

V1.1 nen tap trung lam AI Core dang tin cay truoc khi mo rong sang AI Draft. Thu tu dung la: toan van -> citation lineage -> vector/search -> UI ung dung -> Sprint 6.
