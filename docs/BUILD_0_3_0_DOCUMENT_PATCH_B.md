# Build 0.3.0 - Patch B

## Nội dung

Patch B bổ sung Upload Engine cho Phân hệ Soạn thảo văn bản.

## Hoàn thành

- Thêm `DocumentUploadResult`.
- Thêm `DocumentUploadService`.
- Hỗ trợ lưu file mẫu từ đường dẫn local.
- Hỗ trợ lưu file từ stream upload của Streamlit.
- Chỉ cho phép `.doc`, `.docx`, `.pdf`.
- Giới hạn file tối đa 50MB.
- Tạo tên file an toàn trong `documents/templates`.
- Tính checksum SHA-256 để kiểm tra file.
- Bổ sung API upload trong `DocumentService` và `TemplateService`.
- Bổ sung test upload engine.

## Kiểm thử

```bash
python -m pytest -q
```

Kết quả:

```text
15 passed
```
