# BXD Smart Office - Offline

Build hiện tại: **0.2.3**

## Chức năng chính

- Dashboard điều hành.
- Phân hệ 0: Hồ sơ vai trò, nhân sự, mã việc, KPI.
- Phân hệ 1: Quản lý nhiệm vụ, tiến độ, minh chứng, KPI, xuất Excel.
- Workspace Lite: gom nhiệm vụ theo hồ sơ công việc.
- AI Review: duyệt đề xuất trước khi ghi nhiệm vụ.
- Audit Log: nhật ký thao tác hệ thống.
- Architecture Hardening: model nghiệp vụ, thư mục tài liệu/workspace, migration SQL nền.

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

Phân hệ Soạn thảo văn bản bắt đầu từ tầng dữ liệu: mẫu văn bản, section/bố cục và dự thảo.

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

