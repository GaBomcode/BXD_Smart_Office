# CHANGELOG

## Build 0.6.0 - AI Draft Foundation

### Added
- Thêm migration `008_ai_draft_engine.sql` cho `ai_draft_requests`, `ai_draft_results`, `ai_draft_citations`, `ai_draft_revisions`.
- Thêm model `AIDraftRequest`, `AIDraftResult`, `AIDraftCitation`.
- Thêm `AIDraftRepository` và `AIDraftService`.
- Thêm nhận diện loại văn bản rule-based với confidence score.
- Thêm template selector top 5 có score, lý do chọn và citation.
- Thêm evidence collector dùng Knowledge Engine semantic search.
- Thêm outline generator với trạng thái `pending_outline_review`.
- Thêm draft generator chỉ chạy sau khi người dùng duyệt dàn ý.
- Thêm review workflow, revision history và audit log.
- Thêm export DOCX chỉ cho dự thảo đã duyệt.
- Thêm menu Streamlit `AI Soạn thảo`.
- Thêm tests `tests/test_ai_draft_foundation.py`.

### Notes
- Không làm chatbot, agent, API cloud hoặc AI tự ban hành.
- AI Draft Engine chỉ tham mưu; người dùng duyệt trước khi lưu/xuất.
- Không bắt đầu Sprint 7.

## Build 0.5.1 - AI Core Optimization

### Added
- Thêm migration `007_ai_core_optimization.sql`.
- Thêm incremental indexing theo checksum.
- Thêm `knowledge_embedding_cache` và `knowledge_index_state`.
- Thêm embedding cache với `embedding_version`, `embedding_model`, `embedding_hash`.
- Mở rộng citation semantic search thành object render-ready.
- Tối ưu relation: unique relation, bidirectional flag, confidence.
- Thêm batch processing, progress callback và đồng bộ Document Library -> Knowledge Engine.
- Thêm performance tests với 100, 1000, 5000 file thật.

### Notes
- Không phát triển Sprint 6 trong build này.
- Không thêm Chat UI, Agent hoặc AI Draft.

## Build 0.5.0 - AI Knowledge Engine

### Added
- Thêm migration `006_ai_knowledge.sql` cho `knowledge_documents`, `knowledge_chunks`, `knowledge_entities`, `knowledge_relations`, `knowledge_jobs`, `knowledge_logs`.
- Thêm model tri thức: `KnowledgeDocument`, `KnowledgeChunk`, `KnowledgeEntity`, `KnowledgeRelation`.
- Thêm `KnowledgeRepository` và `KnowledgeService`.
- Thêm chunk engine rule-based, keyword/entity engine, relation engine và knowledge graph SQLite.
- Thêm embedding backend interface, local hash backend và Ollama backend local.
- Thêm semantic search Top K có score và citation.
- Thêm tài liệu `docs/BUILD_0_5_AI.md` và tests Sprint 5.

### Notes
- Không thêm Chat UI/chatbot/agent trong Sprint 5.
- Không gọi API cloud.

## Build 0.4.0 - Document Library Foundation

### Added
- Thêm phân hệ `Kho văn bản` trong sidebar.
- Thêm migration `005_document_library.sql` cho `documents`, `document_keywords`, `document_relations`.
- Thêm model `LibraryDocument`, `DocumentKeyword`, `DocumentRelation`.
- Thêm `DocumentLibraryRepository` và `DocumentLibraryService`.
- Thêm scanner metadata thư mục nhiều tầng, bỏ qua file tạm và nhận DOC/DOCX/PDF/XLS/XLSX/TXT.
- Thêm reader chuẩn hóa cho DOCX, PDF, XLSX, TXT.
- Thêm extractor rule-based cho số ký hiệu, ngày văn bản, cơ quan ban hành, loại văn bản, trích yếu, người ký, lĩnh vực, từ khóa.
- Thêm persist index vào SQLite với trạng thái indexed/failed/need_ocr/need_review/duplicate/unsupported.
- Thêm workflow duyệt metadata trên UI và audit log khi lưu duyệt.
- Thêm test foundation, reader, extractor, indexing và review workflow.

### Notes
- Sprint 4 chỉ làm kho văn bản và index nền, chưa làm AI Search.

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
