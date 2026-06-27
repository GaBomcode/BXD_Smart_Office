# Build 0.3.0 - Document Module Patch A

## Phạm vi

Khởi tạo tầng dữ liệu cho phân hệ Soạn thảo văn bản. Patch này chưa làm giao diện Streamlit và chưa kết nối Ollama.

## Thành phần

- Migration: `database/migrations/003_document_module.sql`
- Models: `DocumentTemplate`, `DocumentSection`, `DocumentDraft`
- Repository: `DocumentRepository`
- Services: `DocumentService`, `TemplateService`
- Tests: `tests/test_document_repository.py`

## Nguyên tắc

AI chưa tự ghi dữ liệu. Các bảng được thiết kế để phục vụ luồng: nạp mẫu -> phân tích -> người dùng duyệt -> tạo dự thảo -> xuất văn bản.
