# Knowledge Metadata

## Metadata Engine

`services/knowledge_metadata_service.py` đọc `knowledge_documents`, metadata gốc và bản ghi Document Library để tạo `KnowledgeMetadata`.

Thông tin chuẩn hóa:

- `document_number`
- `document_type`
- `normalized_type`
- `field`
- `issuing_agency`
- `signer`
- `issued_date`
- `source_checksum`
- `metadata_hash`

## Authority Engine

Authority Engine là rule-based:

- `central`: cơ quan trung ương như Trung ương, Bộ Chính trị, Ban Bí thư.
- `internal`: văn bản nội bộ Ban Xây dựng Đảng.
- `party_committee`: cấp ủy Đảng như Đảng ủy, Huyện ủy, Tỉnh ủy.
- `normative`: văn bản có tính quy định/quyết định.
- `known_agency`: có cơ quan ban hành nhưng chưa phân nhóm cao hơn.
- `unknown`: thiếu cơ quan ban hành.

## Validity Engine

Validity Engine không tự suy diễn ngoài nguồn:

- `valid`: có ngày văn bản và chưa phát hiện hết hiệu lực.
- `pending`: ngày hiệu lực ở tương lai.
- `expired`: quá ngày hết hiệu lực.
- `unknown`: thiếu ngày văn bản hoặc thiếu metadata đủ tin cậy.

## Relationship Engine V2

Relationship V2 dùng metadata để tạo quan hệ:

- `reports`
- `implements`
- `references`
- `related`

Quan hệ V2 lưu riêng trong `knowledge_relationship_v2`, không ghi đè `knowledge_relations` cũ.

## Citation Metadata

Semantic search result được làm giàu thêm:

- authority level
- validity status
- document type
- issued date
- checksum
- page/section/chunk

Thông tin này giúp Sprint sau render citation có căn cứ hơn.
