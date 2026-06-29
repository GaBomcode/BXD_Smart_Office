# Knowledge Schema

## Migration

Build 0.7.1 thêm:

`database/migrations/009_knowledge_metadata_engine.sql`

Migration chỉ dùng:

- `CREATE TABLE IF NOT EXISTS`
- `CREATE INDEX IF NOT EXISTS`

Không dùng `ALTER TABLE`, không đổi bảng cũ.

## Bảng mới

### knowledge_metadata

Lưu metadata chuẩn hóa cho mỗi `knowledge_document`.

Trường chính:

- `knowledge_document_id`
- `library_document_id`
- `document_number`
- `document_type`
- `normalized_type`
- `authority_level`
- `authority_score`
- `validity_status`
- `metadata_hash`

### knowledge_relationship_v2

Lưu quan hệ metadata V2.

Trường chính:

- `source_knowledge_document_id`
- `target_knowledge_document_id`
- `relation_type`
- `direction`
- `weight`
- `confidence`
- `evidence_json`

### knowledge_citation_metadata

Lưu citation metadata từ semantic search.

Trường chính:

- `query_text`
- `source_knowledge_document_id`
- `source_chunk_id`
- `authority_level`
- `validity_status`
- `score`
- `citation_json`

### knowledge_metadata_cache

Cache payload metadata theo:

- `cache_key`
- `knowledge_document_id`
- `source_checksum`
- `metadata_hash`
- `payload_json`

## Repository

`repositories/knowledge_repository.py` được mở rộng bằng các method:

- `upsert_metadata`
- `get_metadata`
- `list_metadata`
- `replace_relationships_v2_for_document`
- `list_relationships_v2`
- `add_citation_metadata`
- `list_citation_metadata`
- `upsert_metadata_cache`
- `get_metadata_cache`
