# Service Audit - Build 0.6.2

## Phạm vi

Đã kiểm tra các Streamlit page trong `modules/` và các service trong `services/`.

## Cách kiểm tra

- Đối chiếu xử lý AI Draft trong `modules/ai_draft/page.py` với `services/ai_draft_service.py`.
- Đối chiếu Document Library UI với `services/document_library_service.py`.
- Đối chiếu Document Draft UI với `services/document_service.py`.

## Kết quả

- Các page Streamlit chủ yếu nhận input, gọi service, hiển thị kết quả và xử lý state UI.
- Business logic AI Draft như intent detection, template selection, evidence collection, outline/draft generation, review gate và export gate nằm trong `services/ai_draft_service.py`.
- Database write/read đi qua repository.
- Validation nghiệp vụ chính nằm trong service/model, không nằm trực tiếp trong Streamlit page.

## Điều chỉnh

Không refactor workflow. Build 0.6.2 chỉ chuẩn hóa chữ hiển thị và audit.

## Rủi ro

- Low: Một số điều kiện hiển thị trên page là UI flow control, không phải business logic. Cần giữ ranh giới này khi Sprint 7 bổ sung thể thức văn bản.

## Kết luận

Service Layer đạt yêu cầu: AI, database, workflow và validation chính được đặt ở service/repository/model.
