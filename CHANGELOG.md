# CHANGELOG

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
