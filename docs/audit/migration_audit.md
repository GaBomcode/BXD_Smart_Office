# Migration Audit - Build 0.6.2

## Phạm vi

Đã kiểm tra `database/migrations/*.sql` và runner trong `database/init_db.py`.

## Kết quả

- Migration runner dùng bảng `schema_migrations`, nên luồng chuẩn `python -m database.init_db` không chạy lại migration đã ghi nhận.
- Các `CREATE TABLE` và `CREATE INDEX` trong migration dùng `IF NOT EXISTS`.
- `database/migrations/007_ai_core_optimization.sql` có các câu `ALTER TABLE ... ADD COLUMN`.

## Điều chỉnh

Không thay đổi schema trong Build 0.6.2 vì không cần thiết cho nghiệp vụ và SQLite runtime hiện tại không hỗ trợ cú pháp `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`.

## Technical debt

- Medium: Nếu chạy tay riêng file `007_ai_core_optimization.sql` nhiều lần ngoài migration runner, các câu `ALTER TABLE ... ADD COLUMN` có thể lỗi vì cột đã tồn tại.
- Luồng vận hành chuẩn vẫn an toàn nhờ `schema_migrations`.

## Khuyến nghị

- Build 1.0 nên chuyển các migration thêm cột sang cơ chế Python safe-alter hoặc schema validator, thay vì yêu cầu idempotent thuần SQL cho `ALTER TABLE`.

## Kết luận

Migration đạt yêu cầu trong luồng runner chuẩn. Có technical debt rõ ràng ở migration 007 nếu chạy thủ công nhiều lần.
