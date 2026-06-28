# BXD Smart Office - Offline

Build hiện tại: **0.5.1**

## Chức năng chính

- Dashboard điều hành.
- Phân hệ 0: Hồ sơ vai trò, nhân sự, mã việc, KPI.
- Phân hệ 1: Quản lý nhiệm vụ, tiến độ, minh chứng, KPI, xuất Excel.
- Workspace Lite: gom nhiệm vụ theo hồ sơ công việc.
- AI Review: duyệt đề xuất trước khi ghi nhiệm vụ.
- Audit Log: nhật ký thao tác hệ thống.
- Architecture Hardening: model nghiệp vụ, thư mục tài liệu/workspace, migration SQL nền.
- Phân hệ 2: Soạn thảo văn bản theo mẫu, phân tích mẫu, sinh dự thảo chờ duyệt, xuất DOCX.
- Phân hệ 3: Kho văn bản, quét thư mục nhiều tầng, lưu metadata và chuẩn bị nền index.
- AI Knowledge Engine: chunk, keyword, relation, graph, embedding, semantic search có citation.

## Sprint 4 - Build 0.4

Kho văn bản thông minh bắt đầu từ nền chỉ mục: scan thư mục, đọc DOCX/PDF/XLSX/TXT, trích metadata rule-based, lưu SQLite, quản lý trạng thái và duyệt metadata trước khi dùng cho AI Search ở Sprint 5.

Chạy kiểm thử:

```bash
python -m pytest -q
```

Chạy ứng dụng:

```bash
python -m streamlit run app/main.py
```

## Sprint 5 - Build 0.5

AI Knowledge Engine là lõi tri thức offline của hệ thống. Sprint này không thêm Chat UI và không để AI tự ghi dữ liệu nghiệp vụ.

Thành phần chính:

- Chunk engine rule-based.
- Keyword/entity engine rule-based.
- Relation engine và knowledge graph SQLite.
- Embedding backend có thể thay thế, gồm local deterministic backend và Ollama backend.
- Semantic search Top K có score và citation.

## Build 0.5.1 - AI Core Optimization

Build tối ưu hóa Sprint 4 + Sprint 5:

- Incremental indexing theo checksum.
- Embedding cache để không gọi lại backend khi nội dung không đổi.
- Rich citation sẵn cho UI Sprint sau.
- Relation graph tránh trùng và có confidence.
- Batch processing có progress callback.
- Document Library tự đồng bộ Knowledge Engine khi thêm/sửa/xóa file.

## Cài đặt nhanh

```bash
cd BXD_Smart_Office
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m database.init_db
pytest -q
streamlit run app/main.py
```

## Lưu ý nâng cấp

Nếu đã tải nhiều phần Build 0.1 và Build 0.2 trước đó, chỉ cần giải nén bản mới nhất **Build 0.2.2** vào một thư mục sạch. Không cần ghép từng file cũ bằng tay.

Nếu muốn giữ dữ liệu cũ, sao lưu file:

```text
database/bxd_smart_office.db
workspace/uploads/
workspace/exports/
```

sau đó chép vào Build 0.2.2 và chạy:

```bash
python -m database.init_db
```

Lệnh này sẽ tự bổ sung bảng/cột mới.


## Quy trình Git

Sau khi cập nhật source:

```bash
python -m database.init_db
pytest -q
git add .
git commit -m "chore(architecture): harden project foundation"
```


## Sprint 3 - Build 0.3

Phân hệ Soạn thảo văn bản hỗ trợ nạp mẫu, phân tích bố cục, gợi ý mẫu, sinh dự thảo chờ duyệt, kiểm tra thể thức và xuất DOCX.

Chạy kiểm thử:

```bash
python -m pytest -q
```

## Sprint 3 - Soạn thảo văn bản

### Build 0.3.0 - Patch B

Đã bổ sung Upload Engine cho kho mẫu văn bản:

- Nhận file DOC, DOCX, PDF.
- Lưu file vào `documents/templates/`.
- Tạo tên file an toàn, tránh trùng.
- Tính checksum SHA-256.
- Đăng ký mẫu vào bảng `document_templates`.

Chạy kiểm thử:

```bash
python -m pytest -q
```

### Sprint 3 hoàn thiện

- Mở menu `Soạn thảo văn bản` trong sidebar.
- Nạp và phân tích mẫu văn bản chuẩn.
- Nhập yêu cầu soạn thảo, nhận gợi ý mẫu gần nhất.
- Sinh dự thảo ở trạng thái chờ duyệt.
- Cấu hình thể thức: cơ quan, ký hiệu, địa danh, người ký, font, lề.
- Kiểm tra nhanh thể thức và xuất DOCX theo cấu hình.
