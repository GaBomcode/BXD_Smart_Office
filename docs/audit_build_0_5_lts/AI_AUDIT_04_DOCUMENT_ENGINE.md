# AI_AUDIT_04_DOCUMENT_ENGINE

## Tong quan

Document Engine gom Sprint 3 Document Draft va Sprint 4 Document Library. Build hien tai co doc file, trich metadata, checksum, trang thai review, kho van ban va dong bo sang Knowledge Engine.

## Pham vi da doc

- `modules/documents/page.py`
- `modules/document_library/page.py`
- `services/document_service.py`
- `services/document_upload_service.py`
- `services/template_service.py`
- `services/document_library_service.py`
- `services/document_metadata_extractor.py`
- `services/readers/*.py`
- `models/document_*.py`, `models/library_document.py`
- `repositories/document_repository.py`, `repositories/document_library_repository.py`
- `tests/test_document_*.py`

## Diem dat

- DOCX, PDF, XLSX, TXT co reader rieng trong `services/readers/`.
- `.doc` va `.xls` cu duoc danh dau unsupported thay vi doc sai: `services/readers/docx_reader.py:19`, `services/readers/xlsx_reader.py:19`.
- PDF khong co text duoc danh dau `need_ocr`: `services/readers/pdf_reader.py:26`.
- Metadata extractor co rule cho so van ban, ngay, loai van ban, co quan, nguoi ky, tom tat, linh vuc, keyword tai `services/document_metadata_extractor.py:32`.
- Scanner tinh checksum va phan biet `new`, `existing`, `changed` trong `services/document_library_service.py:60`.
- UI kho van ban co thao tac scan/index, loc va review metadata trong `modules/document_library/page.py`.

## Van de phat hien

- **High**: Noi dung day du cua file sau khi doc chua duoc luu vao bang `documents` va khong duoc truyen sang Knowledge Engine trong sync mac dinh. Bang chung: `services/document_library_service.py:143` doc `reader_result.text`, nhung `LibraryDocument` chi luu metadata; `services/knowledge_service.py:160` fallback chi gom title/number/summary/keywords.
- **Medium**: `modules/document_library/page.py:18` cho nhap truc tiep duong dan thu muc nguon. Viec nay phu hop ung dung local/offline, nhung chua co allowlist/canh bao van hanh cho kho chuan.
- **Medium**: `services/document_library_service.py:226` xac dinh file nam trong root bang string prefix, co the sai voi cac path co tien to giong nhau.
- **Low**: OCR chua duoc tich hop; PDF scan chi co trang thai `need_ocr` tai `services/readers/pdf_reader.py:26`. Day la gioi han da duoc code bieu thi ro, khong phai loi doc text.

## Muc do rui ro

- Critical: Khong phat hien.
- High: Knowledge Engine co the khong co toan van.
- Medium: Ranh gioi thu muc nguon va xoa file can chat hon.
- Low: OCR chua co.

## Khuyen nghi

- Trong V1.1, them truong/luong luu extracted text hoac content store rieng, gan checksum va source path.
- Thiet lap workspace root mac dinh cho Document Library, han che nhap nham thu muc.
- OCR nen la module sau, khong chen vao Build 0.5 LTS neu chua co yeu cau.

## Viec nen lam ngay

- Tai lieu hoa rang PDF scan se vao `need_ocr`, khong coi la indexed day du.
- Lap backlog fix path ownership trong `mark_missing_files_deleted()`.

## Viec dua vao V1.1

- Content store cho toan van da extract.
- Review flow cho van ban `need_ocr` va `unsupported`.
- Chuan hoa root kho van ban theo cau hinh.

## Ket luan

Document Engine dat nen tang tot cho kho van ban offline. De AI Core that su manh, V1.1 can uu tien luu/truyen toan van thay vi chi metadata.
