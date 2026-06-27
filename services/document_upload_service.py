"""Upload engine cho kho mẫu văn bản.

Patch B chỉ chịu trách nhiệm nhận file DOC/DOCX/PDF, kiểm tra định dạng,
lưu file vào documents/templates và trả về thông tin đã chuẩn hóa. Việc đọc
nội dung sâu sẽ được bổ sung ở các patch Document Intelligence sau.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import hashlib
import logging
import re
import shutil
from typing import BinaryIO

from core.config import DOCUMENT_TEMPLATE_DIR
from models.document_template import ALLOWED_TEMPLATE_EXTENSIONS
from models.document_upload import DocumentUploadResult

logger = logging.getLogger(__name__)

MAX_TEMPLATE_SIZE_BYTES = 50 * 1024 * 1024


class DocumentUploadService:
    """Lưu và chuẩn hóa file mẫu văn bản được người dùng upload."""

    def __init__(self, template_dir: Path | None = None) -> None:
        self.template_dir = template_dir or DOCUMENT_TEMPLATE_DIR
        self.template_dir.mkdir(parents=True, exist_ok=True)

    def save_local_file(self, source_path: str | Path) -> DocumentUploadResult:
        """Sao chép một file có sẵn trên máy vào kho templates."""
        path = Path(source_path)
        self._validate_source_path(path)
        target_path = self._build_target_path(path.name)
        shutil.copy2(path, target_path)
        logger.info("Uploaded local template file: %s -> %s", path, target_path)
        return self._build_result(original_name=path.name, stored_path=target_path)

    def save_uploaded_file(self, file_obj: BinaryIO, original_name: str) -> DocumentUploadResult:
        """Lưu file từ Streamlit uploader hoặc một stream nhị phân tương đương."""
        safe_original = Path(original_name).name
        ext = Path(safe_original).suffix.lower()
        self._validate_extension(ext)
        target_path = self._build_target_path(safe_original)
        total_size = 0
        with target_path.open("wb") as output:
            while True:
                chunk = file_obj.read(1024 * 1024)
                if not chunk:
                    break
                total_size += len(chunk)
                if total_size > MAX_TEMPLATE_SIZE_BYTES:
                    output.close()
                    target_path.unlink(missing_ok=True)
                    raise ValueError("File mẫu vượt quá giới hạn 50MB")
                output.write(chunk)
        if total_size <= 0:
            target_path.unlink(missing_ok=True)
            raise ValueError("File upload rỗng")
        logger.info("Uploaded stream template file: %s -> %s", safe_original, target_path)
        return self._build_result(original_name=safe_original, stored_path=target_path)

    def _validate_source_path(self, path: Path) -> None:
        """Kiểm tra file nguồn có hợp lệ để upload không."""
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Không tìm thấy file mẫu: {path}")
        self._validate_extension(path.suffix.lower())
        size = path.stat().st_size
        if size <= 0:
            raise ValueError("File mẫu rỗng")
        if size > MAX_TEMPLATE_SIZE_BYTES:
            raise ValueError("File mẫu vượt quá giới hạn 50MB")

    @staticmethod
    def _validate_extension(ext: str) -> None:
        """Chỉ cho phép DOC, DOCX và PDF."""
        if ext.lower() not in ALLOWED_TEMPLATE_EXTENSIONS:
            logger.error("Upload rejected because extension is unsupported: %s", ext)
            raise ValueError("Chỉ hỗ trợ DOC, DOCX và PDF")

    def _build_target_path(self, original_name: str) -> Path:
        """Tạo tên file an toàn, tránh trùng trong kho templates."""
        original = Path(original_name)
        ext = original.suffix.lower()
        self._validate_extension(ext)
        stem = self._slugify(original.stem) or "mau-van-ban"
        date_prefix = datetime.now().strftime("%Y%m%d")
        candidate = self.template_dir / f"{date_prefix}_{stem}{ext}"
        index = 1
        while candidate.exists():
            candidate = self.template_dir / f"{date_prefix}_{stem}_{index}{ext}"
            index += 1
        return candidate

    @staticmethod
    def _slugify(value: str) -> str:
        """Chuẩn hóa tên file để an toàn trên Windows và dễ sao lưu."""
        value = value.strip().lower()
        value = re.sub(r"[^0-9a-zA-ZÀ-ỹ]+", "-", value, flags=re.UNICODE)
        value = re.sub(r"-+", "-", value).strip("-")
        return value[:100]

    @staticmethod
    def _sha256(path: Path) -> str:
        """Tính mã kiểm tra để phát hiện file trùng/lỗi sao chép."""
        digest = hashlib.sha256()
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _build_result(self, *, original_name: str, stored_path: Path) -> DocumentUploadResult:
        """Tạo kết quả upload đã chuẩn hóa."""
        return DocumentUploadResult(
            original_name=original_name,
            stored_name=stored_path.name,
            stored_path=str(stored_path),
            file_ext=stored_path.suffix.lower(),
            file_size=stored_path.stat().st_size,
            checksum_sha256=self._sha256(stored_path),
        )
