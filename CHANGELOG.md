# CHANGELOG

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
