# Build 0.5.0 - Sprint 5 AI Knowledge Engine

## Phạm vi

Sprint 5 xây dựng lõi AI Knowledge Engine. Không làm Chat UI, chatbot, agent, AI Draft hay AI Summary trên giao diện.

## Pipeline

```text
Document Library
-> Chunk
-> Keyword
-> Relation
-> Knowledge Graph
-> Embedding
-> Semantic Search
-> Citation
```

## Hoàn thành

- Migration `006_ai_knowledge.sql`.
- Models: `KnowledgeDocument`, `KnowledgeChunk`, `KnowledgeEntity`, `KnowledgeRelation`.
- Repository `KnowledgeRepository`.
- Service `KnowledgeService`.
- Chunk engine rule-based theo section văn bản hành chính.
- Keyword/entity engine rule-based: keyword, lĩnh vực, loại văn bản, cơ quan, người ký, số văn bản.
- Relation engine: `replaces`, `references`, `follows`, `implements`, `reports`, `related`.
- Knowledge graph lưu và đọc từ SQLite.
- Embedding backend interface, local deterministic backend và Ollama backend local cho Qwen3.
- Semantic search Top K có score và citation.

## Nguyên tắc

- Không gọi API cloud.
- Không tự ghi dữ liệu nghiệp vụ.
- Không tạo chatbot.
- Kết quả Knowledge Engine là nền kỹ thuật cho Sprint 6.

## Kiểm thử

```bash
python -m pytest -q
```

## Technical Debt Chuyển Sprint Sau

- Chưa có UI AI Search.
- Chưa có OCR PDF scan.
- Chưa tối ưu vector backend bằng FAISS/Chroma.
- Ollama cần máy người dùng có model embedding phù hợp; local hash backend giúp test offline ổn định.
