# Build 0.4.0 - Sprint 4 Document Library

## Phạm vi

Sprint 4 xây dựng phân hệ Kho văn bản và nền index offline. Sprint này không làm AI Search và không quay lại nâng cấp soạn thảo văn bản.

## Hoàn thành

- Thêm menu `Kho văn bản`.
- Thêm bảng `documents`, `document_keywords`, `document_relations`.
- Quét thư mục nhiều tầng, bỏ qua file tạm và nhận `.doc`, `.docx`, `.pdf`, `.xlsx`, `.xls`, `.txt`.
- Tính checksum SHA-256 để phát hiện file mới, file đã có, file thay đổi và file trùng.
- Reader chuẩn hóa cho DOCX, PDF, XLSX, TXT; DOC/XLS cũ đánh dấu `unsupported`.
- Metadata extractor rule-based cho văn bản hành chính Đảng: số ký hiệu, ngày, cơ quan, loại văn bản, trích yếu, người ký, lĩnh vực, từ khóa.
- Lưu chỉ mục vào SQLite với trạng thái `indexed`, `failed`, `need_ocr`, `need_review`, `duplicate`, `unsupported`.
- UI lọc theo loại file, loại văn bản, năm, cơ quan, trạng thái, lĩnh vực và tìm nhanh.
- Workflow duyệt metadata: người dùng sửa và bấm lưu trước khi cập nhật.

## Kiểm thử

```bash
python -m pytest -q
```

## Chưa làm

- AI Search, embedding, hỏi đáp có nguồn: chuyển sang Sprint 5.
- OCR PDF scan: chuyển sang Sprint sau khi chốt engine OCR offline.
