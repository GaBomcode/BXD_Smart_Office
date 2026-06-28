# Build 0.6.0 - AI Draft Foundation

## Tong quan

Build 0.6.0 khoi dong Sprint 6: AI Draft Engine. Engine nay dung Knowledge Engine hien co de tham muu soan thao van ban co citation, nhung khong phai chatbot va khong tu quyet dinh thay nguoi dung.

## Pham vi

- Python 3.12.
- Streamlit.
- SQLite.
- Repository Pattern.
- Service Layer.
- MVC/module architecture.
- Khong goi API cloud.
- Khong lam Sprint 7.

## Thanh phan moi

- `models/ai_draft_request.py`
- `models/ai_draft_result.py`
- `models/ai_draft_citation.py`
- `repositories/ai_draft_repository.py`
- `services/ai_draft_service.py`
- `modules/ai_draft/page.py`
- `database/migrations/008_ai_draft_engine.sql`
- `tests/test_ai_draft_foundation.py`

## Database

Migration `008_ai_draft_engine.sql` tao:

- `ai_draft_requests`
- `ai_draft_results`
- `ai_draft_citations`
- `ai_draft_revisions`

Bang moi co index theo request, result, status va citation type de phuc vu workflow duyet.

## Workflow

1. Nguoi dung nhap yeu cau.
2. He thong nhan dien loai van ban rule-based.
3. Neu confidence thap, nguoi dung chon lai loai van ban.
4. He thong goi y mau top 5 kem citation.
5. He thong thu thap can cu bang semantic search kem citation day du.
6. He thong sinh dan y, trang thai `pending_outline_review`.
7. Nguoi dung duyet hoac sua dan y.
8. He thong moi sinh noi dung du thao, trang thai `pending_user_review`.
9. Nguoi dung sua va duyet du thao.
10. Chi du thao da duyet moi duoc xuat DOCX.

## Nguyen tac an toan

- AI chi tham muu.
- Khong co chatbot.
- Khong co agent.
- Khong tu ban hanh.
- Khong co nguon thi khong khang dinh chac chan.
- Moi du thao phai kem citation neu co nguon trong Knowledge Engine.

## Kiem thu

Test moi bao phu:

- Migration foundation.
- Intent detection va chon lai loai van ban khi confidence thap.
- Template selector top 5 co citation.
- Evidence collector dung semantic search.
- Outline review gate.
- Draft review gate.
- Export DOCX chi sau approval.

Chay:

```bash
python -m pytest -q
```

## Kiem tra thu cong tren giao dien

1. Chay ung dung:

```bash
streamlit run app/main.py
```

2. Mo menu `AI Soạn thảo`.
3. Tab `Yeu cau`: nhap yeu cau soan thao va tao request.
4. Neu confidence thap, chon lai loai van ban.
5. Tab `Mau & can cu`: goi y mau va tim van ban can cu.
6. Tab `Dan y`: sinh dan y, sua neu can va duyet.
7. Tab `Du thao`: sinh noi dung, sua va duyet.
8. Tab `Duyet & xuat`: xuat DOCX sau khi du thao da duyet.

## Technical debt chuyen Sprint 7

- Hoan thien the thuc Dang 100% khi export DOCX.
- Nang cap full-text ingestion tu Document Library sang Knowledge Engine theo audit Build 0.5 LTS.
- Bo sung LLM abstraction neu can sinh van ban linh hoat hon; van khong dung API cloud.
- Cai thien UI citation de hien thi nguon gon hon.

## Ket luan

Build 0.6.0 dat nen mong AI Draft Foundation: co request, intent, template, evidence, outline, draft, review, citation va export co dieu kien. He thong van giu nguyen nguyen tac nguoi dung quyet dinh cuoi cung.
