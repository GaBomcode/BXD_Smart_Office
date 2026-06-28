# Architecture Audit - Build 0.6.2

## 1. Kiến trúc hiện tại

BXD Smart Office - Offline đang theo kiến trúc Streamlit + SQLite, chia lớp:

- `modules/`: UI Streamlit.
- `services/`: nghiệp vụ, workflow, validation, AI orchestration.
- `repositories/`: truy cập SQLite.
- `models/`: dataclass nghiệp vụ.
- `database/`: schema, migration, connection.
- `core/`: config, logger, theme, version.

AI Draft Engine vẫn giữ nguyên nguyên tắc: AI chỉ tham mưu, người dùng duyệt dàn ý/dự thảo trước khi xuất DOCX.

## 2. Điểm mạnh

- Repository Pattern được giữ: không có `sqlite3.connect()`, `conn.execute()`, `cursor.execute()` trực tiếp trong `modules/` hoặc `services/`.
- Service Layer rõ cho Document Library, Knowledge Engine và AI Draft.
- MVC/module architecture phù hợp Streamlit offline.
- CI GitHub Actions đã có workflow chạy init DB và pytest.
- Smoke test router/UI AI Draft đã được bổ sung.
- Logging đã loại lời gọi stdout còn lại.

## 3. Điểm yếu

- Migration 007 còn `ALTER TABLE ... ADD COLUMN`, không idempotent nếu chạy tay ngoài migration runner.
- Một số helper public chưa dùng được đánh dấu giữ lại tới Build 1.0.
- Chưa có static type checker trong CI.
- UI Streamlit vẫn có flow-control ở page, tuy chưa phải business logic.

## 4. Technical Debt

- Chuẩn hóa migration thêm cột bằng safe-alter/schema validator.
- Quyết định xóa hoặc giữ các API đã đánh dấu `TODO REMOVE AFTER BUILD 1.0`.
- Cân nhắc mypy/pyright trước Build 1.0.
- Tiếp tục xử lý full-text handoff từ Document Library sang Knowledge Engine theo audit Build 0.5 LTS.

## 5. Rủi ro

- Medium: Migration 007 có thể lỗi nếu vận hành viên chạy SQL file trực tiếp nhiều lần.
- Medium: Sprint 7 có nguy cơ làm UI chứa thêm nghiệp vụ nếu không giữ kỷ luật Service Layer.
- Low: Test suite có performance tests nên thời gian CI có thể dài.

## 6. Mức sẵn sàng Sprint 7

Sẵn sàng có điều kiện.

Điều kiện:

- Không đưa nghiệp vụ thể thức văn bản vào Streamlit page.
- Mọi validation/export/AI policy mới phải vào service.
- Không tự xuất/ban hành văn bản nếu chưa có trạng thái duyệt.

## 7. Đề xuất Build 1.0

- Schema validation sau migration.
- Static type check.
- Audit dependency direction bằng tool tự động.
- Quyết định dead code đã đánh dấu.
- Chuẩn hóa migration strategy cho SQLite.

## Kết luận

Build 0.6.2 đạt mục tiêu Architecture Audit trước Sprint 7 mà không thay đổi nghiệp vụ, UI flow hoặc database schema.
