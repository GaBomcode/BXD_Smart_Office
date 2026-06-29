# Knowledge Engine

## Tổng quan

Knowledge Engine là lõi tri thức offline của BXD Smart Office. Engine không phải chatbot, không tự quyết định nghiệp vụ và không tự ghi dữ liệu nghiệp vụ ngoài các bảng chỉ mục/citation/cache kỹ thuật.

## Pipeline hiện tại

```text
Document Library
-> Knowledge Document
-> Chunk
-> Entity / Keyword
-> Relation
-> Embedding
-> Semantic Search
-> Citation
-> Metadata Enrichment
```

## Build 0.7.1

Build 0.7.1 bổ sung lớp Knowledge Metadata Engine:

- Metadata Engine: chuẩn hóa loại văn bản, số ký hiệu, lĩnh vực, cơ quan, người ký, ngày văn bản.
- Authority Engine: đánh giá mức thẩm quyền từ cơ quan ban hành và loại văn bản bằng rule-based logic.
- Validity Engine: xác định trạng thái hiệu lực ở mức tham mưu dựa trên ngày văn bản/ngày hiệu lực/ngày hết hiệu lực.
- Relationship Engine V2: sinh quan hệ metadata độc lập với relation cũ.
- Citation Metadata: làm giàu semantic search citation bằng authority và validity.
- Metadata Cache: lưu payload metadata theo checksum/hash để tránh xử lý lại.

## Nguyên tắc

- Không khẳng định chắc chắn khi thiếu nguồn.
- Không thay đổi Document Library hoặc AI Draft workflow.
- Không gọi API cloud.
- Không thay thế quyết định của người dùng.
