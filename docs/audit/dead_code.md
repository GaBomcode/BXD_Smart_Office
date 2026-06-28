# Dead Code Audit - Build 0.6.2

## Phạm vi

Đã rà soát function/method/class trong source chính bằng đối chiếu tham chiếu tên trong `app/`, `core/`, `database/`, `models/`, `repositories/`, `services/`, `modules/`, `tests/`.

## Kết quả

Không xóa code. Các API chưa thấy source path gọi trực tiếp đã được đánh dấu:

- `services/template_service.py::TemplateService.list_all`
- `services/document_service.py::DocumentService.create_template_record`
- `services/document_service.py::DocumentService.ensure_template_directory`
- `repositories/knowledge_repository.py::KnowledgeRepository.create_job`
- `repositories/knowledge_repository.py::KnowledgeRepository.finish_job`

## Điều chỉnh

Đã thêm comment:

`# TODO REMOVE AFTER BUILD 1.0`

trước các method trên.

## Rủi ro

- Low: Đây là public/helper API có thể đang được giữ để mở rộng. Vì vậy Build 0.6.2 chỉ đánh dấu, không xóa.

## Kết luận

Dead code audit hoàn tất theo nguyên tắc không xóa và không đổi hành vi.
