# AI_AUDIT_07_SECURITY_PERFORMANCE

## Tong quan

He thong thiet ke offline/local, dung SQLite va khong goi cloud API trong Knowledge Engine. Performance Build 0.5.1 da co incremental indexing, embedding cache, batch processing va test 100/1000/5000 file.

## Pham vi da doc

- `core/config.py`
- `services/document_library_service.py`
- `services/knowledge_service.py`
- `repositories/knowledge_repository.py`
- `database/migrations/007_ai_core_optimization.sql`
- `modules/document_library/page.py`
- `tests/test_ai_core_optimization.py`

## Diem dat

- Checksum duoc tinh streaming theo block tai `services/document_library_service.py:314`, khong doc file mot lan vao RAM de tinh hash.
- Scanner phan biet file unchanged bang checksum tai `services/document_library_service.py:60`.
- Incremental skip trong Knowledge Engine tai `services/knowledge_service.py:143`.
- Embedding cache reuse theo hash tai `services/knowledge_service.py:361`.
- Batch/progress callback co trong `services/document_library_service.py:168` va `services/knowledge_service.py:196`.
- Test performance tao 100, 1000, 5000 file tai `tests/test_ai_core_optimization.py:151`.
- `OllamaEmbeddingBackend` goi local endpoint `localhost`, khong thay API cloud trong source.

## Van de phat hien

- **Medium**: Semantic search duyet tat ca chunk va parse JSON embedding trong Python tai `services/knowledge_service.py:403`. Day la gioi han hieu nang khi so chunk lon.
- **Medium**: UI cho nhap duong dan thu muc nguon tu do tai `modules/document_library/page.py:18`; voi ung dung local day khong phai loi nghiem trong, nhung co rui ro index nham thu muc nhay cam.
- **Medium**: Xoa/mark deleted dung string prefix tai `services/document_library_service.py:226`; co rui ro xac dinh nham pham vi thu muc.
- **Low**: Test performance 5000 file nam trong pytest chinh tai `tests/test_ai_core_optimization.py:151`, lam test suite cham hon. Lan chay truoc trong workspace ghi nhan `40 passed` voi thoi gian khoang vai phut.

## Muc do rui ro

- Critical: Khong phat hien.
- High: Khong phat hien.
- Medium: Vector scan tuyen tinh; path input tu do; path prefix delete.
- Low: Test performance lam pipeline test cham.

## Khuyen nghi

- Giu SQLite cho LTS, nhung chuan bi vector backend co the thay the qua interface embedding/search.
- Gioi han thu muc kho van ban bang cau hinh trong V1.1.
- Tach performance test thanh nhom rieng neu CI can nhanh, van giu test that khong mock.

## Viec nen lam ngay

- Khuyen cao van hanh: chi index thu muc kho van ban da duoc chuan bi.
- Ghi nhan semantic search hien la brute-force scan tren chunk embedding.

## Viec dua vao V1.1

- Backend vector thay the duoc.
- Job log/progress persistent hon cho indexing lon.
- Co chinh sach root folder va audit log cho hanh dong index.

## Ket luan

Security/performance dat muc chap nhan cho ung dung offline Build 0.5 LTS. Rui ro chinh la kha nang mo rong semantic search va an toan van hanh khi chon thu muc nguon.
