# AI_AUDIT_06_UI_UX

## Tong quan

UI hien tai la Streamlit local/offline, phuc vu Dashboard, Ho so, Nhiem vu, Soan thao van ban va Kho van ban. Sprint 5/Build 0.5.1 khong them Chat UI, dung yeu cau dong bang AI Core backend.

## Pham vi da doc

- `app/main.py`
- `app/router.py`
- `core/theme.py`
- `modules/dashboard/page.py`
- `modules/document_library/page.py`
- `modules/documents/page.py`
- `modules/profile/page.py`
- `modules/tasks/page.py`
- `modules/knowledge_engine/__init__.py`

## Diem dat

- Menu chinh duoc khai bao ro tai `app/router.py:9-13`.
- Khong co menu Chat, Agent, AI Draft moi trong router.
- UI kho van ban co scan/index, loc theo loai/co quan/linh vuc/nam/keyword, xem chi tiet va cap nhat metadata.
- UI soan thao van ban van nam trong Sprint 3, khong bi mo rong sang AI Draft trong Build 0.5.1.
- Theme tap trung o `core/theme.py`.

## Van de phat hien

- **Medium**: `modules/document_library/page.py:18` cho nguoi dung nhap duong dan thu muc nguon bang text input. Chua thay UI xac nhan rui ro hay gioi han root theo cau hinh.
- **Low**: Ket qua scan va chi tiet van ban duoc render bang `st.json` tai `modules/document_library/page.py:31` va `modules/document_library/page.py:59`. Cach nay huu ich cho debug/audit, nhung chua phai trai nghiem nguoi dung cuoi cho van hanh dai han.
- **Low**: `modules/knowledge_engine/` chua co trang UI. Day la dung yeu cau "khong phat trien UI truoc" cua Sprint 5, nhung can ghi ro de nguoi nghiem thu khong tim Chat UI.

## Muc do rui ro

- Critical: Khong phat hien.
- High: Khong phat hien.
- Medium: Nhap path tu do trong UI kho van ban.
- Low: Mot so hien thi con thien ve ky thuat.

## Khuyen nghi

- Giu nguyen viec khong co UI chat/agent trong Build 0.5 LTS.
- V1.1 nen co cau hinh root kho van ban va UI xac nhan truoc khi index hang loat.
- Thay `st.json` bang bang/tom tat than thien hon khi vao giai do polish UI.

## Viec nen lam ngay

- Ghi chu trong release: Knowledge Engine la backend-only.
- Huong dan nguoi van hanh chon dung thu muc kho van ban khi index.

## Viec dua vao V1.1

- UI quan tri indexing co progress va lich su job than thien hon.
- UI citation/render ket qua chi nen lam sau khi Sprint 6/7 bat dau dung AI Core.

## Ket luan

UI hien tai phu hop trang thai Build 0.5 LTS: du de van hanh kho van ban, khong vuot pham vi sang chat hay AI Draft. Diem can canh la nhap path tu do trong Document Library.
