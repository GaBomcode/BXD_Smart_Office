# CHANGELOG

## Build 0.3.0 - Sprint 3 Document Module

### Added
- Thêm giao diện `Soạn thảo văn bản` trong sidebar Streamlit.
- Thêm luồng nạp mẫu, phân tích mẫu, gợi ý mẫu gần nhất, sinh dự thảo chờ duyệt.
- Thêm kiểm tra nhanh thể thức văn bản trước khi xuất.
- Thêm xuất dự thảo DOCX vào `documents/exports`.
- Thêm cấu hình thể thức văn bản: cơ quan, ký hiệu, địa danh, nơi nhận mặc định, người ký, font và lề.
- Thêm test Sprint 3 cho phân tích mẫu, gợi ý mẫu, sinh dự thảo và xuất DOCX.

### Notes
- AI/offline engine chỉ tham mưu; người dùng vẫn duyệt và chỉnh sửa trước khi xuất văn bản.

## Build 0.3.0 - Document Module Patch A

### Added
- Thêm migration `003_document_module.sql` cho `document_templates`, `document_sections`, `document_drafts`.
- Thêm model `DocumentSection` và nâng cấp `DocumentTemplate`, `DocumentDraft` với validation.
- Thêm `DocumentRepository`, `DocumentService`, `TemplateService`.
- Mở rộng `BaseRepository` với insert/update/delete/find/list.
- Thêm test dữ liệu cho phân hệ Soạn thảo văn bản.

### Tests
- 11/11 tests passed.

## Build 0.2.3 - Architecture Hardening

### Added
- Bổ sung tầng `models/` đầy đủ cho vai trò, nhân sự, mã việc, KPI, nhiệm vụ, workspace, audit log.
- Chuẩn bị model nền cho Sprint 3: `DocumentTemplate`, `DocumentDraft`.
- Bổ sung thư mục runtime: `documents/templates`, `documents/drafts`, `documents/exports`, `workspace/attachments`, `workspace/cache`, `workspace/temp`.
- Thêm cơ chế chạy SQL migration trong `database/migrations`.
- Thêm migration `002_architecture_hardening.sql` và index phục vụ nhiệm vụ/timeline/audit.
- Thêm test kiến trúc Build 0.2.3.

### Changed
- Cập nhật `core/config.py` để quản lý tập trung các thư mục tài liệu và workspace.
- Cập nhật `database/init_db.py` để tự áp dụng migration khi khởi tạo/nâng cấp database.

### Tests
- 7/7 tests passed.

## Build 0.2.2 - Sprint 2

### Added
- Workspace Lite: hồ sơ công việc để gom nhiệm vụ theo vụ việc/chuyên đề.
- Upload nhiều file minh chứng cho từng nhiệm vụ.
- Timeline cập nhật tiến độ nhiệm vụ.
- AI Review offline: AI/Người dùng tạo đề xuất, người dùng duyệt trước khi ghi nhiệm vụ.
- Audit Log: nhật ký thao tác tạo/sửa/xóa/cập nhật/upload/duyệt.
- Phân quyền nền bằng trường `system_role` cho 8 nhân sự.
- Xuất Excel 5 sheet: nhiệm vụ, KPI, timeline, minh chứng, audit log.

### Changed
- Nâng version lên 0.2.2.
- Nâng schema SQLite nhưng vẫn có migration để chạy từ Build 0.2/0.2.1.

### Tests
- 4/4 tests passed.

## Build 0.3.0 - Patch B

### Added
- Upload Engine cho kho mẫu văn bản.
- `DocumentUploadResult` model.
- `DocumentUploadService` hỗ trợ DOC, DOCX, PDF.
- API `upload_template_file` trong `DocumentService` và `TemplateService`.
- Test upload file local, stream upload, từ chối file rỗng và file không hỗ trợ.

### Test
- `python -m pytest -q`
- Kết quả: `15 passed`
