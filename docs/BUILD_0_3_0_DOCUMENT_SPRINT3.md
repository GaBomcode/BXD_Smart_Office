# Build 0.3.0 - Sprint 3 Document Module

## Phạm vi

Hoàn thiện phân hệ Soạn thảo văn bản theo MASTER DESIGN V1.1 ở mức offline, giữ nguyên nghiệp vụ Sprint 1 và Sprint 2.

## Hoàn thành

- Thêm giao diện Streamlit `Soạn thảo văn bản`.
- Nạp mẫu DOC, DOCX, PDF từ giao diện.
- Phân tích mẫu DOCX/PDF để nhận diện bố cục, tín hiệu thể thức, từ khóa.
- Gợi ý mẫu gần nhất theo loại văn bản, lĩnh vực và nội dung yêu cầu.
- Liệt kê thông tin còn thiếu trước khi sinh dự thảo.
- Sinh dự thảo ở trạng thái `Chờ duyệt`; người dùng xem/sửa trước khi xuất.
- Kiểm tra nhanh thể thức: quốc hiệu, tiêu ngữ, số ký hiệu, nơi nhận, chữ ký.
- Xuất dự thảo sang DOCX và lưu đường dẫn vào `document_drafts`.
- Cấu hình thể thức văn bản: tên cơ quan, ký hiệu, địa danh, nơi nhận mặc định, người ký, font và lề.
- Xuất DOCX theo cấu hình thể thức đã duyệt.

## Nguyên tắc

AI/offline engine chỉ tham mưu. Dự thảo luôn đi qua màn hình duyệt, người dùng chỉnh sửa trước khi xuất DOCX.

## Kiểm thử

```bash
python -m pytest -q
```
