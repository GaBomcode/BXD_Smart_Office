# Build 0.2.3 - Architecture Hardening

Commit chuẩn bị nền kiến trúc trước Sprint 3 - Soạn thảo văn bản.

## Mục tiêu

- Bổ sung tầng model nghiệp vụ.
- Chuẩn hóa thư mục tài liệu và workspace.
- Thêm cơ chế migration SQL.
- Không thay đổi nghiệp vụ đang chạy của Sprint 2.

## Kết quả

- `models/` có model nền cho Phân hệ 0, Phân hệ 1 và model chuẩn bị cho Phân hệ 2.
- `documents/templates`, `documents/drafts`, `documents/exports` sẵn sàng cho Sprint 3.
- `workspace/attachments`, `workspace/cache`, `workspace/temp` sẵn sàng cho file đính kèm, cache và xử lý tạm.
- `database/migrations/002_architecture_hardening.sql` thêm index và bảng ghi nhận migration.

## Kiểm thử

```bash
python -m database.init_db
pytest -q
```
