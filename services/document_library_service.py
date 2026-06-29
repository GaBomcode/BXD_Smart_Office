"""Service nghiệp vụ cho phân hệ Kho văn bản."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
import hashlib
import logging

from models.document_keyword import DocumentKeyword
from models.library_document import LibraryDocument
from repositories.document_library_repository import DocumentLibraryRepository
from services.document_metadata_extractor import DocumentMetadataExtractor
from services.readers import DocxReader, PdfReader, ReaderResult, TxtReader, XlsxReader

logger = logging.getLogger(__name__)

SUPPORTED_LIBRARY_EXTENSIONS = {".doc", ".docx", ".pdf", ".xlsx", ".xls", ".txt"}
IGNORED_FILE_NAMES = {"desktop.ini"}
IGNORED_SUFFIXES = {".tmp", ".lock"}


@dataclass(slots=True)
class ScanResult:
    """Kết quả quét thư mục ở mức metadata."""

    root_path: str
    total_files: int = 0
    accepted_files: int = 0
    ignored_files: int = 0
    new_files: int = 0
    changed_files: int = 0
    existing_files: int = 0
    unsupported_files: int = 0
    files: list[dict[str, Any]] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "root_path": self.root_path,
            "total_files": self.total_files,
            "accepted_files": self.accepted_files,
            "ignored_files": self.ignored_files,
            "new_files": self.new_files,
            "changed_files": self.changed_files,
            "existing_files": self.existing_files,
            "unsupported_files": self.unsupported_files,
            "files": self.files or [],
        }


class DocumentLibraryService:
    """Điều phối scanner, reader, extractor và repository cho kho văn bản."""

    def __init__(self, repository: DocumentLibraryRepository | None = None) -> None:
        self.repository = repository or DocumentLibraryRepository()
        self.extractor = DocumentMetadataExtractor()

    def scan_folder(self, root_path: str | Path) -> ScanResult:
        """Quét thư mục nhiều tầng, chỉ lấy metadata và checksum."""
        root = Path(root_path)
        if not root.exists() or not root.is_dir():
            raise FileNotFoundError(f"Không tìm thấy thư mục kho văn bản: {root}")
        result = ScanResult(root_path=str(root), files=[])
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            result.total_files += 1
            if self._should_ignore(path):
                result.ignored_files += 1
                continue
            ext = path.suffix.lower()
            if ext not in SUPPORTED_LIBRARY_EXTENSIONS:
                result.unsupported_files += 1
                continue
            checksum = self.calculate_checksum(path)
            existing = self.repository.get_by_path(str(path))
            state = "new"
            if existing and existing.get("checksum") == checksum:
                state = "existing"
                result.existing_files += 1
            elif existing:
                state = "changed"
                result.changed_files += 1
            else:
                result.new_files += 1
            result.accepted_files += 1
            result.files.append(
                {
                    "file_name": path.name,
                    "file_path": str(path),
                    "file_ext": ext,
                    "file_size": path.stat().st_size,
                    "checksum": checksum,
                    "state": state,
                }
            )
        logger.info("Scanned document library folder %s: %s accepted", root, result.accepted_files)
        return result

    def register_file_metadata(self, file_info: dict[str, Any], *, status: str = "new") -> int:
        """Ghi metadata file vào kho văn bản, chưa đọc nội dung."""
        path = Path(str(file_info["file_path"]))
        document = LibraryDocument(
            title=path.stem,
            file_name=str(file_info.get("file_name") or path.name),
            file_path=str(path),
            file_ext=str(file_info.get("file_ext") or path.suffix.lower()),
            file_size=int(file_info.get("file_size") or path.stat().st_size),
            checksum=str(file_info.get("checksum") or self.calculate_checksum(path)),
            status=status,
        )
        return self.repository.upsert_document(document)

    def read_document(self, path: str | Path) -> ReaderResult:
        """Đọc nội dung file bằng reader phù hợp."""
        file_path = Path(path)
        ext = file_path.suffix.lower()
        if ext in {".doc", ".docx"}:
            return DocxReader().read(file_path)
        if ext == ".pdf":
            return PdfReader().read(file_path)
        if ext in {".xls", ".xlsx"}:
            return XlsxReader().read(file_path)
        if ext == ".txt":
            return TxtReader().read(file_path)
        return ReaderResult(text="", status="unsupported", error=f"Không hỗ trợ định dạng {ext}")

    def index_file(self, file_info: dict[str, Any]) -> int:
        """Đọc nội dung, trích metadata và persist một văn bản."""
        path = Path(str(file_info["file_path"]))
        checksum = str(file_info.get("checksum") or self.calculate_checksum(path))
        duplicate = self.repository.get_by_checksum(checksum)
        existing = self.repository.get_by_path(str(path))
        if duplicate and (not existing or int(duplicate["id"]) != int(existing["id"])):
            document_id = self.register_file_metadata({**file_info, "checksum": checksum}, status="duplicate")
            self.repository.update_document(document_id, {"summary": f"Trùng checksum với văn bản #{duplicate['id']}"})
            return document_id

        reader_result = self.read_document(path)
        status = self._status_from_reader(reader_result)
        metadata = self.extractor.extract(reader_result.text, file_name=path.name) if reader_result.text else {}
        title = str(metadata.get("title") or path.stem)
        document = LibraryDocument(
            title=title,
            file_name=str(file_info.get("file_name") or path.name),
            file_path=str(path),
            file_ext=str(file_info.get("file_ext") or path.suffix.lower()),
            file_size=int(file_info.get("file_size") or path.stat().st_size),
            checksum=checksum,
            document_type=metadata.get("document_type"),
            document_number=metadata.get("document_number"),
            issued_date=metadata.get("issued_date"),
            issuing_agency=metadata.get("issuing_agency"),
            signer=metadata.get("signer"),
            summary=metadata.get("summary") or reader_result.error,
            keywords=metadata.get("keywords"),
            field=metadata.get("field"),
            status=status,
            indexed_at=datetime.now().isoformat(timespec="seconds") if status in {"indexed", "need_review"} else None,
        )
        document_id = self.repository.upsert_document(document)
        if document.keywords:
            self._replace_keyword_text(document_id, document.keywords)
        return document_id

    def index_folder(
        self,
        root_path: str | Path,
        *,
        batch_size: int = 50,
        progress_callback: Callable[[dict[str, int]], None] | None = None,
        sync_knowledge: bool = True,
    ) -> dict[str, Any]:
        """Quét và index toàn bộ file trong thư mục nguồn."""
        if batch_size <= 0:
            raise ValueError("batch_size phải lớn hơn 0")
        scan = self.scan_folder(root_path)
        indexed_ids: list[int] = []
        counts = {
            "indexed": 0,
            "failed": 0,
            "need_ocr": 0,
            "need_review": 0,
            "duplicate": 0,
            "unsupported": 0,
            "existing": 0,
            "deleted": 0,
        }
        files = scan.files or []
        processed = 0
        for start in range(0, len(files), batch_size):
            for file_info in files[start : start + batch_size]:
                processed += 1
                if file_info["state"] == "existing":
                    counts["existing"] += 1
                    if progress_callback:
                        progress_callback({"total": len(files), "processed": processed, **counts})
                    continue
                document_id = self.index_file(file_info)
                indexed_ids.append(document_id)
                document = self.repository.get_document(document_id) or {}
                status = str(document.get("status") or "failed")
                counts[status] = counts.get(status, 0) + 1
                if sync_knowledge and status in {"need_review", "indexed"}:
                    self.sync_knowledge_document(document_id)
                if progress_callback:
                    progress_callback({"total": len(files), "processed": processed, **counts})
        if sync_knowledge:
            counts["deleted"] = self.mark_missing_files_deleted(root_path)
            self.sync_deleted_knowledge_documents()
        logger.info("Indexed folder %s: %s", root_path, counts)
        return {"scan": scan.to_dict(), "indexed_ids": indexed_ids, "counts": counts}

    def mark_missing_files_deleted(self, root_path: str | Path) -> int:
        """Đánh dấu các file từng index nhưng đã bị xóa khỏi thư mục nguồn."""
        root = Path(root_path).resolve()
        deleted = 0
        for document in self.repository.list_documents(limit=None):
            file_path = Path(str(document.get("file_path") or ""))
            try:
                resolved = file_path.resolve()
            except OSError:
                resolved = file_path
            if str(resolved).startswith(str(root)) and not file_path.exists() and document.get("status") != "deleted":
                self.repository.update_document(int(document["id"]), {"status": "deleted"})
                deleted += 1
        return deleted

    def sync_knowledge_document(self, library_document_id: int) -> int:
        """Đồng bộ một văn bản kho sang Knowledge Engine theo incremental checksum."""
        from services.knowledge_service import KnowledgeService

        document = self.repository.get_document(library_document_id)
        if not document:
            raise ValueError("Khong tim thay van ban kho")
        reader_result = self.read_document(str(document.get("file_path") or ""))
        return KnowledgeService(library_repository=self.repository).ingest_library_document(
            library_document_id,
            text=reader_result.text,
        )

    def sync_deleted_knowledge_documents(self) -> int:
        """Đồng bộ trạng thái xóa từ Document Library sang Knowledge Engine."""
        from services.knowledge_service import KnowledgeService

        return KnowledgeService(library_repository=self.repository).sync_deleted_library_documents()

    def list_documents(self, **filters: Any) -> list[dict[str, Any]]:
        """Danh sách văn bản trong kho."""
        return self.repository.list_documents(**filters)

    def get_document(self, document_id: int) -> dict[str, Any] | None:
        return self.repository.get_document(document_id)

    def status_counts(self) -> dict[str, int]:
        return self.repository.status_counts()

    def filter_values(self) -> dict[str, list[str]]:
        return {
            "file_ext": self.repository.distinct_values("file_ext"),
            "document_type": self.repository.distinct_values("document_type"),
            "field": self.repository.distinct_values("field"),
            "issuing_agency": self.repository.distinct_values("issuing_agency"),
            "status": self.repository.distinct_values("status"),
        }

    def update_review_metadata(self, document_id: int, data: dict[str, Any], *, actor: str = "Người dùng") -> int:
        """Cập nhật metadata sau khi người dùng duyệt/sửa."""
        allowed = {
            "title",
            "document_type",
            "document_number",
            "issued_date",
            "issuing_agency",
            "signer",
            "summary",
            "keywords",
            "field",
            "status",
        }
        cleaned = {key: value for key, value in data.items() if key in allowed}
        if not cleaned:
            return 0
        if cleaned.get("status") is None:
            cleaned["status"] = "indexed"
        result = self.repository.update_document(document_id, cleaned)
        if "keywords" in cleaned:
            self._replace_keyword_text(document_id, str(cleaned.get("keywords") or ""))
        self._log_review_action(actor, document_id, cleaned)
        return result

    @staticmethod
    def _status_from_reader(reader_result: ReaderResult) -> str:
        if reader_result.status == "read":
            return "need_review"
        if reader_result.status == "need_ocr":
            return "need_ocr"
        if reader_result.status == "unsupported":
            return "unsupported"
        return "failed"

    def _replace_keyword_text(self, document_id: int, keywords: str) -> None:
        values = [item.strip() for item in keywords.split(",") if item.strip()]
        self.repository.replace_keywords(
            document_id,
            [DocumentKeyword(keyword=value, weight=max(1, 10 - index)) for index, value in enumerate(values)],
        )

    def _log_review_action(self, actor: str, document_id: int, data: dict[str, Any]) -> None:
        try:
            self.repository.execute(
                "INSERT INTO audit_logs(actor, action, entity_type, entity_id, detail) VALUES(?,?,?,?,?)",
                (actor, "Duyệt metadata kho văn bản", "document", document_id, str(data)[:500]),
            )
        except Exception as exc:
            logger.warning("Cannot write audit log for document review: %s", exc)

    @staticmethod
    def calculate_checksum(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _should_ignore(path: Path) -> bool:
        name = path.name.lower()
        return name.startswith("~$") or name in IGNORED_FILE_NAMES or path.suffix.lower() in IGNORED_SUFFIXES
