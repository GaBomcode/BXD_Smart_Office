"""Reader PDF cho kho văn bản."""

from __future__ import annotations

from pathlib import Path
import logging

from services.readers.base import ReaderResult

logger = logging.getLogger(__name__)


class PdfReader:
    """Đọc PDF bằng PyMuPDF."""

    def read(self, path: str | Path) -> ReaderResult:
        file_path = Path(path)
        try:
            import fitz

            texts: list[str] = []
            with fitz.open(file_path) as document:
                for page in document:
                    texts.append(page.get_text("text"))
                text = "\n".join(texts).strip()
                status = "read" if text else "need_ocr"
                return ReaderResult(
                    text=text,
                    pages=document.page_count,
                    metadata={"page_count": document.page_count},
                    status=status,
                    error=None if text else "PDF không có text layer, cần OCR",
                )
        except Exception as exc:
            logger.exception("Cannot read PDF file: %s", file_path)
            return ReaderResult(text="", status="failed", error=str(exc))
