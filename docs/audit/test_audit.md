# Test Audit - Build 0.6.2

## Phạm vi

Đã kiểm tra test hiện có và bổ sung smoke test cho router/UI AI Draft.

## Điều chỉnh

- Thêm `tests/test_smoke_imports.py`.
- Test xác nhận import `app.router`, import `modules.ai_draft.page`, key `AI Soạn thảo` và callable `render_ai_draft`.

## Kết quả

Đã chạy:

```bash
python -m database.init_db
python -m pytest -q
```

Kết quả:

- `python -m database.init_db`: pass.
- `python -m pytest -q`: `45 passed in 315.96s (0:05:15)`.

## Rủi ro

- Low: Performance tests hiện có làm thời gian chạy pytest lâu hơn. Không thay đổi trong Build 0.6.2 vì đây là audit trước Sprint 7.

## Kết luận

Test coverage có smoke test cần thiết cho router/UI AI Draft trước Sprint 7.
