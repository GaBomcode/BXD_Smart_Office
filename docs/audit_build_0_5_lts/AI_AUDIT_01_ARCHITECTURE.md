# AI_AUDIT_01_ARCHITECTURE

## Tong quan

Build 0.5.1 da hinh thanh kien truc Streamlit + SQLite theo huong MVC, Repository Pattern va Service Layer. Sprint 4 va Sprint 5 duoc tach thanh Document Library va Knowledge Engine, khong co UI chat, khong co agent, khong bat dau Sprint 6.

## Pham vi da doc

- `app/main.py`, `app/router.py`
- `core/config.py`, `core/logger.py`, `core/theme.py`, `core/version.py`
- `database/schema.sql`, `database/init_db.py`, `database/migrations/*.sql`
- `models/`, `repositories/`, `services/`, `modules/`, `tests/`
- `README.md`, `CHANGELOG.md`, `docs/`

## Diem dat

- Router UI duoc tap trung tai `app/router.py`, cac module Streamlit nam duoi `modules/`.
- Service Layer tach nghiep vu kho van ban va tri thuc tai `services/document_library_service.py` va `services/knowledge_service.py`.
- Repository Pattern duoc dung qua `repositories/base_repository.py`, `repositories/document_library_repository.py`, `repositories/knowledge_repository.py`.
- Plugin/module architecture da co module rieng: `modules/document_library/`, `modules/documents/`, `modules/dashboard/`, `modules/profile/`, `modules/tasks/`, `modules/knowledge_engine/`.
- Version build duoc khai bao tai `core/version.py`.

## Van de phat hien

- **High**: Dong bo Document Library sang Knowledge Engine chua dua noi dung day du cua file vao pipeline tri thuc. `services/document_library_service.py:143` doc `reader_result.text` de trich metadata, nhung `sync_knowledge_document()` o `services/document_library_service.py:231` chi truyen `library_document_id`. `services/knowledge_service.py:160` tao `content` tu `title`, `document_number`, `summary`, `keywords` khi khong co tham so `text`. Dieu nay lam Knowledge Engine co nguy co chi index metadata thay vi toan van.
- **Medium**: `BaseRepository.update()` mac dinh them `updated_at=CURRENT_TIMESTAMP` tai `repositories/base_repository.py:53`. Cach nay phu hop cac bang co cot `updated_at`, nhung la rang buoc an trong lop dung chung; neu repository moi dung cho bang khong co `updated_at` se loi SQL.
- **Low**: `modules/knowledge_engine/__init__.py` ton tai de khai bao module, nhung chua co UI hoac entry router rieng. Dieu nay dung voi yeu cau Sprint 5 khong lam chat/UI AI, nhung can ghi ro trong tai lieu kien truc de tranh nham thanh thieu module.

## Muc do rui ro

- Critical: Khong phat hien.
- High: Knowledge Engine co kha nang index thieu toan van khi dong bo tu Document Library.
- Medium: Lop repository dung chung co rang buoc `updated_at` an.
- Low: Module Knowledge Engine la backend-only, can tiep tuc giu nguyen trong Build 0.5 LTS.

## Khuyen nghi

- Ghi ro hop dong giua Document Library va Knowledge Engine: noi dung file day du phai duoc luu hoac truyen vao Knowledge Engine trong qua trinh index.
- Neu tiep tuc dung `BaseRepository.update()`, can quy uoc tat ca bang cap nhat qua base repository phai co `updated_at`.
- Duy tri nguyen tac khong them Chat UI/Agent trong Build 0.5 LTS.

## Viec nen lam ngay

- Lap issue ky thuat cho viec dong bo toan van tu Document Library sang Knowledge Engine.
- Bo sung tai lieu noi bo ve cac bang duoc phep dung `BaseRepository.update()`.

## Viec dua vao V1.1

- Chuan hoa contract "Document Library -> Knowledge Engine" gom metadata, checksum, extracted text, status, citation.
- Them ADR kien truc cho AI Core backend-only, truoc khi Sprint 6 bat dau AI Draft.

## Ket luan

Kien truc dat nen tang dung huong cho Build 0.5 LTS. Rui ro lon nhat nam o diem noi giua Document Library va Knowledge Engine: pipeline da co, nhung can dam bao Knowledge Engine nhan du toan van de lam loi AI Core.
