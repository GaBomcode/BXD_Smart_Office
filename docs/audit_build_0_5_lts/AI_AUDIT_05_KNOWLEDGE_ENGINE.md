# AI_AUDIT_05_KNOWLEDGE_ENGINE

## Tong quan

Knowledge Engine da co pipeline backend-only: Document Library -> Chunk -> Keyword/Entity -> Relation -> Embedding -> Semantic Search -> Citation. Khong co chatbot, khong co agent, khong co AI Draft UI trong module nay.

## Pham vi da doc

- `modules/knowledge_engine/__init__.py`
- `services/knowledge_service.py`
- `repositories/knowledge_repository.py`
- `models/knowledge_document.py`
- `models/knowledge_chunk.py`
- `models/knowledge_entity.py`
- `models/knowledge_relation.py`
- `database/migrations/006_ai_knowledge.sql`
- `database/migrations/007_ai_core_optimization.sql`
- `tests/test_knowledge_foundation.py`
- `tests/test_knowledge_engines.py`
- `tests/test_ai_core_optimization.py`

## Diem dat

- Chunk engine co trong `services/knowledge_service.py`, test tai `tests/test_knowledge_engines.py:20`.
- Keyword/entity engine rule-based, khong dung LLM, test tai `tests/test_knowledge_engines.py:38`.
- Relation engine va graph co test tai `tests/test_knowledge_engines.py:55`.
- Embedding cache co bang `knowledge_embedding_cache` va test tai `tests/test_ai_core_optimization.py:73`.
- Rich citation tra ve title, document number, issued date, page, chunk, section, file path, checksum, relevance tai `services/knowledge_service.py:403`.
- Semantic search tra ve top K va score tai `services/knowledge_service.py:403`.
- `OllamaEmbeddingBackend` ton tai tai `services/knowledge_service.py:108`, mac dinh service dang dung `LocalHashEmbeddingBackend` neu khong cau hinh backend.

## Van de phat hien

- **High**: Ingestion mac dinh khong lay lai toan van tu Document Library. `services/knowledge_service.py:143` nhan tham so `text`, nhung `services/document_library_service.py:231` khong truyen tham so nay; `services/knowledge_service.py:160` tao noi dung tu metadata.
- **Medium**: Semantic search hien tai duyet toan bo chunk trong SQLite: `services/knowledge_service.py:403` lap qua `self.repository.list_chunks()`. Khi kho van ban lon, day la gioi han hieu nang da thay truc tiep trong code.
- **Medium**: Embedding backend mac dinh la local hash trong `services/knowledge_service.py` constructor, con Ollama la backend co san nhung khong phai default. Dieu nay giup test offline on dinh, nhung can cau hinh ro trong moi truong van hanh neu muon dung Ollama/Qwen3.
- **Low**: Citation da giau thong tin, nhung `page` phu thuoc chunk duoc tao tu text dau vao; neu dau vao chi metadata thi page/section khong phan anh van ban goc.

## Muc do rui ro

- Critical: Khong phat hien.
- High: Tri thuc co the thieu toan van.
- Medium: Search vector scan tuyen tinh; cau hinh backend embedding can ro.
- Low: Citation phu thuoc chat luong chunk nguon.

## Khuyen nghi

- Uu tien sua hop dong ingestion de Knowledge Engine nhan extracted text day du.
- Giu interface embedding backend hien co, nhung them cau hinh van hanh cho Ollama trong V1.1.
- Khi du lieu lon, thay vector scan bang backend vector qua abstraction, khong doi nghiep vu.

## Viec nen lam ngay

- Dong bang pham vi Build 0.5 LTS: khong them UI chat/agent.
- Viet note van hanh: mac dinh test/local co the dung hash embedding, production offline can cau hinh Ollama.

## Viec dua vao V1.1

- Full-text ingestion.
- Vector backend thay the SQLite scan.
- Health check cho Ollama/model embedding.

## Ket luan

Knowledge Engine da dung vai tro "bo nao" backend, khong bi bien thanh chatbot. Dieu kien quan trong truoc Sprint 6 la dam bao no duoc nuoi bang toan van, khong chi metadata.
