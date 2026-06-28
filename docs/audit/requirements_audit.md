# Requirements Audit - Build 0.6.2

## Phạm vi

Đã đối chiếu `requirements.txt` với import thực tế trong source/test.

## Kết quả

- `streamlit`: dùng trong `app/` và `modules/`.
- `pandas`: dùng trong dashboard, document UI, task export/UI.
- `openpyxl`: dùng trong reader/test Excel.
- `python-docx`: dùng trong document service/export và test reader/export.
- `PyMuPDF`: import dạng `fitz` trong PDF reader/document service.
- `requests`: dùng trong `services/knowledge_service.py` cho Ollama backend local.
- `pytest`: dùng cho test suite.

## Điều chỉnh

Không bỏ package và không bổ sung package mới.

## Rủi ro

- Low: `requests` chỉ cần khi dùng Ollama backend; vẫn là dependency hợp lệ theo Sprint 5/6.

## Kết luận

`requirements.txt` phù hợp với import thực tế.
