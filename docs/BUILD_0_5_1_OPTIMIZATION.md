# Build 0.5.1 - AI Knowledge Engine Integration & Optimization

## Phạm vi

Build 0.5.1 đóng băng AI Core ở mức tối ưu kiến trúc. Không phát triển Sprint 6, không làm AI Draft, không Chat UI, không Agent.

## Hoàn thành

- Incremental indexing theo checksum.
- File không đổi được bỏ qua: không đọc lại, không chunk lại, không keyword lại, không relation lại, không embedding lại.
- Embedding cache lưu `embedding_version`, `embedding_model`, `embedding_hash`, backend, vector và checksum.
- Semantic search trả rich citation: tên văn bản, số văn bản, ngày, trang, chunk, section, file path, checksum, relevance.
- Relation optimization: tránh duplicate relation, quan hệ hai chiều cho relation phù hợp, weight và confidence.
- Batch processing: batch size, progress callback, resume qua `knowledge_index_state`.
- Document Library tự đồng bộ sang Knowledge Engine khi thêm/sửa/xóa file.
- Performance tests với 100, 1000, 5000 file thật.

## Migration

- `database/migrations/007_ai_core_optimization.sql`

## Kiểm thử

```bash
python -m pytest -q
```

## Technical Debt

- Chưa tối ưu backend vector bằng FAISS/Chroma.
- Local hash embedding dùng cho test/offline fallback; khi dùng Ollama cần cấu hình model embedding phù hợp.
- OCR PDF scan vẫn chuyển sang Sprint sau.

## Chuẩn bị Sprint 6

Sprint 6 có thể dùng Knowledge Engine để soạn thảo AI có căn cứ, nhưng phải giữ nguyên nguyên tắc người dùng duyệt trước.
